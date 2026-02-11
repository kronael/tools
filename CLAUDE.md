# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Overview

Meta-repository for Claude Code configuration:
- **claude-template/**: Skills, agents, commands for Claude Code
- **usage-patterns/**: 12 usage patterns extracted from 57 production projects

## Installation

```bash
cd claude-template
# Say "install"
```

Claude compares with existing ~/.claude/, shows diffs, asks before overwriting.

## Components

**Commands** (7): /build, /improve, /learn, /readme, /refine, /ship, /visual

**Agents** (5): distill, improve, learn, readme, visual

**Skills** (15): build, cli, commit, data, go, ops, python, refine, rust, service, ship, sql, trader, typescript, wisdom

## Working on This Repo

- ALWAYS keep files under 200 lines
- ALWAYS use ALWAYS/NEVER/SHOULD statements
- Focus on non-obvious patterns LLMs fail to grasp
