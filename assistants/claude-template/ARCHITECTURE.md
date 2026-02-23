# Architecture

## Overview

Claude Code configuration: 8 agents, 5 commands, 18 auto-activating skills.
Install by opening Claude Code here and saying "install".

## Components

### Global (installed to ~/.claude/)

**CLAUDE.md**: Universal development principles

**agents/** (8): Specialized task agents
- Quality: @improve, @visual, @learn
- Research: @deep-research, @research, @distill
- Utilities: @readme, @refine

**commands/** (5): Slash commands
- /improve, /learn, /readme, /refine, /visual

**skills/** (18): Auto-activating skills
- Languages: go, python, rust, sql, typescript
- Services: cli, data, ops, service, trader
- Infrastructure: infrastructure, testing
- Workflow: commit, refine, tweet, wisdom

## Installation Flow

```
From this directory, say "install"

Sync strategies:
  Replace:    agents/, commands/, skills/, hooks/ (fresh copy)
  Merge:      CLAUDE.md, settings.json (diff, ask)
  Never touch: settings.local.json, LOCAL.md
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
/refine
  └─> @improve, @readme

@deep-research, @distill, @improve, @learn, @readme, @refine, @research, @visual (leaf agents)
```

## Design Principles

- **Auto-activation**: Skills match on file context
- **Lazy loading**: Skill content loaded when activated
- **Progressive refinement**: @learn improves skills from usage
- **Safe updates**: /install compares, asks, backs up
- **State separation**: Ship state in root (PROGRESS.md), build state in .ship/
- **Clean delegation**: /ship → /build → leaf agents (@improve/@readme/@visual)
