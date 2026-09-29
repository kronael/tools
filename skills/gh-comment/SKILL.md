---
name: gh-comment
description: Post inline review comments to a GitHub PR, and reply to / resolve existing review threads. Handles pending review conflicts, batch inline comments, thread fetch/reply/resolve, and fallback general comments for lines outside the diff.
when_to_use: "posting review findings to a GitHub PR as inline comments, replying to a PR review thread, resolving a PR review thread, fetching PR review thread status"
user-invocable: false
---

# gh-comment

## Setup

```bash
gh auth status >/dev/null 2>&1 || echo 'no gh config in $HOME — export GH_TOKEN=<token> or pass it inline'
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

ALWAYS present each finding, thread reply, or re-review request to the user before posting. In Claude Code use `AskUserQuestion` (`multiSelect: true`, each finding as a short option label, body in description, unselected findings dropped silently, max 4 per question). In Codex `AskUserQuestion` is unavailable — ALWAYS list findings in chat and NEVER post before receiving explicit confirmation.

## Comment body — distilled

Every body goes through two passes before it is posted. Drafting straight into
the final text does not work: the first version always carries the reasoning
that got you there.

1. **Draft** the finding with its evidence, wherever you are keeping notes.
2. **Distill** to one line naming the defect plus one optional line giving the
   fix, then **de-slop** it: load the `humanize` skill and apply it. Cut em
   dashes, hedges, passive voice, "it is worth noting", significance padding
   and rule-of-three phrasing. Speak in the `caveman` register: maximum
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

## Fetch threads (resolution + author)

REST (`pulls/<PR>/comments`) carries comment bodies but no thread id or
resolution state. Only GraphQL exposes both — needed to tell a resolved
thread from an open one, and a bot author from a human one, before replying:

```bash
gh api graphql -f query='
  query($owner:String!,$name:String!,$pr:Int!,$after:String){
    repository(owner:$owner,name:$name){
      pullRequest(number:$pr){
        reviewThreads(first:100,after:$after){
          pageInfo{ hasNextPage endCursor }
          nodes{
            id
            isResolved
            comments(first:1){ nodes{ id databaseId path line author{login} body } }
          }
        }
      }
    }
  }' -f owner="${REPO%/*}" -f name="${REPO#*/}" -F pr=<PR>
```

Paginate with `after`/`pageInfo.hasNextPage` past 100 threads. Bot-authored:
`author.login` is `coderabbitai` or any login ending `[bot]`.

## Reply to a thread

REST, keeps the reply inside the existing thread instead of opening a new
review:

```bash
gh api repos/$REPO/pulls/<PR>/comments/<comment_databaseId>/replies -f body="🤖 <reply>"
```

`<comment_databaseId>` is the thread's first comment `databaseId` from the
fetch above — NOT the GraphQL `id`. Same distillation rules as any other body
(§ Comment body); a reply states the disposition — won't-fix (cite the
invariant/`BUGS.md` entry it matches), deferred, or refuted (say why). A
fixed thread gets NO reply: the re-review request (§ Re-review request)
announces the fix.

## Resolve a thread

GraphQL mutation, by the thread's GraphQL `id` (not `databaseId`):

```bash
gh api graphql -f query='mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{id isResolved}}}' -f id=<thread_id>
```

ALWAYS resolve a fixed thread after the push, with no reply — the re-review
request announces the fix. ALWAYS reply before resolving any other thread — a
resolved thread with no reply and no fix reads as dismissed unread. NEVER
resolve a thread this pass did not address.

## Re-review request

After the push, ONE general comment @-mentions the reviewer, names in about
four words the most important thing the round fixed, and asks for a
re-review — it is the only announcement a fixed thread gets. NEVER compose
the phrase here: hand the `distill` skill the list of fixes, take back its
~4-word phrase, and put that in the comment. Same sign-off gate as every
other body.

```bash
gh pr comment <PR> --body "🤖 @<reviewer> CI is green now. Please re-review."
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
- ALWAYS resolve a fixed thread after the push with NO reply — the re-review
  request announces it; NEVER resolve one this pass did not address
- ALWAYS reply to a won't-fix, deferred or refuted thread before resolving it —
  it has no commit to point at
- ALWAYS post ONE re-review request after the push — a general comment
  @-mentioning the reviewer, the round's most important fix in ~4 words from
  the `distill` skill; NEVER compose that phrase yourself, NEVER a per-thread
  "fixed" reply
- NEVER confuse a thread's GraphQL `id` (resolve) with a comment's REST `databaseId` (reply) — mixing them 404s
