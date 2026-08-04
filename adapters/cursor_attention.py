#!/usr/bin/env python3
"""Cursor hold hook: play attention sound when shell/MCP needs you."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.platforms import should_debounce, spawn_detached  # noqa: E402


def _load_config() -> dict:
    try:
        return json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> int:
    # Drain stdin so Cursor doesn't block on a full pipe.
    try:
        sys.stdin.read()
    except OSError:
        pass

    cfg = _load_config()
    debounce_ms = max(int(cfg.get("debounce_ms", 1500)), 2000)
    # "ask" = keep/create the approval hold + play need-you cue (default).
    # "allow" = play the cue only, do not change Cursor's approve/deny UI.
    mode = str(cfg.get("cursor_permission_mode", "ask")).lower().strip()
    if mode not in ("ask", "allow", "deny"):
        mode = "ask"

    if not should_debounce("attention", debounce_ms):
        py = sys.executable or "python"
        spawn_detached([py, str(ROOT / "play.py"), "attention", "--wait", "--no-debounce"])

    print(json.dumps({"permission": mode}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
