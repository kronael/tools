---
name: docs-audit
description: Audit project documentation against actual codebase. Multi-phase parallel subagent pattern.
triggers:
  - audit docs
  - docs vs code
  - documentation critique
---

# Docs Audit

## Phases

```
A+B parallel (6 agents)  → A: fetch docs/blog/community, B: extract code truth from repos
C   sequential (1)       → cross-reference A vs B, initial critique
D   parallel (4)         → D1-D3: 4x deeper re-audit, D4: UX-only critique
E   sequential (1)       → merge, deduplicate, reclassify
```

Dependencies: A+B→C→D→E. Max 4 parallel agents.

## Execution

- ALWAYS use TaskCreate at start with one task per phase (A+B, C, D, E).
  Update status as phases complete. Main agent ONLY orchestrates and writes
  files from agent output — never does the research itself.
- ALWAYS delegate ALL research to subagents (Agent tool). Main context stays
  clean for orchestration. Subagents do the reading, fetching, analyzing.
- ALWAYS run subagents with `run_in_background: true` for parallel phases.
  Poll with TaskOutput. Write files from returned content in main context.
- Main agent's job: launch agents, wait, write files, track tasks, launch
  next phase. Nothing else.

## Non-obvious

- Initial pass catches ~30% of issues. Deep-dive (Phase D) is not optional.
- UX/organization critique is a SEPARATE agent and separate output from
  technical accuracy findings. Never mix them.
- B agents extract file:line evidence. Without this, findings are opinions.
- Include at least one CORRECT finding. Pure criticism reads as a hitpiece.
- Save raw research (sources/, code-vs-docs/) before synthesis. If synthesis
  agent fails, the expensive gather work is recoverable.
- Blog posts are a rich source of outdated claims — cross-check them in D.
- critique-master.md must be self-contained: a docs team should act on it
  without reading any other file.

## Output

All under `res/`. Key files: critique-master.md (all findings),
improvements.md (P1/P2/P3 fix plan), deep-dive/doc-ux-critique.md
(organization/UX, separate from bugs).
