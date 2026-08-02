"""Install / uninstall Claude Code notification hooks."""

from __future__ import annotations

from pathlib import Path

from lib.merge_json import load_json, python_command, save_json

MARKER = "ai-audio-notify"


def settings_path() -> Path:
    return Path.home() / ".claude" / "settings.json"


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
    path = settings_path()
    data = load_json(path, {})
    if not isinstance(data, dict):
        data = {}
    hooks = data.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        hooks = {}
        data["hooks"] = hooks

    finished = python_command(repo_root, "finished")
    attention = python_command(repo_root, "attention")

    stop = _strip_ours(list(hooks.get("Stop") or []), repo_root)
    stop.append(
        {
            "hooks": [
                {
                    "type": "command",
                    "command": finished,
                }
            ]
        }
    )
    hooks["Stop"] = stop

    # No matcher: catch every notification (permission prompts, questions,
    # and the "waiting for your input" idle notice) so the attention cue
    # always fires. A restrictive matcher here can silently never match.
    notif = _strip_ours(list(hooks.get("Notification") or []), repo_root)
    notif.append(
        {
            "hooks": [
                {
                    "type": "command",
                    "command": attention,
                }
            ],
        }
    )
    hooks["Notification"] = notif

    save_json(path, data)
    return path


def uninstall(repo_root: Path) -> Path | None:
    path = settings_path()
    if not path.is_file():
        return None
    data = load_json(path, {})
    if not isinstance(data, dict):
        return None
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return None
    changed = False
    for key in ("Stop", "Notification"):
        if key in hooks and isinstance(hooks[key], list):
            cleaned = _strip_ours(hooks[key], repo_root)
            if len(cleaned) != len(hooks[key]):
                changed = True
            hooks[key] = cleaned
    if changed:
        save_json(path, data)
    return path
