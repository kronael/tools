---
name: sweep
description: Dispatch a background audit for a PROBLEM CATEGORY across the whole codebase, filing each real instance in BUGS.md. NOT for a single known bug (use /bugs), NOT for fixing anything found (record-only, see CLAUDE.md Bug Triage Protocol), NOT for foreground/inline audits (use /dispatch directly).
when_to_use: "sweep for similar problems, find more like this across the codebase, are there other instances of this bug class, audit the whole repo for X pattern"
user-invocable: true
---

# Sweep

Launch (Agent tool, `run_in_background: true`, general-purpose, no waiting — same
launch shape as `/dispatch`) a background agent that audits the **entire**
codebase for one problem CATEGORY and files each real instance as its own
`BUGS.md` entry, per `/bugs`'s format/ID rules (read that skill first — sweep
is the search, not the file mechanics). Record only — never fix what it finds
(CLAUDE.md Bug Triage Protocol).

## Category

- `/sweep <description>` — audit for exactly that pattern, repo-wide.
- `/sweep` with no argument — read the most recent `BUGS.md` "✅ FIXED"/
  "Resolved" entries and the latest `.diary/` entry to find the pattern class
  of what was just fixed, then sweep for other instances of that same class
  that the original fix didn't touch.

## Coordination

Dispatch prompt must tell the agent to check `git status` first — if unrelated
uncommitted work is present (another agent active), stay read-only until the
final `BUGS.md` write.

Report back the entries filed (IDs + one-line titles), nothing else.
