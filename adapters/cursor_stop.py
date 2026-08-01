#!/usr/bin/env python3
"""Cursor stop hook: play finished sound only when status is completed."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAY = ROOT / "play.py"


def main() -> int:
    raw = ""
    try:
        raw = sys.stdin.read()
    except OSError:
        pass

    status = ""
    try:
        if raw.strip():
            payload = json.loads(raw)
            status = str(payload.get("status") or "")
    except json.JSONDecodeError:
        status = ""

    if status == "completed":
        try:
            subprocess.Popen(
                [sys.executable, str(PLAY), "finished"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(ROOT),
            )
        except Exception:
            pass

    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
