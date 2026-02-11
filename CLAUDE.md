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

**Skills** (14):
- Languages: rust, python, typescript, go, sql
- Services: trader, data, service, cli
- Ops: ops
- Workflow: commit, refine, ship, wisdom

**Commands** (5): /improve, /learn, /readme, /refine, /visual

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
