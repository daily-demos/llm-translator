# Translatorbot

Live speech-to-speech translation in a Daily call.

This demo has two parts. This app contains the daily-python code that powers the translation. It works with a client app based on the daily-react example app. It's currently in a branch [located here](https://github.com/chadbailey59/custom-video-daily-react-hooks/tree/chad/llm-translator).

## Getting Started

Install everything you need for the Python app:

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Then, copy `.env.example` to `.env` and add your keys, as well as the URL of the Daily room you want to use for testing.

Next, run `python daily-llm.py -i spanish -o english` to start a Spanish-to-English translator.

There's currently a bug preventing `daily-python` from starting translation in languages other than English, so you'll need to start transcription yourself directly in the browser for now. You can do that by running `callObject.startTranscription({"language": "es"});` in a call client with an owner token.
