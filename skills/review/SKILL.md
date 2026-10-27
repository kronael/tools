---
name: review
description: Give or take a code review — produce findings (give) or apply them (take); local by default, or a GitHub PR with `gh`. NOT for arbitrary PR comments (use gh-comment) or issues (use gh-issue).
when_to_use: "review this, review my changes, review the diff, code review, review PR, critique a PR, post review findings on a PR, take a review, apply GH review comments, address review comments, resolve review threads, CodeRabbit comments"
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
| apply a PR's review comments | `take.md` § GitHub PR |
| apply a local findings list / `BUGS.md` | `take.md` |

Bare `/review` = give, local. `give` produces findings (read-only); `take`
applies them.

ALWAYS take the user's own word for it: they said `take`, they mean apply a
review that already exists, and a review is almost always a PR's comments —
`gh pr list` and go. "and fix the issues" does not make it `give`; `take` ends
in fixes too.

## Rules

- ALWAYS route GitHub posting through the `gh-comment` skill — its distill and
  review-on-wisdom phases, approval gate and `🤖` prefix.
- NEVER `gh pr merge` or `gh pr review`. A review is submitted only on the
  user's ask, through the permission dialog the hook raises on the submit
  (`gh-comment` § Submit).
