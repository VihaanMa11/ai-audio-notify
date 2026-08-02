#!/usr/bin/env python3
"""Play finished / attention notification sounds for AI coding tools."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.platforms import play_file, should_debounce, spawn_detached  # noqa: E402


def load_config() -> dict:
    path = ROOT / "config.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "sounds": {
                "finished": "sounds/task-finished.mp3",
                "attention": "sounds/needs-attention.mp3",
            },
            "debounce_ms": 2000,
        }


def read_stdin_json() -> dict | None:
    if sys.stdin.isatty():
        return None
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return None
        return json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Play AI agent notification sounds")
    parser.add_argument(
        "event",
        choices=["finished", "attention"],
        help="Which sound to play",
    )
    parser.add_argument(
        "--require-status",
        default="",
        help="Only play if stdin JSON status matches (e.g. completed)",
    )
    parser.add_argument(
        "--antigravity-idle",
        action="store_true",
        help="Only play when Antigravity stdin has fullyIdle=true; emit allow decision",
    )
    parser.add_argument(
        "--no-debounce",
        action="store_true",
        help="Skip debounce window",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Play in this process and block until done (internal: used by the "
        "detached child; hooks should not pass this)",
    )
    args = parser.parse_args()

    # Only the wrapper modes need the hook payload. Reading stdin when nothing
    # consumes it risks blocking forever if the caller holds the pipe open.
    payload = None
    if args.require_status or args.antigravity_idle:
        payload = read_stdin_json()

    # Cursor stop: only on completed
    if args.require_status:
        status = ""
        if isinstance(payload, dict):
            status = str(payload.get("status") or "")
        if status != args.require_status:
            if args.require_status:  # Cursor wrapper expects JSON out
                print("{}")
            return 0

    # Antigravity Stop: only when fully idle
    if args.antigravity_idle:
        fully_idle = True
        if isinstance(payload, dict):
            fully_idle = bool(payload.get("fullyIdle", True))
        if not fully_idle:
            print(json.dumps({"decision": "allow"}))
            return 0

    config = load_config()
    debounce_ms = int(config.get("debounce_ms", 2000))
    if not args.no_debounce and should_debounce(args.event, debounce_ms):
        if args.require_status:
            print("{}")
        elif args.antigravity_idle:
            print(json.dumps({"decision": "allow"}))
        return 0

    sounds = config.get("sounds") or {}
    rel = sounds.get(args.event)
    if not rel:
        if args.require_status:
            print("{}")
        elif args.antigravity_idle:
            print(json.dumps({"decision": "allow"}))
        return 0

    sound_path = (ROOT / rel).resolve()
    # Guard: must stay under repo (relative paths only)
    try:
        sound_path.relative_to(ROOT)
    except ValueError:
        if args.require_status:
            print("{}")
        elif args.antigravity_idle:
            print(json.dumps({"decision": "allow"}))
        return 0

    if args.wait:
        play_file(sound_path)
    else:
        # Hand playback to a detached child so the hook returns in milliseconds
        # instead of stalling the agent for the length of the clip.
        py = sys.executable or "python"
        spawned = spawn_detached(
            [py, str(ROOT / "play.py"), args.event, "--wait", "--no-debounce"]
        )
        if not spawned:
            play_file(sound_path)

    if args.require_status:
        print("{}")
    elif args.antigravity_idle:
        print(json.dumps({"decision": "allow"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
