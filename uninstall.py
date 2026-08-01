#!/usr/bin/env python3
"""Remove ai-audio-notify hooks from installed AI tools."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters import antigravity as ag_adapter  # noqa: E402
from adapters import claude as claude_adapter  # noqa: E402
from adapters import cursor as cursor_adapter  # noqa: E402

ADAPTERS = {
    "claude": claude_adapter,
    "cursor": cursor_adapter,
    "antigravity": ag_adapter,
}

STATE_PATH = ROOT / "install-state.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Uninstall AI audio notification hooks")
    parser.add_argument(
        "--tools",
        default="",
        help="Comma-separated tool ids (default: from install-state.json or all)",
    )
    args = parser.parse_args()

    if args.tools:
        selected = [t.strip() for t in args.tools.split(",") if t.strip()]
    elif STATE_PATH.is_file():
        try:
            state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            selected = list(state.get("installed_tools") or list(ADAPTERS.keys()))
        except (json.JSONDecodeError, OSError):
            selected = list(ADAPTERS.keys())
    else:
        selected = list(ADAPTERS.keys())

    for tid in selected:
        adapter = ADAPTERS.get(tid)
        if not adapter:
            print(f"Unknown tool: {tid}")
            continue
        path = adapter.uninstall(ROOT)
        print(f"Uninstalled {tid}" + (f" ({path})" if path else ""))

    if STATE_PATH.is_file():
        try:
            STATE_PATH.unlink()
        except OSError:
            pass

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
