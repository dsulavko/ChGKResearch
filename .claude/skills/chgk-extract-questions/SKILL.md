---
name: chgk-extract-questions
description: Parse a cleaned "Что? Где? Когда?" game transcript (from youtube-transcript/output/clean/) into a structured table of question number, author, full question text, and correct answer. Use when the user asks to extract, parse, or analyze questions/answers from a ChGK transcript or stenogram.
---

# ChGK question/answer extraction

## Input

`args` is either a bare video ID (e.g. `gQY8DmmIUTc`) or an explicit path to a cleaned
transcript.

- If it looks like a bare ID, resolve it to `youtube-transcript/output/clean/<id>.txt`
  (relative to the repo root).
- Otherwise treat it as a path as given.
- If the file doesn't exist, tell the user and stop — don't guess at a different file.

Read the whole transcript before doing anything else.

## Extraction rules (apply exactly as written)

Преобразовывать фрагменты стенограмм игры «Что? Где? Когда?» в структурированную
таблицу со следующими колонками: номер вопроса; автор вопроса (в формате «Имя Фамилия
(Город)»; если нет — «не указан»); полный текст вопроса; правильный ответ.

**Где начинается вопрос.** Вопрос начинается с любой из типичных меток: «Вопрос:»,
«Вопрос номер X», «Вопрос №X», «Вопрос N», «Следующий вопрос…», «Внимание, вопрос!»,
«Читаю вопрос…», «Сектор…» (если дальше следует текст вопроса). Всё после этой метки до
официального объявления ответа — это полный текст вопроса.

**Что включать в полный текст вопроса.** Все абзацы и фразы между меткой вопроса и
объявлением ответа ведущим; ремарки ведущего, относящиеся к вопросу (например: «На
экране появляется фотография…»); описания видео/аудио/картин в текстовом виде;
упоминания сектора и ставки, если они находятся внутри блока вопроса.

Не включать: обсуждение команды, шутки и эмоции, реплики знатоков, «Время!»,
«Стоп-игра!».

**Определение автора вопроса.** Автор может быть указан в одной из форм: «Автор
вопроса — Иван Иванов, Москва.», «Вопрос прислал…», «Автор: …». Если автор указан не
полностью (только имя, только фамилия, только город) — сохранять как есть. Если автор
не указан — вернуть «не указан». Формат отображения: «Имя Фамилия (Город)»; если города
нет — без скобок; если указано иначе — не исправлять и не додумывать.

**Объявление правильного ответа.** Ответ начинается при появлении одной из меток:
«Правильный ответ: …», «Ответ: …», «Верный ответ — …», «Так что правильный ответ: …»,
либо просто декларация ведущего («Это …»). Всё, что после этих формулировок и до начала
следующего вопроса, считается ответом (кроме комментариев ведущего). Комментарии
ведущего после ответа не включать.

**Что считать шумом** (не должно попадать в таблицу): обсуждения игроков, предположения
знатоков, перебранки, «Стоп! Время!», звонок и т.п., оценочные комментарии ведущего, не
связанные с формулировкой вопроса.

## Execution

1. Read the full transcript file.
2. If it's longer than roughly 30,000 characters (true for essentially every full
   episode), delegate the actual extraction to a `general-purpose` subagent via the
   Agent tool rather than doing the close sequential read inline: pass it the rules
   above verbatim plus the transcript text (or its path), and ask it to return a JSON
   array of objects `{"number": ..., "author": ..., "question": ..., "answer": ...}`,
   in transcript order. For short transcripts, do the extraction directly.
3. Sanity-check coverage: count explicit markers like "Вопрос номер N" / "Вопрос №N" in
   the raw transcript and compare against the number of rows extracted. If rows are
   missing, note it rather than silently under-reporting.
4. Write the JSON array to `youtube-transcript/output/questions/<video_id>.json`
   (`json.dumps(..., ensure_ascii=False, indent=2)`).
5. Convert it to a CSV at `youtube-transcript/output/questions/<video_id>.csv` with
   columns `№,Автор,Вопрос,Ответ`. Do this with the stdlib `csv` module (e.g. a small
   `python3 -c` snippet reading the JSON just written) rather than hand-writing CSV
   text — question/answer text routinely contains commas and quotes that need proper
   escaping.
6. Report back to the user: how many questions were extracted, any coverage mismatch
   from step 3, and a short preview (first 2-3 rows).
