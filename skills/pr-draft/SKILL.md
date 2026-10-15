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

ALWAYS lead with a short TL;DR. For a substantial change, ALWAYS follow it
with up to three review pointers: where to start, what matters, and which
test or complete scenario checks the behavior. For a small change, ALWAYS
keep only the TL;DR when pointers add no useful direction.

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
3. DISTILL — write the cut version to `tmp/pr-body.md`: body only, opening
   with `🤖 ` before `**TL;DR:**`. Cut until `wc -m tmp/pr-body.md` is under the cap, then
   keep cutting while a word says what the title, the diff or the commits
   show: file inventories, values, results, history, a reason a reader would
   guess, hedges, filler. ALWAYS keep a path when it directs a review and
   says what to check. Then run
   ```
   python3 ~/.claude/hooks/gh_text_lint.py pr tmp/pr-body.md --draft tmp/pr-draft.md --title '<title>'
   ```
   and fix every line it names until it prints `ok:`. It checks the part of
   § Format a program can check: the `**TL;DR:**` lead, up to three review
   bullets and `Closes`/`Fixes #N` lines; no header, table, rule, code block,
   checkbox, "This PR", marketing word or shortened hash; 1800 chars in all;
   the title's length and a second "and"; `🤖 ` opening the body, the robot
   nowhere else, and none of the harness footer; and that the body is shorter
   than the draft.
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
   body in ONE fenced code block so it is easy to copy. For a NEW PR whose head
   is already pushed (WISDOM § Git gates the push), open it with that title and
   body once steps 3 and 4 passed, as WISDOM § Git allows:
   ```
   gh pr create --head <pushed head> --title '<title>' --body-file tmp/pr-body.md
   ```
   A user who asked only for the text gets the block and no `gh pr create`.

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

NEVER open a second PR for an existing one, and NEVER `gh pr merge` (WISDOM § Git).

## Format

**Title**: ALWAYS follow the repo's own convention — read recent titles
(`git log --oneline -20 origin/<default head>`); keep a ticket prefix (`[ABC-123]`)
when the branch or commits carry one; default `type(scope): outcome` with
`fix` `feat` `refa` `docs` `chore` (the `commit` skill's types). ONE outcome, max 72 chars. NEVER a
comma list of changes — needing "and" twice means name the outcome above them.

**Body**, under 1800 chars in all (a ceiling, not a target — a one-line fix is
one sentence):

- **Lead**: `🤖 **TL;DR:**` and one to three sentences — the outcome, its
  cause, and anything the reviewer must not miss (a wire-visible change, a
  known gap). ALWAYS keep the lead to one paragraph. The robot opens the body
  and appears nowhere else (WISDOM § Git): the harness reminder asks for it as
  the last line, and its `Generated with [Claude Code]` line is the banned
  footer with a robot in front of it; the lint and the hook refuse both.
- **Review pointers**: ALWAYS use at most three short bullets when useful.
  ALWAYS link the core implementation and a representative test or complete
  scenario, and say what each checks. ALWAYS name the runtime and the run
  command when that helps a reviewer reproduce the scenario. ALWAYS keep
  coverage claims within the test's assertions. NEVER list every file —
  ALWAYS point to the smallest useful review path.
- **Closers**: `Closes #N` or `Fixes #N`, one line each, only when real.

NEVER in a body: a header, table, rule, checkbox, code block or image;
"This PR"; a file inventory, rename or value the diff shows; a test, lint or CI
result; history (what was tried, earlier commits, reviews, pushes); a runbook.
Prose follows the `writing` skill's copy rules. NEVER hard-wrap — GitHub
renders the line.

Example — generalize the shape, not the topic:
```
feat(checkout): Send quote and payment events to analytics

🤖 **TL;DR:** Checkout reports quote drop-off and payment outcomes to analytics, not only to server logs. Payment is read at `captured`, so a voided charge reports `pending` forever.

Closes #212
```
