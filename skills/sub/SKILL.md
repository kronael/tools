---
name: sub
description: /sub — launch background subagent, auto-select model tier by complexity. NOT for tasks the main thread needs results from immediately.
when_to_use: do this in the background, run this separately, spawn a sub, launch sub, background agent, sub for this, do X while I do Y, background task, async work, run in background, implement this, write these tests, fix this bug, check this file, grep and report
user-invocable: true
---

Classify the task, then launch a background agent with the right tier.
Report which tier was chosen and why. Continue immediately without waiting.

## Tier decision

ALWAYS pick exactly one tier before launching. Be explicit about the choice.

**haiku** — single-file mechanical work, no judgment needed:
- Find-and-replace, rename, typo fix, add a constant, swap a class name
- Grep + summarize (read-only, one file/area)
- Boilerplate: test stub, repetitive struct, constant list

**sonnet** — investigation, hunting, analysis:
- Find bugs, find simplification opportunities, survey the codebase
- Pre-review: flag issues before implementing
- Exploration with no code changes; read-only analysis across files

**opus** — implementation, execution:
- Multi-file feature implementation, applying fixes, writing code
- Architecture decisions + executing them, cross-package refactors
- Security review + implementing the hardening

## Launch rules

NEVER pass a bare task — ALWAYS include: exact file paths, what to change, what to return.
ALWAYS write the prompt as if the subagent has no memory of this session.
ALWAYS use `subagent_type: "haiku"` / `subagent_type: "sonnet"` / `subagent_type: "opus"` on the Agent tool.
NEVER use `model:` parameter alone — effort is set by the agent definition, not the model param.
