"""Install / uninstall Cursor notification hooks."""

from __future__ import annotations

from pathlib import Path

from lib.merge_json import load_json, save_json

MARKER = "ai-audio-notify"


def hooks_path() -> Path:
    return Path.home() / ".cursor" / "hooks.json"


def wrapper_path(repo_root: Path) -> Path:
    return repo_root / "adapters" / "cursor_stop.py"


def _is_ours(entry: dict, repo_root: Path) -> bool:
    cmd = str(entry.get("command") or "")
    root = str(repo_root).replace("\\", "/").lower()
    normalized = cmd.replace("\\", "/").lower()
    return MARKER in normalized or ("play.py" in normalized and root in normalized) or "cursor_stop.py" in normalized


def install(repo_root: Path) -> Path:
    path = hooks_path()
    data = load_json(path, {"version": 1, "hooks": {}})
    if not isinstance(data, dict):
        data = {"version": 1, "hooks": {}}
    data.setdefault("version", 1)
    hooks = data.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        hooks = {}
        data["hooks"] = hooks

    # Prefer dedicated wrapper for reading stdin once
    wrapper = wrapper_path(repo_root)
    import sys

    py = sys.executable or "python"
    cmd = f'"{py}" "{wrapper.resolve()}"'

    stop = [e for e in (hooks.get("stop") or []) if not (isinstance(e, dict) and _is_ours(e, repo_root))]
    stop.append({"command": cmd})
    hooks["stop"] = stop

    save_json(path, data)
    return path


def uninstall(repo_root: Path) -> Path | None:
    path = hooks_path()
    if not path.is_file():
        return None
    data = load_json(path, {})
    if not isinstance(data, dict):
        return None
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return None
    if "stop" in hooks and isinstance(hooks["stop"], list):
        cleaned = [e for e in hooks["stop"] if not (isinstance(e, dict) and _is_ours(e, repo_root))]
        if len(cleaned) != len(hooks["stop"]):
            hooks["stop"] = cleaned
            save_json(path, data)
    return path
