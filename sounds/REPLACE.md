# Replacing notification sounds

Default sounds (Antoni voice cues):

| Event | File |
|---|---|
| Task finished | `task-finished.mp3` |
| Needs attention | `needs-attention.mp3` |

## Quick replace

1. Drop your own audio files into this folder.
2. Either:
   - **Overwrite** `task-finished.mp3` / `needs-attention.mp3` with the same names, or
   - Put new files here and edit `../config.json` relative paths, e.g.:

```json
{
  "sounds": {
    "finished": "sounds/my-done.mp3",
    "attention": "sounds/my-ping.mp3"
  }
}
```

## Notes

- Paths in `config.json` must be **relative to the repo root** (never absolute).
- MP3 works on macOS (`afplay`), Windows (WPF MediaPlayer), and Linux (`ffplay` / `mpg123` / `paplay`).
- No reinstall needed after swapping files — hooks always call `play.py`, which reads `config.json`.
- Test with:

```bash
python play.py finished
python play.py attention
```
