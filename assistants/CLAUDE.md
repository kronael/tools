# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Overview

Meta-repository for Claude Code configuration:
- **claude-template/**: Skills, agents, hooks for Claude Code
- **usage-patterns/**: 12 usage patterns extracted from 57 production projects

## Installation

```bash
cd claude-template
# Say "install"
```

Claude compares with existing ~/.claude/, shows diffs, asks before overwriting.

## Components

**Agents** (6): @distill, @improve, @learn, @readme, @refine, @visual

**Skills** (32): agent-browser, cli, commit, create-eval, data, diary, docs-audit, go, improve, learn, merge-trivial, ops, pr-draft, py, readme, recall-memories, refine, release, rs, service, sh, ship, specs, sql, sub, testing, trader, ts, tsx, tweet, visual, wisdom

The improve/learn/readme/visual skills are user-invocable wrappers that
launch their corresponding agents (`/improve` → @improve, etc.).

**Hooks** (5): nudge (keyword->agent routing), local (LOCAL.md injection on first prompt + compact), reclaude (RECLAUDE.md injection on first prompt + compact), learn (flow reports on compact/end), stop (commit + diary nudge on Stop)

## Architecture

- @refine delegates to @improve + @readme for finalization
- Nudge hook uses fuzzy matching (edit distance) to route prompts to agents
- Stop hook runs a pure script — blocks on uncommitted changes and on
  missing/stale diary entries (no LLM call)
- Slash commands like /improve, /refine, /readme are skill-defined
  (user-invocable: true) — they dispatch to their @-named agents
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
- Local/private content belongs in ~/.claude/LOCAL.md (auto-injected by local.py hook)
- global/CLAUDE.md references LOCAL.md for sync paths — NEVER hardcode them
- The /srv paths with ${PREFIX:-} variable substitution are OK (generic pattern)
