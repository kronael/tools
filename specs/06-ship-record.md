---
status: planned
---

# Ship record under `.claude/ship/`

The shipping work record — the `ship` plan, the `assess`, `eval-all` and
`specs` critiques, and any other typed scratch file a skill writes while
delivering a change — lives at `<main tree>/.claude/ship/`, flat, kept out
of git by a root-anchored `/.claude/ship/` line in the project's
`.gitignore`.

## Problem

A bespoke top-level hidden directory is one more thing a reader of the
repository has to learn and one more `.gitignore` line every project carries
for a convention Claude Code knows nothing about. Claude Code already owns a
per-project directory, `.claude/`, and already keeps local-only working
state in subdirectories of it: `worktrees/`, which its docs tell the user to
add to `.gitignore`, and `agent-memory-local/`
(code.claude.com/docs/en/claude-directory, code.claude.com/docs/en/worktrees).
The record belongs in that directory, under that pattern.

## Location

`<main tree>/.claude/ship/<type>-<name>.md`. Filenames carry their type as
the prefix: `plan-NN-name.md`, `critique-<role>-<date>.md`,
`critique-useless-<date>.md`, `eval-all-<date>.md`.

- Main tree, not the current worktree: the first entry of `git worktree
  list`, addressed by absolute path from every worktree. A linked worktree
  is a fresh checkout that `git worktree remove` deletes, and a gitignored
  file in it is invisible from the main tree. `diary` resolves the main
  tree the same way for a gitignored diary. From a worktree at
  `<root>/.wt1` of a repository at `<root>`, the record is
  `<root>/.claude/ship/plan-03-foo.md`.
- `ship` collides with no name Claude Code uses under a project's `.claude/`.
  The documented entries are `CLAUDE.md`, `settings.json`,
  `settings.local.json`, `rules/`, `skills/`, `agents/`, `commands/`,
  `hooks/`, `output-styles/`, `workflows/`, `agent-memory/`,
  `agent-memory-local/` and `worktrees/`. The documented loaders read those
  directories by name; none scans `.claude/` for others, so a file in
  `.claude/ship/` never registers as a command, skill or rule.
- A reader of the checkout finds shipping scratch where agent state already
  lives, not in a second hidden directory at the root.

### Rejected

- `.claude/plans/` — Claude Code's `plansDirectory` setting points plan mode
  at a project-relative directory
  (code.claude.com/docs/en/settings-reference#plansdirectory), so this name
  invites plan mode's own files into the record directory, and Claude Code
  sweeps plan-mode files older than `cleanupPeriodDays` (30 days by default)
  from its default plans directory (claude-directory, "Cleaned up
  automatically"). Critiques, state and research files are not plans. The
  house layout rule bans a `plans/` directory by name; this spec keeps the
  ban intact instead of carving an exception into it.
- `.plans/` — no part of Claude Code reads or writes it, so it is no more
  Claude-native than `.ship/`; it is the banned `plans/` directory with a
  dot; it misnames every file that is not a plan.
- `~/.claude/projects/<project>/` — outside the repository: a container, a
  second machine or a reader of the checkout never sees it, and Claude Code
  owns its layout and sweeps the transcripts beside it.
- The session scratchpad — purged with the OS temp directory and unknown to
  the next session; the record has to outlive both.

## Gitignore

The rule is `/.claude/ship/`: root-anchored per the house layout rule, with
the trailing slash so only the directory matches. It leaves the committed
content of `.claude/` — `settings.json`, `commands/`, `skills/`, `agents/`,
`rules/` — tracked, which a bare `.claude/` line does not.

A project acquires it from the first skill that writes there. `ship` §
Work record has the writer run `git check-ignore -q .claude/ship/x` and,
when that fails, append `/.claude/ship/` to `.gitignore` and commit that
line alone. A project that already ignores all of `.claude/` passes the
check and gets no line. `assess`, `eval-all` and `skills/specs/useless.md` point at
that section rather than repeating it.

Rejected: a global git exclude, which is what Claude Code does for
`settings.local.json`, protects one machine and lets a fresh clone commit
the record; a hook or the `ship` CLI is machinery `skills/ship/runtime.md` forbids,
and not every record is written through either.

## The `ship` CLI

The CLI (kronael/ship, checked out at `~/app/refs/ship`) keeps its own
state — `tasks.json`, `work.json`, a lock, logs and the trace — in
`DATA_DIR`, default `.ship` (its `config.py`), and wipes that directory on
a fresh start (`_wipe_state` in its `__main__.py`). That state is the
CLI's, not the work record, and a directory the CLI wipes cannot hold the
record. `skills/ship/cli.md` names the CLI's directory as the CLI's own and forbids
pointing `DATA_DIR` at `.claude/ship/`. The CLI needs no change for this
spec; moving its default under `.claude/ship/<slug>/` is a separate proposal
for that repository.

## Transition

Nothing in the bundle reads `.ship/`. A change whose record already exists
is reused where it is: `ship` Stage 1 recovers the record from the diary,
the transcript and the owner's words, which carry its path, and a record is
never relocated mid-change because a running session addresses it by
absolute path. Existing `.ship/` directories are the owner's to move or
delete. This repository's own `.gitignore` keeps `/.ship/` for as long as
its directory exists.

## Code pointers

- `skills/ship/SKILL.md` § Work record — the location, the main-tree rule
  and the ignore check; the one place the rule lives.
- `skills/ship/cli.md` — the CLI's directory is not the record's.
- `skills/assess/SKILL.md`, `skills/eval-all/SKILL.md`,
  `skills/specs/useless.md` — critiques written into the same directory.
- `skills/readme/topology.md` — the house layout and the root-anchored
  ignore list; `skills/global/SKILL.md` § Documentation carries the one-line
  form that `~/.claude/CLAUDE.md` is generated from.
- `skills/software/docker.md` — `.dockerignore` excludes `.claude` whole.
