---
name: create-eval
description: Generate project-specific eval skill. NOT for running existing evals.
when_to_use: "create eval", create eval criteria, scaffold eval skill
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
- ALWAYS express assertions as programmatically checkable (grep counts, thresholds, exit codes) — NEVER "looks healthy" / "works well"
- ALWAYS sanity-check the generated eval against real log samples before declaring it done
