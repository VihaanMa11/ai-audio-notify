"""Cross-platform MP3 playback helpers (stdlib only)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def play_file(path: Path) -> None:
    """Play an audio file using the best available OS player. Never raises."""
    path = path.resolve()
    if not path.is_file():
        return

    try:
        if sys.platform == "darwin":
            _play_macos(path)
        elif sys.platform == "win32":
            _play_windows(path)
        else:
            _play_linux(path)
    except Exception:
        pass


def _play_macos(path: Path) -> None:
    subprocess.Popen(
        ["afplay", str(path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _play_linux(path: Path) -> None:
    candidates = [
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(path)],
        ["mpg123", "-q", str(path)],
        ["paplay", str(path)],
        ["aplay", str(path)],
    ]
    for cmd in candidates:
        if shutil.which(cmd[0]):
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return


def _play_windows(path: Path) -> None:
    # In-process winmm MCI starts audio almost immediately (no PowerShell cold start).
    # Blocking until the clip ends is fine: Cursor already detaches via cursor_stop.py,
    # and Claude Stop/Notification hooks can wait a couple seconds for the sound.
    if not _play_windows_mci(path):
        _play_windows_powershell(path)


def _play_windows_mci(path: Path) -> bool:
    """Play via winmm.dll. Blocks until playback ends. Returns False if open/play failed."""
    import ctypes

    winmm = ctypes.windll.winmm
    alias = f"aianotify{os.getpid()}"
    media = str(path.resolve())

    def mci(cmd: str) -> int:
        return int(winmm.mciSendStringW(cmd, None, 0, None))

    mci(f"close {alias}")
    err = mci(f'open "{media}" type mpegvideo alias {alias}')
    if err != 0:
        err = mci(f'open "{media}" alias {alias}')
    if err != 0:
        return False
    # Start immediately; `wait` only blocks until the clip finishes (does not delay start).
    err = mci(f"play {alias} wait")
    mci(f"close {alias}")
    return err == 0


def _play_windows_powershell(path: Path) -> None:
    # Fallback only: spawning powershell is slow (~0.5–2s).
    uri = path.as_uri()
    ps = f"""
Add-Type -AssemblyName PresentationCore
$p = New-Object System.Windows.Media.MediaPlayer
$p.Open([Uri]'{uri}')
$deadline = (Get-Date).AddSeconds(5)
while ($p.NaturalDuration.HasTimeSpan -eq $false -and (Get-Date) -lt $deadline) {{
  Start-Sleep -Milliseconds 20
}}
$p.Play()
if ($p.NaturalDuration.HasTimeSpan) {{
  Start-Sleep -Milliseconds ([int]$p.NaturalDuration.TimeSpan.TotalMilliseconds + 200)
}} else {{
  Start-Sleep -Seconds 3
}}
$p.Close()
"""
    subprocess.Popen(
        [
            "powershell.exe",
            "-NoProfile",
            "-WindowStyle",
            "Hidden",
            "-Command",
            ps,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def should_debounce(event: str, debounce_ms: int, state_dir: Path | None = None) -> bool:
    """Return True if this play should be skipped due to recent playback."""
    if debounce_ms <= 0:
        return False
    directory = state_dir or Path(os.environ.get("TEMP", "/tmp")) / "ai-audio-notify"
    try:
        directory.mkdir(parents=True, exist_ok=True)
        stamp = directory / f"last-{event}.ts"
        now = time.time()
        if stamp.is_file():
            try:
                last = float(stamp.read_text(encoding="utf-8").strip())
                if (now - last) * 1000 < debounce_ms:
                    return True
            except ValueError:
                pass
        stamp.write_text(str(now), encoding="utf-8")
    except Exception:
        return False
    return False
