#!/usr/bin/env python3
"""Cursor stop hook: play finished sound when the agent turn completes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.platforms import play_file  # noqa: E402


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
            status = str(payload.get("status") or "").lower()
    except json.JSONDecodeError:
        status = ""

    # Play on completed. If status is missing (older payloads), still play —
    # skip only clear abort/error so silence isn't the default failure mode.
    should_play = status in ("", "completed")
    if status in ("aborted", "error", "cancelled", "canceled"):
        should_play = False

    if should_play:
        # Play in-process so Cursor doesn't kill a child when this hook exits.
        config_path = ROOT / "config.json"
        rel = "sounds/task-finished.mp3"
        try:
            import json as _json

            cfg = _json.loads(config_path.read_text(encoding="utf-8"))
            rel = (cfg.get("sounds") or {}).get("finished") or rel
        except Exception:
            pass
        sound = (ROOT / rel).resolve()
        try:
            sound.relative_to(ROOT)
        except ValueError:
            sound = ROOT / "sounds" / "task-finished.mp3"
        play_file(sound)

    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
