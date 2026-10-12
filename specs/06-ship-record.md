---
status: shipped
---

# Ship record under the global Claude directory

The shipping work record — the `ship` plan, the `eval` and `specs`
critiques, and any other typed scratch file a skill writes while delivering
a change — lives at `~/.claude/projects/<slug>/ship/`, beside the project's
transcripts and `memory/`. Plan mode's own plans stay in Claude Code's
default `~/.claude/plans/`. A repository carries none of it: no
`plansDirectory` setting, no `.claude/plans/` or `.ship/` directory, no
ignore line.

## Problem

A record kept inside the repository needs machinery in every repository: a
committed `.claude/settings.json` pinning `plansDirectory`, a root-anchored
`/.claude/plans/` ignore line, and a `.ship/` the CLI leaves behind — three
artifacts per clone that exist for the agent, not the project, and that
every new repository has to acquire before its first record. The owner's
rule: plans and ship records live in the global Claude directory, never in
a repo.

## Location

`~/.claude/projects/<slug>/ship/<type>-<name>.md`. A record carries its
type as the filename prefix: `plan-NN-name.md`, `critique-<role>-<date>.md`,
`critique-useless-<date>.md`, `eval-all-<date>.md`.

- `<slug>` is the MAIN tree's absolute path with every non-alphanumeric
  character replaced by `-` — the directory Claude Code keeps that tree's
  transcripts and `memory/` in. A session started in a linked worktree gets
  its own transcript directory under the worktree's path; the record dir is
  keyed on the main tree regardless. `skills/ship/SKILL.md` § Work record is
  the one place that names the dir; every other skill points at it.
- Addressed by absolute path from every worktree: the dir is keyed on the
  main tree, and `git worktree remove` deletes whatever a worktree holds.
- Plan mode: with `plansDirectory` unset, Claude Code writes plans to
  `~/.claude/plans` (code.claude.com/docs/en/settings-reference#plansdirectory:
  "unset, so Claude Code uses `~/.claude/plans`"). Nothing to configure.
- Retention: `cleanupPeriodDays` governs the transcript sweep; `kronael/sync`
  step 5 sets it to 3650000 on every synced host. The docs list `plans/`
  among the swept application data and `memory/` as kept beside the
  transcripts (code.claude.com/docs/en/claude-directory); whether the sweep
  walks a `ship/` sibling is not documented and was not measured.

### Rejected

- `<main tree>/.claude/plans/` pinned by `plansDirectory` — survives the
  sweep and sits beside the checkout, but costs a settings file, an ignore
  line and a `.claude/plans/` in every repository.
- `~/.claude/plans/` for the ship record — plan mode names its own files by
  a generated session slug in the same flat directory, and the sweep lists
  it.
- `.ship/`, `.plans/` in the tree — no part of Claude Code reads them, and
  they are repository artifacts for the agent's benefit.
- The session scratchpad — purged with the OS temp directory and unknown to
  the next session.

## Codex

The Kronael block (`codex/AGENTS.md`, merged into `~/.codex/AGENTS.md` by
`kronael/sync` step 6) states the NEVER half — no plan machinery in a
repository — and points at `ship` § Work record for the dir; the `ship`
skill reaches Codex through `~/.agents/skills`.

## The `ship` CLI

The CLI (kronael/ship) keeps `tasks.json`, `work.json`, a lock and logs in
`DATA_DIR`, default `.ship/<spec slug>` under the working directory
(`config.py:165`, `__main__.py:326`), and wipes it on `-f`, on stale state
and on a changed spec (`__main__.py:364-445`); `DATA_DIR` replaces the
per-spec subdirectory. `skills/ship/cli.md` launches it with
`DATA_DIR=<record dir>/cli/<plan name>`, so a wipe reaches neither the
record nor another change's state and no `.ship/` is created for state. Its
trace log is hard-coded under the working directory's `.ship/`
(`claude_code.py:333`) and lands in the tree until the CLI changes —
`BUGS.md` SHIP-CLI-TRACE-LOG-IN-TREE.

## Transition

A change whose record already exists is reused where it is; a record is
never relocated mid-change. The owner moves settled records: `plan-*`,
`critique-*` and `eval-all-*` files from a repository's `.claude/plans/` or
`.ship/` into `~/.claude/projects/<slug>/ship/`, plan mode's slug-named
files into `~/.claude/plans/`, then drops the `plansDirectory` key and the
`/.claude/plans/` ignore line. Repositories with a tracked
`.claude/settings.json` carrying `plansDirectory` are their owners' to
change. This repository's `.gitignore` keeps `/.ship/` while the CLI's trace
log lands there.

## Code pointers

- `skills/ship/SKILL.md` § Work record — the dir, the slug, the main-tree
  rule and the NEVER list; the one place the dir is named.
- `skills/ship/cli.md` — `DATA_DIR` placement; the CLI's directory is not
  the record's.
- `skills/eval/SKILL.md`, `skills/eval/all.md`,
  `skills/eval/ceo/demo-audit.md`, `skills/eval/cto/code-audit.md`,
  `skills/specs/useless.md` — critiques written into the record dir.
- `skills/readme/topology.md` — the house layout and the root-anchored
  ignore list; `skills/global/SKILL.md` § Documentation carries the one-line
  form that `~/.claude/CLAUDE.md` is generated from; `hooks/prompt_nudge.py`
  `DOCS_RULES` is the hook's copy of it.
- `codex/AGENTS.md` — the Kronael block's statement for Codex.
