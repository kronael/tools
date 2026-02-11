# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Overview

Meta-repository for Claude Code configuration:
- **claude-template/**: Skills, agents, commands, hooks for Claude Code
- **usage-patterns/**: 12 usage patterns extracted from 57 production projects

## Installation

```bash
cd claude-template
# Say "install"
```

Claude compares with existing ~/.claude/, shows diffs, asks before overwriting.

## Components

**Commands** (9): /build, /distill, /improve, /learn, /readme, /refine, /ship, /tweet, /visual

**Agents** (5): distill, improve, learn, readme, visual

**Skills** (16): build, cli, commit, data, go, ops, python, refine, rust, service, ship, sql, trader, tweet, typescript, wisdom

**Hooks** (5): nudge (keyword->agent routing), context (rule injection on continue), redirect (toolchain command mapping), learn (flow reports on compact/end), reclaude (session restore)

## Architecture

- /ship is the outer loop: specs -> components -> completion
- /build is the inner loop: plan -> parallel workers -> commit
- /refine delegates to /improve + /readme for finalization
- Nudge hook uses fuzzy matching (edit distance) to route prompts to agents
- See [WORKFLOW.md](claude-template/WORKFLOW.md) for agent hierarchy

## Working on This Repo

- ALWAYS keep files under 200 lines
- ALWAYS use ALWAYS/NEVER/SHOULD statements
- Focus on non-obvious patterns LLMs fail to grasp

## Sync Rules

When syncing claude-template/global/ to other assistants repos or ~/.claude/:
- NEVER include local paths (~/wk/..., /home/user/...)
- NEVER include org-specific repo names or private project references
- NEVER include secrets, API keys, or credential file paths
- Local/private content belongs in ~/.claude/LOCAL.md (auto-injected by context hook)
- generic/CLAUDE.md references LOCAL.md for sync paths — NEVER hardcode them
- The /srv paths with ${PREFIX:-} variable substitution are OK (generic pattern)
