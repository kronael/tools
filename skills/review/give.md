# Give — produce a review

Read-only: bucket → parallel lens agents → fable deep-dive + reverification →
minimality → triage → report. Supersedes the built-in `/code-review` locally.

## 1. Scope

Default = the local uncommitted diff (`git diff` + `git diff --staged`).
Override only when the user names files, a branch (`main...HEAD`), or a range.
Empty diff → say so and stop.

## 2. Bucket + lenses

Group files into ≤4 non-overlapping buckets by domain. Per bucket pick 3-5
orthogonal lenses: correctness, simplicity, error handling, type safety, test
coverage, security, performance, API contract, invariant/topology.

**Invariant/topology lens** — topology/multiplicity/scope changes (one process
split into many, a new scope-key on shared storage, a type gaining a collection
variant) read locally correct hunk-by-hunk while a structurally-guaranteed
property silently disappears. ALWAYS check for this shape.

## 3. Parallel lens agents

One `Agent(subagent_type="general-purpose", model="opus", run_in_background=true)`
per bucket. Give each its lens, files, the language skills for those
extensions, and the house rules from project CLAUDE.md — without them agents
propose fixes the project forbids. Findings only, no edits, each as
`file:line — [lens] what / why it matters / fix if non-obvious`.

ALWAYS wait for all agents before step 4.

## 4. Fable deep-dive + reverification

A single `Agent(model="fable")` doing both jobs at once:

1. **Fresh review** — read the diff and key files itself, hunting gross bugs,
   regression risks, and broken invariants. NEVER seed it with the sonnet
   findings for this job; it approaches cold.
2. **Reverify** — KEEP or DROP each sonnet finding with a one-line reason. KEEP
   only what is real, impactful, in changed code, and non-obvious to the author.

Feed it the change goal and house rules. Final pool = its findings + the KEEPs.
ALWAYS run this pass. ALWAYS trust its DROPs over the sonnet findings.

## 5. Minimality

Walk every hunk; flag any that don't serve the stated goal — behavior-free
renames, reflow of untouched lines, unrelated refactors, whitespace churn,
premature abstractions. ALWAYS prefer less diff for the same outcome, unless
quality or aim suffers.

## 6. Triage

Drop findings that add abstractions, target code outside the changed lines
(grep to confirm), are style/formatting (CI catches those), or can't be
verified by reading the files.

ALWAYS read the surrounding code to verify each suggested fix — agents propose
plausible fixes that don't work (wrong shell idioms, broken regexes). NEVER
forward an unverified fix.

## 7. Report

Critical / Important / Minor, each finding carrying `file:line` and a stable
`C1`/`I2`/`M3` id so triage, `take`, and PR replies can reference it. Name the
buckets that came back clean.

Then log every unfixed finding to `BUGS.md` immediately, without asking, and
record the round in the diary — one line. Then stop.

## Model tier

Standalone review → `model="opus"` for step 3. A `refine` flag pass → the
caller passes `model="sonnet"` (cheap high-recall flagging; the subsequent
`improve` call does opus verify+fix). ALWAYS respect the caller's model.

## GitHub PR (gh)

Same engine over `gh pr diff <N>` — `/review give gh [<N>]`. No args = current
branch.

```bash
gh pr view --json number,headRefOid,baseRefName,title,body
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
gh api repos/$REPO/pulls/<N>/comments --paginate   # inline comments
```

Head SHA anchors inline comments; title/body is the change goal for fable's
job 1. ALWAYS read existing comments and DROP anything already raised — never
re-litigate a resolved thread.

Present the report and WAIT. On "post", hand the survivors to `gh-comment`,
which owns the gate, batching, out-of-diff fallback, and 🤖 markers. A whole-PR
summary body gets a bare 🤖 prepended when most of the PR was auto-generated
(ask if unsure), and a bare 🤖 appended.
