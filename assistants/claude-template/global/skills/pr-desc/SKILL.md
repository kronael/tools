---
name: pr-desc
description: Create a PR with a short, clear description. Trigger on /pr-desc, "open a PR", "create PR", "write PR description".
user-invocable: true
---

# PR Description

Run directly in main context (no subagent).

## Workflow

1. `git log main..HEAD --oneline` + `git diff main..HEAD --stat` to understand scope
2. Draft title and body (see format below)
3. Show draft, ask if they want to tweak anything
4. STOP — NEVER run `gh pr create` or open the PR

## Format

**Title**: `[type] Short imperative sentence` (max 72 chars)
Types: `fix` `feat` `refactor` `docs` `chore`

**Body**: plain prose, 2-4 sentences max
- What changed and why
- Any non-obvious approach decision
- Nothing else

## Rules

- NEVER create the PR — output only, user runs `gh pr create` themselves
- NEVER bullet-list changed files
- NEVER add test plans, checklists, or boilerplate sections
- NEVER start with "This PR..."
