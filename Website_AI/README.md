# Snoopy's Playground (Streamlit App)

An interactive Streamlit app with multiple tabs (Chat, Music, Video, Game, Article, Fortune). It’s designed to work with an LM Studio-compatible OpenAI API endpoint and includes playful Snoopy-themed styling.

## Features

- Chat with multiple “robot” personas (General Assistant, Code Expert, Creative Writer, Fortune Teller, Teacher)
- Local-only Music playback with a small library saved under `Website_AI/assets`
- Video tab to embed a featured YouTube video or your own video/URL
- Mini game: Snoopy's Gold Miner (simple click-to-mine game with score/level/time)
- Fortune tab for daily fortune and tarot card draws
- Article writer with adjustable word count and tone
- Customizable background image, scaling mode, and opacity (default 70%)

## Requirements

- Python 3.9+
- Packages: `streamlit`, `openai`
- Optional: `watchdog` (improves auto-reload performance on macOS)

You can install the essentials with:

```bash
pip install streamlit openai
# Optional for faster reloads
pip install watchdog
```

## Quick Start

From the repository root:

```bash
# Using your current Python
streamlit run Website_AI/lmstudio_chatbot_tabs.py

# Or explicitly via a venv (example)
./.venv/bin/python -m streamlit run Website_AI/lmstudio_chatbot_tabs.py
```

The app will start at:
- Local URL: http://localhost:8501

## LM Studio / API Setup

In the sidebar under “⚙️ Server Configuration”:
- Server URL: `http://localhost:1234/v1` (LM Studio default)
- API Key: `lm-studio` (or anything; LM Studio typically ignores it)
- Model Name: e.g. `lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF`

Make sure LM Studio is running and serving an OpenAI-compatible endpoint on the given URL.

## Tabs Overview

- Chat: streaming chat completion using your configured server/model. Sessions can be created/cleared from the sidebar.
- Music: upload a local audio file to play immediately. Files are also saved to `Website_AI/assets` so you can play them later from the Local Library.
- Video: watch the featured video or upload your own / paste a URL to embed.
- Game: simple clicker mini game (Gold Miner) with score, lives, levels, and a countdown timer.
- Fortune: quick fortune reading or random tarot card draws.
- Article: generate a short article with sections.

## Background Customization

Sidebar → Appearance:
- Upload a custom image (stored locally at `Website_AI/assets/background.jpg`)
- Adjust background opacity (default 0.7) and scaling mode (cover/contain/stretch)

## Local Assets

- Audio files you upload in the Music tab are stored in `Website_AI/assets/`.
- You can also manually drop supported audio files there: `.mp3`, `.wav`, `.ogg`, `.m4a`.

## Troubleshooting

- Page doesn’t reload on changes: Install `watchdog` and ensure your venv is active.
- Chat errors: Verify LM Studio is running at the Server URL and that the model name is correct.
- Background not updating: Try re-uploading; the image is cached to `Website_AI/assets/background.jpg`. Adjust opacity/fit and the app will rerun.
- Audio won’t appear in the library: Confirm the file has a supported extension and that the app has write permissions to `Website_AI/assets`.

## Notes

- This app uses only local files for Music playback—no external music services.
- The background image is cached locally so the app can work offline after the first fetch.

## License

Educational and personal use. Adapt freely with attribution.
