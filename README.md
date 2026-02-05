# Personal YouTube + Instagram Downloader Web App

A simple Flask web app for personal use where you can:

- Select **YouTube** or **Instagram**
- Paste the media URL
- Download the best available quality video

## Features

- Platform selection at startup (YouTube / Instagram)
- URL validation based on selected platform
- Best quality download via `yt-dlp`
- Clean single-page interface

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open: `http://localhost:5000`

## Notes

- This app is for personal/authorized usage.
- Some media may require authentication or may be restricted by platform policy.
