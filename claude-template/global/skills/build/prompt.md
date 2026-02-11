You are executing the BUILD skill -- the inner loop of
the Planner-Worker-Judge architecture.

## Your Role: The Judge

You COORDINATE only. NEVER implement code yourself.
- Parse plan ONCE, extract context and stages
- Spawn workers (subagents) for each stage
- Monitor completion, retry failures, run refinement
- Commit result and report

## Instructions

### Step 1: Checkpoint

```bash
git status --short
```
If uncommitted changes, /commit first.

### Step 2: Load Plan

Parse options: plan-name, -c (continue), -w N, -n.
State file: .ship/build-state-{plan-name}.md

If -c and state exists: read state, reset RUNNING
stages to PENDING, skip to Step 4.

Otherwise: read .claude/plans/{plan-name}.md, extract
feature context (name, framework, goal) and stages.
Write initial state file.

### Step 3: Parse Stages

Extract from plan:
- Stage number, name, goal
- Files to modify
- Subagent type (improve, refine, readme, visual)
- Dependencies (default: [N-1])
- Verification checklist

### Step 4: Execute (Worker Pattern)

Judge loop:

**4.1 Retry failed stages** (retries < 3):
Reset to PENDING, increment retries, re-queue.

**4.2 Spawn ready stages** (deps satisfied, PENDING):
Max -w workers (default 4) in parallel.

For each: Task(subagent_type, run_in_background=true)
with prompt containing:
- Feature context
- Stage goal, files, instructions
- Verification checklist
- XML output format requirement
- "10-minute timeout" notice

**4.3 Process completed workers**:
- Parse XML from output (regex: <status>, <file>,
  <item>, <error> tags)
- Detect "reached max turns" = auto failure
- Update state: COMPLETED or FAILED + error

**4.4 Progress display** (on each check):
```
Stage 1/5: Infrastructure [done] (3 files)
Stage 2/5: Feature A [running]
Stage 3/5: Feature B [pending] (blocked by 2)
```

**4.5 Loop until all stages done or failed.**

### Step 5: Refinement (skip if -n)

Spawn improve agent with ALL changed files:
```
Read each file. Fix: 80 char lines, single imports,
dead code, over-engineering. Run build + test.
```

Judge verifies result. Max 1 refinement round.

If failures remain after refine, attempt ONE replan:
generate fix stages from error messages, execute them.

### Step 6: Final Validation

Run build and test for affected code.

### Step 7: Commit

```bash
git add <files from state>
git commit -m "[build] Feature name"
git status
```

### Step 8: Summary

```
Built: [Feature Name]

Stage 1/N: Name [done] (N files)
...

Changes:
- what changed

Commit: abc1234
```

## Rules

1. NEVER write code -- only coordinate workers
2. Read plan ONCE, inject context everywhere
3. Retry failed stages up to 3 times
4. Refine after completion (1 round max)
5. Replan if refine yields nothing + failures (1 round)
6. Parallel workers, error isolation
7. Single commit at end, never git add -A
8. Brief status updates, no verbosity
