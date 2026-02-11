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

## claude-template/

**Agents** (5):
- **distill**: Extract key points from long content
- **improve**: DO-CRITICIZE-EVALUATE-IMPROVE loop
- **learn**: Extract patterns from history into skills
- **readme**: Sync README/ARCHITECTURE with code
- **visual**: Render-inspect-adjust for SVG/UI

**Skills** (15):
- Languages: go, python, rust, sql, typescript
- Services: cli, data, ops, service, trader
- Workflow: build, commit, refine, ship, wisdom

**Commands** (7): /build, /improve, /learn, /readme, /refine, /ship, /visual

## usage-patterns/

Analysis of 57 production projects (1.3MB logs). Top patterns:
- Iterative debugging: short commands ("fix it", "continue", "commit")
- Criticism-driven: request harsh criticism before PRs
- Integration tests: skip mocks, test real data flows
- Config-first: TOML config before implementation

## Working on This Repo

- ALWAYS keep files under 200 lines
- ALWAYS use ALWAYS/NEVER/SHOULD statements
- Focus on non-obvious patterns LLMs fail to grasp
