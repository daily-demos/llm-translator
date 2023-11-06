# Translatorbot

Live speech-to-speech translation in a Daily call.

This demo has two parts. `translatorbot` contains the daily-python code that powers the translation. `llm-translator.html` is a basic call client that allows participants to select which audio and subtitles they receive.

## Getting Started

Install everything you need for the Python app:

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Then, copy `.env.example` to `.env` and add your keys, as well as the URL of the Daily room you want to use for testing.

Next, run `python daily-llm.py -l spanish` to start a Spanish translator.

Finally, open `llm-translator.html?host=true` in your browser to join as a host. In another tab, open `llm-translator.html` without `host=true` to join in 'audience mode'.
