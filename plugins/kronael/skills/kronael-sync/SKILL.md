---
name: kronael-sync
description: Sync Kronael into ~/.claude from Codex (bundle + CLI tools rig/udfix/dockbox), first setup included; bridge global/project CLAUDE.md, skills, and hooks into Codex. NOT for a sync inside Claude Code (use /kronael:sync) or bringing the git line up to date with origin (use merge).
when_to_use: "@kronael-sync, sync kronael from codex, set up kronael in codex, bridge claude skills into codex, bridge hooks into codex, kronael skills missing in codex, kronael hooks missing in codex"
---

# Kronael Sync

ALWAYS sync the existing Claude Code bundle from the Source Root below.
NEVER copy or port the bundle into the Codex plugin directory.

The installed Codex plugin contains only this sync skill. It does NOT
contain the Kronael Claude skills. Codex sees those skills only through the
Codex Bridge (`~/.agents/skills` or project `.agents/skills`). For sync
requests from Codex, create the global bridge and install Codex hook wiring
automatically after the sync succeeds.

## Invocation

Users usually invoke:

```text
Use @kronael-sync to sync Kronael.
```

If the user says "sync kronael" or "install kronael" without naming this
skill, still run this workflow.

If the user asks only to make Codex see the installed skills, or says skills
are missing after a sync, skip the sync workflow and use the Codex Bridge
section.

## Source Root

For sync requests, find the source root by checking, in order:

1. Ancestors of `cwd`.
2. Ancestors of this skill's path.
3. Codex marketplace snapshots:
   - `$CODEX_HOME/.tmp/marketplaces/*`
   - `~/.codex/.tmp/marketplaces/*`

The source root is the first directory that holds the asset list of
`kronael/sync/SKILL.md` step 0 plus `kronael/sync/SKILL.md` and
`kronael/sync/reference.md`.

NEVER use the installed plugin cache as the bundle source unless it holds
all of them; normal plugin installs cache only this bridge skill.

If no source root is found, ask the user to run
`codex plugin marketplace add kronael/tools` or
`codex plugin marketplace upgrade kronael` (`kronael-local` for older
installs), then start a fresh Codex thread. NEVER invent paths. The Codex
plugin is only a sync bridge; the GitHub marketplace snapshot owns the
bundle.

For Codex Bridge-only requests, discover the source root when the requested
bridge step needs source-owned files (`codex/AGENTS.md`, `codex-hooks.json`, or
per-skill symlinks). Skip source-root discovery only for project guidance or the
simple `~/.agents/skills -> ~/.claude/skills` symlink case.

## Sync

1. Read `kronael/sync/SKILL.md` completely, plus the
   `kronael/sync/reference.md` it points to, and follow them as the source of
   truth from the discovered source root. NEVER run `/kronael:sync`; that is a
   Claude Code slash command.
2. Present the first-sync questionnaire inline as numbered options. NEVER
   restate or fork the canonical steps here; that file is the only source of
   truth and copies drift.
3. After a successful sync from Codex, run the Codex Bridge below. This is
   part of the Codex sync path.

## Codex Bridge

Run `kronael/sync/reference.md` § Codex bridge from the discovered source
root. A bridge-only request reads the same section. The two steps that need
no source run without one: the top-level key
`project_doc_fallback_filenames = ["CLAUDE.md"]` in `~/.codex/config.toml`,
and `ln -s ~/.claude/skills ~/.agents/skills` when `~/.agents/skills` is
absent; anything else waits for the source root.

## Report

Report only:

- canonical sync result from `kronael/sync/SKILL.md` if the sync ran
- Codex bridge paths changed: `~/.codex/AGENTS.md`, `~/.codex/config.toml`, project `AGENTS.md`,
  `~/.agents/skills`, `.agents/skills`, `~/.codex/hooks.json`
- whether Codex can now see global guidance, installed skills, and hook wiring; tell the
  user to start a new thread, use `/skills` or `@skill-name`, and open `/hooks`
  once to trust changed hooks

NEVER duplicate the full sync report in the bridge. Link paths and say
whether each bridge step was applied or skipped.
