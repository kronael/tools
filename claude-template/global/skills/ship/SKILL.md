---
name: ship
description: Ship project from specs to completion. Outer loop orchestrator, specs scanning, component dependencies, PROGRESS.md, critique cycles.
user-invocable: true
---

# Ship Skill (Outer Loop)

Outer orchestration loop: specs → components → completion.
Reads spec directory or inline plan, identifies components
and their dependencies, progressively builds each one using
/build, updates PROGRESS.md after each phase, and launches
a critique of progress and readiness.

## HARD RULES (read first, always follow)

1. NEVER write code yourself — ALWAYS delegate via /build
2. ALWAYS critique after EVERY component — no exceptions
3. ALWAYS commit after each component — not at end
4. ALWAYS update PROGRESS.md after EVERY phase
5. If plan comes inline (not from specs dir), write it to
   .ship/plan-{component}.md FIRST, then follow the same
   protocol as if it came from specs
6. The protocol is: plan → /build → test → critique →
   fix → commit. Skipping steps is NEVER acceptable.
7. If you catch yourself about to write implementation
   code, STOP and delegate to /build instead.

## Workflow

1. **Scan Specs** — read specs dir or inline plan,
   identify components and their spec files
2. **Dependency Order** — topological sort of components
3. **Phase Loop** — for each component in order:
   a. Generate build plan from spec
   b. Execute via /build (inner loop)
   c. Run tests for component
   d. Update PROGRESS.md with completion %
   e. Launch critique of progress + readiness
   f. If critique finds issues, generate fix plan, /build
   g. Commit the component
4. **Final Audit** — full spec compliance check
5. **Ship Summary** — what shipped, coverage, gaps

## Usage

```
/ship [specs-dir] [-c] [-p component]
/ship to deliver the latest plan    # inline plan mode
```

- specs-dir: path to specs (default: specs/)
- -c: continue from PROGRESS.md state
- -p: build only specific component
- "to deliver the latest plan": extract plan from context,
  write to .ship/, then execute protocol

## Input Modes

### Mode 1: Specs directory
Read all *.md in specs dir. Group by component using
naming convention. Unknown specs logged and skipped.

### Mode 2: Inline plan (from context/plan mode)
When plan is provided inline (user message, plan mode
output, or previous conversation):
1. Extract components from the plan
2. Write each to .ship/plan-{component}.md
3. Proceed with normal protocol (build/test/critique)

NEVER skip the protocol just because the plan is detailed
enough to implement directly. The protocol exists to catch
errors that seem obvious in hindsight.

## Component Dependencies

Build in topological order. Earlier components must
pass tests before later ones start. Extract dependency
graph from project structure (imports, Cargo.toml deps,
package.json, etc).

## Phase Execution

For each component:

1. Read component spec + test spec
2. Check current state (build + test, existing code)
3. Generate build plan (.ship/plan-{component}.md)
   with stages extracted from spec sections
4. Execute: /build {component}
5. After build completes:
   a. Run tests for component
   b. Count spec requirements vs implemented
   c. Update PROGRESS.md: component %, test count
   d. Spawn critique agent (spec compliance review)
6. Commit the component

## Critique (per phase)

After each component build, launch a critique agent:

```
Task(subagent_type="Explore", prompt="""
Critique: {component} readiness

Read the spec: specs/{SPEC}.md
Read the implementation: {source}
Read the tests: {test-source}

Report:
1. Spec coverage: N/M requirements implemented
2. Test coverage: which spec sections have tests
3. Gaps: what's missing or incomplete
4. Issues: correctness concerns, spec violations
5. Readiness: ready for integration? blockers?

Be specific. Cite spec sections and code lines.
""")
```

Store critique in .ship/critique-{component}.md.
If critique finds gaps > 10%, generate fix plan and
re-run /build for that component.

## PROGRESS.md Format

```markdown
# Progress

## Components

| Component | Spec % | Tests | Status |
|-----------|--------|-------|--------|
| types     | 100%   | 10    | done   |
| core      | 95%    | 45    | done   |
| api       | 75%    | 30    | wip    |
| gateway   | 85%    | 15    | wip    |

## Last Phase: api
- Built: auth module, rate limiting
- Critique: missing replication, retry logic
- Next: gateway

## Gaps
- api: retry logic, circuit breaker
- gateway: JWT auth, per-IP rate limit
```

## Rules

- NEVER implement yourself — delegate via /build
- Update PROGRESS.md after EVERY phase
- Critique after EVERY phase (not optional)
- Commit after each component (not at end)
- If critique finds >10% gap, re-plan and re-build
- Max 2 critique→fix rounds per component
- Skip components already at 100%
