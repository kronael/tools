---
name: gh-review
description: Deep review of a GitHub PR, posted back to the PR. NOT for local uncommitted changes (use review); NOT for posting arbitrary comments (use gh-comment).
when_to_use: "review PR, review the pull request, review the PR on GitHub, review and post to the PR, critique a PR, post review findings on a PR"
user-invocable: true
---

# gh-review

The GitHub hook over the `review` engine. Resolve the PR → fetch its diff and
existing comments → run the `review` workflow on that diff → post surviving
findings back via `gh-comment` (with its approval gate).

`review` does the analysis; this skill only adds the PR source and the post.

## Workflow

### 1. Resolve the PR

If the user gives a number, use it. Otherwise resolve from the current branch:

```bash
gh pr view --json number,headRefOid,baseRefName,title,body
```

Capture the number, head SHA (for inline anchoring), base ref, and the
title/body (feed the goal into fable's Job 1 focus).

### 2. Fetch the diff AND existing comments

```bash
gh pr diff <N>                                                    # the diff to review
gh pr view <N> --json comments                                     # issue/general comments
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
gh api repos/$REPO/pulls/<N>/comments --paginate                   # inline review comments
```

ALWAYS read the existing comments first — DROP any finding that merely repeats
a point already raised on the PR. Don't re-litigate resolved threads.

### 3. Run the review engine

Run the `review` skill's workflow (steps 2-6: bucket → lenses → parallel
agents → fable deep-dive + reverification → per-hunk minimality → triage) on
the PR diff, with the PR title/body as the change goal. Use `model="opus"` for
the agents unless the caller specifies otherwise.

### 4. Present, then post via gh-comment

Present the report (review step 7) and wait. When the user says to post, hand
the surviving findings to the `gh-comment` skill:

- gh-comment owns the **mandatory approval gate** — show every finding and get
  explicit confirmation before anything is posted.
- gh-comment handles pending-review clearing, batch inline comments, and the
  general-comment fallback for lines outside the diff.
- gh-comment applies the `🤖` robot-head markers on posted bodies.

For a whole-PR summary review body, prepend a bare `🤖` at the top when most of
the PR was auto-generated / vibe-coded (ask if unsure, or when told to
"robothead it"), and append a bare `🤖` at the very end — just the head, no
explanation.

## Rules

- NEVER `git push`
- NEVER `gh pr create`, `gh pr merge`, or `gh pr review --approve` — if asked, refuse and cite CLAUDE.md
- NEVER post directly — ALWAYS route posting through the `gh-comment` skill and its approval gate
- ALWAYS fetch and honor existing PR comments so findings don't repeat prior points
- ALWAYS present the report and wait before posting
- ALWAYS include `file:line` in every finding
