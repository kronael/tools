---
name: review
description: Deep code review with discussion and GitHub posting. Reviews code by bucketing files into groups, applying orthogonal lenses, running parallel analysis agents, then presenting findings for discussion before optionally posting to a GitHub PR.
when_to_use: reviewing code changes, "review this", "review the branch", "review PR <N>"
user-invocable: true
---

# Review Skill

Deep code review: bucket → lenses → parallel agents → discuss → GitHub post.

## Input

Accept as args or infer from context:
- **files** — explicit list, or default to `git diff --name-only main..HEAD`
- **PR number** — optional; if given, findings can be posted as a PR review

## Workflow

### 1. Gather scope

If no files specified:
```bash
git diff --name-only main..HEAD 2>/dev/null || git diff --name-only HEAD~1..HEAD
```

If a PR number is given, get its head SHA for linking:
```bash
gh pr view <N> --json headRefOid,baseRefName,title,body
```

### 2. Bucket + lenses

Group files into ≤4 non-overlapping buckets by domain. Per bucket:
- List applicable skills by file extension (`.rs`→rs, `.ts/.tsx`→ts/tsx, `tests/`→testing, `.go`→go, `.py`→py, `.sql`→sql, `.sh`→sh)
- Propose 3-5 orthogonal lenses from: correctness, simplicity, error handling, type safety, test coverage, security, performance, API contract

### 3. Parallel review agents

For each bucket, spawn `Task(subagent_type="improve", run_in_background=true)`:

```
Lens: <lens-name>
Skills: <comma-separated skills>
Files: <list of absolute paths>
House rules: <relevant excerpts from project CLAUDE.md / WISDOM — e.g. "no comments unless behavior is shocking", "no premature abstraction">

Report findings only, NO edits. Format each finding as:
- File:line — [Lens] Short description
  Why it matters
  Fix: (if non-obvious)
```

`improve` is repurposed for read-only here — the `NO edits` line is the contract; restate it. Always pass house rules so the agent doesn't suggest changes that violate them.

Wait for all agents to complete before proceeding.

### 4. Per-hunk minimality pass

Walk every hunk in `git diff <base>..HEAD`. Flag those that don't serve the stated goal:
- Renames with no behavior change
- Reflow of lines the change didn't need to touch
- Refactors bundled with an unrelated fix
- Whitespace churn
- Premature abstractions

ALWAYS prefer less diff for the same outcome — unless quality or aim suffers.

### 5. Triage

Drop findings that:
- (a) add abstractions or new patterns
- (b) target code outside the changed lines (grep to verify)
- (c) are style/formatting (CI catches these)
- (d) can't be verified by reading the files

ALWAYS verify each suggested fix by reading the surrounding code — agents propose plausible-looking fixes that don't actually work (wrong shell idioms, broken regexes). NEVER forward an unverified fix to the apply step.

### 6. Present report

Output the consolidated findings in this format:

```markdown
## Review: <scope description>

### Critical
- ...

### Important
- ...

### Minor
- ...

### No issues in
- Bucket X: <reason>
```

Then stop and wait. Let the user ask questions, push back, or ask for clarification on any finding.

### 7. Post to GitHub (on user request)

When the user says "post", "upload", "comment on PR", or similar:

If no PR number was provided, run `gh pr list` and ask which PR.

Post as a PR review body (not individual inline comments unless user asks):
```bash
gh pr review <N> --comment --body "$(cat <<'EOF'
## Code Review

<findings in markdown>

---
*Posted via /review skill*
EOF
)"
```

For inline comments on specific lines, use:
```bash
gh api repos/:owner/:repo/pulls/<N>/comments \
  --method POST \
  --field body="<comment>" \
  --field commit_id="<head-sha>" \
  --field path="<file>" \
  --field line=<line>
```

Get the repo from:
```bash
gh repo view --json nameWithOwner --jq .nameWithOwner
```

## Rules

- NEVER make code edits — read-only analysis only
- NEVER post to GitHub without explicit user confirmation
- Present report first, always wait for user discussion before offering to post
- Inline comments require `--field side=RIGHT` for added lines
- Always include the file:line reference in every finding
