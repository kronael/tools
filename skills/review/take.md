# Take — apply a review

Apply a worklist of review findings as minimal code fixes, then verify. The
worklist is a local findings list / `BUGS.md` by default; the GitHub-PR variant
sources it from a PR's comments (last section).

## 1. Gather the worklist

- **Local** (default) — the findings the user points at: a `BUGS.md`, a report
  from `give`, or an inline list. If none is named, ask which.
- **By ID** — a `give` report assigns stable IDs (`C1`/`I2`/`M3`); accept
  selectors like `all`, `C1`, `C1,I2`, or "the last one" and resolve them
  against that report before classifying.
- **GitHub PR (`gh`)** — see the GitHub PR section below.

## 2. Classify each item

ALWAYS re-verify each finding against the CURRENT code before classifying —
it may be stale, already-fixed, or refuted outright. Never take a finding's
claim on faith.

- **(a) actionable code bug** — a concrete fix the diff should carry
- **(b) design / product decision** — reverses a product choice, changes scope,
  or is a judgement call
- **(c) already-addressed or refuted** — current code already satisfies it, or
  the finding doesn't hold up — report it, NEVER edit around it
- **(d) question / non-actionable** — a question, praise, or a note needing no change

## 3. Apply the actionable fixes

Apply fixes for (a) ONE AT A TIME. For each: make the **minimal** edit that
resolves it — no refactors, no scope creep. VERIFY in the same pass with the
project's typecheck and tests, capturing once: `make test 2>&1 | tee test.log && tail -8 test.log`.

## 4. Surface (b), never guess

For every design/product decision, STOP and present it — never unilaterally
reverse a product decision. List each with the source text and what deciding
either way would mean.

## GitHub PR (gh)

`/review take gh [<N>]` — "take GH review", "apply GH review comments", "answer
the PR comments" all mean this. Source the worklist from EVERY open thread —
human and bot (CodeRabbit etc.) alike, never a hand-picked subset. If `gh`
is unauthenticated, see `gh-comment` § Setup for `GH_TOKEN`.

```bash
gh pr view <N> --json number,headRefOid,title,body            # no <N>: gh-comment § Setup finds it
gh pr view <N> --json comments                                # issue-level comments
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
gh api repos/$REPO/pulls/<N>/comments --paginate               # inline review comments (REST — no resolution state)
```

REST comments carry no thread id or resolution state. Pull those from
`gh-comment` § Fetch threads (GraphQL `reviewThreads`: `id`, `isResolved`,
`author`, `body`) — needed to tell a resolved thread from an open one, a bot
author from a human one, and to reply/resolve later.

Classify (§2 above) with two GH additions:

- Automated-reviewer (bot: `coderabbitai`, or any `login` ending `[bot]`)
  findings skew false-positive — before calling one (a), check it against the
  project's `CLAUDE.md` design-invariants section and `BUGS.md`. A documented
  invariant or by-design entry makes it (c) refuted, not a fix.
- `isResolved: true` on a thread, or a bot's own "Addressed in ..." banner, is
  a CLAIM, not evidence — re-verify the finding at HEAD regardless of what
  GitHub or the bot already claims happened.

Fix → verify as above (§3), then answer EVERY thread — the default for "take
GH review"; skip only if the user explicitly asked for code-only, no reply.
`gh-comment` owns every disposition (§ Reply to a thread, § Resolve a thread,
§ Re-review request) — NEVER call the thread API directly from here. Reply to
the unfixed threads now, then STOP with the push refspec shown: the push is
the user's own ask (WISDOM § Git). The fixed threads' resolve and the one
re-review request run once that push has landed.

## Rules

- ALWAYS make minimal edits one at a time and VERIFY with typecheck + tests in the same pass
- ALWAYS re-verify a finding against current code before editing — report
  refuted/already-fixed findings, NEVER edit around them
- NEVER unilaterally act on a design/product decision — surface it and wait
- NEVER post to a PR, push, or run a `gh pr` action from here — ALWAYS
  through `gh-comment` and WISDOM § Git, which own those gates
