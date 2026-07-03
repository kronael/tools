# Give — produce a review

The review engine (read-only; never edits code): bucket → lenses → parallel
agents → fable deep-dive + reverification → per-hunk minimality → triage →
report. Local diff by default; the GitHub-PR wrapper is the last section.
Supersedes the built-in `/code-review` for local work.

## Target

Default = the **local uncommitted working diff** (`git diff` plus
`git diff --staged`). Override only when the user names something:

- **files** — an explicit list they give
- **a branch** — "review the branch" → `git diff main...HEAD`
- **a commit range** — e.g. `abc123..def456`

`review` STOPS at the report — it never fetches from or posts to GitHub. For a
GitHub PR use the `gh-review` skill.

## Workflow

### 1. Gather scope

```bash
# default: local uncommitted work
git diff --name-only; git diff --staged --name-only
# branch: git diff --name-only main...HEAD
# range:  git diff --name-only <base>..<head>
```

If the diff is empty, say so and stop — nothing to review.

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
that a fast reviewer would miss. Focus on: [domain-specific invariants from the change goal].
Format: FILE:LINE — [Type] Title / Problem / Fix

**Job 2 — Sonnet findings reverification**
For each finding below, answer KEEP or DROP with one-line justification.
Only KEEP findings that are: real, clearly impactful, in changed code, non-obvious.
Sonnet findings:
<paste all findings>

Change goal / context:
<what the diff is meant to do>

House rules:
<relevant CLAUDE.md excerpts>
```

Output is: fable's own findings + KEEP list from sonnet. Merge both into the final pool.

ALWAYS run this pass. ALWAYS trust fable's DROP judgements over sonnet's findings.

### 5. Per-hunk minimality pass

Walk every hunk in the diff. Flag any that don't serve the stated goal:
- Renames with no behavior change
- Reflow of untouched lines
- Refactors bundled with an unrelated fix
- Whitespace churn
- Premature abstractions

ALWAYS prefer less diff for the same outcome — unless quality or aim suffers.

### 6. Triage

Drop findings that:
- add abstractions or new patterns
- target code outside the changed lines (grep to verify)
- are style/formatting (CI catches these)
- can't be verified by reading the files

ALWAYS verify each suggested fix by reading the surrounding code — agents propose plausible-looking fixes that don't actually work (wrong shell idioms, broken regexes). NEVER forward an unverified fix.

### 7. Present report

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
to record. Then stop.

## Tiered model use

- **Standalone review** — use `model="opus"` for all agents (step 3). High quality, no cost
  pressure.
- **Flag pass for refine** — caller passes `model="sonnet"` to step-3 agents. Cheap, high-recall
  flagging only. Opus verify+fix is handled by the subsequent `improve` call.

ALWAYS respect the model the caller specifies. NEVER upgrade to Opus silently when Sonnet was
requested.

## Rules

- NEVER make code edits — read-only analysis only
- ALWAYS log unfixed findings to BUGS.md without asking
- ALWAYS present the report and then stop
- ALWAYS include `file:line` in every finding

## GitHub PR (gh)

Same engine, over a PR instead of the local diff — `/review give gh [<N>]`.

### 1. Resolve + fetch

```bash
gh pr view --json number,headRefOid,baseRefName,title,body   # no args = current branch
gh pr diff <N>                                                # diff to review
gh pr view <N> --json comments                               # issue/general comments
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
gh api repos/$REPO/pulls/<N>/comments --paginate             # inline review comments
```

Capture the head SHA (inline anchoring) and title/body (feed as the change goal
into fable's Job 1). ALWAYS read existing comments and DROP any finding that
repeats a point already raised — never re-litigate resolved threads.

### 2. Review, present, post

Run the engine above (bucket → … → triage) on the PR diff. Present the report
and wait. When the user says post, hand the surviving findings to the
`gh-comment` skill — it owns the approval gate, pending-review clearing, batch
inline comments, the general-comment fallback for lines outside the diff, and
the 🤖 markers. Prepend a bare 🤖 to a whole-PR summary body when most of the PR
was auto-generated (ask if unsure, or when told to "robothead it"); append a
bare 🤖 at the end.

- NEVER post directly — ALWAYS route through `gh-comment` and its gate.
- NEVER `gh pr create`, `gh pr merge`, `gh pr review --approve`, or `git push`.
