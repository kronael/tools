# Assistants

Claude Code configuration: 18 skills, 7 agents, 4 commands, 7 hooks.

## Why Skills?

Claude Code is capable out of the box, but it doesn't know *your*
patterns. Skills are auto-activating SKILL.md files that inject domain
knowledge when relevant files are open. Touch a `.rs` file and Claude
learns your Rust conventions (FxDashMap, enum states, debug builds).
Open a Dockerfile and ops patterns activate (multi-stage, pin versions,
graceful shutdown). No manual prompting — context arrives automatically.

This matters because LLMs repeat the same mistakes without guardrails:
wrong test patterns, verbose SQL, missing health endpoints, unsafe async
cleanup. Skills encode the lessons so every session starts informed.

## Contents

**[claude-template/](claude-template/)** - Skills, agents, commands, and
hooks for Claude Code. Open Claude Code there and say "install".

**[usage-patterns/](usage-patterns/)** - 12 usage patterns extracted from
57 production projects (1.3MB logs).

## Installation

```bash
cd claude-template
# Say "install"
```

Claude compares with existing ~/.claude/, shows diffs, asks before
overwriting.

## Skills (18)

Auto-activate based on file context. No setup needed per project.

### Language Skills

| Skill | Activates on | What it teaches |
|-------|-------------|-----------------|
| **go** | .go, go.mod | testing.Short(), test files next to code |
| **python** | .py, pyproject.toml | Modern type hints, asyncpg direct, uv, pyright |
| **rust** | .rs, Cargo.toml | FxDashMap, enum states, tracing, testcontainers |
| **typescript** | .ts/.tsx, package.json | Arrow style, class-validator, Bun, Playwright |
| **sql** | SQL queries, migrations | JOIN USING, no AS aliases, one migration per change |

### Domain Skills

| Skill | Activates on | What it teaches |
|-------|-------------|-----------------|
| **cli** | argparse, click, clap | Config precedence, exit codes, --json flag |
| **service** | /health, /ready, /v1/ | Versioned paths, validate-before-persist, caching |
| **data** | scrapers, ETL, feeds | LeakyBucket, state recovery, dedup, cache-first |
| **ops** | Dockerfile, systemd | Multi-stage builds, Prometheus, graceful shutdown |
| **trader** | exchange APIs, WebSocket | State machines, paper trading, precision rounding |
| **testing** | test infrastructure | Real APIs first, testcontainers, RAII cleanup |

### Workflow Skills

| Skill | Activates on | What it teaches |
|-------|-------------|-----------------|
| **commit** | /commit | Structured git flow, section markers, HEREDOC format |
| **build** | /build | Planner-Worker-Judge, parallel stages, .ship/ state |
| **ship** | /ship | Spec-driven outer loop, topological sort, critique |
| **refine** | /refine | Delegates to @improve + @readme, never self-improves |
| **tweet** | /tweet | Dense threads, no fluff, personal framing |
| **wisdom** | SKILL.md, CLAUDE.md | ALWAYS/NEVER statements, YAML frontmatter |

## Agents (7)

| Agent | Purpose |
|-------|---------|
| **@distill** | Extract key points from long content |
| **@improve** | DO-CRITICIZE-EVALUATE-IMPROVE loop |
| **@learn** | Extract patterns from history into skills |
| **@readme** | Sync README/ARCHITECTURE with code |
| **@refine** | Checkpoint, @improve, @readme, commit |
| **@research** | Research and knowledge synthesis |
| **@visual** | Render-inspect-adjust for SVG/UI |

## Commands (4)

| Command | Role |
|---------|------|
| **/build** | Inner loop: plan, stages, parallel workers, judge |
| **/refine** | Finalization: @improve, @readme, commit |
| **/ship** | Outer loop: specs, components, /build, critique |
| **/tweet** | Share work on social media |

### /ship — Spec-Driven Delivery

Reads specs/ directory or an inline plan, topological-sorts components by
dependency, delegates each to /build, commits after each component, tracks
progress in PROGRESS.md. After every phase a critique agent scores
completeness — if gaps exceed 10%, it re-builds.

```
specs/ or inline plan → dependency order → for each component:
  plan → /build → test → critique → fix gaps → commit
→ final audit → ship summary
```

### /refine — Polish Before PR

Seven-step finalization pass. Checkpoints current state, validates
build/test, delegates code improvement to @improve and documentation to
@readme, verifies again, commits `[refined]`. Never does improvement
work itself — pure orchestration.

```
checkpoint → validate → @improve → @readme → verify → commit [refined]
```

## Agent Hierarchy

```
/ship (outer loop: specs -> components)
  └── /build (inner loop: plan -> parallel workers -> commit)

/refine (finalization: @improve + @readme)

@improve, @readme, @learn, @visual, @distill, @research (leaf agents)
```

Nudge hook routes prompts to agents via fuzzy keyword matching.

## Hooks (7)

| Hook | Trigger | Purpose |
|------|---------|---------|
| **nudge** | prompt submit | Routes keywords to matching agents |
| **local** | session start | Injects LOCAL.md rules |
| **redirect** | tool call | Maps toolchain commands |
| **learn** | compact/end | Generates flow reports |
| **reclaude** | session start | Restores session context |
| **stop** | prompt submit | Classifies prompt type |
| **context** | prompt submit | Manages context |

## References

- [WORKFLOW.md](claude-template/WORKFLOW.md) - agent hierarchy
- [ARCHITECTURE.md](claude-template/ARCHITECTURE.md) - component details
- [hooks ARCHITECTURE.md](claude-template/global/hooks/ARCHITECTURE.md) - hook system

## See Also

**[kronael/ship](https://github.com/kronael/ship)** - Autonomous coding
agent that implements the planner-worker-judge pipeline as a standalone
Python tool. Same architectural pattern as /ship and /build here, but as
an independent tool consuming ~/.claude/skills/.
