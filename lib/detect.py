"""Detect installed AI coding tools."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ToolInfo:
    id: str
    name: str
    installed: bool
    download_url: str
    detail: str = ""


def home() -> Path:
    return Path.home()


def _which(names: list[str]) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def detect_claude() -> ToolInfo:
    path = _which(["claude", "claude.exe"])
    settings = home() / ".claude"
    installed = bool(path) or settings.is_dir()
    detail = path or (str(settings) if settings.is_dir() else "")
    return ToolInfo(
        id="claude",
        name="Claude Code",
        installed=installed,
        download_url="https://docs.anthropic.com/en/docs/claude-code",
        detail=detail,
    )


def detect_cursor() -> ToolInfo:
    path = _which(["cursor", "cursor.exe", "Cursor"])
    cursor_dir = home() / ".cursor"
    # Common Windows install locations
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    app_paths = [
        local / "Programs" / "cursor" / "Cursor.exe",
        local / "Programs" / "Cursor" / "Cursor.exe",
    ]
    has_app = any(p.is_file() for p in app_paths)
    installed = bool(path) or cursor_dir.is_dir() or has_app
    detail = path or (str(cursor_dir) if cursor_dir.is_dir() else "")
    return ToolInfo(
        id="cursor",
        name="Cursor",
        installed=installed,
        download_url="https://cursor.com",
        detail=detail,
    )


def detect_antigravity() -> ToolInfo:
    path = _which(["agy", "agy.exe", "antigravity"])
    gemini = home() / ".gemini"
    markers = [
        gemini / "antigravity",
        gemini / "antigravity-cli",
        gemini / "antigravity-ide",
        gemini / "config",
    ]
    has_marker = any(m.exists() for m in markers)
    installed = bool(path) or has_marker
    detail = path or (str(gemini) if gemini.is_dir() else "")
    return ToolInfo(
        id="antigravity",
        name="Google Antigravity",
        installed=installed,
        download_url="https://antigravity.google",
        detail=detail,
    )


DETECTORS = {
    "claude": detect_claude,
    "cursor": detect_cursor,
    "antigravity": detect_antigravity,
}


def detect_all(tool_ids: list[str] | None = None) -> list[ToolInfo]:
    ids = tool_ids or list(DETECTORS.keys())
    results: list[ToolInfo] = []
    for tid in ids:
        fn = DETECTORS.get(tid)
        if fn:
            results.append(fn())
    return results
