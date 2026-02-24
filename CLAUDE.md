# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository

Two sections: CLI tools (`rig/`) and Claude Code configuration
(`assistants/`).

## Tools

Each tool lives in its own directory with an executable, Makefile
(`install`/`clean` targets), and README. Installs to `~/.local/bin/`.

### Ratpoison Design Philosophy

Optimized for **MAX INFLOW of information**: keyboard-driven, stays
in terminal, single-purpose, scriptable, no visual cruft. Named after
the keyboard-only window manager.

### rig - ripgit

Single busybox-style bash script (`rig/rig`). Symlinks detect
invocation name and dispatch to subcommands.

```bash
rig co [pattern]   # Checkout origin/branch, detached (rio)
rig p [branch]     # Push HEAD to origin/branch (rip)
rig r [pattern]    # Rebase -i on origin/branch (rir)
rig m [pattern]    # Merge origin/branch (rim)
rig install        # Create symlinks in script's directory
```

**Shared flags**: `-z` offline (no fetch), `-n` dry-run, `?` force fzf

**Implementation**: helpers at top, flags parsed, then main logic.
Clear sections: `# Parse flags`, `# Select branch`, `# Execute`.

### dockbox - Dockerized Claude Code sandbox

Bash script (`dockbox/dockbox`) that runs Claude Code in an isolated
Docker container. Multi-directory mounts, per-project `.dockboxrc`
config, all permissions bypassed (container is the sandbox).

Makefile targets: `image` (build), `install` (build+install), `clean`.

## Assistants

Claude Code configuration in `assistants/`.

- **claude-template/**: Skills, agents, commands, hooks — say
  "install" to deploy to `~/.claude/`
- **usage-patterns/**: 12 usage patterns extracted from 57 projects

### Components

**Skills** (16): auto-activate based on file context (bash, cli,
commit, data, go, ops, python, refine, rust, service, sql,
testing, trader, tweet, typescript, wisdom)

**Agents** (6): @distill, @improve, @learn, @readme,
@refine, @visual

**Commands** (5): /improve, /learn, /readme, /refine, /visual

**Hooks** (7): nudge (keyword->agent routing), local (rule
injection), redirect (toolchain mapping), learn (flow reports),
reclaude (session restore), stop (prompt classification),
context (context management)

### Sync Rules

When syncing `claude-template/global/` to `~/.claude/`:
- NEVER include local paths, org-specific refs, or secrets
- Local content belongs in `~/.claude/LOCAL.md`

## Coding Philosophy

**"Debugging is twice as hard as writing the code."** - Kernighan

- Readability > Performance > Cleverness
- Linear flow, minimal branching, one way to do things
- Helper functions at top, main logic at bottom
- Section comments: `# Parse flags`, `# Execute`
- POSIX-compatible bash, `[[ ]]` for conditions
- ALWAYS keep files under 200 lines

## Development

**Adding tools**: create `toolname/` with executable, Makefile,
README. Follow ratpoison + boring code principles. Update root
README.

**Working on assistants**: ALWAYS use ALWAYS/NEVER statements.
Focus on non-obvious patterns LLMs fail to grasp. Test by
installing then using in a real project.
