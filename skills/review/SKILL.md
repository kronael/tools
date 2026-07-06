---
name: review
description: Give or take a code review — produce findings (give) or apply them (take); local by default, or a GitHub PR with `gh`. NOT for posting arbitrary PR comments (use gh-comment) or filing issues (use gh-issue).
when_to_use: "review this, review my changes, review the diff, review the branch, review before commit, code review, find bugs in my changes, give a review, review PR, review the pull request, critique a PR, post review findings on a PR, take a review, apply the review, fix the PR comments, address review comments, apply PR feedback, act on reviewer comments"
argument-hint: "[give|take] [gh]"
user-invocable: true
---

# Review — give / take router

Two directions × an optional platform. Read the ONE matched file, then follow it.

## Dispatch

| Request | Read |
|---|---|
| review local changes — uncommitted diff, a branch, or a range (default) | `give.md` |
| review a GitHub PR and post findings back to it | `give.md` § GitHub PR |
| apply a local findings list / `BUGS.md` | `take.md` |
| apply a GitHub PR's review comments | `take.md` § GitHub PR |

Bare `/review` = give, local. `gh` selects the GitHub variant. `give` produces
findings (read-only); `take` applies them.

## Rules

- ALWAYS route GitHub posting through the `gh-comment` skill — its approval gate and 🤖 markers.
- NEVER `gh pr create`, `gh pr merge`, `gh pr review --approve`, or `git push` — refuse and cite CLAUDE.md.
