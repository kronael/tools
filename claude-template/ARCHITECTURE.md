# Architecture

## Overview

Claude Code configuration: 5 agents, 5 commands, 15 auto-activating skills.
Install by opening Claude Code here and saying "install".

## Components

### Global (installed to ~/.claude/)

**CLAUDE.md**: Universal development principles

**agents/** (5): Specialized task agents
- Quality: improve, visual, learn
- Utilities: readme, distill

**commands/** (5): Slash commands
- /improve, /learn, /readme, /refine, /visual

**skills/** (15): Auto-activating skills
- Languages: rust, python, typescript, go, sql
- Services: trader, data, service, cli, infrastructure, builder
- Development: commit, refine, ship, wisdom

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

## Design Principles

- **Auto-activation**: Skills match on file context
- **Lazy loading**: Skill content loaded when activated
- **Progressive refinement**: /learn improves skills from usage
- **Safe updates**: /install compares, asks, backs up
