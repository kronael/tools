---
name: gh-issue
description: Assemble and file a GitHub issue on a repo, with a mandatory approval gate — never posts without showing the exact title+body first. Derived from gh-comment.
when_to_use: "filing a bug report or issue on a GitHub repo, often a different repo than the current one (e.g. an upstream dependency), file an issue, open an issue, report a bug upstream"
user-invocable: true
---

# gh-issue

Assemble a terse, actionable issue and file it — but ALWAYS show the exact
content and get explicit approval BEFORE posting. Mirrors gh-comment's sign-off
gate.

## 1. Target repo

The issue often targets a DIFFERENT repo than the cwd (e.g. an upstream). Take
the `owner/repo` explicitly; never assume the current repo.

```bash
# current repo (only if the issue is about THIS project)
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
# otherwise the user names it, e.g. REPO=marinade-finance/waypoint
```

If unsure which repo, ASK — do not guess a slug.

## 2. Draft (terse, to the point)

- **Title**: `Short imperative sentence` describing the defect (no type prefix).
- **Body**: lead with the symptom, then a minimal repro, then expected vs actual.
  Follow the `writing` skill rules — no preamble, no padding, no "This issue…".
  Include a copy-pasteable repro (curl/command) when there is one. Keep it to
  what a maintainer needs to act; cut everything else.
- Prefer real evidence (status codes, exact response bodies, versions) over prose.

## 3. Sign-off gate (MANDATORY)

ALWAYS present the exact title + body to the user before posting. In Claude Code
use `AskUserQuestion`; elsewhere paste it in chat. NEVER run `gh issue create`
until the user explicitly approves the content and the target repo. Editing the
draft is expected — re-show after edits.

## 4. Post (only after approval)

```bash
gh issue create --repo "$REPO" \
  --title "<title>" \
  --body "$(cat <<'EOF'
<body>
EOF
)" \
  --label "<label>"   # optional; omit if unsure
```

Return the issue URL that `gh issue create` prints.

- Labels: only pass `--label` for labels that exist (`gh label list --repo "$REPO"`);
  a non-existent label makes the command fail. Omit when unsure.
- If `gh` is unauthenticated (`gh auth status` fails), do NOT attempt to post.
  Show the approved title+body and the ready `gh issue create` command, and tell
  the user to `gh auth login` (or run it themselves). Suggest `! gh auth login`
  in Claude Code so its output lands in the session.

## Rules

- NEVER post without an explicit approval of the exact content AND repo.
- NEVER guess the repo slug — ask if not given.
- Keep it terse: shortest issue that a maintainer can act on wins.
- One issue per invocation; don't batch unrelated problems into one issue.
- Report facts (repro, status, body, version), not speculation about their code.
- This skill only FILES issues. It does not comment on PRs (use gh-comment) and
  NEVER touches `gh pr create/merge`, `gh release create`, or `git push`.
