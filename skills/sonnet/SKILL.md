---
name: sonnet
description: "/sonnet — high-effort background subagent for investigation, bug hunts, pre-review, and the steps of a written plan. NOT for mapping or mechanical edits (use /haiku), or a design call the plan leaves open (use /opus)."
when_to_use: "do this in a sonnet sub, spawn a sonnet sub, use sonnet, sonnet sub, plan and delegate, delegate to sonnets, split the work across subagents, execute the plan step by step, too big for one pass, multi-file refactor, orchestrate subagents, investigation, bug hunt, find bugs, pre-review, flagging, find simplification, survey codebase, read-only analysis"
user-invocable: true
---

With a prompt after /sonnet: launch it as a background agent (`run_in_background: true`, `subagent_type: "sonnet"`), report what was launched, and continue without waiting. For work too big for one sub, run § Plan, then execute — it launches one sub per step.

ALWAYS reach for /sonnet without being asked when the task is:
- A bug hunt, a pre-review sweep, or a read-only survey or audit.
- One step of a written plan.

- ALWAYS use `subagent_type: "sonnet"`, NEVER `model: "sonnet"`: `agents/sonnet.md` pins Sonnet 5.5 at effort `high`, and a sub without the agent type inherits the parent's effort (often xhigh).
- NEVER set effort with prompt text ("Effort: low") — only the agent file sets it. ALWAYS take lighter work to `/haiku` instead.
- ALWAYS brief per `dispatch`: a self-contained prompt with paths, errors, scope, out-of-bounds, and what to return.
- Mapping and mechanical edits go to `/haiku`; a design call or a step that failed twice goes to `/opus`.

## Plan, then execute

For work too big for one pass — a feature across packages, a refactor, a change at many call sites — the parent (the main thread) plans, a sonnet sub executes each step, and the parent reviews each step before the next. A step reviewed this way is not the unattended code generation that global § Agents sends to `/fable`. Spec-sized or multi-session work goes to `ship`, which runs steps 2-4 for its build steps.

NEVER delegate a step that takes less time to do than to brief (under ~10 min) — ALWAYS do it in the parent.

1. **Plan.** ALWAYS read the code first and name real paths and symbols — NEVER plan from the task text. ALWAYS write the plan to a file (scratchpad or `.ship/`) with a status per step; a plan held only in context is lost at compaction.
   - ALWAYS settle every cross-cutting choice in the plan: names, signatures, data shapes, the error convention, which existing mechanism to extend. A choice left to the executors gets a different answer in each step.
   - ALWAYS make each step one coherent behaviour change that leaves the tree green. A step that must break the build says so, and its repair step comes next.
   - ALWAYS give each step its files, its non-goals, and its gate: the exact command and the expected result.
   - ALWAYS keep the judgment-heavy step (a concurrency fix, a conflict between two steps) in the parent or an `/opus` sub — NEVER hand it to sonnet because it is "just a step".
   - ALWAYS run a mechanical pattern change as a codemod in the parent (`astgrep`, sed) — NEVER as N sonnet runs.

   Completion criterion: every step names its files, decisions, non-goals and gate.
2. **Brief.** ALWAYS pass the step's decisions verbatim as constraints — the `dispatch` ban on passing your analysis keeps an investigation from anchoring; it NEVER makes an executor re-decide the design. ALWAYS tell the sub to stop and report when the code contradicts the plan — NEVER to work around it. ALWAYS ask for the files changed, each command run with its output, and every deviation from the step.

   Completion criterion: the brief makes sense to a reader who never saw this session.
3. **Review.** Before the step, snapshot the tree: `s=$(git stash create); s=${s:-HEAD}` (no stash entry, no tree change). After it, read `git diff $s` and `git status`, then run the gate yourself.
   - ALWAYS look for what the sub weakened or removed: deleted or skipped tests, loosened assertions, new lint suppressions, swallowed errors, stubs, TODOs.
   - ALWAYS grep the whole repo — docs, configs, tests — for a renamed or removed name. NEVER check only the files the sub reported.
   - ALWAYS fix a small finding (a missed call site, a wrong name) in the parent, and name it in the report.

   Completion criterion: the gate passes in the parent's own run.
4. **Recover.** On a failure, read the tree, fix the brief, and re-brief once with the exact gate output — NEVER rerun an unchanged brief. After a second failure, take the step over or escalate to `/opus`. When the failure shows the plan is wrong, ALWAYS fix the later steps too.
5. **Close.** After the last step, ALWAYS run the full suite (`make test-all` and lint) and one end-to-end check of the goal — green steps do not prove the whole. Report what ran, what was only read, and what remains.

Parallel steps run only in separate worktrees (global § Agents).
