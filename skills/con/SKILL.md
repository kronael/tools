---
name: con
description: /con — goal mode. Recall every interrupted, paused, or
  abandoned task/plan/goal from this session (not just live agent
  processes) and drive each to actual completion. NOT for just pushing the
  single current in-flight task to completion without stopping (use fin).
when_to_use: >
  "continue", "resume", "pick up where we left off", "finish the unfinished",
  "resume the agents", "resume the paused work", "what was left"
user-invocable: true
---

# /con — continue mode (goal mode)

A persistent goal-tracking mode: recall everything interrupted, paused, or
left abandoned this session — tasks, plans, agent runs, half-finished
goals, however they surfaced — and pursue each to real completion. The
scope is recall-then-resume, not a single task; fin's scope is one
in-flight task, narrower and already running.

## Procedure

### 1. Load context

- ALWAYS read `~/.claude/projects/<slug>/memory/MEMORY.md`
  (slug = absolute CWD with `/` → `-`, e.g. `/home/user/app/foo` →
  `-home-user-app-foo`)
- ALWAYS read the most recent `<cwd>/.diary/*.md` entry
- ALWAYS skim the conversation for the last task list, plan, or eval output

### 2. Inventory in-flight work

- ALWAYS check every agent notification in the session (running / paused /
  completed). Note each agentId and last known state.
- ALWAYS list every pending item found anywhere in the conversation:
  unactioned eval findings, plan phases not yet built, "remaining" notes,
  half-done features, failing tests left open.

### 3. Resume agents

- Still resumable — ALWAYS `SendMessage` to its agentId with a concise nudge
  ("continue from where you left off: [last known state]"); NEVER re-brief
  from scratch, context is intact.
- Not resumable — ALWAYS re-launch a fresh agent with: original task + what
  was already done + what remains. Be specific.
- ALWAYS relay each agent's final message back; NEVER dump raw file output.

### 4. Action pending tasks

- ALWAYS complete every unactioned item found in step 2 in priority order.
- ALWAYS verify with the actual command this turn — NEVER treat confidence
  or a success report as evidence; check the diff or run the command.

### 5. Pursue every recalled goal to actual completion

- NEVER stop early — a goal recalled in step 2 isn't done until verified done.
- NEVER ask except on **genuine ambiguity**: two approaches with real
  tradeoffs, contradictory requirements, missing info that cannot be
  inferred — ALWAYS pick one and go on plain implementation details instead.
- ALWAYS self-correct on blockers — NEVER declare something "should pass";
  fails twice → try a third angle.

## Constraints (from CLAUDE.md)

- NEVER run multiple code-editing subagents in parallel on the shared
  tree. Read-only subs (verify / review / research) and fully-isolated
  worktrees may run in parallel.
- Spawn ≤4 subagents; 1-2 is typical.
- Always work in detached HEAD in the main repo and every worktree.
- NEVER `git push`, `git commit --amend`, squash, or add Co-Authored-By.
- Commit only when the user explicitly asks.

## Done when

- Every inventoried agent has finished or is confirmed unblockable.
- Every pending task is completed and verified.
- Brief report: what was resumed, what was completed, what (if anything)
  is blocked and why.
