# youtube-transcript

Fetches a YouTube video's captions and cleans them into a single continuous line of
plain text, ready to feed into further research.

## Usage

```
pip install -r requirements.txt
python fetch_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Options:

- `--lang <code>` — caption language to fetch (default: `ru`)
- `--output-dir <dir>` — where to write output (default: `output`)

This writes three files per video:

- `output/raw/<video_id>.json` — the raw caption track (YouTube's json3/srv3 format)
- `output/raw/<video_id>.meta.json` — title, channel, upload date, and which caption
  track (manual/automatic) was used
- `output/clean/<video_id>.txt` — the cleaned transcript: caption text joined into one
  line, with bracket annotations like `[музыка]`/`[смех]`/`[аплодисменты]` and line
  breaks stripped out

## Next stage: extracting questions

Once a transcript is cleaned, run the `/chgk-extract-questions` skill (in Claude Code,
from the repo root) to turn it into a structured table:

```
/chgk-extract-questions gQY8DmmIUTc
```

This reads `output/clean/<video_id>.txt`, applies the question/author/answer parsing
rules defined in `.claude/skills/chgk-extract-questions/SKILL.md`, and writes:

- `output/questions/<video_id>.json` — array of `{number, author, question, answer}`
- `output/questions/<video_id>.csv` — the same data as a spreadsheet-friendly CSV

## Next stage: finding sources

Once questions are extracted, run the `/chgk-find-sources` skill to research each
answer and attach a confirming source:

```
/chgk-find-sources gQY8DmmIUTc
```

This reads `output/questions/<video_id>.json`, runs one parallel web-research subagent
per question (rules in `.claude/skills/chgk-find-sources/SKILL.md`), and writes the
result back into the **same file**, adding `source_url`, `source_summary`, and `status`
(`Найдено` / `Не найдено`) to each question object.

## Notes

- Captions are fetched via `yt-dlp`, which resolves YouTube's signed caption URLs and
  handles its bot-detection challenges. If a fetch fails outright, try upgrading
  yt-dlp (`pip install -U yt-dlp`) — YouTube changes this fairly often — or pass a
  browser cookies file via yt-dlp's `cookiefile` option if a video needs it.
- Manual (human-provided) captions are preferred over auto-generated ones when both
  exist for the requested language.
