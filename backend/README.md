# NovaCart Backend — Local Dev Guide

FastAPI server that powers the NovaCart dashboard. Runs locally against a SQLite database — no Snowflake account needed.

---

## Requirements

- Windows 10/11
- [Python 3.11](https://www.python.org/) — install via:
  ```bat
  winget install Python.Python.3.11
  ```

---

## Quick Start

From the `backend/` directory:

```bat
run.bat
```

That's it. The script will:
1. Verify Python 3.11 is installed
2. Create a virtual environment (`/venv/`) if one doesn't exist
3. Install all dependencies from `requirements.txt`
4. Start the server at **http://localhost:8000**

---

## Environment Variables

Copy the example env file before first run:

```bat
copy .env.example .env
```

Default settings work out of the box for local development — no changes needed.

| Variable | Default | Description |
|---|---|---|
| `DATA_BACKEND` | `sqlite` | Use `sqlite` locally, `snowflake` for SPCS |
| `SQLITE_PATH` | `../data/novacart_gold.db` | Path to the local SQLite database |
| `PORT` | `8000` | Server port |

---

## Useful URLs

| URL | Description |
|---|---|
| http://localhost:8000/docs | Swagger UI — browse and test all endpoints |
| http://localhost:8000/health | Health check — confirms DB connection |

---

## Controls

| Action | Command |
|---|---|
| Start server | `run.bat` |
| Stop server | `Ctrl+C`, then `Y` when prompted |
| Restart server | `Ctrl+C` → `run.bat` again |
| Add a dependency | `venv\Scripts\pip install <package>` then add to `requirements.txt` |

---

## Troubleshooting

**`Python 3.11 is not installed`** — Run `winget install Python.Python.3.11`, close and reopen your terminal, then try again.

**`Failed to install requirements`** — Make sure you're running `run.bat` from inside the `backend/` directory, not the project root.

**`SQLite database not found`** — Confirm `data/novacart_gold.db` exists in the project root. Run `run.bat` from inside `backend/`.

**`501 Not implemented`** — Expected. Those are the endpoints you need to build in `main.py`.

**CORS error in browser** — Confirm `CLIENT_VALIDATION=Dev` is set in your `.env`.
