import json
import io
import random
import re
import struct
import time
import traceback
from datetime import datetime
from queue import Queue
from queue import Empty

from services.mock_ai_service import MockAIService

from scenes.translator_scene import TranslatorScene

from threading import Thread

class Orchestrator():
    def __init__(self, image_setter, microphone, ai_tts_service, ai_image_gen_service, ai_llm_service, story_id, in_language, out_language):
        self.image_setter = image_setter
        self.microphone = microphone

        self.ai_tts_service = ai_tts_service
        self.ai_image_gen_service = ai_image_gen_service
        self.ai_llm_service = ai_llm_service

        
        self.in_language = in_language
        self.out_language = out_language

        self.tts_getter = None
        self.image_getter = None
        self.llm_response_thread = None

        self.scene_queue = Queue()
        self.stop_threads = False

    def handle_user_speech(self, message):
        print(f"👅 Handling user speech: {message}")
        Thread(target=self.request_llm_response, args=(message,)).start()

    def request_llm_response(self, message):
        try:
            msgs = [{"role": "system", "content": f"You will be provided with a sentence in {self.in_language.capitalize()}, and your task is to translate it into {self.out_language.capitalize()}."}, {"role": "user", "content": message['text']}]
            message['response'] = self.ai_llm_service.run_llm(msgs)
            self.handle_translation(message)
        except Exception as e:
            print(f"Exception in request_llm_response: {e}")

    def handle_translation(self, message):
        # Do this all as one piece, at least for now
        llm_response = message['response']
        out = ''
        for chunk in llm_response:
            if len(chunk["choices"]) == 0:
                continue
            if "content" in chunk["choices"][0]["delta"]:
                if chunk["choices"][0]["delta"]["content"] != {}: #streaming a content chunk
                    next_chunk = chunk["choices"][0]["delta"]["content"]
                    out += next_chunk
        #sentence = self.ai_tts_service.run_tts(out)
        message['translation'] = out
        message['translation_language'] = self.out_language
        self.enqueue(TranslatorScene, message=message)

    def request_tts(self, message):
        try:
            for chunk in self.ai_tts_service.run_tts(message):
                yield chunk
        except Exception as e:
            print(f"Exception in request_tts: {e}")
            
    def handle_audio(self, audio):
        b = bytearray()
        final = False
        try:
            for chunk in audio:
                b.extend(chunk)
                l = len(b) - (len(b) % 640)
                if l:
                    self.microphone.write_frames(bytes(b[:l]))
                    b = b[l:]
        
            final = True
            self.microphone.write_frames(bytes(b))
            time.sleep(len(b) / 1600)
        except Exception as e:
            print(f"Exception in handle_audio: {e}", len(b), final)

    def enqueue(self, scene_type, **kwargs):
        # Take the newly created scene object, call its prepare function, and queue it to perform
        kwargs['orchestrator'] = self
        self.scene_queue.put(scene_type(**kwargs))
        pass

    def action(self):
        # start playing scenes. This allows us to prepare scenes
        # before we actually start playback
        self.playback_thread = Thread(target=self.playback)
        self.playback_thread.start()

    def playback(self):
        while True:
            try:
                if self.stop_threads:
                    print("🎬 Shutting down playback thread")
                    break
                scene = self.scene_queue.get(block=False)
                if 'sentence' in scene.__dict__:
                    print(f"🎬 Performing scene: {type(scene).__name__}, {scene.sentence}")
                else:
                    print(f"🎬 Performing sentenceless scene: {type(scene).__name__}")
                scene.perform()
            except Empty:
                time.sleep(0.1)
                continue


if __name__ == "__main__":
    mock_ai_service = MockAIService()
    class MockImageSetter():
        def set_image(self, image):
            print("setting image", image)

    class MockMicrophone():
        def write_frames(self, frames):
            print("writing frames")

    uim = Orchestrator("context", MockImageSetter(), MockMicrophone(), mock_ai_service, mock_ai_service, mock_ai_service, 0)
    uim.handle_user_speech("hello world")

