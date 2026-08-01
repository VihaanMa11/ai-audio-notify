# Custom sounds

Default cues are short Antoni-style voice lines:

| Event | File |
| --- | --- |
| Task finished | `task-finished.mp3` |
| Needs attention | `needs-attention.mp3` |

## Replace in 30 seconds

1. Generate or download two short MP3s (see the main [README](../README.md#where-to-generate-audio)).
2. Overwrite the two files above **with the same names**, **or** add new files and edit `../config.json`.
3. Test:

```bash
python ../play.py finished
python ../play.py attention
```

No reinstall required — hooks always call `play.py`, which reads `config.json`.

## config.json example

```json
{
  "sounds": {
    "finished": "sounds/task-finished.mp3",
    "attention": "sounds/needs-attention.mp3"
  }
}
```

Use paths **relative to the repo root** only.

## Good clip checklist

- Under ~3 seconds
- Distinct “done” vs “need you” character
- Normalized volume (Audacity → Normalize is fine)
- MP3 preferred for cross-platform playback
