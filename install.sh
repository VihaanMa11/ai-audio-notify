#!/usr/bin/env bash
# One-command installer for macOS / Linux.
set -euo pipefail
cd "$(dirname "$0")"

echo
echo " ========================================"
echo "  ai-audio-notify installer"
echo " ========================================"
echo
echo " Scans for Claude Code, Cursor, and Antigravity,"
echo " then installs sound hooks."
echo

PY=""
if command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
fi

if [[ -z "$PY" ]]; then
  echo " [!] Python 3 was not found on PATH."
  echo
  echo " Install Python 3, then run: ./install.sh"
  echo "   https://www.python.org/downloads/"
  echo
  if [[ -t 0 ]]; then
    read -r -p "Press Enter to close..."
  fi
  exit 1
fi

echo " Using: $PY"
echo
"$PY" ./install.py "$@"
code=$?
echo
if [[ "$code" -ne 0 ]]; then
  echo " Installer exited with code $code."
else
  echo " Done. You can close this terminal."
fi
echo
if [[ -t 0 ]]; then
  read -r -p "Press Enter to close..."
fi
exit "$code"
