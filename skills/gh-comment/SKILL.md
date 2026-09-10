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

## Comment body — distilled

Every body goes through two passes before it is posted. Drafting straight into
the final text does not work: the first version always carries the reasoning
that got you there.

1. **Draft** the finding with its evidence, wherever you are keeping notes.
2. **Distill** to one line naming the defect plus one optional line giving the
   fix, then **de-slop** it: load the `humanize` skill and apply it. Cut em
   dashes, hedges, passive voice, "it is worth noting", significance padding
   and rule-of-three phrasing. Speak in the `80-caveman` register: maximum
   signal per token, no preamble, no recap.

Cap the result at 2 lines / ~200 chars. If it will not fit, the finding is two
findings or the evidence belongs in the report.

- Lead with the defect — "Overflows at `u64::MAX`", NOT "I noticed this
  arithmetic could potentially..."
- NEVER restate the code, the diff, or what the function does — the reader is
  looking at it
- NEVER hedge ("might", "consider", "perhaps", "you may want to"). State the
  failure or drop the finding
- Fix line ONLY when non-obvious, written as code or an imperative — never a
  paragraph
- Severity sits right after the robot prefix: 🔴 blocker (must fix before
  merge), 🟡 important (not merge-blocking), `nit:` for style and cosmetics.
  NEVER give a nit an emoji — the word carries it
- Rationale, repro steps, and alternatives belong in the chat report, NEVER in
  the comment
- Re-raising a finding on a thread someone resolved: ALWAYS say so in the first
  clause ("Re-raising the thread X resolved: none of it changed"). Without it a
  second comment on the same line reads as a duplicate, and distillation is
  exactly what cuts that clause

```
🤖 🔴 Charges `sold_lamports`, the RETAINED piece, so it liquidates the wrong account.
Fix: use the sale leg's lamports here.
```

## Batch inline post

One API call per review, all comments in `comments[]`. Omit `event` — review stays PENDING for user to submit.

```bash
gh api repos/$REPO/pulls/<PR>/reviews --method POST --input - <<'EOF'
{
  "commit_id": "<HEAD_SHA>",
  "comments": [
    {"path": "src/file.ts", "line": 46, "side": "RIGHT", "body": "🤖 <finding>"}
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
gh pr comment <PR> --body "🤖 <finding with file:line reference>"
```

## Rules

- ALWAYS prefix comment body with `"🤖 "`
- ALWAYS follow the robot prefix with 🔴 or 🟡 on a blocker or an important
  finding, and with `nit:` on a nit — NEVER mix the two
- ALWAYS run the draft-then-distill pass in § Comment body, `humanize` included
  — a full-prose finding pasted into a PR comment is a defect
- ALWAYS re-read a distilled body against the draft before posting: check that
  the cut did not take the re-raise clause, a file:line, or the failing input
- ALWAYS leave the review PENDING — NEVER include `event` unless user asks to submit
- ALWAYS batch inline comments into one POST — NEVER loop individual calls
- ALWAYS fall back to a general PR comment with explicit `file:line` if a line is outside the diff
- ALWAYS return the review `html_url` from the API response
- To submit when asked: `POST /pulls/<PR>/reviews/<review_id>/events` with `{"event":"COMMENT","body":""}`
- NEVER expect to append to a pending review — `POST /pulls/<PR>/reviews/<review_id>/comments`
  returns 404. ALWAYS `DELETE /pulls/<PR>/reviews/<review_id>` and re-POST the whole
  `comments[]`, then report the new review id and comment count
