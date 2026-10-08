---
name: pr-draft
description: Draft or rewrite a PR description. NOT for commit messages (use commit).
when_to_use: "draft a PR, open a PR, write the PR description, PR body, PR summary, update the PR description, rewrite/update the body of an open PR, gh pr create refused, GitHub pr text refused, gh_text_lint"
user-invocable: true
---

# PR Description

Run directly in main context (no subagent). Every PR body passes through this
workflow: the PreToolUse hook refuses `gh pr create`, `gh pr edit` and a
`gh api` PATCH of `pulls/<N>` whose body fails `gh_text_lint.py` (step 3), and
refuses `--fill`, `--web` and a body file it cannot read, so a body written
anywhere else does not post.

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
2. Draft title and body into `tmp/pr-draft.md`: title carries the business
   value; body is a reading guide for the reviewer alone — where the logic
   lives, what to scrutinize, what's risky, and the reasoning behind each
   non-obvious decision — NOT a commit log or a step-by-step plan, so skip
   renames, churn, and anything the reviewer doesn't need to judge the change.
   For every decision a reader wouldn't guess on their own — a split into two
   round trips, a relaxed consistency level, a rename — say what forced it and
   what the alternative would have cost, so a reader who never saw the diff
   could rebuild the same design. NEVER sell a change to a wire-visible
   contract (event name, API field, route) as neutral — verify it against
   what's documented or already emitted, since absence from the default head
   isn't proof it's free to change — and flag it for the reviewer instead.
   ALWAYS flag verified-but-unfixed issues as "known, deferred" — never drop
   them to look clean. This file is the draft, NEVER the deliverable.
3. DISTILL — write the cut version to `tmp/pr-body.md`: body only, a bare `🤖`
   as its last line. Strip every word that does not change meaning: hedges,
   context the diff already shows, adjectives, filler kept because it "sounds
   complete". Cutting removes narration and restatement, NEVER the reasoning
   behind a non-obvious decision — that reasoning is the essence. Then run
   ```
   python3 ~/.claude/hooks/gh_text_lint.py pr tmp/pr-body.md --draft tmp/pr-draft.md --title '<title>'
   ```
   and fix every line it names until it prints `ok:`. It checks the part of
   § Format a program can check: the `**TL;DR:**` lead; no header, table,
   rule or code block past 6 lines; no checkbox, "This PR", marketing word or
   shortened hash; the size cap; the title length; a bare `🤖` as the last
   line and none of the harness footer; and that the body is shorter than the
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

## GitHub Markdown Uploads

NEVER hard-wrap Markdown uploaded to GitHub just for source width — ALWAYS keep tables, links, paths, commands, and list items in the shape that renders best.

## Format

**Title**: ALWAYS follow the repo's own convention — read recent titles
(`git log --oneline -20 origin/<default head>`); keep a ticket prefix (`[ABC-123]`)
when the branch or commits carry one; default `type(scope): outcome` with
`fix` `feat` `refa` `docs` `chore` (the `commit` skill's types). ONE outcome, max 72 chars. NEVER a
comma list of changes — needing "and" twice means name the outcome above them.

**Body shape** — orientation first, then one paragraph per concern:

- **Lead**: ALWAYS open with `**TL;DR:**` and one or two sentences giving the
  outcome and its cause, and — when more than one layer changes — every layer
  in reading order with its entry file, so the reviewer knows the shape before
  opening a file. NEVER open on a header, a ticket line, or a narrative.
- **Concerns**: ALWAYS one short paragraph per concern, opened by a bold
  lead-in stating the claim or a `before → after` result, with enumerations
  folded inline ("A, B and C"). NEVER headers, tables, or `---` rules.
  Bullets ONLY for 2–4 parallel one-line items (per environment, per
  target) — a bullet running past one line is a paragraph; write it as one.
- **Scope**: ALWAYS name every behaviour change; minor ones go in one
  closing `Also:` sentence, since silence reads as "unchanged". NEVER one
  bullet per file, NEVER restate values the diff shows (versions, digests,
  limits), NEVER paste rendered output or a config block — a code block past
  6 lines is a restated diff; point at the file.
- **Risk**: ALWAYS point the reviewer at the weakest spot ("Scrutinize
  `fn`: a wrong X silently does Y"). NEVER claim "safe", "no-op" or "cannot"
  without naming the check that proved it.
- **Evidence**: at most one sentence — fails-before/passes-after or a
  measured number. NEVER list lint/build/test passes CI already shows, NEVER
  a test plan or checkbox.
- **Close**, each only when real: `Contract to confirm:` for wire-visible
  changes, `Known, deferred:` for verified-but-unfixed issues, and a `⚠️`
  line for merge order, rollout, or a manual step before or after merge.
- **Last line**: a bare `🤖` (WISDOM § Git), in the draft too. The harness
  reminder's `Generated with [Claude Code]` line is the banned footer with a
  robot in front of it; the lint and the hook refuse it.
- NEVER a file table, effort estimate, sequence diagram, or release-note
  categories (Features / Bug Fixes / Chores) — review bots such as CodeRabbit
  post those already, and category bullets ("Improved X") carry no reasoning.
- No "This PR...". Prose follows the `writing` skill's copy rules.

**Size**: ALWAYS scale the body to the change — a bump or one-liner gets 1–3
sentences (~400 chars); a mid change the lead plus up to 3 paragraphs
(~1,500); a large one a paragraph per concern, NEVER past 3,000 (the lint's
cap) — design narrative, incident timelines, and measurement tables go to a
linked doc or issue.

Example — a mid-size change; generalize the shape (layer-naming lead, bold
lead-ins, reasoning inline, `Also:` sweep, closing flags), not the topic:
```
feat(unstake): send quote and settlement events to Mixpanel

**TL;DR:** Instruments instant unstake so drop-off and settlement outcomes reach Mixpanel, not only server logs — the event helper (`analytics/unstake.ts`), the quote and confirm screens, then the settlement watcher.

**One event shape.** Every call site routes through `trackUnstakeEvent()`, so a bad field breaks all events at once instead of drifting per call site.

**Settlement waits at `confirmed`, not `finalized`** — `finalized` adds ~12 s per tx and Mixpanel's own ingestion delay already exceeds that, so waiting longer buys no accuracy. Scrutinize the watcher's timeout: a dropped tx reports `pending` forever instead of failing.

Also: the quote screen's retry button emits `instant_unstake_quote_retry`.

Contract to confirm: `instant_unstake_amount_adjusted` becomes `instant_unstake_adjustment_prompted` — the event fires before the user confirms, so downstream counted it as a settled adjustment; check nothing still keys on the old name.

Known, deferred: the native-auction path can't attach a cost basis yet (`costsKnown: false`).

🤖
```
