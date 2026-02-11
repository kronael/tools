# Architecture

## Overview

Claude Code configuration: 5 agents, 9 commands, 16 auto-activating skills.
Install by opening Claude Code here and saying "install".

## Components

### Global (installed to ~/.claude/)

**CLAUDE.md**: Universal development principles

**agents/** (5): Specialized task agents
- Quality: improve, visual, learn
- Utilities: readme, distill

**commands/** (9): Slash commands
- /build, /distill, /improve, /learn, /readme, /refine, /ship, /tweet, /visual

**skills/** (16): Auto-activating skills
- Languages: go, python, rust, sql, typescript
- Services: cli, data, ops, service, trader
- Workflow: build, commit, refine, ship, tweet, wisdom

## Installation Flow

```
From this directory, say "install"

Process:
  1. Compare global/* with ~/.claude/
  2. New files: install directly
  3. Modified: ask user (overwrite/skip/diff)
  4. Backup to ~/.claude/backup/
  5. Report summary
```

## Runtime Flow

```
1. Claude Code starts in a project
2. Loads ~/.claude/CLAUDE.md (global)
3. Loads ./CLAUDE.md (project)
4. Skills auto-activate based on:
   - File extensions (.rs -> rust)
   - Config files (Cargo.toml -> rust)
5. Agents invoked explicitly or by delegation
```

## Agent Hierarchy

See [WORKFLOW.md](WORKFLOW.md) for complete hierarchy and usage guide.

```
/ship (outer loop)
  └─> /build (inner loop) per component
        └─> /improve, /readme, /visual (per stage)

/refine
  └─> /improve, /readme

/improve, /readme, /learn, /visual (leaf commands)
```

## Ship/Build Split

**ship skill** (outer loop):
- Reads specs from directory
- Topological sort for component dependencies
- Generates build plan per component
- Delegates to /build
- Critique loop: spec compliance review, fix gaps if >10% (max 2 rounds)
- State persists to PROGRESS.md (root)

**build skill** (inner loop):
- Reads plan from .claude/plans/
- Spawns parallel workers per stage
- Judge loop: polls workers, retries (max 3), error isolation
- Optional refinement round (max 1)
- Single commit at end
- State persists to .ship/build-state-{plan}.md

## Design Principles

- **Auto-activation**: Skills match on file context
- **Lazy loading**: Skill content loaded when activated
- **Progressive refinement**: /learn improves skills from usage
- **Safe updates**: /install compares, asks, backs up
- **State separation**: Ship state in root (PROGRESS.md), build state in .ship/
- **Clean delegation**: /ship → /build → leaf commands (improve/readme/visual)
