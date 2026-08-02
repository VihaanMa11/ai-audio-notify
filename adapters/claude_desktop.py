"""Install / uninstall hooks for the Claude Desktop app.

The Claude Desktop app runs its Claude Code and cowork sessions through the
same Claude Code engine, which loads Stop / Notification hooks from
~/.claude/settings.json. This adapter therefore shares its hook entries with
adapters/claude.py: installing either tool wires up both, and uninstalling
either removes the shared entries.

Plain claude.ai chats inside the desktop app do not expose local hooks, so
audio cues only fire for Claude Code / cowork sessions.
"""

from __future__ import annotations

from pathlib import Path

from adapters import claude as _claude


def settings_path() -> Path:
    return _claude.settings_path()


def install(repo_root: Path) -> Path:
    return _claude.install(repo_root)


def uninstall(repo_root: Path) -> Path | None:
    return _claude.uninstall(repo_root)
