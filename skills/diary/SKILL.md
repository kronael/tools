---
name: diary
description: Record what matters in <cwd>/.diary/YYYYMMDD.md. USE after significant work to log decisions/milestones. NOT for searching past entries (use recall-memories). Preferences and long-term patterns go to memory (tell the user).
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
- Only important things: decisions, bugs found/fixed, discoveries, open items
- Skip routine operations (reading files, answering questions)
- May compress earlier entries in the same day
- Preferences and recurring patterns → MEMORY.md, report to user verbatim
- Review MEMORY.md for stale entries when writing diary

## When to write

Write at end of significant work (after commit, after fixing a bug,
after a key decision). The Stop hook will nudge — don't wait to be asked.
