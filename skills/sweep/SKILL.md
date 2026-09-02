---
name: sweep
description: Find a class of problem across a codebase, then optionally fix it. Record-only by default (CLAUDE.md Bug Triage Protocol) — filing each real instance in BUGS.md; the Fix and Verify phases run only when the owner asks for them. NOT for a single known bug (use /bugs), NOT for a targeted one-file change (use /improve), NOT for foreground/inline audits (use /dispatch directly).
when_to_use: "sweep for similar problems, find more like this across the codebase, are there other instances of this bug class, audit the whole repo for X pattern, fix all bugs, close all gaps, parity sweep, audit X and fix it"
user-invocable: true
---

# Sweep → (Fix) → Verify

One workflow, three phases, hard sequencing. **Phase 1 always runs. Phases 2
and 3 run only when the owner has asked for changes** — a sweep that fixes what
it finds violates the Bug Triage Protocol, which exists so the owner
prioritises rather than the sweep.

## Phase 1 — Sweep (read-only, parallel OK)

Spawn read-only subs (Sonnet/Explore) to FIND issues. Group by concern; each
sub owns one concern-bucket. Parallel is safe here — no shared writes.

Output: a bucketed issue list with file + line citations. Do NOT fix during
sweep — you will miss scope and interleave reads with writes.

### Record-only mode, which is the default

Launch (Agent tool, `run_in_background: true`, general-purpose, no waiting — same
launch shape as `/dispatch`) a background agent that audits the **entire**
codebase for one problem CATEGORY and files each real instance as its own
`BUGS.md` entry, per `/bugs`'s format/ID rules (read that skill first — sweep
is the search, not the file mechanics). Record only — never fix what it finds
(CLAUDE.md Bug Triage Protocol).

#### Category

- `/sweep <description>` — audit for exactly that pattern, repo-wide.
- `/sweep` with no argument — read the most recent `BUGS.md` "✅ FIXED"/
  "Resolved" entries and the latest `.diary/` entry to find the pattern class
  of what was just fixed, then sweep for other instances of that same class
  that the original fix didn't touch.

#### Coordination

Dispatch prompt must tell the agent to check `git status` first — if unrelated
uncommitted work is present (another agent active), stay read-only until the
final `BUGS.md` write.

Report back the entries filed (IDs + one-line titles), nothing else.

## Verify a finding before you fix it

A finding is a claim, not a fact — this applies to commissioned adversarial
audits (hostile reviewer, CEO/CTO persona, "prove this is useless") as much
as ordinary sweep subs, and sharper personas need MORE independent
verification, not less. Two failure modes, both caught the same way:
re-derive from source instead of re-reading the claim.

- **A false finding.** Reproduce it yourself — grep, re-run, recompute —
  before scheduling a fix.
- **A true finding stated backwards.** A claim like "this ratio reads
  inverted" or "the number is too high" can itself have the direction wrong.
  Re-derive the raw comparison (which side is baseline, which is the value
  under test) instead of accepting the sub's framing of it. Taking a
  backwards claim at face value can flip a correct result into its opposite
  — worse than ignoring the finding entirely.

When two adversarial subs disagree on a finding, a third check that MEASURES
rather than asserts settles it, not a re-read of either sub's prose.

Findings that check out get fixed (Phase 2) or, if fixing them is a
redesign, filed to `BUGS.md` as a proposal needing owner sign-off (CLAUDE.md
Bug Triage Protocol). Findings that don't check out get reported as dropped,
with the reason — silence about a rejected finding reads as it having been
missed rather than checked.

## Phase 2 — Fix (sequential, one concern per sub)

Spawn one opus sub per concern. Hard rules:

- **One concern per sub** — authz scope is not migrate enumeration is not
  dispatch lifecycle. If a "fix" spans concerns, split it.
- **Sequential on the shared tree** — NEVER run two code-editing subs in
  parallel on the same checkout. They interleave: one reverts the other's
  edits, mid-flight commits, half-edited files. Parallel is ONLY safe with
  isolated worktrees (Agent `isolation: "worktree"`).
- **Include tests** — every new param, response field, MCP tool, REST
  endpoint, or behavior change gets a test IN THE SAME SUB, not a
  follow-up. Security-sensitive changes (authz, scoping, secrets) need
  explicit isolation/cross-tenant tests. A sub that ships behavior without
  tests is not done.
- **Partial commits are broken commits** — a test file committed without
  its impl (or vice versa) leaves HEAD broken. Verify the sub committed both.

## Phase 3 — Verify the artifact, not the report

NEVER trust a sub's "all green" claim. After each sub:

```bash
make build 2>&1 | tee ./tmp/build.log && tail -5 ./tmp/build.log
make test  2>&1 | tee ./tmp/test.log  && tail -8 ./tmp/test.log && grep -E "FAIL|---" ./tmp/test.log
git diff --name-only HEAD~1
```

Check the diff yourself. If the sub claimed it added function `Foo` — grep
for it. Agent success reports are not evidence; the diff is.

## Commit discipline

After verifying each sub's output:

1. `git diff --name-only` — take the FULL list, no tail.
2. Stage an explicit file list — never `git add -A` or `git add -a`.
3. One commit per concern. Format: `[section] message`.
4. Never amend, never squash, never push.
5. Watch for parallel hazard: if another session is editing the shared
   tree (user mid-edit, another sub in flight), scope your `git add` to
   YOUR files only. Verify `git diff --cached` before committing.

## Worktree reconciliation

Full isolation + reconciliation rules: `Skill(worktree)`.

When a sub ran with `isolation: "worktree"`, bring its work back with:

```bash
git diff <fork-base> <sub-tip> -- <sub-owned-files> | git apply --3way
```

Do NOT `git cherry-pick` — on linked worktrees it silently empties and
slips HEAD. See `[[worktree_reconcile]]` memory for the full recipe.

## Hard rules (non-negotiable)

- NEVER trust a sub's "build passes" or "tests green" — run it yourself.
- NEVER fix a finding without reproducing it — an adversarial sub's claim
  can be wrong outright, or right but stated backwards.
- NEVER run overlapping code-editing subs on the shared tree.
- NEVER commit a behavior change without its test.
- NEVER use `git add -A` or amend/squash.
- NEVER conflate multiple concerns in one sub or one commit.

## Failure modes this prevents

| Failure | Rule violated |
|---------|--------------|
| Sub commits test without impl → broken HEAD | partial-commit check |
| dashd auth guard committed without tests, security hole ships silently | ship-with-tests |
| cherry-pick on worktree branch empties commit, HEAD slips | worktree-reconcile |
| Two subs edit same file, one reverts the other | sequential-on-shared-tree |
| Sub says "green", build actually broken | verify-the-artifact |
| Parallel session's uncommitted edit captured by `git add -A` | explicit-file-list |
| Audit finding accepted on its framing, direction was inverted | verify-a-finding-before-you-fix-it |

Real incidents (arizuko, 2026-05-28 to 2026-06-05):
- dashd auth guard scaffolded but NEVER applied to routes — existed unwired
  for weeks; only caught by a full route audit, not by the original commit.
- cherry-pick on worktree branches dropped reconciled bucket work off HEAD
  twice in one session; required `git reflog` recovery both times.
- Rebuilding krons image without SECRETS_KEY in .env crash-looped gated;
  a "deployed successfully" sub report masked the actual state until the
  502s were noticed.

Real incidents (turbocharge, 2026-08-15 to 2026-08-19):
- A commissioned CTO audit reported that a fix's ratio "reads backwards";
  re-deriving which side of the pair was baseline showed the number was
  right and only the prose sentence had the direction inverted — fixing the
  claim as stated would have flipped a correct warning into an endorsement.
- Two independent art-director subs disputed a font-fallback finding; settled
  by measuring rendered ink-width in pixels against each candidate font's
  known advance width, not by picking a side.