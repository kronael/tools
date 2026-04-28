---
name: pr-draft
description: Draft a short, clear PR description. Trigger on /pr-draft, "draft a PR", "write PR description", "PR description". USE to write a PR description from staged changes. NOT for the commit message itself (use commit).
user-invocable: true
---

# PR Description

Run directly in main context (no subagent).

## Workflow

1. Try `main` then `origin/main` as base; if neither resolves, ask the user. Run `git log <base>..HEAD --oneline` + `git diff <base>..HEAD --stat`
2. Draft title and body (see format below)
3. Show draft, ask if they want to tweak anything
4. STOP — NEVER run `gh pr create` or open the PR

## Format

**Title**: `[type] Short imperative sentence` (max 72 chars)
Types: `fix` `feat` `refactor` `docs` `chore`

**Body**: short prose lines, 2-4 lines total. Lead with the main point.
No bullets, no "This PR...", no test plans or checklists.

Example:
```
Extends dockbox with full headless browser support.
Playwright installs as root with --with-deps, replacing 15 manually-listed Chrome libs.
agent-browser CLI, playwright chromium, and puppeteer chrome are baked into the image.

Also adds skills for browser automation, PR drafting,
and a py rule against empty __init__.py files.
```
