---
name: create-eval
description: Generate project-specific eval skill. Use when asked to create eval criteria, set up evaluation, or "create eval" for a project. USE to scaffold a project-specific eval skill. NOT for running existing evals (use the project's eval skill directly).
user-invocable: true
---

# Create Eval

Generate `.claude/skills/eval/SKILL.md` for the current project.

The eval skill runs periodically to read logs, verify correctness,
and generate improvement specs when issues are found.

## Process

1. Read CLAUDE.md, README, specs/, ARCHITECTURE.md, docs/
2. Identify what this project does and what "correct" means
3. Ask user: what does "good" look like? What does "best" look like?
4. Ask user about known failure modes
   - Logs: check ops skill, /srv/log, /var/log, or ask
5. Write `.claude/skills/eval/SKILL.md` with:
   - Log locations and what to grep for
   - Health checks (pass/fail criteria from logs)
   - When to generate improvement specs (to specs/ or .ship/)

## Rules

- ALWAYS read project docs before generating
- NEVER include generic criteria — derive everything from the project
- NEVER generate without asking the user first
