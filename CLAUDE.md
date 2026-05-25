# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Repository

Three things live here:
1. CLI tools (`dockbox/`, `rig/`, `tw-fetch/`, `tg-fetch/`, `dc-fetch/`, `clp/`) — each with its own Makefile.
2. Claude Code plugin (`.claude-plugin/`, `kronael/`) — installer skill that deploys the bundle to `~/.claude/`.
3. Bundle (`skills/`, `agents/`, `hooks/`, `settings-recommended.json`, `RECLAUDE.md`) — what `/kronael:install` copies. Same content also installs via the manual "say install" path.

## CLI tools

### Ratpoison Design Philosophy

Optimized for **MAX INFLOW of information**: keyboard-driven, stays in terminal, single-purpose, scriptable, no visual cruft. Named after the keyboard-only window manager.

### rig — ripgit

Single busybox-style bash script (`rig/rig`). Symlinks detect invocation name and dispatch to subcommands.

```bash
rig co [pattern]   # Checkout origin/branch, detached (rco)
rig p [branch]     # Push HEAD to origin/branch (rip)
rig r [pattern]    # Rebase -i on origin/branch (rir)
rig m [pattern]    # Merge origin/branch (rim)
rig install        # Create symlinks in script's directory
```

**Shared flags**: `-z` offline (no fetch), `-n` dry-run, `?` force fzf.

### dockbox — Dockerized Claude Code sandbox

Bash script (`dockbox/dockbox`) that runs Claude Code in an isolated Docker container. Multi-directory mounts, per-project `.dockboxrc`, all permissions bypassed (container is the sandbox). Ctrl-Z is ignored (would suspend dockbox itself, not the inner container).

Makefile: `image` (build), `install` (build+install), `clean`.

#### Ephemeral overmounts

Build-artifact dirs under workdir (`node_modules`, `.next`, `dist`, `build`, `.turbo`, `.cache`) are overmounted so the container always sees fresh empty dirs. Unified ownership flow regardless of backend: container starts as root (`--user 0:0`), `dockbox-init` chowns every path in `$DOCKBOX_EPH_PATHS` to `claude:claude`, then `gosu` drops to `claude` before exec'ing the user command. Backend just picks the mount type:
- **tmpfs** (default): kernel `--tmpfs`, RAM-backed.
- **volume** (`-T`): anonymous Docker volume, disk-backed.

**Both backends leave ZERO footprint after the container exits.** `docker run --rm` (always used) removes anonymous volumes; tmpfs dies with the mount namespace. NEVER add cleanup logic, EXIT traps, "remember to remove" comments, or worry-prose about leaks — there is nothing to leak.

## Claude Code toolkit

Two install paths share the same source:

- **Plugin**: `/plugin marketplace add kronael/tools` → `/plugin install kronael@kronael` → `/kronael:install` (or just say "install kronael").
- **Manual**: open Claude Code at the repo root and say **"install"**.

Both paths follow [`kronael/install/SKILL.md`](kronael/install/SKILL.md) — the single source of truth for the install procedure (backup, copy assets, install wisdom, merge settings, external tools). When the user says "install" in this repo, follow that skill.

### Source rules

When editing bundle files:
- NEVER include local paths, org-specific refs, or secrets in source (they go in `~/.claude/LOCAL.md`, auto-injected by `local.py`).
- The `global` skill body becomes `~/.claude/CLAUDE.md` on install — the always-loaded wisdom file.
- `RECLAUDE.md` is the re-injection template for the `reclaude` hook (PreCompact + manual continue/recap triggers).
- ALWAYS verify the matching reinject path when a skill changes:
  - **Skill rule changed?** Update its dedicated reinject if there is one — `hooks/nudge.py` `COMMIT_RULES`/`DOCS_RULES` for the commit/docs skills, `hooks/stop.py` nudge text for stop-time rules.
  - **Cross-cutting rule with no dedicated reinject?** Update `RECLAUDE.md` (filesystem, build, scope, writing — see its topic list).
  - **Commit rules** specifically live in three places that must stay in sync: `skills/commit/SKILL.md` (full reference), `hooks/nudge.py` `COMMIT_RULES` (fires on prompts with "commit"), `hooks/stop.py` (fires on uncommitted state). RECLAUDE.md does NOT carry them — would be redundant noise.

## Coding philosophy

**"Debugging is twice as hard as writing the code."** — Kernighan

- Readability > Performance > Cleverness
- Linear flow, minimal branching, one way to do things
- Helper functions at top, main logic at bottom
- Section comments: `# Parse flags`, `# Execute`
- POSIX-compatible bash, `[[ ]]` for conditions
- ALWAYS keep files under 200 lines

## Development

**Adding tools**: create `toolname/` with executable, Makefile, README. Follow ratpoison + boring-code principles. Update root README.

**Working on the toolkit**: ALWAYS use ALWAYS/NEVER statements. Focus on non-obvious patterns LLMs fail to grasp. Test by re-installing and using in a real project.
