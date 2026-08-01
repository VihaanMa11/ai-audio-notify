# ai-audio-notify

**Hear when your AI is done — and when it needs you.**

Drop-in audio cues for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Cursor](https://cursor.com), and [Google Antigravity](https://antigravity.google). One sound when a task finishes. Another when the agent is waiting for you.

Clone the repo, double-click install, optionally swap in your own voice. No accounts, no paid SDKs, no npm — just Python and two small MP3s.

| Cue | When it plays | Default file |
| --- | --- | --- |
| **Finished** | Agent turn / loop completed | `sounds/task-finished.mp3` |
| **Attention** | Permission prompt or input needed | `sounds/needs-attention.mp3` |

---

## Quick start

### 1. Get the repo

```bash
git clone https://github.com/VihaanMa11/ai-audio-notify.git
cd ai-audio-notify
```

Or download the ZIP from GitHub and open the folder.

### 2. Run the installer

**Windows** — double-click `Install.bat`  
(or in CMD / PowerShell: `Install.bat`)

**macOS / Linux**

```bash
chmod +x install.sh
./install.sh
```

**Already have Python handy**

```bash
python install.py
```

### 3. Pick your tools

The installer scans your machine and lists what it found (Claude Code, Cursor, Antigravity).

| You type | Result |
| --- | --- |
| `Enter` | Install for every tool that was detected |
| `all` | Install for every supported tool (even if missing — missing ones get download links) |
| `1,2` or `claude,cursor` | Install only the ones you choose |

### 4. Restart & test

Restart Claude Code / Cursor / Antigravity so hooks reload, then:

```bash
python play.py finished
python play.py attention
```

You should hear the default Antoni voice cues. Run a short agent task next — the finished sound should fire when it stops.

**Requirements:** Python 3.9+ on your PATH. No pip packages.

---

## Custom audio — use your own sounds

Everything lives in the `sounds/` folder. Hooks never hard-code absolute paths; they read relative paths from `config.json`.

### Option A — overwrite (simplest)

1. Create or download two short clips (ideally under ~3 seconds).
2. Replace these files **keeping the exact names**:
   - `sounds/task-finished.mp3` → finished cue  
   - `sounds/needs-attention.mp3` → attention cue  
3. Test:

```bash
python play.py finished
python play.py attention
```

No reinstall needed.

### Option B — new filenames

1. Put your files in `sounds/` (e.g. `my-done.mp3`, `my-ping.mp3`).
2. Edit `config.json`:

```json
{
  "sounds": {
    "finished": "sounds/my-done.mp3",
    "attention": "sounds/my-ping.mp3"
  },
  "debounce_ms": 400,
  "supported_tools": ["claude", "cursor", "antigravity"]
}
```

Paths must stay **relative to the repo root** (never `C:\...` or `/Users/...`).

### Tips for good notification audio

- Keep clips **short** (0.5–2.5s) so they don’t interrupt flow.
- Prefer **MP3**; WAV also works on most setups.
- Make the two cues **distinct** (pitch, word, or timbre) so “done” never sounds like “help.”
- Export at a moderate volume — OS notification levels vary.

More detail: [`sounds/REPLACE.md`](sounds/REPLACE.md).

---

## Where to generate audio

You can use any voice or SFX source. These are common options that work well for this project:

### AI voice (spoken cues)

| Tool | Notes |
| --- | --- |
| [ElevenLabs](https://elevenlabs.io) | High-quality TTS. Search voices (e.g. “Antoni”) or clone your own. Generate two lines like *“Task complete”* and *“Input needed”*, download MP3. |
| [OpenAI TTS](https://platform.openai.com/docs/guides/text-to-speech) | API / Playground voices; export and drop into `sounds/`. |
| [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech) | Many languages and neural voices. |
| [Microsoft Edge Read Aloud](https://www.microsoft.com/edge) + record | Free quick option: paste text, record system audio (quality varies). |
| macOS `say` | Built-in: `say -v Samantha "Task complete" -o finished.aiff` then convert to MP3. |

**Prompt ideas**

- Finished: `Task complete.` / `All done.` / `Ready for the next step.`
- Attention: `Input needed.` / `Waiting for you.` / `Approval required.`

### Sound effects (beeps, chimes, UI clicks)

| Source | Notes |
| --- | --- |
| [Freesound](https://freesound.org) | Huge CC library — filter by duration and license. |
| [Pixabay Sound Effects](https://pixabay.com/sound-effects/) | Free SFX, simple license for personal use. |
| [Mixkit](https://mixkit.co/free-sound-effects/) | Short UI / notification packs. |
| Your DAW | GarageBand, Audacity, FL Studio — design a two-note motif. |

### Convert / trim

- [Audacity](https://www.audacityteam.org) (free) — trim silence, normalize volume, export MP3.
- [CloudConvert](https://cloudconvert.com) — WAV/M4A → MP3 in the browser.

Then overwrite `sounds/task-finished.mp3` and `sounds/needs-attention.mp3` (or point `config.json` at your new files).

---

## What gets installed

The installer only adds **hooks** into tools already on your machine. It does not download Claude, Cursor, or Antigravity.

| Tool | Finished cue | Attention cue |
| --- | --- | --- |
| **Claude Code** | `Stop` → `~/.claude/settings.json` | `Notification` (permission / input) |
| **Cursor** | `stop` when `status=completed` → `~/.cursor/hooks.json` | Not available yet (no idle hook in v1) |
| **Antigravity** | `Stop` when fully idle → `~/.gemini/config/hooks.json` | `ask_permission` / `ask_question` |

### Uninstall

```bash
python uninstall.py
```

Removes this project’s hook entries and leaves your other settings alone.

### Non-interactive install

```bash
python install.py --tools claude,cursor,antigravity --yes
```

---

## Project layout

```text
ai-audio-notify/
├── Install.bat          # Windows: double-click to install
├── install.sh           # macOS / Linux launcher
├── install.py           # Detect tools → select → wire hooks
├── uninstall.py
├── play.py              # Plays finished / attention sounds
├── config.json          # Relative paths to your audio
├── sounds/
│   ├── task-finished.mp3
│   ├── needs-attention.mp3
│   └── REPLACE.md
├── lib/                 # Detect + playback helpers
└── adapters/            # Claude / Cursor / Antigravity hooks
```

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `Install.bat` says Python not found | Install [Python 3](https://www.python.org/downloads/) and enable **Add python.exe to PATH**, then run again. |
| No sound after an agent run | **Restart Cursor / Claude / Antigravity** so hooks reload. Run `python play.py finished` — you should hear audio. Check `%TEMP%\ai-audio-notify\last-play.log` for `ok powershell` / errors. |
| `play.py` silent on Windows | This PC may lack the MCI MP3 driver; the app falls back to PowerShell MediaPlayer. Confirm the log shows `ok powershell`. Unmute system volume. |
| Wrong or old sound | Confirm files under `sounds/` and paths in `config.json`. Test with `play.py`. |
| Sound fires twice | Debounce is in `config.json` (`debounce_ms`). Raise it slightly (e.g. `800`) if needed. |
| Tool shows “not found” | Install that app first, or skip it in the selector. The installer prints download links for missing tools. |

---

## License

MIT — see [LICENSE](LICENSE). Ship it, fork it, swap the voices, make it yours.
