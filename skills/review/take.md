# Take — apply a review

Turn an existing findings list into minimal verified fixes.

## 1. Worklist

A review is almost always a PR's comments — start at § GitHub PR below unless
the user points somewhere else. Otherwise it is a `BUGS.md`, a `give` report
(whose ids resolve selectors like `all`, `C1,I2`, "the last one"), or an inline
list; if none is named, find the obvious candidate and confirm it.

## 2. Classify

ALWAYS re-verify each finding against the CURRENT code first — findings go
stale, get fixed, or don't hold up. NEVER take a claim on faith.

- **(a) actionable bug** — a concrete fix
- **(b) design / product decision** — reverses a product choice or is a judgement call
- **(c) already-fixed or refuted** — report it, NEVER edit around it
- **(d) question / praise** — no change

## 3. Fix

Apply (a) ONE AT A TIME, each the minimal edit that resolves it — no refactors,
no scope creep. VERIFY in the same pass with the project's typecheck and tests.

## 4. Surface (b), never guess

STOP and present every design decision with its source text and what deciding
either way would mean. NEVER reverse a product choice unilaterally.

## GitHub PR (gh)

`/review take gh [<N>]` — worklist comes from the PR instead:

```bash
gh pr view <N> --json comments                      # general comments
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
gh api repos/$REPO/pulls/<N>/comments --paginate    # inline comments
```

Classify → fix → verify → surface as above. Replying is optional and only via
`gh-comment` after showing the user; skip it if they just wanted code fixed.
Each reply carries its disposition — fixed / deferred / declined. Bot threads
may be resolved the same turn; human threads get the reply and stay open.
