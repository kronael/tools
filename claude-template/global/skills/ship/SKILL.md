---
name: ship
description: Ship multi-stage feature from plan
user-invocable: true
---

# Ship Skill

Orchestrates multi-stage feature delivery from plan file. Runs in main context for coordination, delegates implementation to subagents to avoid context pollution.

## Workflow (Demiurg-Inspired)

Adopts Cursor's proven **Planner-Worker-Judge** pattern for scalable agent orchestration:

1. **Load/Resume Plan** - read from `.claude/plans/`, restore state if continuing
2. **Parse Stages** - extract stage breakdown with dependencies
3. **Initialize State** - create `./tmp/ship-state.json` for progress tracking
4. **Execute Stages** - spawn workers (parallel where dependencies allow)
5. **Judge Completion** - verify all stages complete, trigger refinement if needed
6. **Refinement Round** (optional) - identify follow-up tasks (tests, fixes, docs)
7. **Final Validation** - E2E verification stage (if in plan)
8. **Final Commit** - single commit with all changes
9. **Ship Summary** - what shipped, main impact, no fluff

**Key Features**:
- State persistence (resume interrupted ships)
- Parallel execution (independent stages run concurrently)
- Error isolation (failed stages don't block unrelated stages)
- Refinement loop (automatic follow-up tasks)
- Minimal context (extract once, reuse)

## Plan Structure Expected

Plans must have stages marked as:
```markdown
### Stage 1: [Name]
**Goal**: ...
**Files**: ...
**Subagent**: improve|refine|readme|visual|...
**Dependencies**: [] (or [1, 2] for stages that depend on 1 and 2)
**Verification**:
- [ ] Test 1
- [ ] Test 2
```

**Dependencies** (optional): List of stage numbers this stage depends on. Used for parallel execution scheduling. If omitted, assumes sequential dependency on previous stage.

## Stage Execution (Worker Pattern)

**Parallel Execution** (demiurg-inspired):
- Stages with satisfied dependencies run concurrently
- Default: 1-4 workers depending on ready stages
- Dependencies block stage start (e.g., Stage 3 waits for Stage 2)
- Failed stages DON'T block unrelated stages (error isolation)

Example parallelization:
```
Time 0s: Stage 1 (Infrastructure) → running
Time 15s: Stage 1 complete → Stage 2, 3 both ready → spawn both
Time 23s: Stage 2 complete, Stage 3 still running
Time 28s: Stage 3 complete → Stage 4 ready → spawn
Time 31s: Stage 4 complete → Stage 5 ready → spawn
Time 150s: Stage 5 (E2E validation) complete
```

**Subagent Selection** (from plan's `**Subagent**` field):
- `improve` - Code enhancements, refactors, fixes
- `refine` - Feature additions, modifications
- `readme` - Documentation updates
- `visual` - UI/styling changes
- `learn` - Pattern extraction (rare)

**Prompt Format** (to subagent):
```
Feature Context: {extracted_context}

Stage N: [Name]

Goal: [from plan]

Files to modify:
- file1.py
- file2.ts

Changes required:
[detailed instructions from plan]

Verification checklist:
- [ ] Item 1
- [ ] Item 2

IMPORTANT: Report completion in this XML format:
<stage-result>
<status>completed|failed</status>
<files>
<file>api/test_data/factories.py - Added game_status parameter</file>
<file>api/test_data/time_series.py - Added data_end_offset_days</file>
</files>
<verification>
<item status="pass">Tests pass</item>
<item status="pass">DB columns verified</item>
</verification>
<error>Error message if failed</error>
</stage-result>
```

**XML Parsing** (demiurg pattern):
- Robust regex-based extraction from subagent output
- Fallback: Parse plain text if XML missing
- Detect "reached max turns" as automatic failure

## Rules (Enhanced with Demiurg Patterns)

**Coordination (Main Agent)**:
- NEVER do implementation work - ALWAYS delegate to subagents
- Keep context minimal: only state file, test outputs, git status
- Read plan ONCE at start, extract context and stages
- State mutations protected by file-based locking (atomic write-rename)
- Main agent is the Judge: polls state, triggers refinement, exits on completion

**Execution (Workers)**:
- Stages run in parallel where dependencies allow
- Each worker isolated: no inter-worker communication
- Workers pull from queue: next ready stage (dependencies satisfied)
- Timeout: Tell subagent 10min, actual timeout 20min (buffer for graceful handling)
- Max turns detection: Parse "reached max turns" → automatic failure

**Verification**:
- Parse XML from subagent output (fallback to plain text)
- Failed verification marks stage as `failed`, stores error
- Verification checklist copied to stage result
- No automatic retries (refinement loop handles follow-ups)

**State Management**:
- Single state file: `./tmp/ship-state.json`
- Atomic updates: write to temp, rename (no corruption)
- Continuation: `--continue` resumes from state (running → pending)
- Timestamps: Track started_at, completed_at for duration reporting

**Commits**:
- NO commits between stages (single commit at end)
- Checkpoint BEFORE starting (preserve work-in-progress)
- Final commit format: `[ship] Feature name` with stage summary
- NEVER use `git add -A` (explicit file adds only)
- Follow CLAUDE.md commit discipline (no --amend, no Co-Authored-By)

## State Management (Demiurg Pattern)

**State Persistence** (`./tmp/ship-state.json`):
```json
{
  "plan_file": "sunny-hatching-yao.md",
  "feature_name": "Comprehensive Test Data Generation",
  "is_complete": false,
  "refine_count": 0,
  "stages": [
    {
      "id": 1,
      "name": "Infrastructure",
      "status": "completed",
      "started_at": "2025-02-07T10:30:00Z",
      "completed_at": "2025-02-07T10:30:15Z",
      "files_changed": ["api/test_data/factories.py", "api/test_data/time_series.py"],
      "result": "Added game_status and error_message support",
      "error": null
    },
    {
      "id": 2,
      "name": "State Coverage Scenario",
      "status": "running",
      "started_at": "2025-02-07T10:30:15Z",
      "completed_at": null,
      "files_changed": [],
      "result": null,
      "error": null
    }
  ]
}
```

**Stage States** (demiurg TaskStatus pattern):
- `pending` - Not started yet, waiting for dependencies
- `running` - Subagent currently executing
- `completed` - Successfully finished with verification passed
- `failed` - Execution or verification failed (with error message)

**Continuation Support**:
- `--continue` flag resumes interrupted ship from state file
- Running stages reset to pending on restart
- Completed/failed stages preserved

## Context Management (Minimal Injection Pattern)

**To avoid context pollution**:
1. Extract feature context ONCE from plan (planner phase)
2. Inject context into ALL subagent prompts (no re-reading)
3. Subagents handle all implementation file reads
4. Main agent only reads: state file, test outputs, git status
5. Summarize subagent output: "Stage N complete: 3 files, tests pass"

**Feature Context** (extracted by parser):
```
Project: Dashboard test data generator
Framework: Python + FastAPI + SQLAlchemy
Goal: Add scenarios covering all UI states
```

Injected into every subagent prompt to provide consistent context without re-reading plan.

**Stage Status Display**:
```
Stage 1/5: Infrastructure ✅ (3 files, 15s)
Stage 2/5: State Coverage 🔄 (running, 8s elapsed)
Stage 3/5: Edge Cases ⏸️  (pending, blocked by Stage 2)
Stage 4/5: Documentation ⏸️  (pending, blocked by Stage 3)
Stage 5/5: Validation ⏸️  (pending, blocked by Stage 4)
```

## Configuration

**Command Options**:
```bash
/ship <plan-name> [-c] [-w N] [-n]
```

- `<plan-name>` - Plan filename without .md extension (e.g., `sunny-hatching-yao`)
- `-c` - Continue: resume interrupted ship from state file
- `-w N` - Workers: max parallel workers (default: 4, min: 1)
- `-n` - No refine: skip refinement loop after stages complete

**State File Location**: `./tmp/ship-state.json` (or `./tmp/ship-state-<plan-name>.json` for multiple concurrent ships)

**Skills Injection**: Automatically loads from `~/.claude/skills/` and injects into all subagent prompts (truncated to 1000 chars each).

## Example Usage

**Fresh Ship**:
```bash
/ship sunny-hatching-yao
```
Loads `.claude/plans/sunny-hatching-yao.md`, extracts 5 stages, executes with parallel workers, triggers refinement if needed, commits result.

**Resume Interrupted Ship**:
```bash
/ship sunny-hatching-yao -c
```
Restores state from `./tmp/ship-state.json`, resets running stages to pending, continues execution.

**Single-Threaded Ship** (for debugging):
```bash
/ship sunny-hatching-yao -w 1
```
Sequential execution, easier to debug individual stage failures.

**No Refinement** (skip follow-up tasks):
```bash
/ship sunny-hatching-yao -n
```
Execute only the plan stages, skip refinement loop.

## Refinement Loop (Demiurg Judge Pattern)

After initial stages complete, trigger **up to 1 refinement round**:

1. **Analyze Completed Work**:
   - Review last 5 completed stages
   - Review any failed stages with errors
   - Check if follow-up tasks needed (tests, fixes, docs, integration)

2. **Generate Follow-Up Stages** (via planner):
   ```
   Recent completed stages:
   - [DONE] Stage 1: Infrastructure (added game_status support)
   - [DONE] Stage 2: State coverage scenario (8 clients)
   - [FAILED] Stage 3: Edge cases (zero equity client failed generation)

   Based on this, identify follow-up tasks needed:
   - Fix failed stages with alternative approaches
   - Add missing tests
   - Update documentation
   - Integration validation

   Output XML:
   <refinement>
   <stage>Fix edge-zero-equity generation with adjusted parameters</stage>
   <stage>Add pytest test for state_coverage scenario verification</stage>
   <stage>Update README.md with new scenario documentation</stage>
   </refinement>

   Or if complete:
   <refinement></refinement>
   ```

3. **Execute Refinement Stages**:
   - New stages added to queue with `pending` status
   - Execute same worker pattern (parallel where possible)
   - Max 1 refinement round to prevent infinite loops

**When Refinement Triggers**:
- All initial stages completed/failed
- `refine_count < 1` (single refinement pass)
- At least 1 completed or failed stage exists

## Failure Handling (Error Isolation Pattern)

**Stage-Level Failures** (demiurg pattern):
- Failed stage marked with error, stays `failed` status
- Other stages continue if dependencies satisfied
- Refinement loop can generate fix attempts
- No automatic retries (explicit refinement only)

**Error Types**:
- Verification failed → Error details in state
- Subagent timeout → "Timeout after Ns" error
- "Reached max turns" detected → Automatic failure
- Exception during execution → Exception message captured

**User Intervention**:
- Critical failures pause execution
- Display current state, stage status, errors
- User can: continue (skip failed), retry stage, abort ship

## Success Criteria

- ✅ All stages completed
- ✅ All verification checklists checked
- ✅ Final tests pass
- ✅ Final commit created
- ✅ User informed of ship status

## Output Format

```
📦 Shipping: [Feature Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Stage 1/5: Infrastructure ✅ (3 files, 15s)
Stage 2/5: Feature A ✅ (2 files, 8s)
Stage 3/5: Feature B ✅ (1 file, 5s)
Stage 4/5: Documentation ✅ (2 files, 3s)
Stage 5/5: Validation ✅ (manual checks, 2min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ Shipped: [Feature Name]

Changes:
- Added X to Y
- Enhanced Z with W
- Documented V

Impact: [Brief description]

Commit: abc1234
```
