---
name: create-eval
description: Generate project-specific eval skill. Use when asked to create eval criteria, set up evaluation, or "create eval" for a project.
user-invocable: true
---

# Create Eval

Generate a project-specific `.claude/skills/eval/SKILL.md` by reading the project.

## Process

1. ALWAYS read first: CLAUDE.md, README, specs/, ARCHITECTURE.md, docs/
2. Identify what this project does — its core promises
3. Ask user: "What does correct look like for this project?"
4. Ask user: "What are the known failure modes?"
5. Generate `.claude/skills/eval/SKILL.md` with:
   - Project-specific verification steps (what to check)
   - Project-specific pass/fail criteria
   - Known gotchas and past failures
   - Storage path: `eval/<topic>/YYYYMMDD.md`

## Generated Eval Skill Structure

```
name: eval
description: Evaluate agent responses for <project>.

# Eval: <project>

## What to Verify
- <project-specific checks derived from docs>

## Pass/Fail Criteria
- <what PASS means for this project>
- <what FAIL means for this project>

## Known Gotchas
- <from user answers and docs>

## Rules
- ALWAYS read CLAUDE.md before evaluating
- ALWAYS verify file changes exist
- ALWAYS run tests if available
- NEVER score without evidence
```

## Rules

- ALWAYS read project docs before generating — NEVER guess
- ALWAYS ask user at least 2 questions before generating
- NEVER copy generic criteria — every line must be project-specific
- Output goes to `.claude/skills/eval/SKILL.md` in the project
