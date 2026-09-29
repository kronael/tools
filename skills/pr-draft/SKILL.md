---
name: pr-draft
description: Draft or rewrite a PR description. NOT for commit messages (use commit).
when_to_use: "draft a PR, open a PR, write the PR description, PR body, PR summary, update the PR description, rewrite/update the body of an open PR"
user-invocable: true
---

# PR Description

Run directly in main context (no subagent).

## Workflow

1. Find true merge base and read the whole change:
   ```
   BASE=$(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD main)
   git log $BASE..HEAD --oneline
   git diff $BASE..HEAD --stat
   git diff $BASE..HEAD
   ```
   The base is the merge-base with main, NOT `origin/main` itself — that misses commits
   already on the branch before the last merge. If both fail, ask the user.
   ALWAYS read the full diff, NEVER draft from the stat and the commit log —
   the one-line changes a stat hides (a pinned key, a changed default, a
   dropped field) are the ones a review bot names and the author's body misses.
2. Draft title and body: title carries the business value; body is a reading
   guide for the reviewer alone — where the logic lives, what to scrutinize,
   what's risky, and the reasoning behind each non-obvious decision — NOT a
   commit log or a step-by-step plan, so skip renames, churn, and anything
   the reviewer doesn't need to judge the change. For every decision a
   reader wouldn't guess on their own — a split into two round trips, a
   relaxed consistency level, a rename — say what forced it and what the
   alternative would have cost, so a reader who never saw the diff could
   rebuild the same design. NEVER sell a change to a wire-visible contract
   (event name, API field, route) as neutral — verify it against what's
   documented or already emitted, since absence from `origin/main` isn't
   proof it's free to change — and flag it for the reviewer instead. ALWAYS
   flag verified-but-unfixed issues as "known, deferred" — never drop them
   to look clean.
3. Cut to the shape and size below.
4. Show the draft and ask if they want to tweak anything. For a NEW PR, STOP —
   NEVER run `gh pr create` or open the PR.

## Setting the description on an EXISTING PR

To update an existing PR's body, write the body to `tmp/body.md` and PATCH via
REST. NEVER use `gh pr edit --body` — it runs a GraphQL `login` query that
requires `read:org`; the REST endpoint needs only `repo`:

This path actually posts to GitHub as the user, unlike a new-PR draft the user
still has to submit themselves — ALWAYS end `tmp/body.md` with a bare `🤖`
line before the PATCH, so a reader can tell Claude wrote the description.

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

**Title**: ALWAYS follow the repo's own convention — read recent titles
(`git log --oneline -20 origin/main`); keep a ticket prefix (`[ABC-123]`)
when the branch or commits carry one; default `type(scope): outcome` with
`fix` `feat` `refactor` `docs` `chore`. ONE outcome, max 72 chars. NEVER a
comma list of changes — needing "and" twice means name the outcome above them.

**Body shape** — orientation first, then one paragraph per concern:

- **Lead**: ALWAYS open with one or two sentences giving the outcome and its
  cause, and — when more than one layer changes — every layer in reading
  order with its entry file, so the reviewer knows the shape before opening a
  file. NEVER open on a header, a ticket line, or a narrative.
- **Concerns**: ALWAYS one short paragraph per concern, opened by a bold
  lead-in stating the claim or a `before → after` result, with enumerations
  folded inline ("A, B and C"). NEVER headers, tables, or `---` rules.
  Bullets ONLY for 2–4 parallel one-line items (per environment, per
  target) — a bullet running past one line is a paragraph; write it as one.
- **Scope**: ALWAYS name every behaviour change; minor ones go in one
  closing `Also:` sentence, since silence reads as "unchanged". NEVER one
  bullet per file, NEVER restate values the diff shows (versions, digests,
  limits).
- **Risk**: ALWAYS point the reviewer at the weakest spot ("Scrutinize
  `fn`: a wrong X silently does Y"). NEVER claim "safe", "no-op" or "cannot"
  without naming the check that proved it.
- **Evidence**: at most one sentence — fails-before/passes-after or a
  measured number. NEVER list lint/build/test passes CI already shows, NEVER
  a test plan or checkbox.
- **Close**, each only when real: `Contract to confirm:` for wire-visible
  changes, `Known, deferred:` for verified-but-unfixed issues, and a `⚠️`
  line for merge order, rollout, or a manual step before or after merge.
- NEVER a file table, effort estimate, sequence diagram, or release-note
  categories (Features / Bug Fixes / Chores) — review bots such as CodeRabbit
  post those already, and category bullets ("Improved X") carry no reasoning.
- NEVER a claude.ai session URL or a second attribution footer.
- No "This PR...". Prose follows the `writing` skill's copy rules.

**Size**: ALWAYS scale the body to the change — a bump or one-liner gets 1–3
sentences (~400 chars); a mid change the lead plus up to 3 paragraphs
(~1,500); a large one a paragraph per concern, NEVER past ~3,000 — design
narrative, incident timelines, and measurement tables go to a linked doc or
issue.

ALWAYS draft then cut — the first version is a draft, NEVER the deliverable.
Strip every word that doesn't change meaning: hedges, context the diff
already shows, adjectives, filler kept only because it "sounds complete."
Cutting removes narration and restatement, NEVER the reasoning behind a
non-obvious decision — that reasoning is the essence, not the filler around
it. Only the trimmed result is real — shortest version that still gives the
reviewer what they need, including why; NEVER pad to look thorough.

ALWAYS output the draft (title + body) in one fenced code block so it is easy
to copy.

Example — a mid-size change; generalize the shape (layer-naming lead, bold
lead-ins, reasoning inline, `Also:` sweep, closing flags), not the topic:
```
feat(unstake): send quote and settlement events to Mixpanel

Instruments instant unstake so drop-off and settlement outcomes reach Mixpanel, not only server logs — the event helper (`analytics/unstake.ts`), the quote and confirm screens, then the settlement watcher.

**One event shape.** Every call site routes through `trackUnstakeEvent()`, so a bad field breaks all events at once instead of drifting per call site.

**Settlement waits at `confirmed`, not `finalized`** — `finalized` adds ~12 s per tx and Mixpanel's own ingestion delay already exceeds that, so waiting longer buys no accuracy. Scrutinize the watcher's timeout: a dropped tx reports `pending` forever instead of failing.

Also: the quote screen's retry button emits `instant_unstake_quote_retry`.

Contract to confirm: `instant_unstake_amount_adjusted` becomes `instant_unstake_adjustment_prompted` — the event fires before the user confirms, so downstream counted it as a settled adjustment; check nothing still keys on the old name.

Known, deferred: the native-auction path can't attach a cost basis yet (`costsKnown: false`).
```
