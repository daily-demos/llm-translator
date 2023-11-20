import io
import os
import struct
from pyht import Client
from dotenv import load_dotenv
from pyht.client import TTSOptions
from pyht.protos.api_pb2 import Format

from services.ai_service import AIService


class PlayHTAIService(AIService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.speech_key = os.getenv("PLAY_HT_KEY") or ''
        self.user_id = os.getenv("PLAY_HT_USER_ID") or ''
        self.speakers = {"male": [], "female": []}
        self.client = Client(
            user_id=self.user_id,
            api_key=self.speech_key,
        )

        # PlayHT is English-only for now
        self.languages = {
            "english": {
                "lang": "en-US",
                "voices": {
                    "male": ["s3://voice-cloning-zero-shot/0b5b2e4b-5103-425e-8aa0-510dd35226e2/mark/manifest.json"],
                    "female": ["s3://voice-cloning-zero-shot/820da3d2-3a3b-42e7-844d-e68db835a206/sarah/manifest.json"]}}}

    def run_tts(self, message):
        sentence = message['translation']
        language = message['translation_language']
        voice = message['voice']
        sid = message['session_id']
        if language not in self.languages:
            raise Exception(
                f"PlayHT doesn't currently support {language}. Currently configured languages: {', '.join(self.languages.keys())}")
        if sid not in self.speakers[voice]:
            self.speakers[voice].append(sid)

        options = TTSOptions(voice=self.languages[language]['voices'][voice][self.speakers[voice].index(
            sid) % len(self.speakers[voice])], sample_rate=16000, quality="higher", format=Format.FORMAT_WAV)
        sentence = message['translation']

        b = bytearray()
        in_header = True
        for chunk in self.client.tts(sentence, options):
            # skip the RIFF header.
            if in_header:
                b.extend(chunk)
                if len(b) <= 36:
                    continue
                else:
                    fh = io.BytesIO(b)
                    fh.seek(36)
                    (data, size) = struct.unpack('<4sI', fh.read(8))
                    print(
                        f"first attempt: data: {data}, size: {hex(size)}, position: {fh.tell()}")
                    while data != b'data':
                        fh.read(size)
                        (data, size) = struct.unpack('<4sI', fh.read(8))
                        print(
                            f"subsequent data: {data}, size: {hex(size)}, position: {fh.tell()}, data != data: {data != b'data'}")
                    print("position: ", fh.tell())
                    in_header = False
            else:
                if len(chunk):
                    yield chunk
