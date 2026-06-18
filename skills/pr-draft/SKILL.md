---
name: pr-draft
description: Draft a PR description. NOT for commit messages (use commit).
when_to_use: "draft a PR, open a PR"
user-invocable: true
---

# PR Description

Run directly in main context (no subagent).

## Workflow

1. Find true merge base:
   ```
   BASE=$(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD main)
   git log $BASE..HEAD --oneline
   git diff $BASE..HEAD --stat
   ```
   The base is the merge-base with main, NOT `origin/main` itself — that misses commits
   already on the branch before the last merge. If both fail, ask the user.
2. Draft title and body covering ALL changes since that base (see format below)
3. Show draft, ask if they want to tweak anything
4. STOP — NEVER run `gh pr create` or open the PR

## Format

**Title**: `[type] Short imperative sentence` (max 72 chars)
Types: `fix` `feat` `refactor` `docs` `chore`

**Body**: short prose lines, 2-4 lines total. Lead with the main point.
No bullets, no "This PR...", no test plans or checklists.
Prose follows the `writing` skill's copy rules.

ALWAYS output the draft (title + body) in one fenced code block so it is easy
to copy.

Example:
```
[feat] Extend dockbox with full headless browser support

Playwright installs as root with --with-deps, replacing 15 manually-listed Chrome libs.
agent-browser CLI, playwright chromium, and puppeteer chrome are baked into the image.

Also adds skills for browser automation, PR drafting,
and a py rule against empty __init__.py files.
```
