---
name: sonnet
description: "/sonnet — high-effort background subagent for investigation, bug hunts, pre-review, mechanical edits, and the steps of a written plan. NOT for a design call the plan leaves open (use /opus) or unattended multi-file code (use /fable)."
when_to_use: "do this in a sonnet sub, spawn a sonnet sub, use sonnet, sonnet sub, plan and delegate, delegate to sonnets, split the work across subagents, execute the plan step by step, too big for one pass, multi-file refactor, orchestrate subagents, investigation, bug hunt, find bugs, pre-review, flagging, find simplification, survey codebase, read-only analysis, map files, map references, grep and report, find and replace across files, rename across files, mechanical edit, cheap sub, fast sub"
user-invocable: true
---

With a prompt after /sonnet: launch it as a background agent (`run_in_background: true`, `subagent_type: "sonnet"`), report what was launched, and continue without waiting. For work too big for one sub, run § Plan, then execute — it launches one sub per delegated step.

ALWAYS reach for /sonnet without being asked when the task is:
- A bug hunt, a pre-review sweep, or a read-only survey or audit.
- A mechanical edit too wide for the parent (§ Plan: a codemod stays in the parent).
- One step of a written plan whose design the plan settles (a `ship` step goes to `/opus`).

- ALWAYS use `subagent_type: "sonnet"`, NEVER `model: "sonnet"`: `agents/sonnet.md` pins Sonnet 5.5 at effort `high`, and a sub without the agent type inherits the parent's effort (xhigh under a Fable parent).
- NEVER set effort with prompt text ("Effort: low") — ALWAYS rely on the agent file's pin; lighter work stays in the parent (WISDOM § Agents).
- ALWAYS brief per `dispatch`: a self-contained prompt with paths, errors, scope, out-of-bounds, and what to return.
- ALWAYS send a design call or a step that failed twice to `/opus`.

## Plan, then execute

For work too big for one pass — a feature across packages, a refactor, a change at many call sites — the parent (the main thread) plans, a sonnet sub executes each delegated step, and the parent reviews each step before the next. ALWAYS take spec-sized, mostly unattended work to `ship` instead.

NEVER plan or delegate a change under ~200 lines or ~10 minutes — ALWAYS make it in the parent.

1. **Plan.** ALWAYS read the code first and name real paths and symbols — NEVER plan from the task text. In a large or unfamiliar tree, ALWAYS write the questions the task raises and send them, without the task, to a background read-only `/sonnet` research sub; it returns facts with `file:line`, not a solution, so the facts cannot lean toward one design. ALWAYS write the plan to a file (scratchpad or `.claude/plans/`) with a status and a snapshot SHA per step; a plan held only in context is lost at compaction.
   - ALWAYS plan top-down: the end state (what is true when done, the choices the user sees), then the design, then the steps; each level discards bad solutions before the next one builds on them. ALWAYS show the end state to the user when it holds a choice that is theirs. A change the design already pins needs no step list — its one step is "implement this design".
   - ALWAYS settle every cross-cutting choice in the plan: names, signatures, data shapes, the error convention, which existing mechanism to extend. A choice left to the executors gets a different answer in each step.
   - ALWAYS make each step one coherent behaviour change that leaves the tree green and stays readable in one pass (≤ ~1,000 changed lines). A step that must break the build says so, and its repair step comes next.
   - ALWAYS give each step its files, its non-goals, and its gate: the exact command and the expected result.
   - ALWAYS keep the judgment-heavy step (a concurrency fix, a conflict between two steps) in the parent or an `/opus` sub — NEVER hand it to sonnet because it is "just a step".
   - ALWAYS run a mechanical pattern change as a codemod in the parent (`astgrep`, sed) — NEVER as N sonnet runs.

   Completion criterion: every step names its files, decisions, non-goals and gate.
2. **Brief.** ALWAYS pass the step's decisions verbatim as constraints — the `dispatch` ban on passing your analysis keeps an investigation from anchoring; it NEVER makes an executor re-decide the design. ALWAYS tell the sub to stop and report when the code contradicts the plan — NEVER to work around it. ALWAYS ask for the files changed, each command run with its output, and every deviation from the step.

   Completion criterion: the brief makes sense to a reader who never saw this session.
3. **Review.** Before the step, ALWAYS record its snapshot SHA in the plan: `git stash create` prints one (no stash entry, no tree change), or nothing on a clean tree — then take `git rev-parse HEAD`. NEVER keep it in a shell variable; each tool call starts a fresh shell. After the step, read `git diff <sha>` and `git status`, then run the gate yourself.
   - ALWAYS look for what the sub weakened or removed: deleted or skipped tests, loosened assertions, new lint suppressions, swallowed errors, stubs, TODOs.
   - ALWAYS grep the whole repo — docs, configs, tests — for a renamed or removed name. NEVER check only the files the sub reported.
   - ALWAYS fix a small finding (a missed call site, a wrong name) in the parent, and name it in the report.

   Completion criterion: the gate passes in the parent's own run.
4. **Recover.** On a failure, read the tree, restore the step's files (`git restore --source=<sha> --worktree -- <files>`, delete the files it created by name, `git revert` a commit it made), fix the brief, and re-brief once with the exact gate output — NEVER rerun an unchanged brief or re-brief on top of a failed attempt. After a second failure, take the step over or escalate to `/opus`. When the diff shows the design is wrong, NEVER patch it — ALWAYS discard the step the same way, fix the design, and re-plan the steps after it.

   Completion criterion: the step passes its gate, or the plan records the new design and route.
5. **Close.** After the last step, ALWAYS run the project's full test and lint targets and one end-to-end check of the goal — green steps do not prove the whole. ALWAYS report what ran, what was only read, and what remains.

   Completion criterion: the full suite passes in this turn, and the report names what remains.
