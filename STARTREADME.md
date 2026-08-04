# NovaCart — Local Dev Start Guide

How to run the full NovaCart stack (backend + frontend) locally on Windows.

---

## Quick Start

From the **project root**, double-click or run:

```bat
startapp.bat
```

That's it. Two `cmd` windows will open — one for the backend, one for the frontend. The launcher window can be closed once both are running.

---

## What Each Script Does

### `startapp.bat` — Root launcher

Orchestrates the full startup sequence:

1. Launches `backend/startbackend.bat` in a new `cmd` window titled **NovaCart Backend**
2. Polls `http://localhost:8000/health` every 2 seconds until the backend returns HTTP 200 (max 60 s, then continues anyway)
3. Launches `frontend/startfrontend.bat` in a new `cmd` window titled **NovaCart Frontend**

> **Requires:** `curl` — built into Windows 10/11 (build 1803+)

---

### `backend/startbackend.bat` — Backend runner

Runs from the `backend/` directory. Steps:

1. **Check Python 3.11** — errors with install instructions if missing:
   ```bat
   winget install Python.Python.3.11
   ```
2. **Create venv** — creates `backend/venv/` using Python 3.11 only if it doesn't already exist
3. **Install requirements** — compares `requirements.txt` against a stamp file (`venv/.requirements.stamp`). Runs `pip install` only if the file has changed since the last install, then updates the stamp. Skips entirely if nothing changed.
4. **Start the server** — activates the venv and starts uvicorn at **http://localhost:8000**

---

### `frontend/startfrontend.bat` — Frontend runner

Runs from the `frontend/` directory. Steps:

1. **Check / install Node.js** — if `node` is not on PATH:
   - Checks if `winget` is available
   - If yes: runs `winget install OpenJS.NodeJS.LTS --silent`
   - If `node` is still not on PATH after install (new shell needed): prints a message and exits cleanly
   - If `winget` is unavailable: prints a link to https://nodejs.org/ and exits
2. **Install npm dependencies** — uses a stamp file (`node_modules/.package.stamp`) to avoid re-running `npm install` unnecessarily:
   - `node_modules/` missing → runs `npm install`
   - `package.json` changed since last install → runs `npm install`, updates stamp
   - Otherwise → skips entirely
3. **Start the dev server** — runs `npm start` at **http://localhost:3000**

---

## Requirements

| Requirement | Version | Install |
|---|---|---|
| Windows | 10/11 | — |
| Python | 3.11 | `winget install Python.Python.3.11` |
| Node.js | LTS | Auto-installed by `startfrontend.bat`, or `winget install OpenJS.NodeJS.LTS` |
| curl | Built-in | Included with Windows 10/11 build 1803+ |

---

## Environment Setup

### Backend

Copy the example env file before first run:

```bat
copy backend\.env.example backend\.env
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
| http://localhost:8000/health | Health check — confirms DB connection |

---

## Controls

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

---

## Troubleshooting

**`Python 3.11 is not installed`** — Run `winget install Python.Python.3.11`, close and reopen the terminal, then re-run.

**`Failed to install requirements`** — Ensure you are running `startbackend.bat` from inside `backend/`, or use `startapp.bat` from the root.

**`winget is not available`** — Install Node.js manually from https://nodejs.org/ and ensure it is on your PATH.

**`Node.js was installed but is not yet on PATH`** — Close the frontend window and re-run `startfrontend.bat`. winget sometimes requires a new shell session for PATH changes to take effect.

**`SQLite database not found`** — Confirm `data/novacart_gold.db` exists in the project root.

**`Backend did not respond after 60 s`** — The frontend will still launch. Check the backend window for errors (missing `.env`, database not found, port conflict).

**CORS error in browser** — Confirm `CLIENT_VALIDATION=Dev` is set in `backend/.env`.
