---
name: refine
description: Code refinement orchestrator. NOT for targeted fixes (use improve).
when_to_use: "finalizing a finished feature, refine this, polish this"
user-invocable: true
---

# Refine Skill

Orchestrates code refinement. Runs in main context for full conversation visibility.

`/refine` = make the code review-ready (quality refinement + resolve all open PR review threads +
update docs). `/release` = the final pre-release gate (stronger — version bumps etc.). Use `/refine`
first; `/release` after.

## Workflow

1. **Checkpoint** - if uncommitted changes, invoke `Skill(commit, "chore: checkpoint before refine")`
2. **Validate** - run build/test, fix failures
2b. **Language lenses** - map the target files to their language/domain skills (`.rs`→`rs`, `.tsx`→`tsx`, `programs/**`→`solana`) PLUS every skill those require (`tsx` requires `ts`). ALWAYS explore this skill's own directory for the matching lens files and read every one that exists — `<skill>.md` next to this SKILL.md (e.g. `tsx.md`, `ts.md`). List the directory; never assume which exist. Absent file → skip that language silently and fall back to its own `SKILL.md` (plus any review sibling it names, e.g. `solana/review.md`). If a lens file names a validation gate the project's build/test does not cover, run it now and fix failures before continuing. ALWAYS also `Skill(<matched skill>)` for every language/domain skill matched here (e.g. `rs`, `ts`) BEFORE step 4's review — the lens file is a hunting rubric, but the skill's own cold rules (code-style baseline, comment policy, testing conventions) must be loaded into context too, not just referenced by name, or the review has nothing to enforce them against.
2c. **PR review intake** - detect the open PR for the current work (`gh pr list`/`gh pr view`; auth via `GH_TOKEN` env var; a detached-HEAD worktree has no local branch, so find the PR by the pushed branch or head SHA, not by local branch name). No PR found → skip this step silently. Fetch UNRESOLVED review threads via `gh api graphql` (`repository.pullRequest.reviewThreads`), capturing each thread's node `id`, `isResolved`, and first comment's path/line/author/body. Triage each comment **FIX vs WON'T-FIX**, grounding every decision against the live WISDOM: the project `CLAUDE.md` "Design invariants (not bugs)" section (or equivalent) and `BUGS.md` — a flagged item matching a documented invariant or a by-design entry is WON'T-FIX. Working assumption: automated-reviewer (e.g. CodeRabbit) findings skew false-positive here — verify each premise against the actual code before believing it, never take the comment's claim at face value. Out-of-scope core-logic changes are flagged, not applied. Carry the triaged list (thread id, verdict, reason) forward — FIX items feed step 3's buckets, WON'T-FIX items feed step 7b.
3. **Bucket + lenses + skills** - group target files into ≤4 non-overlapping buckets, folding in any FIX items from 2c alongside the refinement targets. Per bucket: (a) list applicable skills by file extension and domain (e.g. .rs→rs, tests/→testing); (b) derive lenses from two sources — **language lenses** read in 2b AND **WISDOM lenses**: read the live WISDOM (global + project `CLAUDE.md` plus the loaded `SKILL.md` files) and enumerate EVERY thematic rule it currently states — not a sampled subset. At minimum this means one lens each for: minimality/grug, orthogonality, fail-loud-and-surface-to-user, retry-only-transient-errors, no-duplication/amend-the-original (grep for an existing mechanism before adding a parallel one), one-renderer-many-sinks, strict-not-magical, naming, comments-policy (only shocking/non-obvious; delete echo/label comments), testing, and docs — PLUS any further themes the live WISDOM holds beyond this list. Never trim to a subset for convenience; the list above is a floor, not a ceiling, and it is still derived from the LIVE text each run, NEVER a frozen checklist — a theme absent from the live WISDOM is skipped, one newly added is picked up. Tag each lens `simplify` (reuse / dead-code / minimization) or `correctness` (bugs, logic errors, edge cases), and scale the lens count to the diff (see Rules) — full enumeration of themes and scaling the number of lenses/sub-agents to diff size are independent: a small diff still gets checked against every relevant theme, just via fewer, broader-scoped subs (see Rules) rather than skipping themes.
4. **Review** - parallel read-only `Task(agent="improve", model=<by tag>)`, **1-3 lenses per sub, never more** (a focused rubric beats a groupthink dump). Prompt: "Lenses: <1-3, each with the exact WISDOM excerpt or language-lens rule it checks>. Read: <absolute path of the `<skill>.md` lens file any lens came from, so the sub gets it verbatim>. Skills: <list>. Files: <bucket>. Report violations only, NO edits."
4b. **Triage findings as they return** - drop findings that (a) add abstractions, (b) target unused code (grep first), (c) conflict with the original Intent, (d) can't be verified against the codebase. A survivor that needs a redesign (new contract, changed control flow, cross-cutting) → record in `BUGS.md` as `proposed` (CLAUDE.md System-change discipline), NOT applied without sign-off. Only inline-simple survivors go to Apply.
5. **Apply** - serial Task(agent="improve") per bucket. Run build/test between buckets — abort bucket on failure. Prompt: "Skills: <list>. Findings: <aggregated>. Apply only if simpler. Reject abstractions and cleverness. ALSO enforce, explicitly, whichever of these the findings or the touched code implicate: comments-policy (delete echo/label comments; keep only shocking/non-obvious ones), amend-don't-duplicate (grep for an existing mechanism before adding a parallel one; extend/fix the original instead), fail-loud-to-user (a user-facing error must surface — thrown/returned/delivered — never swallowed or only logged), and retry-only-transient (retries limited to network/remote calls and DB busy/locked; everything else — misconfig, missing data, programming errors — throws immediately, no retry/fallback/best-effort)."
6. **Document** - spawn `Task(agent="readme")`. Non-optional: the readme agent MUST reflect the actual changes (new endpoints, flags, migrations, config, behavior) in the relevant `README.md`/`ARCHITECTURE.md`/docs, not just be spawned as a formality. List exactly what changed (file + one-line each, per the Prompt Structure below) so it has something concrete to reconcile against, not "go check for drift."
7. **Verify** - final build/test
7b. **Resolve PR threads** - for each 2c FIX thread whose fix landed in step 5/7: reply via `gh api graphql` `addPullRequestReviewThreadReply(input:{pullRequestReviewThreadId, body})` citing the commit SHA + what changed, then `resolveReviewThread(input:{threadId})`. For each WON'T-FIX thread: reply with the concrete reason (the invariant/BUGS.md entry it matches, or the design rationale), then resolve. Auth via `GH_TOKEN`. Show the reply text before posting — same approval discipline as the `/gh-comment` gate, never post blind. Resolve ONLY threads actually addressed this pass; leave anything else open. HARD rules: NEVER `git push`; NEVER `gh pr merge`, `gh pr review`, or `gh pr create` — this step only replies to and resolves existing threads.
8. **Commit** - if changes, invoke `Skill(commit, "refa: apply refinements")`
9. **Cleanup** - remove stale agent worktrees (detached — no branch to delete):
   ```bash
   for d in .claude/worktrees/*/; do
     git worktree remove "$d" --force
   done
   ```
10. **Summary** - what changed, main impact, no fluff, not marketing

## Prompt Structure

```
Intent: [user's original request, not summary]
Primary: [files to modify]
Context: [read-only reference, if needed]
```

For readme agent: list what changed (file + one-line each).

## Rules

- critique/review/planning/creative second opinions → `oracle`.
- NEVER do improvement work yourself - delegate to improve agent
- NEVER summarize user intent - pass original request
- Explicit scope > vague "review these files"
- ALWAYS scale the review to the diff: a few files / tens of lines / one logical change → 1-2 lenses or an inline review in main context; NEVER fan out 3-5 agents over a ~40-line diff. Full bucket × lens fan-out is for large or risky work only.
- ALWAYS set the review `model=` by lens tag: `simplify` → sonnet, `correctness` → opus. NEVER hunt bugs on sonnet; NEVER burn opus on candidate-finding. (improve pins no model — the call site controls it.)
- ALWAYS run all steps; NEVER skip commit unless no file changes
- Language lens files live at `<skill>.md` in this skill's directory, named for the skill matched in 2b — ALWAYS list that directory in 2b rather than guessing which languages are covered. One lens per `##` heading, each heading ending in its own tag — simplify or correctness — so step 4 can set `model=` without re-reading the code. To cover a new language, add the file — there is nothing else to register. NEVER copy write-time rules from a language skill into its lens file; a lens file carries only what a refine pass must go hunting for.
