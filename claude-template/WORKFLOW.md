# Agent Workflow Hierarchy

```
/ship (outer loop: specs → components → completion)
  │
  ├── Scan specs, topological sort components
  ├── For each component:
  │     ├── Generate build plan from spec
  │     ├── /build (inner loop)
  │     ├── Update PROGRESS.md
  │     ├── Critique (spec compliance review)
  │     └── Fix gaps if >10% (max 2 rounds)
  ├── Final audit
  └── Ship summary

/build (inner loop: plan → stages → workers → commit)
  │
  ├── Parse plan from .claude/plans/
  ├── Spawn parallel workers per stage
  ├── Judge loop: poll, retry (max 3), error isolation
  ├── Refinement round (max 1)
  └── Single commit at end

/refine (finalization pass)
  │
  ├── Checkpoint (commit current state)
  ├── Validate (build/test)
  ├── /improve (code quality)
  ├── /readme (documentation)
  ├── Verify (final build/test)
  └── Commit [refined]

/improve (code quality, single pass)
  │
  └── DO → CRITICIZE → EVALUATE → IMPROVE → VERIFY
      (3-5 iterations max)

/readme (documentation sync)
  │
  └── Update README, ARCHITECTURE, CHANGELOG, CLAUDE.md

/learn (pattern extraction)
  │
  └── Extract patterns from history → write SKILL.md

/visual (UI/styling)
  │
  └── Render → inspect → criticize → adjust (one thing)
```

## When to Use What

| Goal | Agent | Example |
|------|-------|---------|
| Build project from specs | /ship | "ship from specs/" |
| Execute a plan file | /build | "build auth-feature" |
| Polish before PR | /refine | "refine this" |
| Fix specific code issue | /improve | "improve error handling" |
| Update docs | /readme | "readme" |
| Extract learnings | /learn | "learn from this session" |
| Fix UI/styling | /visual | "visual" |

## Hierarchy

- /ship delegates to /build (per component)
- /build delegates to /improve, /readme, /visual (per stage)
- /refine delegates to /improve and /readme
- /improve, /readme, /learn, /visual are leaf commands

## Key Differences

| | /ship | /build | /refine |
|---|---|---|---|
| Input | specs directory | plan file | existing code |
| Scope | whole project | single feature | current changes |
| Commits | per component | single at end | single at end |
| Critique | after each phase | no | no |
| State | PROGRESS.md | .ship/build-state-{plan}.md | none |
