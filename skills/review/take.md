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

`/review take gh [<N>]`. Source the worklist from the PR's comments instead of a
local list:

```bash
gh pr view --json number,headRefOid,title,body               # no args = current branch
gh pr view <N> --json comments                               # issue/general comments
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
gh api repos/$REPO/pulls/<N>/comments --paginate             # inline review comments
```

Then classify → fix → verify → surface as above. Optionally reply to or resolve
threads — but only via the `gh-comment` skill (its approval gate + 🤖 markers),
and only after showing the user; skip if they just wanted the code fixed.

- Each reply carries its disposition — fixed / deferred / declined.
  Bot-authored threads may be resolved in the same turn; human-authored
  threads get the reply only and stay open for the reviewer.

## Rules

- ALWAYS make minimal edits one at a time and VERIFY with typecheck + tests in the same pass
- ALWAYS re-verify a finding against current code before editing — report
  refuted/already-fixed findings, NEVER edit around them
- NEVER unilaterally act on a design/product decision — surface it and wait
- NEVER post to a PR directly — route through `gh-comment` after showing the user
- NEVER `git push`, `gh pr create`, `gh pr merge`, or `gh pr review --approve`
