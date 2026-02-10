You are executing the SHIP skill to deliver a multi-stage feature using the **Planner-Worker-Judge** pattern from demiurg (Cursor's architecture).

## Your Role: The Judge

You are the **Judge** in the Planner-Worker-Judge architecture:
- **Planner**: Parse plan file ONCE, extract context and stages
- **Workers**: Spawn subagents (parallel where dependencies allow)
- **Judge**: Monitor state, verify completion, trigger refinement, exit when done

**CRITICAL**: You are the COORDINATOR only. NEVER do implementation work yourself. ALWAYS delegate to subagents.

## Architecture Pattern

```
Load Plan → Parse Stages → Initialize State
    ↓
Spawn Workers (parallel, queue-based)
    ↓
Judge Loop (poll every 5s)
    ├─ All stages done? → Trigger refinement (max 1 round)
    ├─ Refinement done? → Final validation → Commit → Exit
    └─ Still working? → Display progress, continue loop
```

## Instructions

### Step 1: Checkpoint

Check for uncommitted changes:
```bash
git status --short
```

If uncommitted changes exist, commit them:
```bash
/commit
```

### Step 2: Parse Options & Check for Continuation

Parse command options:
- `-c` - Continue from state file
- `-w N` - Max workers (default: 4)
- `-n` - Skip refinement loop

Check if `-c` flag present and state file exists:
```bash
ls -la ./tmp/ship-state.json 2>&1
```

If state file exists and `-c` flag provided:
- Read state file
- Display: "Resuming ship: [feature_name]"
- Reset `running` stages to `pending` (continuation-safe pattern)
- Skip to Step 4 (execute stages)

Otherwise, proceed to Step 3 (fresh start).

### Step 3: Load Plan & Extract Context

**3.1 Read Plan File**:
```bash
Read: /home/ondra/.claude/plans/{filename}.md
```

**3.2 Extract Feature Context** (planner phase):

Parse plan header for feature context:
- Feature name (from plan title or summary)
- Project/framework info (e.g., "Python + FastAPI + SQLAlchemy")
- Goal (brief 1-2 sentence description)

Store this context to inject into ALL subagent prompts (avoid re-reading plan).

**3.3 Parse Stages**:

Look for sections like:
```
### Stage N: [Name]
**Goal**: ...
**Files**: ...
**Subagent**: [agent-type]
**Dependencies**: [stage-numbers] (optional)
**Verification**:
- [ ] ...
```

Extract for each stage:
- Stage number
- Stage name
- Goal
- Files to modify
- Subagent type (improve, refine, readme, visual, etc.)
- Dependencies (list of stage numbers, default: [N-1] if omitted)
- Verification checklist

**3.4 Initialize State File**:

Write `./tmp/ship-state.json`:
```json
{
  "plan_file": "sunny-hatching-yao.md",
  "feature_name": "Comprehensive Test Data Generation",
  "feature_context": "Project: Dashboard test data generator. Framework: Python + FastAPI. Goal: Add scenarios covering all UI states.",
  "is_complete": false,
  "refine_count": 0,
  "stages": [
    {
      "id": 1,
      "name": "Infrastructure",
      "goal": "Add support for game_status, error_message, OFFLINE simulation",
      "files": ["api/test_data/factories.py", "api/test_data/time_series.py"],
      "subagent": "improve",
      "dependencies": [],
      "verification": ["Tests pass", "DB columns verified"],
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "files_changed": [],
      "result": null,
      "error": null
    },
    // ... more stages
  ]
}
```

**State Locking**: Use atomic write (write to temp file, rename) to prevent corruption.

### Step 4: Execute Stages (Worker Pattern)

**Worker Queue Pattern** (demiurg-inspired):
- Identify ready stages (dependencies satisfied, status = pending)
- Spawn workers for ready stages (parallel where possible)
- Max concurrent workers: min(4, ready_stages_count)
- Each worker: pull stage → execute → update state → repeat

**Judge Loop** (poll every 5s):
```
Loop forever:
  1. Read state file
  2. Check if complete (all stages completed/failed)
  3. If complete: break loop, go to refinement
  4. Display progress
  5. Sleep 5s
```

#### 4.1 Display Progress

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Shipping: [Feature Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Stage 1/5: Infrastructure ✅ (3 files, 15s)
Stage 2/5: State Coverage 🔄 (running, 8s elapsed)
Stage 3/5: Edge Cases ⏸️  (pending, blocked by Stage 2)
Stage 4/5: Documentation ⏸️  (pending)
Stage 5/5: Validation ⏸️  (pending)
```

Update this display on each judge loop iteration (every 5s).

#### 4.2 Spawn Worker for Ready Stage

For each ready stage (dependencies satisfied, status = pending):

**Update state**: Mark stage as `running`, set `started_at` timestamp.

**Spawn subagent** using Task tool:

```
Task(
  subagent_type="[improve|refine|readme|visual]",
  description="Stage N: [Name]",
  run_in_background=true,  # Non-blocking for parallel execution
  prompt="""
Feature Context: {feature_context from state}

Available Skills: [Inject loaded skills here, truncated to 1000 chars each]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stage N: [Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Goal: [Goal from stage]

Files to modify:
[List files from stage.files]

Implementation requirements:
[Detailed instructions from plan's stage section]

Verification checklist:
[Copy verification items from stage.verification]

IMPORTANT: You have a 10-minute timeout (work efficiently).

After completing all changes and running verification, report in this XML format:

<stage-result>
<status>completed|failed</status>
<files>
<file>path/to/file.py - Brief description of changes</file>
<file>path/to/other.ts - Brief description</file>
</files>
<verification>
<item status="pass|fail">Test description</item>
<item status="pass|fail">Other verification</item>
</verification>
<error>Error message if status=failed</error>
</stage-result>

If you cannot complete in time or encounter issues, output status=failed with error details.
"""
)
```

**Important**: Set `run_in_background=true` for parallel execution. Don't wait for completion here.

#### 4.3 Process Completed Workers

In judge loop, for each stage with status `running`:

1. **Check if subagent finished** (via TaskOutput or completion signal)
2. **Parse XML output** from subagent result:
   ```python
   import re
   status_match = re.search(r"<status>(.*?)</status>", output, re.DOTALL)
   files_matches = re.findall(r"<file>(.*?)</file>", output, re.DOTALL)
   verif_matches = re.findall(r'<item status="(.*?)">(.*?)</item>', output, re.DOTALL)
   error_match = re.search(r"<error>(.*?)</error>", output, re.DOTALL)
   ```

3. **Detect "reached max turns"** in output:
   ```python
   if "reached max turns" in output.lower():
       status = "failed"
       error = "Reached max turns"
   ```

4. **Update state**:
   - Set stage status to `completed` or `failed`
   - Set `completed_at` timestamp
   - Store `files_changed` list
   - Store `result` (brief summary) or `error` message
   - Write state file atomically

5. **Brief status update**:
   ```
   ✅ Stage N/TOTAL: [Name] (3 files, 15s)
   ```

#### 4.4 Error Handling (Error Isolation)

If stage fails:
- Mark as `failed` with error message
- Store in state file
- **DO NOT block other stages** (error isolation pattern)
- Refinement loop will identify and potentially fix later

No automatic retries - explicit refinement only.

### Step 5: Refinement Loop (Judge Pattern)

After all initial stages completed/failed (and `-n` not set):

**5.1 Check Refinement Eligibility**:
```
if refine_count >= 1:
    skip refinement (max rounds reached)
if all stages pending:
    skip refinement (nothing completed yet)
```

**5.2 Analyze Completed Work**:

Generate refinement analysis prompt:
```
Feature: [feature_name]
Context: [feature_context]

Recent completed stages (last 5):
- [DONE] Stage 1: Infrastructure (3 files, added game_status support)
- [DONE] Stage 2: State coverage (8 clients, all states tested)
- [DONE] Stage 4: Documentation (updated README with scenarios)

Failed stages:
- [FAILED] Stage 3: Edge cases (zero equity client generation failed: "equity cannot be negative")

Based on this progress, identify follow-up tasks needed:
1. Fix failed stages with alternative approaches
2. Add missing tests for completed features
3. Update documentation for new additions
4. Integration validation if not in plan

Output XML (or empty if no follow-up needed):

<refinement>
<stage>Fix edge-zero-equity generation: use max(0, equity) clamping</stage>
<stage>Add pytest for state_coverage scenario DB verification</stage>
<stage>Integration test: generate state_coverage and verify UI renders all states</stage>
</refinement>

If work is complete and no follow-up needed:
<refinement></refinement>
```

**5.3 Parse Refinement Stages**:

```python
pattern = r"<stage>(.*?)</stage>"
matches = re.findall(pattern, output, re.DOTALL)
new_stages = []
for desc in matches:
    desc = desc.strip()
    if len(desc) > 5:
        new_stages.append({
            "id": max_stage_id + 1,
            "name": f"Refine: {desc[:50]}...",
            "goal": desc,
            "files": [],  # Worker determines files
            "subagent": "refine",
            "dependencies": [],  # No dependencies (all can run parallel)
            "verification": ["Changes complete", "Tests pass"],
            "status": "pending",
            ...
        })
```

**5.4 Execute Refinement Stages**:

If new_stages not empty:
- Increment `refine_count` in state
- Add new stages to state
- Return to Step 4 (execute stages with worker pattern)

If new_stages empty:
- Proceed to Step 6 (final validation)

**Maximum 1 refinement round** to prevent infinite loops.

### Step 6: Final Validation

If plan includes E2E validation stage (manual checks), execute it:
- Usually last stage with `subagent: visual` or checklist-only
- Follow verification checklist
- Report validation results
- If validation fails, report to user for intervention

### Step 7: Final Commit

**7.1 Check for Changes**:
```bash
git status --short
```

**7.2 Commit All Changes**:

If changes exist:

```bash
# Collect all changed files from state
files=$(cat ./tmp/ship-state.json | jq -r '.stages[].files_changed[]' | sort -u)

# Add files explicitly (NEVER git add -A)
git add $files

# Create commit with stage summary (NO Co-Authored-By per CLAUDE.md)
git commit -m "$(cat <<'EOF'
[ship] [Feature Name]

Staged implementation:
- Stage 1: [Name] ([N] files changed)
- Stage 2: [Name] ([N] files changed)
- Stage 3: [Name] ([N] files changed)
- Stage 4: [Name] ([N] files changed)
- Stage 5: [Name] ([N] files changed)
EOF
)"
```

**7.3 Get Commit SHA**:
```bash
git log -1 --format=%h
```

Store commit SHA for summary report.

### Step 8: Ship Summary

**8.1 Mark State Complete**:
Update `./tmp/ship-state.json`:
```json
{
  "is_complete": true,
  ...
}
```

**8.2 Generate Summary Report**:

Read state file for all stage results. Report final status:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ Shipped: [Feature Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Initial Stages:
✅ Stage 1: [Name] ([N] files, [duration])
✅ Stage 2: [Name] ([N] files, [duration])
✅ Stage 3: [Name] ([N] files, [duration])
✅ Stage 4: [Name] ([N] files, [duration])
✅ Stage 5: [Name] ([N] files, [duration])

Refinement:
✅ Refine: [Description] ([N] files, [duration])
✅ Refine: [Description] ([N] files, [duration])

Failed Stages:
❌ Stage 3: [Name] (error: [error_message])
   └─ Fixed in refinement

Summary:
- Total stages: [N] ([N] completed, [N] failed, [N] refined)
- Total files changed: [count unique files]
- Total time: [HH:MM:SS]
- Refinement rounds: [0-1]

Key changes:
- [One-line per major change from stage results]

Impact: [Brief description of what this enables]

Commit: [short SHA]
State: ./tmp/ship-state.json (preserved for reference)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**8.3 Clean Up** (optional):
State file preserved at `./tmp/ship-state.json` for debugging/reference. User can delete manually.

## Rules (Demiurg-Enhanced)

1. **Context Management** (Minimal Injection Pattern):
   - Extract feature context ONCE from plan (planner phase)
   - Inject context into ALL subagent prompts (no re-reading)
   - NEVER read implementation files yourself (subagents do this)
   - Only read: plan (once), state file, test outputs, git status
   - Main agent is Judge: coordinate, verify, report

2. **Subagent Delegation** (Worker Pattern):
   - ALWAYS use Task tool with `run_in_background=true` for parallel execution
   - Pass feature context + skills + stage details to subagent
   - Include XML output format requirement in prompt
   - Tell subagent "10min timeout" (actual: 20min buffer)
   - NO automatic retries (refinement loop handles follow-ups)

3. **State Management** (Demiurg Pattern):
   - ALL progress tracked in `./tmp/ship-state.json`
   - Atomic writes: write temp file, rename (no corruption)
   - Stage states: pending → running → completed|failed
   - Timestamps: track started_at, completed_at for duration
   - Continuation-safe: running stages reset to pending on `-c`

4. **Parallel Execution** (Queue Pattern):
   - Identify ready stages (dependencies satisfied, status=pending)
   - Spawn workers up to `-w N` limit (default: 4)
   - Workers isolated: no inter-worker communication
   - Judge loop polls state every 5s for completion
   - Failed stages DON'T block unrelated stages (error isolation)

5. **Verification** (XML Parsing):
   - Parse `<stage-result>` XML from subagent output
   - Fallback to plain text if XML missing
   - Detect "reached max turns" → automatic failure
   - Failed verification → mark failed, store error, continue
   - Refinement loop identifies and fixes failures

6. **Refinement Loop** (Judge Pattern):
   - Trigger after initial stages complete/fail
   - Maximum 1 refinement round (prevent infinite loops)
   - Analyze completed/failed stages, generate follow-up tasks
   - New stages added to queue, executed with worker pattern
   - Skip if `-n` flag set

7. **Commit Discipline** (CLAUDE.md):
   - Single commit at end (NOT per stage, NOT between stages)
   - Commit message lists all stages with file counts
   - NEVER use `git add -A` (explicit file adds from state)
   - NEVER use Co-Authored-By (violates CLAUDE.md)
   - Follow `[ship] Feature name` format

8. **Error Handling** (Error Isolation):
   - Stage fails → Mark failed with error, continue others
   - Subagent timeout → Detect, mark failed, continue
   - "Max turns" detected → Automatic failure
   - Critical failure → Display state, await user decision
   - User can: continue (skip failed), retry stage, abort

9. **Communication** (Progress Indicators):
   - Update display every 5s in judge loop
   - Status icons: ✅ (completed), 🔄 (running), ⏸️ (pending), ❌ (failed)
   - Show elapsed time for running stages
   - Brief status updates (no verbose explanations)
   - Final summary includes: stages, files, time, refinement, impact

## Example Execution

User: `/ship sunny-hatching-yao`

You:
1. Read `.claude/plans/sunny-hatching-yao.md`
2. Extract 5 stages (Infrastructure, Feature A, Feature B, Documentation, Validation)
3. Execute Stage 1 via improve agent → Verify → Confirm
4. Execute Stage 2 via refine agent → Verify → Confirm
5. Execute Stage 3 via refine agent → Verify → Confirm
6. Execute Stage 4 via readme agent → Verify → Confirm
7. Execute Stage 5 via visual agent (manual validation) → Verify → Confirm
8. Commit all changes with staged summary
9. Report ship summary

Total context usage: Minimal (only coordination, no implementation details)

## Implementation Details

### State File Format

`./tmp/ship-state.json`:
```json
{
  "plan_file": "sunny-hatching-yao.md",
  "feature_name": "Comprehensive Test Data Generation",
  "feature_context": "Project: Dashboard. Framework: Python + FastAPI. Goal: Add test scenarios.",
  "is_complete": false,
  "refine_count": 0,
  "stages": [
    {
      "id": 1,
      "name": "Infrastructure",
      "goal": "Add support for game_status, error_message",
      "files": ["api/test_data/factories.py"],
      "subagent": "improve",
      "dependencies": [],
      "verification": ["Tests pass", "DB verified"],
      "status": "completed",
      "started_at": "2025-02-07T10:30:00.123Z",
      "completed_at": "2025-02-07T10:30:15.456Z",
      "files_changed": ["api/test_data/factories.py", "api/test_data/time_series.py"],
      "result": "Added game_status and error_message parameters",
      "error": null
    }
  ]
}
```

### XML Parsing Examples

**Successful completion**:
```xml
<stage-result>
<status>completed</status>
<files>
<file>api/test_data/factories.py - Added game_status parameter to ClientFactory.create()</file>
<file>api/test_data/time_series.py - Added data_end_offset_days for OFFLINE simulation</file>
</files>
<verification>
<item status="pass">pytest api/tests/test_test_data.py passes</item>
<item status="pass">DB columns verified via migration check</item>
</verification>
</stage-result>
```

**Failure with error**:
```xml
<stage-result>
<status>failed</status>
<error>TypeError: ClientFactory.create() got unexpected keyword argument 'game_status'. Need to add parameter to function signature first.</error>
</stage-result>
```

**Regex patterns**:
```python
status = re.search(r"<status>(.*?)</status>", output, re.DOTALL).group(1)
files = re.findall(r"<file>(.*?)</file>", output, re.DOTALL)
verif = re.findall(r'<item status="(.*?)">(.*?)</item>', output, re.DOTALL)
error = re.search(r"<error>(.*?)</error>", output, re.DOTALL)
```

### Dependency Resolution

Stage becomes "ready" when:
1. Status = `pending`
2. All dependencies have status = `completed`
3. OR dependencies = [] (no deps)

Example:
```
Stage 1: dependencies=[] → ready immediately
Stage 2: dependencies=[1] → ready after Stage 1 completes
Stage 3: dependencies=[1,2] → ready after both Stage 1 AND 2 complete
Stage 4: dependencies=[2] → ready after Stage 2 (parallel with Stage 3)
```

### Atomic State Updates

```python
import json
import os

def save_state(state):
    temp_path = "./tmp/ship-state.json.tmp"
    final_path = "./tmp/ship-state.json"

    # Write to temp file
    with open(temp_path, 'w') as f:
        json.dump(state, f, indent=2)

    # Atomic rename (no corruption even if interrupted)
    os.rename(temp_path, final_path)
```

## Important Notes

- This skill is for PLANNED features with staged breakdown
- Plans must follow structure in SKILL.md (with Stage N: sections)
- If plan lacks stage breakdown, suggest creating plan first via `/plan` or EnterPlanMode
- Subagent types: improve (refactors), refine (features), readme (docs), visual (UI), learn (patterns)
- Stage order from dependencies, NOT sequential (enables parallelization)
- State persisted at `./tmp/ship-state.json` for debugging and continuation
- Skills auto-loaded from `~/.claude/skills/` and injected into worker prompts
