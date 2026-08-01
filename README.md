# ai-audio-notify

Audio notifications for AI coding agents: one sound when a task **finishes**, another when the
agent **needs your attention**.

Works with **Claude Code**, **Cursor**, and **Google Antigravity**. Sounds live in this repo so
you can swap them anytime.

## Install (any machine)

### Windows — double-click

1. Clone or download this repo.
2. Double-click **`Install.bat`**.
3. When prompted, press **Enter** to wire all detected tools, or type numbers / ids
   (e.g. `1,2` or `claude,cursor`).
4. Restart those apps so hooks reload.

From CMD or PowerShell (in this folder):

```bat
Install.bat
```

### macOS / Linux

```bash
chmod +x install.sh
./install.sh
```

### Python directly

```bash
python install.py
```

Non-interactive:

```bash
python install.py --tools claude,cursor,antigravity --yes
```

The installer scans for AI tools, lets you pick which to wire up, and merges notification hooks.
Missing apps get a download link (they are not auto-installed). Requires **Python 3.9+** on PATH.

### Test sounds

```bash
python play.py finished
python play.py attention
```

## Replace the sounds

Overwrite the files in [`sounds/`](sounds/) (keep the names) or edit relative paths in
[`config.json`](config.json). See [`sounds/REPLACE.md`](sounds/REPLACE.md).

| Event | Default file | Source |
|---|---|---|
| Task finished | `sounds/task-finished.mp3` | Antoni — task complete |
| Needs attention | `sounds/needs-attention.mp3` | Antoni — input needed |

## What gets installed

| Tool | Finished | Attention |
|---|---|---|
| Claude Code | `Stop` hook → `~/.claude/settings.json` | `Notification` (permission / input) |
| Cursor | `stop` hook when `status=completed` → `~/.cursor/hooks.json` | Not available in v1 (no idle hook) |
| Antigravity | `Stop` when `fullyIdle` → `~/.gemini/config/hooks.json` | `PreToolUse` on `ask_permission` / `ask_question` |

Uninstall:

```bash
python uninstall.py
```

On Windows you can also run:

```bat
python uninstall.py
```

## Requirements

- Python 3.9+
- No pip packages — uses OS audio players only

## Layout

```text
ai-audio-notify/
├── Install.bat / install.sh   # one-click / one-command launchers
├── install.py / uninstall.py / play.py
├── config.json
├── sounds/
├── lib/          # detect, merge, platforms
└── adapters/     # claude, cursor, antigravity
```

## License

MIT — see [LICENSE](LICENSE).
