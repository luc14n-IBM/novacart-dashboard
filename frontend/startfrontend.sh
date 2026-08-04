#!/usr/bin/env bash
# frontend/startfrontend.sh — macOS frontend launcher for the NovaCart dashboard
# Ensures Node.js is installed, syncs npm dependencies when package.json changes,
# then starts the Vite dev server on http://localhost:3000.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_FILE="$SCRIPT_DIR/startfrontend.log"

# Tee all output to the log file alongside the script
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=== NovaCart Frontend Launcher ($(date)) ==="

# ---------------------------------------------------------------------------
# 1. Ensure Node.js is installed
# ---------------------------------------------------------------------------
if ! command -v node &>/dev/null; then
    echo "ERROR: Node.js was not found on this system."
    echo ""
    if command -v brew &>/dev/null; then
        echo "Installing Node.js via Homebrew..."
        brew install node
        # Refresh PATH so the newly-installed node is visible
        eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv 2>/dev/null || true)"
        if ! command -v node &>/dev/null; then
            echo "ERROR: Node.js installation succeeded but 'node' is still not in PATH."
            echo "Please open a new terminal and run this script again."
            exit 1
        fi
    else
        echo "Homebrew is not installed. Please install Node.js manually:"
        echo "    https://nodejs.org/en/download/"
        echo "Or install Homebrew first: https://brew.sh"
        exit 1
    fi
fi

echo "Using Node: $(node --version)  |  npm: $(npm --version)"

# ---------------------------------------------------------------------------
# 2. Sync npm dependencies when package.json has changed
# ---------------------------------------------------------------------------
STAMP="$SCRIPT_DIR/node_modules/.package.stamp"

if [ ! -d "$SCRIPT_DIR/node_modules" ] || [ ! -f "$STAMP" ] || ! cmp -s "$SCRIPT_DIR/package.json" "$STAMP"; then
    echo "Installing / updating npm dependencies..."
    npm install --no-audit
    cp "$SCRIPT_DIR/package.json" "$STAMP"
    echo "npm dependencies up to date."
else
    echo "npm dependencies already up to date (stamp matches)."
fi

# ---------------------------------------------------------------------------
# 3. Start the Vite dev server
# ---------------------------------------------------------------------------
echo ""
echo "Starting frontend dev server on http://localhost:3000 ..."
echo "(Press Ctrl+C to stop)"
echo ""

npm start
