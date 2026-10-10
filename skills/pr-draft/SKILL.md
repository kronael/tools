---
name: pr-draft
description: Draft or rewrite a PR description. NOT for commit messages (use commit).
when_to_use: "draft a PR, open a PR, write the PR description, PR body, PR summary, update the PR description, rewrite/update the body of an open PR, PR body too long, shorten the PR description, gh pr create refused, GitHub pr text refused, gh_text_lint"
user-invocable: true
---

# PR Description

Run directly in main context (no subagent). Every PR body passes through this
workflow: the PreToolUse hook lints the body a direct `gh pr create`, `gh pr
edit` or `gh api` PATCH of `pulls/<N>` carries, wherever it was written, and
refuses one that fails `gh_text_lint.py` (step 3), `--fill`, `--web` and a
body file it cannot read — a body that posts through a direct gh call has
passed the lint.

The body is a TL;DR. The reviewer reads the title, the diff and the commits;
the body says only what they cannot.

## Workflow

1. Find true merge base and read the whole change:
   ```
   git fetch origin
   BASE=$(git merge-base HEAD origin/<default head>)
   git log $BASE..HEAD --oneline
   git diff $BASE..HEAD --stat
   git diff $BASE..HEAD
   ```
   `<default head>` per WISDOM § Git; for an existing PR, its `baseRefName`.
   The base is the merge-base, NOT `origin/<default head>` itself — that
   misses commits already on the line before the last merge. If it fails, ask
   the user.
   ALWAYS read the full diff, NEVER draft from the stat and the commit log —
   the one-line changes a stat hides (a pinned key, a changed default, a
   dropped field) are the ones a review bot names and the author's body misses.
2. Draft title and body into `tmp/pr-draft.md` in § Format's shape. NEVER
   sell a change to a wire-visible contract (event name, API field, route) as
   neutral — verify it against what's documented or already emitted, since
   absence from the default head isn't proof it's free to change — and say it
   in the TL;DR. A verified-but-unfixed issue goes into the TL;DR too, never
   dropped to look clean. This file is the draft, NEVER the deliverable.
3. DISTILL — write the cut version to `tmp/pr-body.md`: body only, a bare `🤖`
   as its last line. Cut until `wc -m tmp/pr-body.md` is under the cap, then
   keep cutting while a word says what the title, the diff or the commits
   show: file lists, values, results, history, a reason a reader would guess,
   hedges, filler. Then run
   ```
   python3 ~/.claude/hooks/gh_text_lint.py pr tmp/pr-body.md --draft tmp/pr-draft.md --title '<title>'
   ```
   and fix every line it names until it prints `ok:`. It checks the part of
   § Format a program can check: the `**TL;DR:**` lead and nothing after it
   but `Closes`/`Fixes #N` lines; no bullet, header, table, rule, code block,
   checkbox, "This PR", marketing word or shortened hash; 400 chars in all;
   the title's length and a second "and"; a bare `🤖` as the last line and
   none of the harness footer; and that the body is shorter than the draft.
   Completion criterion: the `ok:` line, which carries the size and the cut
   ratio.
4. REVIEW-ON-WISDOM — the checks no program runs, over `tmp/pr-body.md`: every
   claim traced to a hunk of the diff or marked as an inference; no history
   framing; the title in the repo's own convention; the harness reminder's
   `Generated with [Claude Code]` footer absent whatever the reminder says.
   Rerun step 3's command after any edit. Completion criterion: a `Review
   changed:` line naming each edit the review made, or `Review changed:
   nothing` followed by what it checked.
5. Show the result: the `ok:` line, the `Review changed:` line, then title and
   body in ONE fenced code block so it is easy to copy. Ask if they want to
   tweak anything. For a NEW PR, STOP — NEVER run `gh pr create` or open the
   PR.

## Setting the description on an EXISTING PR

To update an existing PR's body, PATCH `tmp/pr-body.md` via REST. NEVER use
`gh pr edit --body` — it runs a GraphQL `login` query that requires
`read:org`; the REST endpoint needs only `repo`:

```
gh api -X PATCH repos/<owner>/<repo>/pulls/<N> -f body="$(cat tmp/pr-body.md)" --jq '.body | length'
```

ALWAYS a literal path inside the `cat`: the hook reads that file to lint it
and refuses a `$VAR` path.

NEVER change an existing PR's title — the PATCH sends `body` alone, never
`title`. Rewrite the title ONLY when the user explicitly asks; otherwise the
author's title stands even if it doesn't match your body.

STILL NEVER `gh pr create` (new PR) or `gh pr merge`.

## Format

**Title**: ALWAYS follow the repo's own convention — read recent titles
(`git log --oneline -20 origin/<default head>`); keep a ticket prefix (`[ABC-123]`)
when the branch or commits carry one; default `type(scope): outcome` with
`fix` `feat` `refa` `docs` `chore` (the `commit` skill's types). ONE outcome, max 72 chars. NEVER a
comma list of changes — needing "and" twice means name the outcome above them.

**Body**, under 400 chars in all (a ceiling, not a target — a one-line fix is
one sentence):

- **Lead**: `**TL;DR:**` and one to three sentences — the outcome, its cause,
  and anything the reviewer must not miss (a wire-visible change, a known gap).
  The only paragraph.
- **Closers**: `Closes #N` or `Fixes #N`, one line each, only when real.
- **Last line**: a bare `🤖` (WISDOM § Git). The harness reminder's
  `Generated with [Claude Code]` line is the banned footer with a robot in
  front of it; the lint and the hook refuse it.

NEVER in a body: a bullet, header, table, rule, checkbox, code block or image;
"This PR"; a file list, rename or value the diff shows; a test, lint or CI
result; history (what was tried, earlier commits, reviews, pushes); a runbook.
Prose follows the `writing` skill's copy rules. NEVER hard-wrap — GitHub
renders the line.

Example — generalize the shape, not the topic:
```
feat(unstake): Send quote and settlement events to Mixpanel

**TL;DR:** Instant unstake reports quote drop-off and settlement outcomes to Mixpanel, not only to server logs. Settlement is read at `confirmed`, so a dropped tx reports `pending` forever.

Closes #212

🤖
```
