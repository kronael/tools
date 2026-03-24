---
name: pr-draft
description: Draft a short, clear PR description. Trigger on /pr-draft, "draft a PR", "write PR description", "PR description".
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

**Body**: short lines, easy to read, not a single blob of text.
Lead with the main point (what this PR is about).
Then describe what was done in prose — no bullets.
2-4 lines total.

Example:
```
Extends dockbox with full headless browser support.
Playwright installs as root with --with-deps, replacing 15 manually-listed Chrome libs.
agent-browser CLI, playwright chromium, and puppeteer chrome are baked into the image.

Also adds skills for browser automation, PR drafting,
and a py rule against empty __init__.py files.
```

## Rules

- NEVER create the PR — output only, user runs `gh pr create` themselves
- NEVER bullet-list changed files
- NEVER add test plans, checklists, or boilerplate sections
- NEVER start with "This PR..."
