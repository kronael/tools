---
name: ship
description: Drive a spec-sized feature from plan to shipped — fable plans, sonnet implements step-by-step, refine polishes. NOT for one-off or <30min fixes (use improve), and NOT for tracking without driving execution (use TODO.md).
when_to_use: "ship this feature, spec this and build it, plan and implement, build this end to end, track this project, drive this to done"
user-invocable: true
---

# Ship

Plan → ship → refine, for work that warrants a spec (multi-file,
multi-session, or architecturally nontrivial). Not for a quick fix —
use `improve` for that.

## Folder layout

`.ship/NN-NAME/` — NN zero-padded sequential, NAME UPPERCASE-KEBAB.
Next NN: `ls .ship/ | grep -E '^[0-9]' | tail -1` + 1.
Plan lives at `.ship/NN-NAME/PLAN.md`.

**Check the project's CLAUDE.md for a `.ship/` policy override before
pruning** — default is gitignored/ephemeral (delete on close-out), but
some repos keep `.ship/` checked in as a build log. Don't force-delete
against an explicit override.

## Workflow

1. **Plan (fable)** — spawn one `fable` subagent (foreground) to
   research the codebase and produce `.ship/NN-NAME/PLAN.md`: a
   comprehensive spec — architecture, tradeoffs, gaps, and a
   step-by-step build order where **each step has a green-gate**
   (build/test/lint command that must pass before the next step).
   Fable does research and writes the plan only — it does not
   implement. See `prompt.md` for the planning brief template.
2. **Confirm** — read PLAN.md yourself, summarize it for the user in
   a few lines (steps + gates), and get a go-ahead before spending
   implementation budget. Skip this only if the user already approved
   the scope.
3. **Ship (sonnet)** — for each PLAN.md step in order: spawn one
   `sonnet` subagent to implement that step, then run the step's
   green-gate yourself. **Never take a sub's report at face value —
   check the diff.** One code-editing sub at a time on the shared
   tree; if a step is genuinely parallelizable, isolate each sub in
   its own `git worktree add --detach` and merge sequentially — never
   run overlapping edits on the same tree. See `prompt.md` for the
   implementation brief template.
4. **Refine** — once all steps are green, run the `refine` skill on
   the touched paths to finalize (dead code, minimization, polish).
5. **Close-out** — distill durable bits (decisions → `.diary/`,
   architecture → `specs/`, release notes → `CHANGELOG.md`) then
   prune `.ship/NN-NAME/` per the folder-layout note above.

## Guardrails (apply throughout, not just at close-out)

- **Detached HEAD only** — never create or attach a local branch, in
  the main tree or any worktree. Isolated work uses
  `git worktree add --detach <path> <ref>`.
- **Path-scoped commits**, conventional-commit format `type(scope): message`
  — never `git add -A`/`-A`-equivalents, never `--amend`, never push, never a
  `Co-Authored-By` trailer.
- **Green-gate every step** — use the project's real commands (e.g.
  `make check && make test && make lint`), not "looks right."
- **Subagent budget**: 1-2 subs typical, never more than 4 concurrent.
- **No external publishing** (crates.io/npm/PyPI/blog/push) unless the
  user explicitly asks — respect the project's publishing policy.

## PLAN.md shape (what fable writes)

```markdown
# NN — <feature name>

## Goal
<what and why, one paragraph>

## Architecture / tradeoffs
<key decisions, alternatives considered, why this one>

## Steps
### Step 1 — <title>
<files, concrete changes>
**Gate:** <build/test/lint command that must pass>

### Step 2 — ...

## Acceptance
- <verifiable, observable checks — not "looks done">

## Out of scope
- <deferred items>
```

## Relationship to other tracking

| Location | Purpose |
|----------|---------|
| `TaskCreate` | in-session multi-step tracking, <30min |
| `TODO.md` | backlog item not yet worth a spec |
| `.ship/NN-NAME/` | this workflow — spec-sized, multi-step, gated |
| `specs/N/*.md` | long-lived architectural reference (plan may cite or graduate into these) |
