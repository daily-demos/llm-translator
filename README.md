# Translatorbot

Live speech-to-speech translation in a Daily call.

This demo has two parts. `translatorbot` contains the daily-python code that powers the translation. `frontend` contains a lightly modified version of Daily's [React demo app](https://github.com/daily-demos/custom-video-daily-react-hooks) that allows participants to select which audio and subtitles they receive.

## `translatorbot`

```bash
cd translatorbot
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## `frontend`

```bash
cd frontend
npm install
npm start
```
