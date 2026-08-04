"""Install / uninstall Cursor notification hooks."""

from __future__ import annotations

from pathlib import Path

from lib.merge_json import load_json, save_json

MARKER = "ai-audio-notify"
OWN_SCRIPTS = ("cursor_stop.py", "cursor_attention.py", "play.py")


def hooks_path() -> Path:
    return Path.home() / ".cursor" / "hooks.json"


def stop_wrapper(repo_root: Path) -> Path:
    return repo_root / "adapters" / "cursor_stop.py"


def attention_wrapper(repo_root: Path) -> Path:
    return repo_root / "adapters" / "cursor_attention.py"


def _is_ours(entry: dict, repo_root: Path) -> bool:
    cmd = str(entry.get("command") or "")
    root = str(repo_root).replace("\\", "/").lower()
    normalized = cmd.replace("\\", "/").lower()
    if MARKER in normalized:
        return True
    if root in normalized and any(name in normalized for name in OWN_SCRIPTS):
        return True
    return any(name in normalized for name in OWN_SCRIPTS)


def _quote_cmd(py: str, script: Path) -> str:
    def q(value: str) -> str:
        text = str(value)
        if any(ch in text for ch in ' \t"&<>|^'):
            return '"' + text.replace('"', '\\"') + '"'
        return text

    return f"{q(py)} {q(str(script.resolve()))}"


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

    import sys

    py = sys.executable or "python"
    stop_cmd = _quote_cmd(py, stop_wrapper(repo_root))
    attention_cmd = _quote_cmd(py, attention_wrapper(repo_root))

    stop = [e for e in (hooks.get("stop") or []) if not (isinstance(e, dict) and _is_ours(e, repo_root))]
    stop.append({"command": stop_cmd})
    hooks["stop"] = stop

    # Approval holds: shell + MCP prompts play the "need you" attention cue.
    for key in ("beforeShellExecution", "beforeMCPExecution"):
        entries = [e for e in (hooks.get(key) or []) if not (isinstance(e, dict) and _is_ours(e, repo_root))]
        entries.append({"command": attention_cmd})
        hooks[key] = entries

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

    changed = False
    for key in ("stop", "beforeShellExecution", "beforeMCPExecution"):
        if key in hooks and isinstance(hooks[key], list):
            cleaned = [e for e in hooks[key] if not (isinstance(e, dict) and _is_ours(e, repo_root))]
            if len(cleaned) != len(hooks[key]):
                changed = True
            hooks[key] = cleaned

    if changed:
        save_json(path, data)
    return path
