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
2. Draft title and body: title carries the business value; body is a reading
   guide for the reviewer alone — where the logic lives, what to scrutinize,
   what's risky — NOT a commit log, so skip renames, churn, and anything the
   reviewer doesn't need to judge the change. NEVER sell a change to a
   wire-visible contract (event name, API field, route) as neutral — verify
   it against what's documented or already emitted, since absence from
   `origin/main` isn't proof it's free to change — and flag it for the
   reviewer instead. ALWAYS flag verified-but-unfixed issues as "known,
   deferred" — never drop them to look clean. Then cut to essence (see
   format below).
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

**Body**: short prose lead; a bulleted reading guide ONLY when it aids
navigation, never to pad or restate the commit log. No "This PR...", no test
plans or checklists. Prose follows the `writing` skill's copy rules.

ALWAYS draft then cut — the first version is a draft, NEVER the deliverable.
Strip every word that doesn't change meaning: hedges, context the diff
already shows, adjectives, filler kept only because it "sounds complete."
Only the trimmed result is real — shortest version that still gives the
reviewer what they need; NEVER pad to look thorough.

ALWAYS output the draft (title + body) in one fenced code block so it is easy
to copy.

Example:
```
[feat] Send unstake quote and settlement events to Mixpanel

Instruments the instant-unstake flow so drop-off and settlement outcomes show up in Mixpanel instead of only server logs.

- `trackUnstakeEvent()` centralizes the event shape — every call site routes through it, so a bad field breaks all events at once.
- Contract change to confirm: renames `instant_unstake_amount_adjusted` to `instant_unstake_adjustment_prompted` — confirm nothing downstream still keys on the old name.

Known, deferred: the native-auction path can't attach a cost basis yet (`costsKnown: false`), logged as a follow-up.
```
