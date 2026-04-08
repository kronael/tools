# Assistants

Claude Code configuration: 32 skills, 6 agents, 5 hooks.

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

**[claude-template/](claude-template/)** - Skills, agents, and hooks
for Claude Code. Open Claude Code there and say "install".

**[usage-patterns/](usage-patterns/)** - 12 usage patterns extracted from
57 production projects (1.3MB logs).

## Installation

```bash
cd claude-template
# Say "install"
```

Claude compares with existing ~/.claude/, shows diffs, asks before
overwriting.

## Skills (32)

Auto-activate based on file context. No setup needed per project.

### Language Skills

| Skill | Activates on | What it teaches |
|-------|-------------|-----------------|
| **go** | .go, go.mod | testing.Short(), test files next to code |
| **py** | .py, pyproject.toml | Modern type hints, asyncpg direct, uv, pyright |
| **rs** | .rs, Cargo.toml | FxDashMap, enum states, tracing, testcontainers |
| **ts** | .ts/.tsx, package.json | Arrow style, class-validator, Bun, Playwright |
| **tsx** | .tsx, React components | React/JSX conventions |
| **sql** | SQL queries, migrations | JOIN USING, no AS aliases, one migration per change |
| **sh** | .sh, shell scripts | POSIX patterns, signal handling |

### Domain Skills

| Skill | Activates on | What it teaches |
|-------|-------------|-----------------|
| **cli** | argparse, click, clap | Config precedence, exit codes, --json flag |
| **service** | /health, /ready, /v1/ | Versioned paths, validate-before-persist, caching |
| **data** | scrapers, ETL, feeds | LeakyBucket, state recovery, dedup, cache-first |
| **ops** | Dockerfile, systemd | Multi-stage builds, Prometheus, graceful shutdown |
| **trader** | exchange APIs, WebSocket | State machines, paper trading, precision rounding |
| **testing** | test infrastructure | Real APIs first, testcontainers, RAII cleanup |
| **agent-browser** | browser automation | Headless playwright via CLI |

### Workflow Skills

| Skill | Activates on | What it teaches |
|-------|-------------|-----------------|
| **commit** | /commit | Structured git flow, section markers, HEREDOC format |
| **pr-draft** | /pr-draft | Short, clear PR descriptions |
| **refine** | /refine | Delegates to @improve + @readme, never self-improves |
| **release** | /release | Version bump, changelog, git tag |
| **ship** | /ship | Plan → build → judge pipeline |
| **specs** | specs/*.md | Spec authoring and index |
| **tweet** | /tweet | Dense threads, no fluff, personal framing |
| **wisdom** | SKILL.md, CLAUDE.md | ALWAYS/NEVER statements, YAML frontmatter |
| **diary** | /diary | Append to `.diary/YYYYMMDD.md` at end of work |
| **create-eval** | /create-eval | Project-specific eval criteria |
| **docs-audit** | /docs-audit | Multi-phase parallel doc audit |
| **recall-memories** | /recall-memories | Search diary + memory + session history |
| **merge-trivial** | /merge-trivial | Resolve trivial merge conflicts |
| **sub** | /sub | Spawn subagents for bucketed work |
| **improve** | /improve | Launch @improve agent (wrapper) |
| **learn** | /learn | Launch @learn agent (wrapper) |
| **readme** | /readme | Launch @readme agent (wrapper) |
| **visual** | /visual | Launch @visual agent (wrapper) |

## Agents (6)

| Agent | Purpose |
|-------|---------|
| **@distill** | Extract key points from long content |
| **@improve** | DO-CRITICIZE-EVALUATE-IMPROVE loop |
| **@learn** | Extract patterns from history into skills |
| **@readme** | Sync README/ARCHITECTURE with code |
| **@refine** | Checkpoint, @improve, @readme, commit |
| **@visual** | Render-inspect-adjust for SVG/UI |

## Slash Commands

Defined as user-invocable skills (the legacy `commands/` directory
was retired). Each launches its corresponding `@`-named agent.

| Command | Role |
|---------|------|
| **/improve** | Launch @improve agent for code quality |
| **/learn** | Launch @learn agent to extract patterns |
| **/readme** | Launch @readme agent to update docs |
| **/refine** | Finalization: @improve, @readme, commit |
| **/visual** | Launch @visual agent for UI/styling |

### /refine — Polish Before PR

Checkpoints current state, validates build/test, delegates code
improvement to @improve and documentation to @readme, verifies again,
commits `[refined]`. Never does improvement work itself — pure
orchestration.

```
checkpoint → validate → @improve → @readme → verify → commit [refined]
```

## Agent Hierarchy

```
/refine (finalization: @improve + @readme)

@distill, @improve, @learn, @readme, @refine, @visual (leaf agents)
```

Nudge hook routes prompts to agents via fuzzy keyword matching.

## Hooks (5)

| Hook | Trigger | Purpose |
|------|---------|---------|
| **nudge** | UserPromptSubmit | Fuzzy-match keywords → agent route |
| **local** | UserPromptSubmit, PreCompact | Inject LOCAL.md on first prompt + compaction |
| **reclaude** | UserPromptSubmit, PreCompact | Inject RECLAUDE.md, preserve across compaction |
| **learn** | PreCompact, SessionEnd | Write flow reports for @learn to process |
| **stop** | Stop | Block with commit + diary nudges when dirty |

## Org Overlays

Org-specific skills live in separate repos layered on top of this base
install. The base never contains org-specific content (repo links,
package refs, internal URLs).

**Pattern:**
1. Install base (this repo)
2. Clone org overlay repo
3. Copy org skills: `cp -r skills/<org> ~/.claude/skills/`

Base install NEVER deletes skills not in source, so org skills persist
across updates.

## References

- [WORKFLOW.md](claude-template/WORKFLOW.md) - agent hierarchy
- [ARCHITECTURE.md](claude-template/ARCHITECTURE.md) - component details
- [hooks ARCHITECTURE.md](claude-template/global/hooks/ARCHITECTURE.md) - hook system
