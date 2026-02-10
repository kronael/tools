# Architecture

## Overview

Claude Code configuration: 5 agents, 3 commands, 11 auto-activating skills.
Install by opening Claude Code here and saying "install".

## Components

### Global (installed to ~/.claude/)

**CLAUDE.md**: Universal development principles

**agents/** (5): Specialized task agents
- Quality: improve, refine, visual, learn
- Utilities: readme

**commands/** (3): Slash commands
- /refine, /learn, /visual

**skills/** (11): Auto-activating skills
- Languages: rust, python, typescript, sql
- Domain: trader, data, service
- Cross-cutting: testing, cli, infrastructure, builder

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
