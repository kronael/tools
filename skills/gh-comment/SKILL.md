---
name: gh-comment
description: Post inline review comments to a GitHub PR. Handles pending review conflicts, batch inline comments, and fallback general comments for lines outside the diff.
when_to_use: posting review findings to a GitHub PR as inline comments
user-invocable: false
---

# gh-comment Skill

Post review findings as inline GitHub PR comments.

## Setup

```bash
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
HEAD_SHA=$(gh pr view <PR> --json headRefOid --jq .headRefOid)
DIFF_FILES=$(gh pr diff <PR> --name-only)
```

## Clear pending review (if any)

One pending review allowed per user per PR. Clear before posting:

```bash
PENDING=$(gh api repos/$REPO/pulls/<PR>/reviews --jq '.[] | select(.state=="PENDING") | .id')
[ -n "$PENDING" ] && gh api repos/$REPO/pulls/<PR>/reviews/$PENDING --method DELETE
```

## Batch inline comments (preferred)

Post all inline comments in one API call — avoids repeated pending review conflicts:

Omit `event` to leave the review pending. The user submits it themselves on GitHub, or tells you to submit.

```bash
gh api repos/$REPO/pulls/<PR>/reviews \
  --method POST \
  --input - <<'EOF'
{
  "commit_id": "<HEAD_SHA>",
  "comments": [
    {
      "path": "relative/path/to/file.ts",
      "line": 46,
      "side": "RIGHT",
      "body": "🤖 claude: <finding>"
    }
  ]
}
EOF
```

**Constraints:**
- `line` must fall within a diff hunk for that file
- New files: every line is valid (the whole file is in the diff)
- Modified files: only lines inside `@@` hunk ranges are valid
- Use `side: "RIGHT"` for added/context lines, `"LEFT"` for deleted lines

## Check if line is in diff

```bash
gh pr diff <PR> | grep -A<N> "diff --git.*<filename>" | grep "^@@"
# Hunk @@ -old,len +new,len @@ → new file lines [new .. new+len] are valid
```

## Fallback: general PR comment

For findings on files/lines not in the diff, post as a regular comment:

```bash
gh pr comment <PR> --body "🤖 claude: <finding with file:line reference>"
```

## Rules

- ALWAYS prefix comment body with `"🤖 claude: "`
- Always leave the review PENDING — never include `event` in the POST body unless the user explicitly asks to submit
- To submit when asked: `POST /pulls/<PR>/reviews/<review_id>/events` with `{"event":"COMMENT","body":""}`
- To add more comments to an existing pending review: `POST /pulls/<PR>/reviews/<review_id>/comments`
- Group inline comments into one batch POST — don't loop individual calls
- If a line is rejected (not in diff), fall back to a general PR comment with explicit `file:line` reference
- After posting, return the review URL from the API response `html_url`
