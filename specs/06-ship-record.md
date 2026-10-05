---
status: shipped
---

# Ship record in plan mode's directory

The shipping work record — the `ship` plan, the `assess`, `eval-all` and
`specs` critiques, and any other typed scratch file a skill writes while
delivering a change — lives at `<main tree>/.claude/plans/`: the directory
Claude Code's plan mode writes to once `<main tree>/.claude/settings.json`
sets `"plansDirectory": ".claude/plans"`. Flat, kept out of git by a
root-anchored `/.claude/plans/` line in the project's `.gitignore`.

## Problem

Claude Code already writes plans: plan mode keeps one file per session in a
directory the `plansDirectory` setting names
(code.claude.com/docs/en/settings-reference#plansdirectory). A separate
directory for the shipping record — `.ship/`, `.claude/ship/` — is a second
place for plans under another name: one more convention a reader of the
checkout has to learn, one more ignore line, and the plan-mode plan and the
ship plan for the same change in two directories. The record belongs where
plan mode writes.

## Location

`<main tree>/.claude/plans/<type>-<name>.md`. A record carries its type as
the filename prefix: `plan-NN-name.md`, `critique-<role>-<date>.md`,
`critique-useless-<date>.md`, `eval-all-<date>.md`. Plan mode names its own
files after the session slug — `<slug>.md` and a `<slug>.workshop.md`
sibling, the slug a generated kebab word string (`getPlanSlug` in the
binary, validated by `^[a-z0-9][a-z0-9-]{0,119}$`) — so a reader tells the
two apart by the type prefix.

- Project-local, not `~/.claude/plans/`, because the retention sweep deletes
  the default directory and leaves a project-local one alone. The docs scope
  the "Cleaned up automatically" table to paths under `~/.claude/` and list
  `plans/` there (code.claude.com/docs/en/claude-directory). In Claude Code
  2.1.289 the plan-directory resolver returns the project root joined with
  `plansDirectory` when the setting is present (rejecting a path outside the
  root with `plansDirectory must be within project root`), while the sweep
  walks `join(configDir, "plans")` — `~/.claude/plans` — and never the
  resolved directory. Observed on that version with a throwaway `HOME`: a
  60-day-old file in `~/.claude/plans/` was deleted with its directory at
  startup; a 60-day-old file in the project's `.claude/plans/`, with
  `plansDirectory` set, stayed.
- Main tree, not the current worktree: the first entry of `git worktree
  list`, addressed by absolute path from every worktree. A linked worktree
  is a fresh checkout that `git worktree remove` deletes, and a gitignored
  file in it is invisible from the main tree. `diary` resolves the main
  tree the same way for a gitignored diary. From a worktree at
  `<root>/.wt1` of a repository at `<root>`, the record is
  `<root>/.claude/plans/plan-03-foo.md`.
- The setting lives in the committed `<main tree>/.claude/settings.json`, so
  every clone's plan mode writes into the same directory; `settings.local.json` is personal
  and never touched. A project that already pins `plansDirectory` elsewhere
  keeps its record there — the setting is the rule, not this name.
- A reader of the checkout finds plans and shipping scratch in one place,
  where agent state already lives.

### Rejected

- `~/.claude/plans/` as it comes — swept after `cleanupPeriodDays` (30 days
  by default), outside the repository, invisible from a container or a second
  machine.
- `.claude/ship/` — collides with nothing, but it is a second plans directory
  beside plan mode's, and the house layout had to ban `plans/` by name to
  keep the two apart.
- `.plans/`, `.ship/` — no part of Claude Code reads or writes them.
- `plansDirectory` in the user-level `settings-recommended.json` — the
  setting resolves against each project root, so plan mode would create an
  untracked `.claude/plans/` in every project with no ignore line, and a
  clone on a machine without the bundle would still write to
  `~/.claude/plans/`. The project setting travels with the clone.
- `~/.claude/projects/<project>/` — outside the repository, and Claude Code
  owns its layout and sweeps the transcripts beside it.
- The session scratchpad — purged with the OS temp directory and unknown to
  the next session; the record has to outlive both.

## Gitignore and the setting

The rule is `/.claude/plans/`: root-anchored per the house layout rule, with
the trailing slash so only the directory matches. It leaves the committed
content of `.claude/` — `settings.json`, `commands/`, `skills/`, `agents/`,
`rules/` — tracked, which a bare `.claude/` line does not.

A project acquires both from the first skill that writes there. `ship` §
Work record has the writer add `"plansDirectory": ".claude/plans"` to that
settings file when the key is absent, append `/.claude/plans/` to
`.gitignore` when `git check-ignore -q .claude/plans/x` fails, and commit
the two alone. A project that already ignores all of `.claude/` passes the
check and gets no line; its settings file is then local to that machine,
which still points plan mode at the directory there. `assess`, `eval-all`
and `skills/specs/useless.md` point at that section rather than repeating it.

Rejected: a global git exclude, which is what Claude Code does for
`settings.local.json`, protects one machine and lets a fresh clone commit
the record; a hook or the `ship` CLI is machinery `skills/ship/runtime.md`
forbids, and not every record is written through either.

## Codex

Codex builds its instruction chain from `~/.codex/AGENTS.override.md` or
`~/.codex/AGENTS.md`, then, from the project root down to the working
directory, one file per directory: `AGENTS.override.md`, `AGENTS.md`, then
the `project_doc_fallback_filenames` list (`CLAUDE.md` here, set by the
Codex bridge in `kronael/sync/reference.md`), concatenated root-down
(developers.openai.com/codex/guides/agents-md). The bundle's Kronael block
(`codex/AGENTS.md`, merged into `~/.codex/AGENTS.md` by `kronael/sync` step
6) also tells Codex to read `~/.claude/CLAUDE.md`, whose layout line names
the directory, and the `ship` skill reaches Codex through
`~/.agents/skills`.

The bundle ships no project `AGENTS.md` template — only that global block
and the pointer example in `kronael/sync/reference.md` — so the rule Codex
must not miss is stated in the block itself: the path, the ignore line and
the reuse of the active change's record, with `ship` § Work record as the
owner. The `astra` and `sol` skills launch Codex; Codex reads its own
instruction chain, not theirs, so they carry no copy.

## The `ship` CLI

The CLI (kronael/ship, checked out at `~/app/refs/ship`) keeps its own
state — `tasks.json`, `work.json`, a lock, logs and the trace — in
`DATA_DIR`, default `.ship` (its `config.py`), and wipes that directory on
a fresh start (`_wipe_state` in its `__main__.py`). That state is the
CLI's, not the work record, and a directory the CLI wipes cannot hold the
record. `skills/ship/cli.md` names the CLI's directory as the CLI's own and
forbids pointing `DATA_DIR` at `.claude/plans/`. The CLI needs no change for
this spec.

## Transition

Nothing in the bundle reads `.ship/` or `.claude/ship/`. A change whose
record already exists is reused where it is: `ship` Stage 1 recovers the
record from the diary, the transcript and the owner's words, which carry its
path, and a record is never relocated mid-change because a running session
addresses it by absolute path. Existing `.ship/` and `.claude/ship/`
directories are the owner's to move or delete. This repository's own
`.gitignore` ignores `.claude/` whole and keeps `/.ship/` for as long as that
directory exists.

## Code pointers

- `skills/ship/SKILL.md` § Work record — the location, the main-tree rule,
  the setting and the ignore check; the one place the rule lives.
- `skills/ship/cli.md` — the CLI's directory is not the record's.
- `skills/assess/SKILL.md`, `skills/eval-all/SKILL.md`,
  `skills/specs/useless.md` — critiques written into the same directory.
- `skills/readme/topology.md` — the house layout and the root-anchored
  ignore list; `skills/global/SKILL.md` § Documentation carries the one-line
  form that `~/.claude/CLAUDE.md` is generated from.
- `codex/AGENTS.md` — the Kronael block's statement of the directory for
  Codex.
- `skills/software/docker.md` — `.dockerignore` excludes `.claude` whole.
