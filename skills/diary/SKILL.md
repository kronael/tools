---
name: diary
description: "Write diary entries to .diary/YYYYMMDD.md (worktree-aware: tracked diary stays in the current worktree, gitignored diary goes to the main tree). NOT for searching entries (use recall-memories)."
when_to_use: "after a commit, bug fix, or key decision, log this decision"
user-invocable: true
---

# Diary

File: `.diary/YYYYMMDD.md`. Append to today's entry; create if missing.

## Where to write (worktree-aware)

The target tree depends on whether `.diary/` is tracked by git. Resolve it
BEFORE writing. Test the actual dated FILE path, not the bare `.diary` dir — a
`.diary/` gitignore rule does NOT match `git check-ignore .diary` (no trailing
slash) but DOES match `.diary/<file>`, so checking the dir gives a false "tracked":

```bash
git check-ignore -q ".diary/$(date +%Y%m%d).md" && echo ignored || echo tracked
```

- **Tracked (not gitignored)** → write in the **current worktree** (`<cwd>/.diary/`).
  A tracked diary is committed on its branch, so each worktree records its own
  work and the entry travels with that branch's commits.
- **Gitignored / not part of git** → write to the **main worktree**
  (`git worktree list | head -1 | awk '{print $1}'`), at `<main>/.diary/`.
  An ignored diary is never committed, so keep one canonical copy in the main
  tree instead of scattering ephemeral entries across worktrees.
- **Not a git repo** → fall back to `<cwd>/.diary/`.

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
