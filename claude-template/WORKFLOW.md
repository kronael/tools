# Agent Workflow Hierarchy

```
/ship (top-level orchestrator)
  │
  ├── Plan stages from spec
  ├── Execute stages (parallel where possible)
  ├── Per-stage: spawn worker agents
  │     └── /improve (per-stage quality)
  ├── Judge results
  └── /refine (final pass)

/refine (finalization orchestrator)
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
  └── Render → inspect → criticize → adjust (one thing at a time)

/commit (git workflow)
  │
  └── Status → diff → stage → commit "[section] Message"
```

## When to Use What

| Goal | Agent | Example |
|------|-------|---------|
| Build feature from spec | /ship | "ship the auth feature" |
| Polish before PR | /refine | "refine this" |
| Fix specific code issue | /improve | "improve error handling" |
| Update docs | /readme | "readme" |
| Extract learnings | /learn | "learn from this session" |
| Fix UI/styling | /visual | "visual" |
| Save progress | /commit | "commit" |

## Hierarchy Rules

- /ship delegates to /improve and /refine
- /refine delegates to /improve and /readme
- /improve, /readme, /learn, /visual, /commit are leaf agents
- NEVER invoke /improve manually if /refine covers the scope
- Use /ship for multi-stage work, /refine for single-pass polish
