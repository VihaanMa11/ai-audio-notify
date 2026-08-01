"""Install / uninstall Google Antigravity notification hooks."""

from __future__ import annotations

from pathlib import Path

from lib.merge_json import load_json, python_command, save_json

HOOK_NAME = "ai-audio-notify"


def hooks_path() -> Path:
    return Path.home() / ".gemini" / "config" / "hooks.json"


def install(repo_root: Path) -> Path:
    path = hooks_path()
    data = load_json(path, {})
    if not isinstance(data, dict):
        data = {}

    finished = python_command(repo_root, "finished", "--antigravity-idle")
    attention = python_command(repo_root, "attention")

    data[HOOK_NAME] = {
        "enabled": True,
        "Stop": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": finished,
                        "timeout": 10,
                    }
                ]
            }
        ],
        "PreToolUse": [
            {
                "matcher": "ask_permission|ask_question",
                "hooks": [
                    {
                        "type": "command",
                        "command": attention,
                        "timeout": 10,
                    }
                ],
            }
        ],
    }

    save_json(path, data)
    return path


def uninstall(repo_root: Path) -> Path | None:
    path = hooks_path()
    if not path.is_file():
        return None
    data = load_json(path, {})
    if not isinstance(data, dict):
        return None
    if HOOK_NAME in data:
        del data[HOOK_NAME]
        save_json(path, data)
    return path
