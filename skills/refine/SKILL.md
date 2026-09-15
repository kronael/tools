---
name: refine
description: Code refinement orchestrator. NOT for a targeted fix (use improve) or a second opinion (use oracle).
when_to_use: "refine this, polish this, refine the changes, final pass before shipping, tighten this before commit, clean up the diff, finalize a finished feature"
user-invocable: true
---

# Refine Skill

Runs in main context so the whole conversation stays visible.

`/refine` = make the code review-ready (quality refinement + resolve all open PR review threads +
update docs). `/release` = the final pre-release gate (stronger — version bumps etc.). Use `/refine`
first; `/release` after.

## Workflow

1. **Checkpoint** — uncommitted changes → `Skill(commit, "chore: checkpoint before refine")`.
   → `git status --porcelain` is empty.
2. **Validate** — build and test; fix failures before reviewing anything.
   → the project's test target exits 0 in this turn.
3. **Language lenses** — map the target files to their language/domain skills
   (`.rs`→`rs`, `.tsx`→`tsx`, `programs/**`→`solana`) plus every skill those
   require (`tsx` requires `ts`). ALWAYS list this skill's own directory and
   read each `<skill>.md` lens that exists; NEVER assume which do. An absent
   lens falls back to that skill's own `SKILL.md` and any review sibling it
   names. ALWAYS also `Skill(<matched skill>)` so its cold rules — style
   baseline, comment policy, testing conventions — are in context, not just
   named. A validation gate a lens names that build/test misses runs now.
   → every matched skill is loaded and its lens read or confirmed absent.
4. **PR review intake** — find the open PR for this work (`gh pr list`/`view`,
   auth via `GH_TOKEN`; a detached worktree has no local branch, so match by
   pushed branch or head SHA). None → skip silently. Fetch UNRESOLVED threads
   via `gh api graphql` (`repository.pullRequest.reviewThreads`), keeping each
   thread `id`, path, line, author and body. Triage each FIX or WON'T-FIX
   against the live WISDOM, the project `CLAUDE.md` design invariants and
   `BUGS.md` — a documented invariant or by-design entry is WON'T-FIX.
   Automated-reviewer findings skew false-positive: ALWAYS verify the premise
   against the code, NEVER take the claim at face value. An out-of-scope
   core-logic change is flagged, never applied.
   → every unresolved thread carries a verdict and a reason.
5. **Bucket and lens** — ≤4 non-overlapping buckets, folding in the step 4 FIX
   items. Per bucket, list the skills that apply by extension and domain, then
   derive lenses: code-quality ones from the file types and the step 3 lenses,
   WISDOM ones by splitting the live WISDOM into thematic chunks, one chunk per
   lens. ALWAYS derive from the live text, NEVER a frozen checklist. ALWAYS
   seed the correctness lenses from **Confessed defaults**. Tag each lens
   `simplify` or `correctness`.
   → every bucket carries 1-3 tagged lenses and no file appears in two buckets.
6. **Review** — parallel read-only `Task(agent="improve", model=<by tag>)`.
   Prompt: "Lenses: <each with the exact excerpt it checks>. Read: <absolute
   path of any lens file a lens came from>. Skills: <list>. Files: <bucket>.
   Report violations only, NO edits."
   → every bucket has returned.
7. **Triage** — DROP a finding that adds an abstraction, targets unused code
   (grep first), conflicts with the Intent, or cannot be verified against the
   codebase. A survivor needing a redesign goes to `BUGS.md` as `proposed`;
   NEVER apply one without sign-off.
   → every surviving finding is a single inline edit.
8. **Apply** — serial `Task(agent="improve")` per bucket. Prompt: "Skills:
   <list>. Findings: <aggregated>. Apply only if simpler. Reject abstractions
   and cleverness." Abort the bucket on a failure.
   → build and test pass after each bucket.
9. **Document** — `Task(agent="readme")` with what changed, one line per file.
   Non-optional: refining a feature includes its docs. The agent reconciles
   `README.md` — and `ARCHITECTURE.md`/`CLAUDE.md` where the project keeps them
   — against what the code now does, and fixes what drifted.
   → docs name every changed behaviour.
10. **Verify and commit** — final build and test, then `Skill(commit, "refa:
    apply refinements")` when files changed.
    → tests pass in this turn and the tree is clean.
11. **Resolve PR threads** — for each step 4 FIX thread whose fix landed: reply
    via `gh api graphql` `addPullRequestReviewThreadReply` citing the commit
    SHA and what changed, then `resolveReviewThread`. For each WON'T-FIX: reply
    with the invariant or `BUGS.md` entry it matches, then resolve. ALWAYS show
    the reply text before posting — the `/gh-comment` gate, NEVER post blind.
    Resolve ONLY threads addressed this pass. NEVER `git push`; NEVER `gh pr
    merge`, `gh pr review` or `gh pr create`.
    → every triaged thread is replied to and resolved, and no other thread is.
12. **Clean up** — `git worktree remove --force` each stale Claude-managed
    worktree under `.claude/worktrees/`; NEVER touch a worktree elsewhere.
    → `git worktree list` shows only the main tree.

Pass the agent `Intent:` (the user's original words), `Primary:` (files to
modify) and `Context:` (read-only reference) — NEVER a summary of the request.

## Confessed defaults — hunt these first

Asked in isolation, models name these as their own defaults while being able to
recite the rule against each. Knowing a rule and following it differ; this is
where the gap shows.

- **Errors** — a broad catch that logs and continues; a fallback `None`/`[]`/`0`
  letting callers proceed on bad data; graceful degradation where crashing is
  cheaper than corrupted output; a guard on a path the caller already
  guarantees; a second logging or helper path because the first was never
  grepped for.
- **Scope** — adjacent code tidied unasked; the reported instance patched while
  sibling cases that fail the same way are left.
- **Tests** — mocks stacked until the test proves nothing; the assertion edited
  when a broken test is annoying; a guessed test command reported green.
- **Comments** — a comment above almost every block, half restating the code;
  docstrings added reflexively to a repo that has none; verbose names where the
  repo is terse.
- **Reporting** — done declared on a green run without exercising the path; a
  partial result softened into language that reads complete; a subagent's
  summary repeated without opening its diff.

## Review Checklist

- ALWAYS scale to the diff: tens of lines or one logical change → 1-2 lenses or
  an inline review; NEVER fan out agents over a ~40-line diff.
- ALWAYS set `model=` by tag: `simplify` → sonnet, `correctness` → opus. NEVER
  hunt bugs on sonnet; NEVER spend opus on candidate-finding.
- ALWAYS delegate the edit to the improve agent; NEVER do the improvement work
  in main context.
- ALWAYS route a critique, plan or creative second opinion to `oracle` instead.
- ALWAYS run every step; NEVER skip the commit unless no file changed.
- A language lens lives at `<skill>.md` in this directory, named for the skill
  step 3 matched — adding the file is the whole registration. One lens per `##`
  heading, each heading ending in its own tag so step 6 can set `model=`
  without re-reading the code. NEVER copy write-time rules from a language
  skill into its lens; a lens carries only what a refine pass goes hunting for.
