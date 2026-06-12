---
name: diary
description: Write diary entries to <cwd>/.diary/YYYYMMDD.md. NOT for searching entries (use recall-memories).
when_to_use: after a commit, bug fix, or key decision, "log this decision"
user-invocable: true
---

# Diary

Path: `<cwd>/.diary/YYYYMMDD.md`. Append to today's entry; create if missing.

## Format

```markdown
---
summary: |
  Working on API gateway. Main focus: auth refactor.
  - twitter: cookies expired, needs refresh
  - discord: bot token missing in staging
---

## 10:32

Fixed WhatsApp reconnect backoff — was always resetting to attempt=1.
503 errors now get 20s minimum delay.

## 14:07

Output-styles confirmed working via SDK outputStyle option in settings.json.
```

YAML `summary:` — project, who you work with, up to 5 critical open items.
Update the summary on every diary write.

## Rules

- `## HH:MM` entries, 250 chars max per entry
- NEVER delete resolved open items — ALWAYS append `- [resolved YYYY-MM-DD: <how>]` instead
- ALWAYS log only decisions, bugs found/fixed, discoveries, open items
- NEVER log routine operations (reading files, answering questions)
- ALWAYS route preferences and recurring patterns to MEMORY.md, report to user verbatim
- ALWAYS review MEMORY.md for stale entries when writing diary
- ALWAYS apply the `writing` skill's copy rules — no preamble, plain verbs

## When to write

End of significant work: after commit, bug fix, key decision. Stop hook nudges — NEVER wait to be asked.
