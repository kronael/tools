---
name: refine
description: Code refinement orchestrator. NOT for a targeted fix (use improve) or a second opinion (use oracle).
when_to_use: "refine this, polish this, refine the changes, final pass before shipping, tighten this before commit, clean up the diff, finalize a finished feature"
user-invocable: true
---

# Refine Skill

Runs in main context so the whole conversation stays visible.

## Workflow

1. **Checkpoint** — uncommitted changes → `Skill(commit, "chore: checkpoint before refine")`.
   → `git status --porcelain` is empty.
2. **Validate** — build and test; fix failures before reviewing anything.
   → the project's test target exits 0 in this turn.
3. **Bucket and lens** — ≤4 non-overlapping buckets. Per bucket, list the skills
   that apply by extension and domain, then derive lenses: code-quality ones
   from the file types, WISDOM ones by splitting the live WISDOM into thematic
   chunks, one chunk per lens. ALWAYS derive from the live text, NEVER a frozen
   checklist. ALWAYS seed the correctness lenses from **Confessed defaults**.
   Tag each lens `simplify` or `correctness`.
   → every bucket carries 1-3 tagged lenses and no file appears in two buckets.
4. **Review** — parallel read-only `Task(agent="improve", model=<by tag>)`.
   Prompt: "Lenses: <each with the exact excerpt it checks>. Skills: <list>.
   Files: <bucket>. Report violations only, NO edits."
   → every bucket has returned.
5. **Triage** — DROP a finding that adds an abstraction, targets unused code
   (grep first), conflicts with the Intent, or cannot be verified against the
   codebase. A survivor needing a redesign goes to `BUGS.md` as `proposed`;
   NEVER apply one without sign-off.
   → every surviving finding is a single inline edit.
6. **Apply** — serial `Task(agent="improve")` per bucket. Prompt: "Skills:
   <list>. Findings: <aggregated>. Apply only if simpler. Reject abstractions
   and cleverness." Abort the bucket on a failure.
   → build and test pass after each bucket.
7. **Document** — `Task(agent="readme")` with what changed, one line per file.
   → docs name every changed behaviour.
8. **Verify and commit** — final build and test, then `Skill(commit, "refa:
   apply refinements")` when files changed.
   → tests pass in this turn and the tree is clean.
9. **Clean up** — `git worktree remove --force` each stale Claude-managed
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
