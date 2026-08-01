"""Cross-platform MP3 playback helpers (stdlib only)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def _log(msg: str) -> None:
    try:
        directory = Path(os.environ.get("TEMP", "/tmp")) / "ai-audio-notify"
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / "last-play.log").open("a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")
    except Exception:
        pass


def play_file(path: Path) -> None:
    """Play an audio file using the best available OS player. Never raises."""
    path = path.resolve()
    if not path.is_file():
        _log(f"missing file: {path}")
        return

    try:
        if sys.platform == "darwin":
            _play_macos(path)
        elif sys.platform == "win32":
            _play_windows(path)
        else:
            _play_linux(path)
    except Exception as exc:
        _log(f"play_file error: {exc!r}")


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
    # Order: CLI players → PowerShell MediaPlayer → MCI last-resort.
    # Many Windows installs lack the MCI mpegvideo driver (error 277); prefer
    # MediaPlayer so hooks don't wait on a guaranteed failure.
    if _play_windows_cli(path):
        _log(f"ok cli: {path.name}")
        return
    if _play_windows_powershell(path):
        _log(f"ok powershell: {path.name}")
        return
    if _play_windows_mci(path):
        _log(f"ok mci: {path.name}")
        return
    _log(f"FAIL all players: {path}")


def _play_windows_cli(path: Path) -> bool:
    for cmd in (
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(path)],
        ["mpg123", "-q", str(path)],
    ):
        if not shutil.which(cmd[0]):
            continue
        try:
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                timeout=60,
                check=False,
            )
            return True
        except Exception:
            continue
    return False


def _play_windows_mci(path: Path) -> bool:
    """Play via winmm.dll. Returns False if the driver/file cannot open."""
    import ctypes

    winmm = ctypes.windll.winmm
    alias = f"aianotify{os.getpid()}"
    media = str(path.resolve())
    err_buf = ctypes.create_unicode_buffer(256)

    def mci(cmd: str) -> int:
        return int(winmm.mciSendStringW(cmd, None, 0, None))

    mci(f"close {alias}")
    for open_cmd in (
        f'open "{media}" type mpegvideo alias {alias}',
        f'open "{media}" type MPEGVideo alias {alias}',
        f'open "{media}" alias {alias}',
    ):
        err = mci(open_cmd)
        if err == 0:
            break
    else:
        winmm.mciGetErrorStringW(err, err_buf, 255)
        _log(f"mci open failed ({err}): {err_buf.value}")
        return False

    err = mci(f"play {alias} wait")
    mci(f"close {alias}")
    if err != 0:
        winmm.mciGetErrorStringW(err, err_buf, 255)
        _log(f"mci play failed ({err}): {err_buf.value}")
        return False
    return True


def _play_windows_powershell(path: Path) -> bool:
    """Reliable MP3 playback via WPF MediaPlayer (blocks until done)."""
    uri = path.resolve().as_uri()
    # Single-quoted URI path; escape any single quotes in the path.
    safe_uri = uri.replace("'", "''")
    ps = f"""
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName PresentationCore
$p = New-Object System.Windows.Media.MediaPlayer
$p.Volume = 1.0
$p.Open([Uri]'{safe_uri}')
$p.Play()
$deadline = (Get-Date).AddSeconds(8)
while (-not $p.NaturalDuration.HasTimeSpan -and (Get-Date) -lt $deadline) {{
  Start-Sleep -Milliseconds 20
}}
if ($p.NaturalDuration.HasTimeSpan) {{
  $remaining = [int]$p.NaturalDuration.TimeSpan.TotalMilliseconds - [int]$p.Position.TotalMilliseconds + 200
  if ($remaining -lt 200) {{ $remaining = 200 }}
  Start-Sleep -Milliseconds $remaining
}} else {{
  Start-Sleep -Milliseconds 2500
}}
$p.Stop()
$p.Close()
"""
    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-WindowStyle",
                "Hidden",
                "-Command",
                ps,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            timeout=60,
            check=False,
        )
        if result.returncode != 0:
            err = (result.stderr or b"").decode("utf-8", errors="replace")[:300]
            _log(f"powershell failed ({result.returncode}): {err}")
            return False
        return True
    except Exception as exc:
        _log(f"powershell exception: {exc!r}")
        return False


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
