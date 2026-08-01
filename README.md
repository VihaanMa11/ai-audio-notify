# ai-audio-notify

Audio notifications for AI coding agents: one sound when a task **finishes**, another when the
agent **needs your attention**.

Works with **Claude Code**, **Cursor**, and **Google Antigravity**. Sounds live in this repo so
you can swap them anytime.

## One-command setup

```bash
cd ai-audio-notify
python install.py
```

The installer detects which tools are on your machine, lets you pick which to wire up, and
merges notification hooks into their configs. Missing apps get a download link (they are not
auto-installed).

Non-interactive example:

```bash
python install.py --tools claude,cursor,antigravity --yes
```

Then **restart** Claude Code / Cursor / Antigravity so hooks reload.

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

## Requirements

- Python 3.9+
- No pip packages — uses OS audio players only

## Layout

```text
ai-audio-notify/
├── install.py / uninstall.py / play.py
├── config.json
├── sounds/
├── lib/          # detect, merge, platforms
└── adapters/     # claude, cursor, antigravity
```

## License

MIT — see [LICENSE](LICENSE).
