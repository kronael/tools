---
name: ship
description: Drive a spec-sized feature from plan to shipped — fable plans, sonnet implements step-by-step, refine polishes. NOT for one-off or <30min fixes (use improve), and NOT for tracking without driving execution (use TODO.md).
when_to_use: "ship this, ship it, let's ship, then ship, ship the feature, spec this and build it, plan and implement, build this end to end, track this project, drive this to done"
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
   - **Ship ALWAYS means plan + re-research, in a fresh subagent
     (never a `fork` — it carries the stale context), against the
     code as it is now** — even when this session already researched
     the area or a PLAN.md / spec already exists. NEVER assemble the
     plan from conversation context; NEVER take an existing plan or
     spec at face value.
   - An existing plan or spec is input to the sub, not its output:
     the sub re-verifies every claim against the current code and
     rewrites what drifted. A spec accurate when written is wrong a
     few commits later, and a stale plan spends the implementation
     budget on code that no longer exists.
2. **Confirm** — read PLAN.md yourself, summarize it for the user in
   a few lines (steps + gates), and get a go-ahead before spending
   implementation budget. Skip this only if the user already approved
   the scope.
3. **Ship (sonnet)** — for each PLAN.md step in order: spawn one
   `sonnet` subagent to implement that step, then review it and run
   the step's green-gate yourself — brief, review and recover per the
   `sonnet` skill § Plan, then execute, steps 2-4. **Never take a
   sub's report at face value — check the diff.** One code-editing
   sub at a time on the shared tree; if a step is genuinely parallelizable, isolate each sub in
   its own `git worktree add --detach` and merge sequentially — never
   run overlapping edits on the same tree. See `prompt.md` for the
   implementation brief template.
4. **Refine** — once all steps are green, run the `refine` skill on
   the touched paths to finalize (dead code, minimization, polish).
5. **Close-out** — distill durable bits (decisions → `.diary/`,
   architecture → `specs/`, release notes → `CHANGELOG.md`) then
   prune `.ship/NN-NAME/` per the folder-layout note above.

## Close-out distillation (step 5)

`.ship/` is scratch, not an archive — unless the project's CLAUDE.md overrides
that (see Folder layout). For each thing in `.ship/NN-NAME/`, ask "where does
this belong long-term?":

| Kind of content | Permanent home |
|---|---|
| Decisions, discoveries, bug post-mortems | `.diary/YYYYMMDD.md` (today's entry) |
| Architectural decisions, design choices | `specs/N/<topic>.md` (move + add `status: shipped`) |
| Release-notes-worthy changes | `CHANGELOG.md` |
| Recurring rules / preferences / patterns | project `CLAUDE.md` or `MEMORY.md` |
| Bench numbers worth tracking | `bench-baseline.json` + a short note in CHANGELOG |
| Critique / review findings | resolved → fold into diary; deferred → `TODO.md` |
| Forced-rank punch lists for "next sprint" | `TODO.md` + maybe seed the next `.ship/` plan |

Then prune. **NEVER recursively remove the directory** (WISDOM bans `rm -r`
and wrapped equivalents such as `git rm -rf`): `git rm` the files by name, or
leave the cleanup to the user.

- NEVER keep a `REPORT.md` "for reference" — commit history + the diary IS the
  reference.
- NEVER keep progress notes after the work ships. The progress is `git log` now.
- NEVER archive into `.ship/archive/` — that is the same hoarding, renamed.
- Exception: a genuinely long-lived reference document (a spec, a runbook) moves
  to `specs/` or `docs/` before the rest is pruned.

**When NOT to prune:** the work is paused mid-flight (keep until it ships or is
cancelled), or a critique/audit doc is the input to the NEXT plan (keep until
that one starts, then fold it in and prune the source).

Alternative execution path: the `ship` CLI (`uv tool install
git+https://github.com/kronael/ship`) runs the plan autonomously instead of
step-by-step subagents. Use it when the user asks for `ship` the tool;
otherwise the subagent workflow above is the default. On this path, `cli.md`
replaces steps 1–3: the planner writes spec files to `.ship/NN-NAME/specs/`,
not a PLAN.md; ship writes its own PLAN.md into its DATA_DIR. Run `cli.md`'s
preflight before the first launch: ship needs a `claude` login of its own,
and its defaults (the `sonnet` model with sonnet-sized role timeouts, 4
workers, state in `./.ship`) need the overrides `cli.md` gives.

## Guardrails (apply throughout, not just at close-out)

- **Detached HEAD only** — never create or attach a local branch, in
  the main tree or any worktree. Isolated work uses
  `git worktree add --detach <path> <ref>`.
- **Path-scoped commits**, conventional-commit format `type(scope): message`
  — never `git add -A`/`-A`-equivalents, never `--amend`, never push.
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

## IO Surfaces
<external APIs, files, ports, processes touched>

## Steps
### Step 1 — <title>
<files, concrete changes, the decisions it must not re-open>
**Out of scope:** <files and changes this step must not touch>
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
