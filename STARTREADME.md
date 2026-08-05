# NovaCart — Local Dev Start Guide

How to run the full NovaCart stack (backend + frontend) locally on **Windows** or **macOS**.

---

## Quick Start

### Windows

From the **project root**, double-click or run:

```bat
startapp.bat
```

Two `cmd` windows will open — one for the backend, one for the frontend. The launcher window can be closed once both are running.

### macOS

Make the scripts executable once (first time only):

```bash
chmod +x startapp.sh backend/startbackend.sh frontend/startfrontend.sh
```

Then from the **project root**, run:

```bash
./startapp.sh
```

Two new macOS Terminal windows will open — one for the backend, one for the frontend.

---

## What Each Script Does

### Root launcher — `startapp.bat` / `startapp.sh`

Orchestrates the full startup sequence:

1. Launches the backend script in a new window
2. Polls `http://127.0.0.1:8000/health` every 2 seconds until the backend returns HTTP 200 (max 60 s)
   - **Windows:** continues anyway if the timeout is reached
   - **macOS:** exits with an error if the backend never becomes ready
3. Launches the frontend script in a new window

> **Requires:** `curl` — built into Windows 10/11 (build 1803+) and macOS.

---

### Backend runner — `backend/startbackend.bat` / `backend/startbackend.sh`

Runs from the `backend/` directory. Steps:

1. **Check Python 3.11** — errors with install instructions if missing:
   - Windows: `winget install Python.Python.3.11`
   - macOS: `brew install python@3.11`
   - macOS also falls back to `python3` if it resolves to a 3.11.x version
2. **Create venv** — creates `backend/venv/` using Python 3.11 only if it doesn't already exist
3. **Install requirements** — compares `requirements.txt` against a stamp file (`venv/.requirements.stamp`). Runs `pip install` only if the file has changed since the last install, then updates the stamp. Skips entirely if nothing changed.
4. **Start the server** — activates the venv and starts uvicorn at **http://127.0.0.1:8000**

---

### Frontend runner — `frontend/startfrontend.bat` / `frontend/startfrontend.sh`

Runs from the `frontend/` directory. Steps:

1. **Check / install Node.js** — if `node` is not on PATH:
   - **Windows:** checks if `winget` is available; if yes runs `winget install OpenJS.NodeJS.LTS --silent`; if no, prints a link to https://nodejs.org/ and exits
   - **macOS:** checks if `brew` is available; if yes runs `brew install node` automatically; if no, prints links to https://nodejs.org/ and https://brew.sh and exits
2. **Install npm dependencies** — uses a stamp file (`node_modules/.package.stamp`) to avoid re-running `npm install` unnecessarily:
   - `node_modules/` missing → runs `npm install --no-audit`
   - `package.json` changed since last install → runs `npm install --no-audit`, updates stamp
   - Otherwise → skips entirely
3. **Log file** — all output is tee'd to `frontend/startfrontend.log` alongside the script
4. **Start the dev server** — runs `npm start` at **http://localhost:3000**

---

## Install Git Hooks (one-time, per developer)

The project includes a pre-push hook that runs the test suite before every `git push`, blocking the push if any test fails.

Run this **once** after cloning (or after a teammate adds new hooks):

### Windows

```bat
hooks\install-hooks.bat
```

### macOS

```bash
bash hooks/install-hooks.sh
```

Once installed, every `git push` will automatically run:
1. Backend tests — `pytest test_api.py`
2. Frontend tests — `npm run test`

If tests fail, the push is blocked with a clear message. In an emergency you can bypass with `git push --no-verify`.

---

## Requirements

### Windows

| Requirement | Version | Install |
|---|---|---|
| Windows | 10 / 11 | — |
| Python | 3.11 | `winget install Python.Python.3.11` |
| Node.js | LTS | Auto-installed by `startfrontend.bat`, or `winget install OpenJS.NodeJS.LTS` |
| curl | Built-in | Included with Windows 10/11 build 1803+ |

### macOS

| Requirement | Version | Install |
|---|---|---|
| macOS | 12 Monterey+ recommended | — |
| Homebrew | Latest | [brew.sh](https://brew.sh) |
| Python | 3.11 | `brew install python@3.11` |
| Node.js | LTS | Auto-installed by `startfrontend.sh`, or `brew install node` |
| curl | Built-in | Included with macOS |

---

## Environment Setup

### Backend

Copy the example env file before first run:

**Windows:**
```bat
copy backend\.env.example backend\.env
```

**macOS:**
```bash
cp backend/.env.example backend/.env
```

Default settings work out of the box for local development — no changes needed.

| Variable | Default | Description |
|---|---|---|
| `DATA_BACKEND` | `sqlite` | Use `sqlite` locally, `snowflake` for SPCS |
| `SQLITE_PATH` | `../data/novacart_gold.db` | Path to the local SQLite database |
| `PORT` | `8000` | Server port |

### Frontend

The frontend reads `REACT_APP_BACKEND_URL` — defaults to `http://localhost:8000` when not set, so no `.env` changes are needed for local dev.

---

## Useful URLs

| URL | Description |
|---|---|
| http://localhost:3000 | React frontend |
| http://localhost:8000/docs | Swagger UI — browse and test all API endpoints |
| http://127.0.0.1:8000/health | Health check — confirms DB connection |

---

## Controls

### Windows

| Action | How |
|---|---|
| Start everything | `startapp.bat` from project root |
| Start backend only | `startbackend.bat` from `backend/` |
| Start frontend only | `startfrontend.bat` from `frontend/` |
| Stop a server | `Ctrl+C` in its window, then `Y` when prompted |
| Force reinstall backend deps | Delete `backend/venv/.requirements.stamp`, re-run `startbackend.bat` |
| Force reinstall frontend deps | Delete `frontend/node_modules/.package.stamp`, re-run `startfrontend.bat` |
| Add a backend dependency | `venv\Scripts\pip install <pkg>`, add to `requirements.txt` |
| Add a frontend dependency | `npm install <pkg>` from `frontend/`, commit updated `package.json` |

### macOS

| Action | How |
|---|---|
| Start everything | `./startapp.sh` from project root |
| Start backend only | `bash startbackend.sh` from `backend/` |
| Start frontend only | `bash startfrontend.sh` from `frontend/` |
| Stop a server | `Ctrl+C` in its Terminal window |
| Force reinstall backend deps | Delete `backend/venv/.requirements.stamp`, re-run `startbackend.sh` |
| Force reinstall frontend deps | Delete `frontend/node_modules/.package.stamp`, re-run `startfrontend.sh` |
| Add a backend dependency | `venv/bin/pip install <pkg>`, add to `requirements.txt` |
| Add a frontend dependency | `npm install <pkg>` from `frontend/`, commit updated `package.json` |

---

## Troubleshooting

### Windows

**`Python 3.11 is not installed`** — Run `winget install Python.Python.3.11`, close and reopen the terminal, then re-run.

**`Failed to install requirements`** — Ensure you are running `startbackend.bat` from inside `backend/`, or use `startapp.bat` from the root.

**`winget is not available`** — Install Node.js manually from https://nodejs.org/ and ensure it is on your PATH.

**`Node.js was installed but is not yet on PATH`** — Close the frontend window and re-run `startfrontend.bat`. winget sometimes requires a new shell session for PATH changes to take effect.

**`Backend did not respond after 60 s`** — The frontend will still launch. Check the backend window for errors (missing `.env`, database not found, port conflict).

### macOS

**`Python 3.11 is not installed`** — Run `brew install python@3.11`, open a new terminal, then re-run.

**`command not found: brew`** — Install Homebrew from https://brew.sh, then re-run.

**`Permission denied: ./startapp.sh`** — Run `chmod +x startapp.sh backend/startbackend.sh frontend/startfrontend.sh` first.

**`Node.js installed but not found in PATH`** — Open a new terminal and re-run `startfrontend.sh`. Homebrew sometimes requires a new shell session for PATH changes to take effect.

**`Backend did not become ready after 60 seconds`** — Check the backend Terminal window for errors, then re-run `startapp.sh` once the issue is resolved.

### Both platforms

**`SQLite database not found`** — Confirm `data/novacart_gold.db` exists in the project root.

**CORS error in browser** — Confirm `CLIENT_VALIDATION=Dev` is set in `backend/.env`.
