---
name: ship
description: Ship a project from specs to completion
user-invocable: true
---

# Ship Skill

Outer orchestration loop: specs -> components -> completion.
Reads spec directory, identifies components and their
dependencies, progressively builds each one using /build,
updates PROGRESS.md after each phase, and launches a
critique of progress and readiness.

## Workflow (Demiurg Outer Loop)

1. **Scan Specs** -- read specs dir, identify components
   and their spec files
2. **Dependency Order** -- topological sort of components
   (types before book, book before matching, etc.)
3. **Phase Loop** -- for each component in order:
   a. Generate build plan from spec
   b. Execute via /build (inner loop)
   c. Update PROGRESS.md with completion %
   d. Launch critique (codex) of progress + readiness
   e. If critique finds issues, generate fix plan, /build
4. **Final Audit** -- full spec compliance check
5. **Ship Summary** -- what shipped, coverage, gaps

## Usage

/ship [specs-dir] [-c] [-p component]

- specs-dir: path to specs (default: specs/v1/)
- -c: continue from PROGRESS.md state
- -p: build only specific component

## Spec Scanning

Read all *.md in specs dir. Group by component:
- ORDERBOOK.md -> rsx-book
- RISK.md -> rsx-risk
- MARKETDATA.md -> rsx-marketdata
- DXS.md, WAL.md -> rsx-dxs
- NETWORK.md, WEBPROTO.md -> rsx-gateway
- MARK.md -> rsx-mark
- LIQUIDATOR.md -> rsx-risk (liquidation)
- TILES.md -> architecture (cross-cutting)
- TESTING-*.md -> test specs per component
- CONSISTENCY.md -> cross-cutting invariants

Mapping is convention-based. Unknown specs logged.

## Component Dependencies

```
rsx-types (no deps)
  -> rsx-book (types)
    -> rsx-matching (book, types)
    -> rsx-marketdata (book, types)
  -> rsx-dxs (types)
    -> rsx-risk (types, dxs)
    -> rsx-gateway (types, dxs)
  -> rsx-mark (types)
  -> rsx-recorder (types, dxs)
```

Build in topological order. Earlier components must
pass tests before later ones start.

## Phase Execution

For each component:

1. Read component spec + test spec
2. Check current state (cargo test, existing code)
3. Generate build plan (.claude/plans/{component}.md)
   with stages extracted from spec sections
4. Execute: /build {component}
5. After build completes:
   a. Run cargo test -p {crate}
   b. Count spec requirements vs implemented
   c. Update PROGRESS.md: component %, test count
   d. Spawn critique agent (codex-style review)

## Critique (per phase)

After each component build, launch a critique agent:

```
Task(subagent_type="Explore", prompt="""
Critique: {component} readiness

Read the spec: specs/v1/{SPEC}.md
Read the test spec: specs/v1/TESTING-{SPEC}.md
Read the implementation: {crate}/src/*.rs
Read the tests: {crate}/tests/*.rs

Report:
1. Spec coverage: N/M requirements implemented
2. Test coverage: which spec sections have tests
3. Gaps: what's missing or incomplete
4. Issues: correctness concerns, spec violations
5. Readiness: ready for integration? blockers?

Be specific. Cite spec sections and code lines.
""")
```

Store critique in ./tmp/critique-{component}.md.
If critique finds gaps > 10%, generate fix plan and
re-run /build for that component.

## PROGRESS.md Format

```markdown
# Progress

## Components

| Component | Crate | Spec % | Tests | Status |
|-----------|-------|--------|-------|--------|
| Orderbook | rsx-book | 99% | 86 | done |
| Matching | rsx-matching | 95% | 12 | done |
| DXS/WAL | rsx-dxs | 88% | 45 | gaps |
| Risk | rsx-risk | 75% | 30 | wip |
| Gateway | rsx-gateway | 85% | 15 | wip |
| Marketdata | rsx-marketdata | 89% | 20 | wip |
| Mark | rsx-mark | 100% | 10 | done |

## Last Phase: rsx-risk
- Built: liquidation engine, margin recalc
- Critique: missing replication, insurance fund
- Next: rsx-gateway

## Gaps
- rsx-dxs: TLS, archive, unknown record skip
- rsx-risk: replication/failover, insurance fund
- rsx-gateway: JWT auth, per-IP rate limit
```

## Rules

- NEVER implement yourself -- delegate via /build
- Update PROGRESS.md after EVERY phase
- Critique after EVERY phase (not optional)
- Commit after each component (not at end)
- If critique finds >10% gap, re-plan and re-build
- Max 2 critique->fix rounds per component
- Skip components already at 100%
