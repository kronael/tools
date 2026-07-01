---
name: gh-comment
description: Post inline review comments to a GitHub PR. Handles pending review conflicts, batch inline comments, and fallback general comments for lines outside the diff.
when_to_use: posting review findings to a GitHub PR as inline comments
user-invocable: false
---

# gh-comment

## Setup

```bash
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
HEAD_SHA=$(gh pr view <PR> --json headRefOid --jq .headRefOid)
DIFF_FILES=$(gh pr diff <PR> --name-only)
```

## Clear pending review

GitHub allows one pending review per user per PR. Clear before posting:

```bash
PENDING=$(gh api repos/$REPO/pulls/<PR>/reviews --jq '.[] | select(.state=="PENDING") | .id')
[ -n "$PENDING" ] && gh api repos/$REPO/pulls/<PR>/reviews/$PENDING --method DELETE
```

## Sign-off questionnaire

ALWAYS present each finding to the user before posting. In Claude Code use `AskUserQuestion` (`multiSelect: true`, each finding as a short option label, body in description, unselected findings dropped silently, max 4 per question). In Codex `AskUserQuestion` is unavailable — ALWAYS list findings in chat and NEVER post before receiving explicit confirmation.

## Batch inline post

One API call per review, all comments in `comments[]`. Omit `event` — review stays PENDING for user to submit.

```bash
gh api repos/$REPO/pulls/<PR>/reviews --method POST --input - <<'EOF'
{
  "commit_id": "<HEAD_SHA>",
  "comments": [
    {"path": "src/file.ts", "line": 46, "side": "RIGHT", "body": "🤖 claude: <finding>"}
  ]
}
EOF
```

Constraints:
- `line` must fall within a diff hunk
- New files: every line is valid
- Modified files: only lines inside `@@` hunk ranges
- `side: "RIGHT"` for added/context, `"LEFT"` for deleted

Check hunk ranges: `gh pr diff <PR> | grep -A<N> "diff --git.*<filename>" | grep "^@@"` — hunk `@@ -old,len +new,len @@` makes new-file lines `[new .. new+len]` valid.

## Fallback: general comment

For lines outside the diff:

```bash
gh pr comment <PR> --body "🤖 claude: <finding with file:line reference>"
```

## Rules

- ALWAYS prefix comment body with `"🤖 claude: "`
- ALWAYS leave the review PENDING — NEVER include `event` unless user asks to submit
- ALWAYS batch inline comments into one POST — NEVER loop individual calls
- ALWAYS fall back to a general PR comment with explicit `file:line` if a line is outside the diff
- ALWAYS return the review `html_url` from the API response
- To submit when asked: `POST /pulls/<PR>/reviews/<review_id>/events` with `{"event":"COMMENT","body":""}`
- To add more comments to a pending review: `POST /pulls/<PR>/reviews/<review_id>/comments`
