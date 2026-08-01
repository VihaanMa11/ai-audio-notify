"""Install / uninstall Google Antigravity notification hooks."""

from __future__ import annotations

from pathlib import Path

from lib.merge_json import load_json, python_command, save_json

MARKER = "ai-audio-notify"


def hooks_path() -> Path:
    return Path.home() / ".gemini" / "config" / "hooks.json"


def _is_ours(entry: dict, repo_root: Path) -> bool:
    hooks = entry.get("hooks") or []
    for h in hooks:
        cmd = str(h.get("command") or "")
        if MARKER in cmd.replace("\\", "/") or str(repo_root).replace("\\", "/") in cmd.replace("\\", "/"):
            if "play.py" in cmd:
                return True
    return False


def _strip_ours(entries: list, repo_root: Path) -> list:
    return [e for e in entries if not (isinstance(e, dict) and _is_ours(e, repo_root))]


def install(repo_root: Path) -> Path:
    path = hooks_path()
    data = load_json(path, {})
    if not isinstance(data, dict):
        data = {}

    # Clean up legacy top-level key if present
    if MARKER in data:
        del data[MARKER]

    hooks = data.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        hooks = {}
        data["hooks"] = hooks

    finished = python_command(repo_root, "finished", "--antigravity-idle")
    attention = python_command(repo_root, "attention")

    stop = _strip_ours(list(hooks.get("Stop") or []), repo_root)
    stop.append(
        {
            "hooks": [
                {
                    "type": "command",
                    "command": finished,
                    "timeout": 10,
                }
            ]
        }
    )
    hooks["Stop"] = stop

    pre_tool = _strip_ours(list(hooks.get("PreToolUse") or []), repo_root)
    pre_tool.append(
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
    )
    hooks["PreToolUse"] = pre_tool

    save_json(path, data)
    return path


def uninstall(repo_root: Path) -> Path | None:
    path = hooks_path()
    if not path.is_file():
        return None
    data = load_json(path, {})
    if not isinstance(data, dict):
        return None

    changed = False
    if MARKER in data:
        del data[MARKER]
        changed = True

    hooks = data.get("hooks")
    if isinstance(hooks, dict):
        for key in ("Stop", "PreToolUse"):
            if key in hooks and isinstance(hooks[key], list):
                cleaned = _strip_ours(hooks[key], repo_root)
                if len(cleaned) != len(hooks[key]):
                    changed = True
                hooks[key] = cleaned

    if changed:
        save_json(path, data)
    return path
