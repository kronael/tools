---
name: create-eval
description: Generate project-specific eval skill. Use when asked to create eval criteria, set up evaluation, or "create eval" for a project.
user-invocable: true
---

# Create Eval

Generate `.claude/skills/eval/SKILL.md` for the current project.

## Process

1. Read CLAUDE.md, README, specs/, ARCHITECTURE.md, docs/
2. Identify what this project does and what "correct" means
3. Ask user until you understand pass/fail criteria and known failure modes
4. Write `.claude/skills/eval/SKILL.md` — every line project-specific

## Rules

- ALWAYS read project docs before generating
- NEVER include generic criteria — derive everything from the project
- NEVER generate without asking the user first
