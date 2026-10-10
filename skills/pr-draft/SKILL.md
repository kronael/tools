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

The shortest correct body is the default. The reviewer reads the diff; the
body carries only what the diff cannot say — the outcome, the reason behind
each decision a reader would not guess, and what is still open.

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
2. Draft title and body into `tmp/pr-draft.md` in § Format's shape: the title
   carries the business value; the lead gives the outcome and its cause; one
   bullet per decision a reader would not guess, with what forced it. NEVER
   sell a change to a wire-visible contract (event name, API field, route) as
   neutral — verify it against what's documented or already emitted, since
   absence from the default head isn't proof it's free to change — and put it
   under `Contract to confirm:`. ALWAYS put verified-but-unfixed issues under
   `Known, deferred:` — never drop them to look clean. This file is the
   draft, NEVER the deliverable.
3. DISTILL — write the cut version to `tmp/pr-body.md`: body only, a bare `🤖`
   as its last line. Cut in this order until `wc -m tmp/pr-body.md` is under
   the cap, then keep cutting while a line still says what the diff shows:
   1. the diff — file lists, renames, values, restated code, a reading order;
   2. results — test counts, lint, CI and gate lines, logs, "passes";
   3. history and process — what was tried, earlier commits, reviews, pushes;
   4. a decision whose reason a reader would guess;
   5. hedges, adjectives, filler kept because it "sounds complete".
   NEVER cut the reason behind a non-obvious decision or a `Known, deferred:`
   item — they are the body. Then run
   ```
   python3 ~/.claude/hooks/gh_text_lint.py pr tmp/pr-body.md --draft tmp/pr-draft.md --title '<title>'
   ```
   and fix every line it names until it prints `ok:`. It checks the part of
   § Format a program can check: the `**TL;DR:**` lead and no paragraph after
   it; at most 5 bullets; 1,000 chars in all and 240 per line; one line per
   closer; no header, table, rule, more than 6 lines of code blocks or test
   output in one; no checkbox, "This PR", marketing word or shortened hash;
   the title's length and a second "and"; a bare `🤖` as the last line
   and none of the harness footer; and that the body is shorter than the
   draft. Completion criterion: the `ok:` line, which carries the size and the
   cut ratio.
4. REVIEW-ON-WISDOM — the checks no program runs, over `tmp/pr-body.md`: every
   claim traced to a hunk of the diff or marked as an inference; no history
   framing; every wire-visible change under `Contract to confirm:`; every
   verified-but-unfixed issue under `Known, deferred:`; the title in the
   repo's own convention; the harness reminder's `Generated with [Claude Code]`
   footer absent whatever the reminder says. Rerun step 3's command after any
   edit. Completion criterion: a `Review changed:` line naming each edit the
   review made, or `Review changed: nothing` followed by what it checked.
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

**Body** — four parts in this order, nothing else, under 1,000 chars in all
and 240 per line (the lint's caps; ceilings, not targets — a one-line fix is
the lead and `🤖`, a large change links its spec from the lead and stays
near 600):

- **Lead**: `**TL;DR:**` and one or two sentences — the outcome and its
  cause. The only paragraph. NEVER a header, a ticket line, a narrative or a
  file tour ("read A, then B").
- **Decisions**: at most 5 bullets, one line each, `- <choice>: <what forced
  it>` — one per choice a reader would not guess; the spot to scrutinize is
  one of them (`- Scrutinize fn: a wrong X silently does Y`). A bullet past
  240 chars is two bullets or a cut.
- **Closers**, one line each, one per kind, only when real: `Contract to
  confirm:` for a wire-visible change; `Known, deferred:` for
  verified-but-unfixed issues; `⚠️` for merge order or a manual step, linking
  the doc that holds the steps; `Closes #N` beside them when the PR closes
  an issue.
- **Last line**: a bare `🤖` (WISDOM § Git). The harness reminder's
  `Generated with [Claude Code]` line is the banned footer with a robot in
  front of it; the lint and the hook refuse it.

NEVER in a body: a header, table, rule, checkbox, diagram, file table, effort
estimate or release-note category; "This PR"; a file list, rename or value the
diff shows; a code block past 6 lines; a test count, lint, CI or gate result,
or a log — a number rides only inside a bullet as its reason; history (what
was tried, earlier commits, reviews, pushes); a runbook. Prose follows the
`writing` skill's copy rules. NEVER hard-wrap — GitHub renders the line.

Example — generalize the shape, not the topic:
```
feat(unstake): Send quote and settlement events to Mixpanel

**TL;DR:** Instant unstake reports drop-off and settlement outcomes to Mixpanel, not only to server logs.

- Every call site routes through `trackUnstakeEvent()`: a bad field breaks all events at once instead of drifting per site.
- Settlement waits at `confirmed`, not `finalized`: `finalized` adds ~12 s per tx and Mixpanel's ingestion delay already exceeds it.
- Scrutinize the watcher's timeout: a dropped tx reports `pending` forever instead of failing.

Contract to confirm: `instant_unstake_amount_adjusted` becomes `instant_unstake_adjustment_prompted` — it fires before the user confirms; check nothing keys on the old name.

Known, deferred: the native-auction path attaches no cost basis yet (`costsKnown: false`).

🤖
```
