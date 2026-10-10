---
name: diary
description: "Write diary entries to ~/.claude/projects/<slug>/diary/YYYYMMDD.md, one dir per main tree, never inside a repo. Standalone reports, audits, and analyses go beside the daily log as YYYYMMDD-<name>.md. NOT for searching entries (use recall-memories)."
when_to_use: "after a commit, bug fix, or key decision, log this decision"
user-invocable: true
---

# Diary

## Where it lives

`~/.claude/projects/<slug>/diary/YYYYMMDD.md` — the **diary dir**, the UTC
date the Stop hook checks. `<slug>` is the MAIN tree's resolved path with
every non-alphanumeric character replaced by `-`: `/home/u/app/x` writes
`~/.claude/projects/-home-u-app-x/diary/`. The first entry of `git worktree
list` is that path, symlinks resolved; outside git use `pwd -P`, NEVER
`$PWD`. A submodule or a `--separate-git-dir` repo lists its git dir first,
so its diary keys on the git dir. Every route into the repo — a symlink, a
subdirectory, a linked worktree — shares this one diary, while Claude Code
may keep that session's transcripts under another slug. `mkdir -p` the dir
before the first write. Append to today's entry; create if missing.

A standalone document goes beside it as `YYYYMMDD-<name>.md` — see "Named
companions" below.

This section owns the dir — every other file points here. ALWAYS address
the diary by absolute path from every worktree: the dir is keyed on the main
tree, not on the worktree's cwd. NEVER put a diary in a repository: no
`.diary/` directory, no ignore line for one — what an agent writes for itself
lives under `~/.claude/`.

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
- ALWAYS route preferences and recurring patterns to memory (`learn` owns the format), report to user verbatim
- ALWAYS review MEMORY.md for stale entries when writing diary
- ALWAYS apply the `writing` skill's copy rules — no preamble, plain verbs

## Named companions

`YYYYMMDD-<name>.md` — same directory and date ordering as the daily log. Use
it for a standalone durable artifact that does not belong inline in the day's
running log: a report, an audit, a design analysis, a postmortem — a
self-contained document a future reader will want to open on its own. The
daily log `YYYYMMDD.md` stays the default and the place for the running
narrative.

- `<name>`: short, kebab-case, says what the document is
  (`20260904-refactor-neutrality.md`)
- ALWAYS reference a companion from that day's `YYYYMMDD.md` — the daily log
  remains the index into the day
- The `## HH:MM` / 250-char rules above scope the daily log; a companion is
  free-form prose in its own structure

## When to write

End of significant work: after commit, bug fix, key decision. Stop hook nudges — NEVER wait to be asked.
