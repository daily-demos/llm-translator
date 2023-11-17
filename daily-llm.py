import argparse
import os
import random
import re
import time
from threading import Thread

from daily import EventHandler, CallClient, Daily
from datetime import datetime
from dotenv import load_dotenv

import config

from orchestrator import Orchestrator
from auth import get_meeting_token, get_room_name

load_dotenv()

class DailyLLM(EventHandler):
    def __init__(
            self,
            room_url=os.getenv("DAILY_URL"),
            token=os.getenv('DAILY_TOKEN'),
            bot_name="Translator",
            in_language="spanish",
            out_language="english"
        ):
        
        self.deepgram_languages = {"spanish": "es", "english": "en", "japanese": "ja"}

        # room + bot details
        self.room_url = room_url
        self.in_language = in_language
        self.out_language = out_language
        room_name = get_room_name(room_url)
        if token:
            self.token = token
        else:
            self.token = get_meeting_token(room_name, os.getenv("DAILY_API_KEY"))
        
        # hard-coding this so clients can find translators
        self.bot_name = f"tb-{self.in_language}-{self.out_language}"
        # Keep participant IDs of anyone that speaks this language
        # So we know to collect their transcription messages
        self.participant_langs = {}

        duration = os.getenv("BOT_MAX_DURATION")
        if not duration:
            duration = 300
        else:
            duration = int(duration)
        self.expiration = time.time() + duration

        print(f"{room_url} Joining", self.room_url, "as", self.bot_name, "leaving at", self.expiration, "current time is", time.time())

        self.print_debug(f"expiration: {datetime.utcfromtimestamp(self.expiration).strftime('%Y-%m-%d %H:%M:%S')}")
        self.print_debug(f"now: {datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}")

        self.my_participant_id = None

        self.print_debug("configuring services")
        self.configure_ai_services()
        self.print_debug("configuring daily")
        self.configure_daily()

        self.stop_threads = False

        self.print_debug("starting orchestrator")
        self.orchestrator = Orchestrator(self, self.mic, self.tts, self.llm, self.story_id, self.in_language, self.out_language)
        self.orchestrator.action()

        self.participant_left = False

        try:
            participant_count = len(self.client.participants())
            self.print_debug(f"{participant_count} participants in room")
            while time.time() < self.expiration and not self.participant_left:
                # all handling of incoming transcriptions happens in on_transcription_message
                time.sleep(1)
        except Exception as e:
            self.print_debug(f"Exception {e}")
        finally:
            #self.client.stop_transcription()
            self.client.leave()

        self.stop_threads = True
        self.print_debug("Shutting down")

    def print_debug(self, s):
        print(f"{self.room_url} {s}", flush=True)

    def configure_ai_services(self):
        self.story_id = hex(random.getrandbits(128))[2:]

        self.tts = config.services[os.getenv("TTS_SERVICE")]()
        self.llm = config.services[os.getenv("LLM_SERVICE")]()

    def configure_daily(self):
        Daily.init()
        self.client = CallClient(event_handler = self)

        self.mic = Daily.create_microphone_device("mic", sample_rate = 16000, channels = 1)
        self.speaker = Daily.create_speaker_device("speaker", sample_rate = 16000, channels = 1)

        Daily.select_speaker_device("speaker")

        self.client.set_user_name(self.bot_name)
        self.client.join(self.room_url, self.token, completion=self.call_joined)

        self.client.update_inputs({
            "camera": {
                "isEnabled": False,
            },
            "microphone": {
                "isEnabled": True,
                "settings": {
                    "deviceId": "mic"
                }
            }
        })

        self.my_participant_id = self.client.participants()['local']['id']
        

    def send_languages(self):
        self.client.send_app_message({"msg": "translatorbot", "data": {"in": self.in_language, "out": self.out_language}})

    def call_joined(self, join_data, client_error):
        self.print_debug(f"call_joined: {join_data}, {client_error}, deepgram language: {self.deepgram_languages[self.in_language]}")
        #self.client.start_transcription(settings={"language": "es"})
        #self.client.start_transcription(settings={"language": self.deepgram_languages[self.in_language] })
        #self.client.start_transcription()
        self.send_languages()
        self.client.send_app_message({"msg": "request-languages"})
        # print(f"Transcription started, hopefully")
        # If you have access to Deepgram's nova-2 model, you can comment out
        # the line above, and uncomment this line instead:
        # self.client.start_transcription(settings={"model": "nova-2-ea" })



    def on_participant_updated(self, participant):
        # print(f"Participant updated: {participant}")
        pass
    
    def on_app_message(self, message, sender):
        print(f"App message received: {message}, sender: {sender}")
        if message['msg'] == 'request-languages':
            self.send_languages()
        elif message['msg'] == 'participant':
            self.participant_langs[sender] = message['data']['lang']
            print(f"Participant langs updated; now it's {self.participant_langs}")

    def on_call_state_updated(self, call_state):
        pass

    def on_inputs_updated(self, inputs):
        pass

    def on_participant_counts_updated(self, participant_counts):
        pass

    def on_active_speaker_changed(self, active_speaker):
        pass

    def on_network_stats_updated(self, network_stats):
        pass

    def on_participant_joined(self, participant):
        pass

    def on_participant_left(self, participant, reason):
        pass
        # Uncomment if we want to leave when the participant leaves
        
        # if len(self.client.participants()) < 2:
            # self.print_debug("participant left")
            # self.participant_left = True

    def on_transcription_message(self, message):
        #if message['session_id'] != self.my_participant_id:
        if not re.match(r"tb\-.*", message['user_name']):
            print(f"💼 Got transcription: {message}")
            print(f"speaker lang: {self.participant_langs[message['session_id']]}")
            if self.participant_langs[message['session_id']] and self.participant_langs[message['session_id']]['spoken'] == self.in_language:
                message['voice'] = self.participant_langs[message['session_id']]['voice']
                print(f"handling user speech: {message}")
                self.orchestrator.handle_user_speech(message)
                # re-emit transcription with language info
                message['translation_language'] = self.in_language
                message['translation'] = message['text']
                self.client.send_app_message(message)
            else:
                print(f"not handling user speech for non-translated language: {message}")


            
        else:
            print(f"💼 Got transcription from translator {message['user_name']}, ignoring")

    def send_app_message(self, message):
        self.client.send_app_message(message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily LLM bot")
    parser.add_argument("-u", "--url", type=str, help="URL of the Daily room")
    parser.add_argument("-t", "--token", type=str, help="Token for Daily API")
    parser.add_argument("-b", "--bot-name", type=str, help="Name of the bot")
    parser.add_argument("-i", "--in_language", type=str, help="Language. Try 'french', 'spanish', 'japanese', or 'english'")
    parser.add_argument("-o", "--out_language", type=str, help="Language. Try 'french', 'spanish', 'japanese', or 'english'")

    args = parser.parse_args()

    url = args.url or os.getenv("DAILY_URL")
    bot_name = args.bot_name or "Translatorbot"
    token = args.token or None
    in_language = args.in_language or "spanish"
    out_language = args.out_language or "english"

    app = DailyLLM(os.getenv("DAILY_URL"), os.getenv("DAILY_TOKEN"), "Translatorbot", in_language, out_language)
