#!/usr/bin/env bash
# backend/startbackend.sh — macOS backend launcher for the NovaCart dashboard
# Ensures Python 3.11 is available, sets up a virtualenv, syncs dependencies,
# then runs the FastAPI/Uvicorn server bound to 127.0.0.1:8000.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ---------------------------------------------------------------------------
# 1. Locate Python 3.11
# ---------------------------------------------------------------------------
PYTHON=""

if command -v python3.11 &>/dev/null; then
    PYTHON="python3.11"
else
    # Fall back: check if the default python3 is 3.11.x
    if command -v python3 &>/dev/null; then
        PY3_VER=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || true)
        MAJOR_MINOR=$(echo "$PY3_VER" | cut -d. -f1-2)
        if [ "$MAJOR_MINOR" = "3.11" ]; then
            PYTHON="python3"
        fi
    fi
fi

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.11 was not found on this system."
    echo ""
    echo "Install it with Homebrew:"
    echo "    brew install python@3.11"
    echo ""
    echo "Then open a new terminal and run this script again."
    exit 1
fi

echo "Using Python: $($PYTHON --version)"

# ---------------------------------------------------------------------------
# 2. Create virtual environment if it does not exist
# ---------------------------------------------------------------------------
VENV_DIR="$SCRIPT_DIR/venv"
ACTIVATE="$VENV_DIR/bin/activate"

if [ ! -f "$ACTIVATE" ]; then
    echo "Creating virtual environment at $VENV_DIR ..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

# ---------------------------------------------------------------------------
# 3. Sync dependencies when requirements.txt has changed
# ---------------------------------------------------------------------------
STAMP="$VENV_DIR/.requirements.stamp"

if [ ! -f "$STAMP" ] || ! cmp -s "$SCRIPT_DIR/requirements.txt" "$STAMP"; then
    echo "Installing / updating dependencies from requirements.txt ..."
    # shellcheck source=/dev/null
    source "$ACTIVATE"
    pip install -q -r "$SCRIPT_DIR/requirements.txt"
    cp "$SCRIPT_DIR/requirements.txt" "$STAMP"
    echo "Dependencies up to date."
else
    # shellcheck source=/dev/null
    source "$ACTIVATE"
    echo "Dependencies already up to date (stamp matches)."
fi

# ---------------------------------------------------------------------------
# 4. Start the Uvicorn server
# ---------------------------------------------------------------------------
echo ""
echo "Starting backend server on http://127.0.0.1:8000 ..."
echo "(Press Ctrl+C to stop)"
echo ""

uvicorn main:app --reload --reload-delay 1 --host 127.0.0.1 --port 8000
