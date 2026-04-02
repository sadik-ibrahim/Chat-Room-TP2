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
- **Framework:** Flet 0.83.1 (Flutter-based Python UI framework)
- **State:** In-memory (rooms, messages, reactions stored as Python dicts/lists)
- **Real-time:** Flet PubSub system (WebSocket-based)
- **File uploads:** Stored in `assets/uploads/` (cleared on startup)

## Project Structure
```
main.py          # Entire application (~686 lines)
pyproject.toml   # Project metadata and dependencies
requirements.txt # pip-compatible requirements
uv.lock          # uv lock file
assets/
  uploads/       # Temporary upload storage (auto-cleared on startup)
```

## Running the App
The app is started using the Flet CLI on port 5000:
```
flet run -w -p 5000 --host 0.0.0.0 main.py
```

## Dependencies
- `flet==0.83.1` - Main framework
- `flet-desktop==0.83.1` - Desktop support
- `flet-cli==0.83.1` - CLI runner
- `flet-web==0.83.1` - Web server (auto-installed by flet-cli at startup)

## Environment Variables
- `SERVER_URL` - Full public URL of this app (used to build absolute file URLs)
  - Development: set to the Replit dev domain
  - Production: update to the `.replit.app` domain after deploy

## Deployment
- **Type:** VM (always-running, uses in-memory state and WebSockets)
- **Run command:** `python main.py`
- **Port:** 5000

## Notes
- The app uses in-memory state, so all chat history is lost on restart
- Uploads folder is cleared every time the app starts
- The `FLET_SECRET_KEY` env var is set to a default dev value in code
- Multiple browser tabs can connect simultaneously (multi-user)
