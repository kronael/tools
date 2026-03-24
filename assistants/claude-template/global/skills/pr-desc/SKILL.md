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
3. Show draft, ask to confirm or tweak
4. `gh pr create --title "..." --body "..."` — only if confirmed
5. Print the PR URL — if `gh` unavailable, print text for copy-paste

## Format

**Title**: `[type] Short imperative sentence` (max 72 chars)
Types: `fix` `feat` `refactor` `docs` `chore`

**Body**: plain prose, 2-4 sentences max
- What changed and why
- Any non-obvious approach decision
- Nothing else

## Rules

- NEVER bullet-list changed files
- NEVER add test plans, checklists, or boilerplate sections
- NEVER start with "This PR..."
- If `gh` is not available, print the text for copy-paste
