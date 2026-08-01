#!/usr/bin/env python3
"""Detect AI tools, let the user choose, and install notification hooks."""

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
from lib.detect import detect_all  # noqa: E402

ADAPTERS = {
    "claude": claude_adapter,
    "cursor": cursor_adapter,
    "antigravity": ag_adapter,
}

STATE_PATH = ROOT / "install-state.json"


def write_state(installed: list[str]) -> None:
    STATE_PATH.write_text(
        json.dumps(
            {
                "repo_root": str(ROOT),
                "installed_tools": installed,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def prompt_selection(tools: list) -> list[str]:
    present = [t for t in tools if t.installed]
    print("\nDetected AI tools:\n")
    for i, t in enumerate(tools, 1):
        mark = "OK" if t.installed else "--"
        status = "installed" if t.installed else "not found"
        print(f"  [{mark}] {i}. {t.name} ({t.id}) — {status}")
        if t.detail:
            print(f"         {t.detail}")

    default_ids = [t.id for t in present]
    default_hint = ",".join(default_ids) if default_ids else "(none)"
    print(
        "\nSelect tools to wire up (comma-separated numbers or ids, "
        f"'all', or Enter for present only: {default_hint})"
    )
    raw = input("> ").strip()
    if not raw:
        return default_ids
    if raw.lower() == "all":
        return [t.id for t in tools]

    selected: list[str] = []
    for token in raw.replace(" ", "").split(","):
        if not token:
            continue
        if token.isdigit():
            idx = int(token) - 1
            if 0 <= idx < len(tools):
                selected.append(tools[idx].id)
        elif token in ADAPTERS:
            selected.append(token)
        else:
            print(f"  Unknown selection: {token}")
    return selected


def install_tools(selected: list[str], tools_by_id: dict) -> list[str]:
    installed: list[str] = []
    for tid in selected:
        info = tools_by_id.get(tid)
        adapter = ADAPTERS.get(tid)
        if not adapter or not info:
            continue
        if not info.installed:
            print(f"\n{info.name} is not installed on this machine.")
            print(f"  Download: {info.download_url}")
            print("  Skipping hook install.")
            continue
        path = adapter.install(ROOT)
        print(f"\nInstalled hooks for {info.name}")
        print(f"  Config: {path}")
        installed.append(tid)
    return installed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install AI audio notification hooks for Claude / Cursor / Antigravity"
    )
    parser.add_argument(
        "--tools",
        default="",
        help="Comma-separated tool ids: claude,cursor,antigravity",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Non-interactive: use --tools or all detected present tools",
    )
    args = parser.parse_args()

    print("ai-audio-notify installer")
    print(f"Repo: {ROOT}")

    tools = detect_all()
    tools_by_id = {t.id: t for t in tools}

    if args.tools:
        selected = [t.strip() for t in args.tools.split(",") if t.strip()]
    elif args.yes:
        selected = [t.id for t in tools if t.installed]
    else:
        selected = prompt_selection(tools)

    if not selected:
        print("\nNothing selected. Exiting.")
        return 1

    unknown = [t for t in selected if t not in ADAPTERS]
    if unknown:
        print(f"Unknown tools: {', '.join(unknown)}")
        return 1

    installed = install_tools(selected, tools_by_id)
    write_state(installed)

    print("\nDone.")
    if installed:
        print("Test sounds:")
        print(f'  "{sys.executable}" "{ROOT / "play.py"}" finished')
        print(f'  "{sys.executable}" "{ROOT / "play.py"}" attention')
        print("\nRestart Claude Code / Cursor / Antigravity sessions so hooks reload.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
