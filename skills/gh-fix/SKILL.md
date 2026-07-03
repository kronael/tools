---
name: gh-fix
description: Apply fixes sourced from a GitHub PR's review comments. NOT for a local screenshot or bug report (use fix); NOT for producing a review (use gh-review).
when_to_use: "fix the PR comments, address the review comments, apply the review, take the GitHub review, fix what reviewers flagged, resolve PR feedback, act on PR comments"
user-invocable: true
---

# gh-fix

The GitHub counterpart of the local `/fix` skill. `/fix` reads `./capture.png`
or a described bug from local files; **gh-fix sources its worklist from a
GitHub PR's comments** — never from screenshots or local reports. Everything
to do lives on the PR.

## Workflow

### 1. Resolve the PR

Number if the user gives one, else the current branch:

```bash
gh pr view --json number,headRefOid,title,body
```

### 2. Fetch every comment

```bash
gh pr view <N> --json comments                                    # issue/general comments
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
gh api repos/$REPO/pulls/<N>/comments --paginate                  # inline review comments
```

### 3. Classify each comment

- **(a) actionable code bug** — a concrete fix the diff should carry
- **(b) design/product decision** — reverses a product choice, changes scope, or is a judgement call
- **(c) already-addressed** — the current code already satisfies it (verify by reading)
- **(d) question / non-actionable** — a question, praise, or a note needing no code change

### 4. Apply the actionable fixes

For each (a): make the **minimal** edit that resolves it — no refactors, no
scope creep. After the edits, VERIFY in the same pass with the project's
typecheck and tests (`make test` / project equivalent), capturing once:
`make test 2>&1 | tee ./tmp/test.log && tail -8 ./tmp/test.log`.

### 5. Surface (b), never guess

For every design/product decision, STOP and present it to the user — never
unilaterally reverse a product decision. List each with the comment text and
what deciding either way would mean.

### 6. Optional: reply / resolve on the PR

Only after showing the user, route any PR reply or thread-resolve through the
`gh-comment` skill (its approval gate + `🤖` markers). Skip if the user just
wanted the code fixed.

## Rules

- ALWAYS source the worklist from the PR — NEVER read `./capture.png` or a local report (that is `/fix`)
- ALWAYS make minimal edits and VERIFY with typecheck + tests in the same pass
- NEVER unilaterally act on a design/product decision — surface it and wait
- NEVER `git push`
- NEVER `gh pr create`, `gh pr merge`, or `gh pr review --approve` — if asked, refuse and cite CLAUDE.md
- NEVER post to the PR directly — route through the `gh-comment` skill after showing the user
