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
2. Draft title and body covering ALL changes since that base, then cut fluff to
   essence — only the trimmed version is real (see format below)
3. Show draft, ask if they want to tweak anything
4. Show draft. For a NEW PR, STOP — NEVER run `gh pr create` or open the PR.

## Setting the description on an EXISTING PR

To update an existing PR's body, write the body to `tmp/body.md` and PATCH via
REST. NEVER use `gh pr edit --body` — it runs a GraphQL `login` query that
requires `read:org`; the REST endpoint needs only `repo`:

```
gh api -X PATCH repos/<owner>/<repo>/pulls/<N> -f body="$(cat tmp/body.md)" --jq '.body | length'
```

NEVER change an existing PR's title — the PATCH sends `body` alone, never
`title`. Rewrite the title ONLY when the user explicitly asks; otherwise the
author's title stands even if it doesn't match your body.

STILL NEVER `gh pr create` (new PR) or `gh pr merge`.

## GitHub Markdown Uploads

NEVER hard-wrap Markdown uploaded to GitHub just for source width — ALWAYS keep tables, links, paths, commands, and list items in the shape that renders best.

## Format

**Title**: `[type] Short imperative sentence` (max 72 chars)
Types: `fix` `feat` `refactor` `docs` `chore`

**Body**: short prose, lead with the main point. No bullets, no "This PR...",
no test plans or checklists. Prose follows the `writing` skill's copy rules.

ALWAYS draft then cut — the first version is a draft, NEVER the deliverable.
Once written, strip every word that doesn't change meaning: hedges, context the
diff already shows, adjectives, any line kept only because it "sounds complete."
Only the trimmed result is final and real. Shortest version that still says it
wins — 2-3 lines beats 4; NEVER pad to look thorough.

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
