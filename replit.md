# TP2 ChatRoom - Flet Real-Time Chat Application

## Overview
A real-time multi-room chat application built with the **Flet** framework (Python). This is a university course project (Mobile Computing, UAlg LESTI 2025/26).

## Features
- Multiple chat rooms (general, random, + user-created rooms)
- Direct messaging between users
- File sharing (images, videos, documents)
- Message editing and deletion
- Emoji reactions
- YouTube video link previews
- Unread message counters

## Architecture
- **Language:** Python 3.11
- **Framework:** Flet (Flutter-based Python UI framework)
- **State:** In-memory (rooms, messages, reactions stored as Python dicts/lists)
- **Real-time:** Flet PubSub system (WebSocket-based)
- **File uploads:** Stored in `assets/uploads/` (cleared on startup)

## Project Structure
```
main.py          # Entire application (683 lines)
pyproject.toml   # Project metadata and dependencies
requirements.txt # pip-compatible requirements
uv.lock          # uv lock file
assets/
  uploads/       # Temporary upload storage (auto-cleared on startup)
```

## Running the App
The app runs as a web server on port 5000:
```
python main.py
```

## Dependencies
- `flet>=0.84.0` - Main framework
- `flet-web>=0.84.0` - Web server support

## Deployment
- **Type:** VM (always-running, uses in-memory state)
- **Run command:** `python main.py`
- **Port:** 5000

## Notes
- The app uses in-memory state, so all chat history is lost on restart
- Uploads folder is cleared every time the app starts
- The `FLET_SECRET_KEY` env var is set to a default dev value in code
