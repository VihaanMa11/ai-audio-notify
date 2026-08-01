"""Safe JSON load/save helpers for merging hook configs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MARKER = "ai-audio-notify"


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.is_file():
        return default
    try:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            return default
        return json.loads(text)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def command_mentions_repo(command: str, repo_root: Path) -> bool:
    if not command:
        return False
    normalized = command.replace("\\", "/").lower()
    root = str(repo_root).replace("\\", "/").lower()
    return MARKER in normalized or "play.py" in normalized and root in normalized


def python_command(repo_root: Path, *args: str) -> str:
    """Build a shell command that invokes play.py with this interpreter."""
    import sys

    py = sys.executable or "python"
    play = str((repo_root / "play.py").resolve())

    def q(value: str) -> str:
        # Quote only when needed so Windows CreateProcess/cmd both work.
        if any(ch in value for ch in ' \t"&<>|^'):
            return '"' + value.replace('"', '\\"') + '"'
        return value

    return " ".join([q(py), q(play), *args])
