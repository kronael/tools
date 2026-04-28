# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Repository

Three things live here:
1. CLI tools (`dockbox/`, `rig/`, `tw-fetch/`) — each with its own Makefile.
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

Bash script (`dockbox/dockbox`) that runs Claude Code in an isolated Docker container. Multi-directory mounts, per-project `.dockboxrc`, all permissions bypassed (container is the sandbox). Ctrl-Z suspends container + returns to host shell; `fg` resumes.

Makefile: `image` (build), `install` (build+install), `clean`.

## Claude Code toolkit

Two install paths share the same source:

- **Plugin**: `/plugin marketplace add kronael/tools` → `/plugin install kronael@kronael` → `/kronael:install` (or just say "install kronael").
- **Manual**: open Claude Code at the repo root and say **"install"**.

Both paths follow [`kronael/install/SKILL.md`](kronael/install/SKILL.md) — the single source of truth for the install procedure (backup, copy assets, install wisdom, merge settings, external tools). When the user says "install" in this repo, follow that skill.

### Source rules

When editing bundle files:
- NEVER include local paths, org-specific refs, or secrets in source (they go in `~/.claude/LOCAL.md`, auto-injected by `local.py`).
- The `global` skill body becomes `~/.claude/CLAUDE.md` on install — the always-loaded wisdom file.
- `RECLAUDE.md` is the re-injection template for the `reclaude` hook.

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
