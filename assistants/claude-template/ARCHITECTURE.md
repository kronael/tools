# Architecture

## Overview

Claude Code configuration: 6 agents, 5 commands, 28 auto-activating
skills, 5 hooks. Install by opening Claude Code here and saying
"install".

## Components

### Global (installed to ~/.claude/)

**CLAUDE.md**: Universal development principles

**agents/** (6): Specialized task agents
- Quality: @improve, @visual, @learn
- Research: @distill (built-in @deep-research also available)
- Utilities: @readme, @refine

**commands/** (5): Slash commands
- /improve, /learn, /readme, /refine, /visual

**skills/** (28): Auto-activating skills
- Languages: go, py, rs, sh, sql, ts, tsx
- Domain: cli, data, ops, service, trader, agent-browser, sub
- Infrastructure: testing
- Workflow: commit, create-eval, diary, docs-audit, merge-trivial,
  pr-draft, recall-memories, refine, release, ship, specs, tweet, wisdom

**hooks/** (5): Lifecycle hooks
- nudge (UserPromptSubmit: keyword → command/agent)
- local (UserPromptSubmit + PreCompact: LOCAL.md injection)
- reclaude (UserPromptSubmit + PreCompact: RECLAUDE.md injection)
- learn (PreCompact + SessionEnd: flow report)
- stop (Stop: commit + diary nudge)

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
   - File extensions (.rs -> rs)
   - Config files (Cargo.toml -> rs)
5. Agents invoked explicitly or by delegation
```

## Agent Hierarchy

See [WORKFLOW.md](WORKFLOW.md) for complete hierarchy and usage guide.

```
/refine
  └─> @improve, @readme

@distill, @improve, @learn, @readme, @refine, @visual (leaf agents)
```

## Design Principles

- **Auto-activation**: Skills match on file context
- **Lazy loading**: Skill content loaded when activated
- **Progressive refinement**: @learn improves skills from usage
- **Safe updates**: /install compares, asks, backs up
- **State separation**: Ship state in root (PROGRESS.md), build state in .ship/
- **Clean delegation**: /ship → /build → leaf agents (@improve/@readme/@visual)
