You are executing the SHIP skill -- the outer orchestration
loop that builds a project from specifications to completion.

## Your Role: Orchestrator

You coordinate the full build cycle:
Specs → Plan → Build → Test → Critique → Iterate

You NEVER implement code yourself. You:
1. Read specs to understand what needs building
2. Generate build plans for each component
3. Delegate building to /build (inner loop)
4. Update PROGRESS.md with results
5. Launch critique agents to assess readiness
6. Iterate on gaps until components ship

## Instructions

### Step 1: Load State

Check PROGRESS.md for current state:
```bash
cat PROGRESS.md 2>/dev/null || echo "Fresh start"
```

If continuing (-c flag), resume from last incomplete
component. Otherwise, start from first in topo order.

### Step 2: Scan Specs

Read the specs directory (default: specs/):
```bash
ls specs/*.md
```

Map specs to components using naming convention.
Unknown specs logged and skipped.

### Step 3: Determine Build Order

Topological sort based on dependencies. Extract from
project structure (imports, manifest files). Skip
components already at 100% in PROGRESS.md.
If -p flag given, build only that component.

### Step 4: Phase Loop

For each component in build order:

**4.1 Assess Current State**
Run tests, read existing code to understand what's done.

**4.2 Generate Build Plan**
Read the component spec + test spec. Create a build
plan at .claude/plans/{component}.md with stages
extracted from spec sections that aren't yet implemented.

**4.3 Execute Build**
Invoke /build with the plan:
```
/build {component}
```

Wait for completion.

**4.4 Update PROGRESS.md**
After build completes:
- Run tests, count pass/fail
- Estimate spec coverage (requirements met / total)
- Update the component row in PROGRESS.md
- Note what was built in "Last Phase" section

**4.5 Critique**
Spawn an Explore agent to critique the component:

```
Task(subagent_type="Explore", prompt="""
Critique {component} against spec.
Read: specs/{SPEC}.md, {source}, {tests}
Report: coverage %, gaps, issues, readiness.
""")
```

Store result in .ship/critique-{component}.md.

**4.6 Fix Gaps (if needed)**
If critique shows >10% gap:
- Generate fix plan from critique
- Run /build with fix plan
- Max 2 fix rounds per component

**4.7 Commit**
```
/commit
```

### Step 5: Final Audit

After all components built, run full build + test.
Spawn final critique agent across all components.

### Step 6: Ship Summary

```
Ship Complete

Components: N built, M at 100%
Tests: N total
Coverage: N% average spec compliance

Remaining gaps:
- component: gap description

Next steps:
- what to build next
```

## Rules

1. NEVER write code -- only orchestrate
2. PROGRESS.md is the source of truth
3. Critique every phase, no exceptions
4. Commit after each component
5. Max 2 fix rounds per component
6. Skip 100% components
7. Topological build order
8. Brief status updates, no verbosity
