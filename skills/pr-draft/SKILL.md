---
name: pr-draft
description: Draft or rewrite a PR description. NOT for commit messages (use commit).
when_to_use: "draft a PR, open a PR, write the PR description, PR body, update the PR description, PR body too long, PR lacks context, gh pr create refused, gh_text_lint"
user-invocable: true
---

# PR Description

Run directly in main context (no subagent). Every PR body passes through this
workflow: the PreToolUse hook lints the body a direct `gh pr create`, `gh pr
edit` or `gh api` PATCH of `pulls/<N>` carries, wherever it was written, and
refuses one that fails `gh_text_lint.py` (step 3), `--fill`, `--web` and a
body file it cannot read — a body that posts through a direct gh call has
passed the lint.

ALWAYS make the description understandable without the conversation: a brief
TL;DR, then only the context a reviewer needs to assess the change.

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
   in the body. ALWAYS disclose a verified-but-unfixed issue that affects the
   review. This file is the draft, NEVER the deliverable.
3. DISTILL — write the concise version to `tmp/pr-body.md`: body only, opening
   with `🤖 ` before `**TL;DR:**`. ALWAYS cut repetition and filler while
   preserving the reasoning required by § Format. NEVER cut necessary context
   to meet a reduction ratio; an already concise draft can stay unchanged. Run
   ```
   python3 ~/.claude/hooks/gh_text_lint.py pr tmp/pr-body.md --draft tmp/pr-draft.md --title '<title>'
   ```
   and fix every line it names until it prints `ok:`. It checks the part of
   § Format a program can check: the `**TL;DR:**` opening paragraph capped at
   400 chars; no table, rule, code block, checkbox, image, "This PR", marketing
   word or shortened hash; the title's length and a second "and";
   `🤖 ` opening the body, the robot
   nowhere else, and none of the harness footer.
   Completion criterion: the `ok:` line, which carries the size and the cut
   ratio for information only.
4. REVIEW-ON-WISDOM — the checks no program runs, over `tmp/pr-body.md`: every
   claim verified against the diff or relevant source, or marked as an inference;
   enough context to assess the change without this conversation; no history
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

**Body**: ALWAYS scale detail to the change; no fixed sections or total-length cap.

- **Lead**: ALWAYS open with `🤖 **TL;DR:**` and one to three sentences naming
  the outcome. ALWAYS keep this paragraph at most 400 chars, including the
  prefix. Attribution follows WISDOM § Git.
- **Context**: ALWAYS explain the problem, resulting behavior and consequential
  design choices, including why the approach fits existing mechanisms. ALWAYS
  state scope boundaries when omission could mislead. A simple change can fit
  entirely in the lead; otherwise use short paragraphs, bullets or headings
  only where they help. ALWAYS include validation or limitations when they
  materially affect confidence in the change.
- **Closers**: ALWAYS use `Closes #N` or `Fixes #N` only for real linked issues.

NEVER substitute a code inventory, chronology, generic checklist or runbook
for that explanation. NEVER use a table, rule, checkbox, code block, image or
"This PR"; ALWAYS use concise prose or a link. ALWAYS follow the `writing`
skill's copy rules. NEVER hard-wrap — GitHub renders the line.
