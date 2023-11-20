# Translatorbot

Live speech-to-speech translation in a Daily call.

This demo has two parts. The `server` directory contains the daily-python code that powers the translation. The `client` directory contains a lightly modified version of the [daily-react example app](https://github.com/daily-demos/custom-vide-daily-react-hooks).

## Running the server

Install everything you need for the Python app:

```bash
cd server
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Then, copy `.env.example` to `.env` and add your keys, as well as the URL of the Daily room you want to use for testing.

Next, run `python daily-llm.py -i spanish -o english` to start a Spanish-to-English translator.

There's currently a bug preventing `daily-python` from starting translation in languages other than English, so you'll need to start transcription yourself directly in the browser for now. You can do that by running `callObject.startTranscription({"language": "es"});` in a call client with an owner token.

## Running the client

```bash
cd client
npm install
npm start
```

Then, open your translation room in the custom UI by visiting a URL like `http://localhost:3000?roomUrl=https://YOURDOMAIN.daily.co/YOURROOM`.

See the README in the `client` directory for more info on the daily-react example app.
