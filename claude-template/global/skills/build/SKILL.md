---
name: build
description: Build multi-stage feature from plan. Planner-Worker-Judge, .claude/plans/, parallel subagents, build-state, XML results.
user-invocable: true
---

# Build Skill (Inner Loop)

Executes a plan file via Planner-Worker-Judge pattern.
Delegates all implementation to subagent workers. Judge
monitors, retries failures, runs refinement, commits result.

## Architecture

```
Load Plan → Parse Stages → Init State
    ↓
Workers (parallel, queue-based)
    ↓
Judge Loop (poll completed workers)
    ├─ All done? → Refine (max 1 round)
    ├─ Refined?  → Replan (max 1 round)
    ├─ Failed?   → Retry (max 3 per stage)
    └─ Complete  → Commit → Exit
```

## Usage

```
/build <plan-name> [-c] [-w N] [-n]
```

- plan-name: file in .claude/plans/ (no .md)
- -c: continue from state file (RUNNING → PENDING)
- -w N: max parallel workers (default: 4)
- -n: skip refinement loop

## Plan Structure

```markdown
### Stage 1: [Name]
**Goal**: ...
**Files**: ...
**Subagent**: improve|refine|readme|visual
**Dependencies**: [] or [1, 2]
**Verification**:
- [ ] Test 1
```

Dependencies default to [N-1] if omitted.

## Worker Execution

For each ready stage (deps satisfied, status=pending):

1. Mark RUNNING in state file
2. Spawn Task(subagent_type, run_in_background=true)
3. Inject: context + skills + stage details + XML format
4. Timeout: tell worker 10min, actual 20min buffer
5. Parse XML result or detect "reached max turns"
6. Mark COMPLETED or FAILED in state

Workers are isolated. Failed stages don't block others.

## XML Output Format (workers report this)

```xml
<stage-result>
<status>completed|failed</status>
<files><file>path - description</file></files>
<verification>
<item status="pass|fail">description</item>
</verification>
<error>message if failed</error>
</stage-result>
```

## State File

`.ship/build-state-{plan-name}.md` — markdown (ephemeral state):

```markdown
# Build: Feature Name
Plan: plan-name.md
Status: in_progress
Refine: 0

## Stage 1: Name — completed
Started: 2025-02-07T10:30:00Z
Completed: 2025-02-07T10:30:15Z
Files: file1.rs, file2.rs
Result: what was done
Retries: 0
```

Stage states: pending → running → completed|failed.
On -c: running stages reset to pending.

## Retry Logic

- Failed stages retried up to 3 times
- On retry: reset to PENDING, increment retries
- Judge triggers retry before checking completion
- "reached max turns" = automatic failure + retry

## Refinement (mandatory unless -n)

After all stages done, Judge runs ONE refine round:

1. Spawn improve agent with all changed files
2. Wisdom checklist: 80 char, single imports, no
   dead code, no over-engineering, lowercase logging
3. Judge verifies: build + test pass
4. Max 1 refinement round

If refine produces no changes AND failures exist,
attempt ONE replan round (generate fix tasks from
failure errors, execute as new stages).

## Commit Discipline

- NO commits between stages (single at end)
- Checkpoint BEFORE starting (preserve WIP)
- Format: `[build] Feature name`
- NEVER git add -A, NEVER --amend

## Rules

1. NEVER implement — delegate to subagent workers
2. Read plan ONCE, extract context, inject everywhere
3. State in markdown (human-readable, LLM-native)
4. Retry failed stages up to 3 times
5. Refine after completion (1 round max)
6. Replan if refine yields nothing + failures exist
7. Parallel workers where deps allow (max 4)
8. Error isolation: failures don't block siblings
9. Brief status updates, no verbosity
