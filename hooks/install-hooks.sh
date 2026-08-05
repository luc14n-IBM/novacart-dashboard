#!/usr/bin/env bash
# hooks/install-hooks.sh — installs the project Git hooks for macOS / Linux.
# Run once after cloning:  bash hooks/install-hooks.sh

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_SRC="$REPO_ROOT/hooks"
HOOKS_DST="$REPO_ROOT/.git/hooks"

echo ""
echo "Installing NovaCart Git hooks..."

cp "$HOOKS_SRC/pre-push" "$HOOKS_DST/pre-push"
chmod +x "$HOOKS_DST/pre-push"

echo "  ✓ pre-push hook installed"
echo ""
echo "The hook runs backend (pytest) and frontend (Vitest) tests before"
echo "every 'git push'. To skip in an emergency: git push --no-verify"
echo ""
