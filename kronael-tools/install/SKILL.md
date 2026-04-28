---
name: install
description: Install (or update) the Kronael toolkit into ~/.claude/. Trigger when the user says "install kronael tools", "install the toolkit", or runs /kronael-tools:install. Copies skills, agents, and hook scripts; merges hook wiring and recommended settings into ~/.claude/settings.json; installs the wisdom skill body into ~/.claude/CLAUDE.md (always-loaded). Run once per machine, then again on plugin updates.
---

# Install Kronael toolkit

Goal: deploy the bundle from `${CLAUDE_PLUGIN_ROOT}` (the cached plugin repo) into `~/.claude/` so skills, agents, and hooks live in the user's persistent config and work bare (no `kronael-tools:` prefix).

## What you'll do

The plugin source contains, at the repo root:
- `skills/` — bundle of skills (language, workflow, domain)
- `agents/` — bundle of agents (@improve, @readme, @refine, …)
- `hooks/` — bundle of hook scripts (nudge.py, local.py, reclaude.py, learn.py, stop.py)
- `settings-recommended.json` — recommended permissions, sandbox, env, hook wiring

Copy them to `~/.claude/`, merge settings, and write the wisdom file.

## Steps

1. **Locate the bundle**. `${CLAUDE_PLUGIN_ROOT}` is the cached repo root — verify `skills/`, `agents/`, `hooks/`, `settings-recommended.json` are present there.

2. **Backup**. Before overwriting anything, copy current `~/.claude/{skills,agents,hooks,CLAUDE.md,settings.json}` to `~/.claude/backup/<timestamp>/`.

3. **Copy assets** (replace strategy):
   - `skills/*` → `~/.claude/skills/` (preserve user-added skills not in source — never delete)
   - `agents/*` → `~/.claude/agents/`
   - `hooks/*.py`, `hooks/lib/` → `~/.claude/hooks/`

4. **Install wisdom**. The `global` skill body (file: `skills/global/SKILL.md`, minus YAML frontmatter) becomes `~/.claude/CLAUDE.md`. If the user already has `~/.claude/CLAUDE.md` with content, show diff and ask before overwriting. Extract any local paths/repo names/secrets references the user has into `~/.claude/LOCAL.md` (auto-injected by `local.py` hook).

5. **Merge settings**. Read `settings-recommended.json` and merge into `~/.claude/settings.json`:
   - **Hooks block** (UserPromptSubmit, Stop, PreCompact, SessionEnd) — replace existing matching events with the recommended wiring (paths use `~/.claude/hooks/*.py`).
   - **Permissions, sandbox, env** — show diff, ask user which restrictions to apply.
   - NEVER overwrite `~/.claude/settings.local.json`.

6. **Report**: print a summary — X skills installed, Y agents, Z hooks, settings merged. `/commit`, `/ship`, `/refine`, etc. are now invocable bare.

## Rules

- NEVER delete files in `~/.claude/` that aren't in source (org overlays, user customizations live there).
- NEVER touch `~/.claude/settings.local.json`, `~/.claude/LOCAL.md`, `~/.claude/CLAUDE.local.md`.
- ALWAYS backup before overwriting.
- Pre-commit reformats / hook scripts that already exist: replace with current versions.
- Skills with name conflicts: replace.
- After install, suggest the user invoke `/recall-memories` once to verify the recall flow works against their existing diary/memory.

## Update flow

Re-run `/kronael-tools:install` after `claude /plugin update` pulls a new version. Same steps; the backup directory grows but stays useful for rollback.
