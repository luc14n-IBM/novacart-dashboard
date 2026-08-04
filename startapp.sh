#!/usr/bin/env bash
# startapp.sh — macOS orchestrator for the NovaCart dashboard
# Starts the backend in a new Terminal window, waits for it to be healthy,
# then starts the frontend in a second new Terminal window.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== NovaCart Dashboard Launcher ==="
echo "Starting backend..."

osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR/backend' && bash startbackend.sh\""

echo "Waiting for backend to be ready at http://127.0.0.1:8000/health ..."

MAX_RETRIES=30
RETRY=0
while [ "$RETRY" -lt "$MAX_RETRIES" ]; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health 2>/dev/null || true)
    if echo "$STATUS" | grep -qx "200"; then
        echo "Backend is ready."
        break
    fi
    RETRY=$(( RETRY + 1 ))
    echo "  Attempt $RETRY/$MAX_RETRIES — backend not yet ready (status: ${STATUS:-none}), retrying in 2 s..."
    sleep 2
done

if [ "$RETRY" -ge "$MAX_RETRIES" ]; then
    echo "ERROR: Backend did not become ready after $(( MAX_RETRIES * 2 )) seconds. Check the backend Terminal window for errors."
    exit 1
fi

echo "Starting frontend..."

osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR/frontend' && bash startfrontend.sh\""

echo ""
echo "=== NovaCart Dashboard is starting up ==="
echo "  Backend : http://127.0.0.1:8000"
echo "  Frontend: http://localhost:3000"
echo ""
echo "Both services are running in separate Terminal windows."
