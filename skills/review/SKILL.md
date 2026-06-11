---
name: review
description: Deep code review with discussion and GitHub posting. Reviews code by bucketing files into groups, applying orthogonal lenses, running parallel analysis agents, then presenting findings for discussion before optionally posting to a GitHub PR.
when_to_use: reviewing code changes, "review this", "review the branch", "review PR <N>"
user-invocable: true
---

# Review

Bucket → lenses → parallel agents → fable reverification → discuss → GitHub post.

## Input

- **files** — explicit list, or default to `git diff --name-only main..HEAD`
- **PR number** — optional; enables posting as a PR review

## Workflow

### 1. Gather scope

```bash
git diff --name-only main..HEAD 2>/dev/null || git diff --name-only HEAD~1..HEAD
```

PR head SHA for linking: `gh pr view <N> --json headRefOid,baseRefName,title,body`.

### 2. Bucket + lenses

Group files into ≤4 non-overlapping buckets by domain. Per bucket:
- List applicable skills by extension (`.rs`→rs, `.ts/.tsx`→ts/tsx, `tests/`→testing, `.go`→go, `.py`→py, `.sql`→sql, `.sh`→sh)
- Propose 3-5 orthogonal lenses from: correctness, simplicity, error handling, type safety, test coverage, security, performance, API contract

### 3. Parallel review agents

Per bucket, spawn `Agent(subagent_type="general-purpose", model="opus", run_in_background=true)` with prompt:

```
Lens: <lens-name>
Skills: <comma-separated skills>
Files: <list of absolute paths>
House rules: <relevant excerpts from project CLAUDE.md / WISDOM>

Report findings only, NO edits. Format each finding as:
- File:line — [Lens] Short description
  Why it matters
  Fix: (if non-obvious)
```

ALWAYS pass house rules so suggestions don't violate them.

ALWAYS wait for all agents before proceeding.

### 4. Fable deep-dive + reverification pass

Run a **single** `Agent(model="fable")` that does two things simultaneously:

1. **Independent deep review** — read the full diff and key changed files itself, hunting for:
   - Gross bugs (incorrect logic, wrong invariants, data loss, panic paths)
   - Regression risks (behavior changes not reflected in tests, broken API contracts)
   - Things sonnet-tier agents are likely to miss or hallucinate fixes for
   Do NOT rely on the sonnet findings for this — approach fresh.

2. **Reverification of sonnet findings** — for each sonnet finding, decide:
   - KEEP — real problem, clear impact, in changed code, non-obvious to the author
   - DROP — false positive, style nit, out-of-scope, or a suggested fix that is wrong/worse

Prompt structure:
```
You are doing a deep adversarial code review. You have two jobs:

**Job 1 — Independent deep review**
Read the full diff and key files. Find gross bugs, regression risks, and invariant violations
that a fast reviewer would miss. Focus on: [domain-specific invariants from PR description].
Format: FILE:LINE — [Type] Title / Problem / Fix

**Job 2 — Sonnet findings reverification**
For each finding below, answer KEEP or DROP with one-line justification.
Only KEEP findings that are: real, clearly impactful, in changed code, non-obvious.
Sonnet findings:
<paste all findings>

PR description:
<paste PR description>

House rules:
<relevant CLAUDE.md excerpts>
```

Output is: fable's own findings + KEEP list from sonnet. Merge both into the final pool.

ALWAYS run this pass. ALWAYS trust fable's DROP judgements over sonnet's findings.

### 5. Per-hunk minimality pass

Walk every hunk in `git diff <base>..HEAD`. Flag any that don't serve the stated goal:
- Renames with no behavior change
- Reflow of untouched lines
- Refactors bundled with an unrelated fix
- Whitespace churn
- Premature abstractions

ALWAYS prefer less diff for the same outcome — unless quality or aim suffers.

### 5. Triage

Drop findings that:
- add abstractions or new patterns
- target code outside the changed lines (grep to verify)
- are style/formatting (CI catches these)
- can't be verified by reading the files

ALWAYS verify each suggested fix by reading the surrounding code — agents propose plausible-looking fixes that don't actually work (wrong shell idioms, broken regexes). NEVER forward an unverified fix.

### 6. Present report

```markdown
## Review: <scope>

### Critical
- ...

### Important
- ...

### Minor
- ...

### No issues in
- Bucket X: <reason>
```

Then log every triaged finding that was not fixed to `BUGS.md` at repo root
(per the Bug Triage Protocol) — do this immediately, NEVER ask permission
to record. Then stop. Wait for user discussion before offering to post.

### 7. Post to GitHub (on user request)

Trigger: "post", "upload", "comment on PR", or similar. If no PR number, `gh pr list` and ask which PR.

Default to one PR review body via `gh pr review <N> --comment --body "$(cat <<'EOF' ... EOF)"`. For inline comments on specific lines, use the gh-comment skill.

## Tiered model use

- **Standalone PR review** — use `model="opus"` for all agents (step 3). High quality, no cost
  pressure.
- **Flag pass for refine** — caller passes `model="sonnet"` to step-3 agents. Cheap, high-recall
  flagging only. Opus verify+fix is handled by the subsequent `improve` call.

ALWAYS respect the model the caller specifies. NEVER upgrade to Opus silently when Sonnet was
requested.

## Rules

- NEVER make code edits — read-only analysis only
- NEVER post to GitHub without explicit user confirmation
- ALWAYS log unfixed findings to BUGS.md without asking — only GitHub
  posting needs confirmation
- ALWAYS present the report first and wait for discussion before posting
- ALWAYS include `file:line` in every finding
