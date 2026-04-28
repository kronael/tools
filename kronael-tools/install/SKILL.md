---
name: install
description: Install (or update) the Kronael toolkit into ~/.claude/. Trigger when the user says "install kronael tools", "install the toolkit", "install" (in this repo), or runs /kronael-tools:install. Copies skills, agents, and hook scripts; merges hook wiring and recommended settings into ~/.claude/settings.json; installs the wisdom skill body into ~/.claude/CLAUDE.md (always-loaded). Run once per machine, then again on plugin updates.
---

# Install Kronael toolkit

Goal: deploy the bundle into `~/.claude/` so skills, agents, and hooks live in the user's persistent config and work bare (no `kronael-tools:` prefix).

This is the single source of truth for the install procedure. `README.md`, `CLAUDE.md`, and `AGENTS.md` all defer to this file.

## Source location

- **Plugin path**: `${CLAUDE_PLUGIN_ROOT}` (the cached plugin repo).
- **Manual path**: the current working directory (user opened Claude Code at the repo root and said "install").

Verify these dirs/files exist at the source root before proceeding:
- `skills/` — bundle of skills (language, workflow, domain)
- `agents/` — bundle of agents (@improve, @readme, @refine, …)
- `hooks/` — bundle of hook scripts (nudge.py, local.py, reclaude.py, learn.py, stop.py) and `hooks/lib/`
- `settings-recommended.json` — recommended permissions, sandbox, env, hook wiring
- `RECLAUDE.md` — re-injection template for the `reclaude` hook

If they're missing, you're in the wrong directory — stop and ask.

## Steps

1. **Backup**. Before overwriting anything, copy current `~/.claude/{skills,agents,hooks,CLAUDE.md,settings.json,RECLAUDE.md}` to `~/.claude/backup/<timestamp>/`.

2. **Copy assets** (replace strategy):
   - `skills/*` → `~/.claude/skills/` **but skip `skills/global/`** — its body is the wisdom file, deployed in step 3 below; copying it as a skill would duplicate the always-loaded content.
   - `agents/*` → `~/.claude/agents/`
   - `hooks/*.py`, `hooks/lib/` → `~/.claude/hooks/`
   - `RECLAUDE.md` → `~/.claude/RECLAUDE.md`
   - Preserve user-added files not in source — never delete.

3. **Install wisdom**. The `global` skill body (file: `skills/global/SKILL.md`, minus YAML frontmatter) becomes `~/.claude/CLAUDE.md` — the always-loaded wisdom file. Single destination: do NOT also write to `~/.claude/skills/global/`. If the user already has `~/.claude/CLAUDE.md` with content, show diff and ask before overwriting. Extract any local paths/repo names/secrets references the user has into `~/.claude/LOCAL.md` (auto-injected by `local.py` hook).

4. **Merge settings**. Read `settings-recommended.json` and merge into `~/.claude/settings.json`:
   - **Hooks block** (UserPromptSubmit, Stop, PreCompact, SessionEnd) — replace existing matching events with the recommended wiring (paths use `~/.claude/hooks/*.py`).
   - **Permissions, sandbox, env** — show diff, ask user which restrictions to apply.
   - NEVER overwrite `~/.claude/settings.local.json`.

5. **External tools** (ask first — not everyone needs all of them):
   - `uv tool install git+https://github.com/kronael/ship` — planner-worker-judge CLI used by `/ship`.
   - `bun install -g agent-browser` — headless browser automation used by the `agent-browser` skill.
   - Skip if already installed and recent.

6. **Report**: print a summary — X skills, Y agents, Z hooks, RECLAUDE.md, settings merged, W external tools. `/commit`, `/ship`, `/refine`, etc. are invocable bare. Suggest the user run `/recall-memories` once to verify the recall flow works against their existing diary/memory.

## Rules

- NEVER delete files in `~/.claude/` that aren't in source (org overlays, user customizations live there).
- NEVER touch `~/.claude/settings.local.json`, `~/.claude/LOCAL.md`, `~/.claude/CLAUDE.local.md`.
- ALWAYS backup before overwriting.
- Skills/hooks with name conflicts: replace with current versions.
- NEVER sync `skipDangerousModePermissionPrompt` from user back into the template.

## Update flow

Re-run `/kronael-tools:install` (or "say install" in this repo) after `claude /plugin update` pulls a new version. Same steps; the backup directory grows but stays useful for rollback.
