---
name: chgk-find-sources
description: Research the internet to find a source URL and fact summary confirming each answer in a "Что? Где? Когда?" questions JSON produced by chgk-extract-questions. Use when the user asks to find sources, verify, confirm, or cite answers for extracted ChGK questions.
---

# ChGK answer source-finding

## Input

`args` is either a bare video ID (e.g. `gQY8DmmIUTc`) or an explicit path to a questions JSON.

- If it looks like a bare ID, resolve it to `youtube-transcript/output/questions/<id>.json`
  (relative to the repo root).
- Otherwise treat it as a path as given.
- If the file doesn't exist, tell the user and stop — don't guess at a different file.

Read and parse the JSON array. Each element has at least `number`, `author`, `question`,
`answer` (a rerun may already carry `source_url`/`source_summary`/`status` from a previous
pass — these will be overwritten).

## Per-question research instructions (give this verbatim to each subagent)

Тебе даны один вопрос и правильный ответ из игры «Что? Где? Когда?». Твоя задача — найти в
интернете источник, который ЯВНО подтверждает этот ответ.

1. Сформируй несколько поисковых запросов на основе вопроса и ответа: используй синонимы,
   альтернативные формулировки, разные поисковые триггеры («почему», «как называют», «факт»,
   «источник», «определение», «объяснение», «подтверждение»).
2. Ищи агрессивно и итеративно: если первый запрос не даёт прямого подтверждения, пробуй
   другие формулировки. Не останавливайся на первой попавшейся ссылке — ищи, пока не найдёшь
   источник, который прямо подтверждает именно этот ответ (а не просто близкий по теме).
3. **Источник должен быть на русском языке.** Используй только поисковые запросы и
   источники на русском языке (сайт может быть международным, но найденная страница/статья
   должна быть на русском). Не принимай источники на других языках, даже если они по теме
   ближе — продолжай искать русскоязычную страницу, которая подтверждает тот же факт.
4. Приоритет источников (жёсткий, по порядку):
   1) энциклопедии, образовательные ресурсы, университеты, официальные сайты;
   2) крупные национальные и международные СМИ;
   3) авторитетные тематические ресурсы и базы фактов.
   Пропускай сомнительные, неавторитетные или непроверяемые страницы.
5. Когда источник найден: извлеки итоговый URL и напиши краткое саммари (2-3 предложения,
   на русском, своими словами) факта, подтверждающего ответ, основанное только на том, что
   написано в источнике.
6. Если после честной попытки с несколькими запросами подтверждающий источник не найден,
   верни `source_url = "Не найдено"`, `source_summary = "Источник подтверждения не найден"`,
   `status = "Не найдено"`. Если источник найден, `status = "Найдено"`.

## Execution

1. Read and parse the input JSON array.
2. For every question object, spawn one `general-purpose` subagent via the Agent tool — pass
   it that object's `question` and `answer` text plus the research instructions above, and
   require it to return strict JSON: `{"source_url": ..., "source_summary": ..., "status": ...}`.
   **Launch all of these subagents in parallel** (a single message with one Agent tool call
   per question) rather than one at a time — each question's research is independent.
3. Merge each subagent's result into its corresponding question object: add/overwrite
   `source_url`, `source_summary`, `status` keys. Leave `number`/`author`/`question`/`answer`
   untouched. Match subagents back to their question by array index/`number`, not by response
   order.
4. Write the augmented array back to the **same file it was read from**
   (`json.dumps(..., ensure_ascii=False, indent=2)`). No CSV for this stage.
5. Report back to the user: a compact Markdown table (columns №, Ответ, Статус, Источник) and
   a one-line count of how many questions got `Найдено` vs `Не найдено`.
