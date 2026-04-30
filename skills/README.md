# Skills

Auto-activating context for Claude Code. Each `<name>/SKILL.md` loads
when its description matches the current task. Some are user-invocable
as slash commands (`/refine`, `/diary`, ...).

## Why these exist

LLMs forget. Every conversation starts cold, every long generation
drifts from the rules, and the right skill rarely fires on its own.
Each skill in this directory addresses one of these problems:

- **Style alignment** — language conventions the model wouldn't guess
- **Session continuity** — facts and history across conversations
- **Multi-pass refinement** — first-pass code drifts from CLAUDE.md
- **Frequent shortcuts** — common instructions named once
- **Discovery nudging** — handled by hooks, not skills (see below)

## Session continuity (memory + diary + recall-memories)

LLMs have no memory between conversations. Three pieces cover this:

- **memory** (instruction-based, defined in `~/.claude/CLAUDE.md`):
  durable facts about the user, project, feedback rules. Types:
  `user`, `feedback`, `project`, `reference`. There is no separate
  `facts` skill — memory subsumes it.
- **diary**: chronological work log at `<cwd>/.diary/YYYYMMDD.md`.
  Different from memory: diary is *what happened today*, memory is
  *what's true forever*.
- **recall-memories**: explicit search across diary + memory + recent
  session transcripts. Memory and diary don't auto-fire on relevant
  prompts — recall-memories is the "look it up" verb.

## Multi-pass refinement (refine, improve, readme)

LLMs drift from CLAUDE.md and codestyle on a single pass. Even when
the rules are loaded, a long generation introduces noise: extra
comments, inconsistent naming, broken imports, stale doc counts.
Refinement is a deliberate second pass that re-reads the rules with
the diff visible.

- **improve**: DO → CRITICIZE → EVALUATE → IMPROVE on changed code
- **readme**: sync README/ARCHITECTURE/CHANGELOG with what shipped
- **refine**: orchestrates both, validates build/test, commits `[refined]`

Reach for these when: about to PR, after a feature lands, after a
long generation pass.

## Shortcuts (fin, sub)

Macros for instructions you'd otherwise type out every time:

- **fin**: "finish all pending tasks without stopping for confirmation"
- **sub**: "spawn this prompt as a background subagent and continue"

These don't add new behavior — they're aliases. The win is muscle
memory: `/fin` is faster than retyping the rule.

## Discovery nudging (hooks, not skills)

Skills auto-activate by description match, but in practice the LLM
often misses the right one. Hooks add explicit nudges:

- **nudge** (UserPromptSubmit): keyword → agent routing
  ("ship", "diary", "commit" → suggested invocations)
- **stop** (Stop): blocks the response when uncommitted changes or
  stale diary detected, suggests `/commit` or `/diary`

Without nudges the LLM picks the wrong skill or none. With them,
common workflows surface automatically. See `../hooks/README.md`.

## Skill index

### Languages — codestyle only

`go`, `py`, `rs`, `sh`, `sql`, `ts`, `tsx` — conventions per language
(naming, idioms, test layout, build flags).

### Domain — patterns for a kind of program

| Skill | Domain |
|-------|--------|
| **agent-browser** | headless browser automation |
| **cli** | argparse/click/clap, exit codes, signals |
| **data** | scrapers, ETL, leaky-bucket, state recovery |
| **ops** | Dockerfile, systemd, Prometheus |
| **service** | REST, /health, versioned paths, validate-before-persist |
| **trader** | exchange APIs, state machines, paper trading |
| **testing** | testcontainers, real-API-first, RAII cleanup |

### Workflow — multi-pass + scaffolding

| Skill | Role |
|-------|------|
| **commit** | structured git flow, `[section] Message`, HEREDOC |
| **diary** | append `## HH:MM` to `.diary/YYYYMMDD.md` |
| **docs-audit** | parallel subagent doc-vs-code audit |
| **improve** | code-quality DO-CRITICIZE-EVALUATE-IMPROVE |
| **learn** | extract patterns from history into skills |
| **merge-trivial** | classify conflicts, resolve trivial unions |
| **pr-draft** | short, clear PR descriptions |
| **readme** | sync README/ARCHITECTURE with code |
| **recall-memories** | search diary + memory + sessions |
| **refine** | orchestrate improve + readme + commit `[refined]` |
| **release** | version bump, changelog, git tag |
| **ship** | plan → build → judge pipeline |
| **specs** | spec authoring and index |
| **wisdom** | meta — how to write SKILL.md / CLAUDE.md |

### Shortcuts

| Skill | What it macros |
|-------|----------------|
| **fin** | "run to completion, no confirmation prompts" |
| **sub** | "fire-and-forget background subagent" |

### Generators / one-offs

| Skill | What it generates |
|-------|-------------------|
| **create-eval** | project-specific eval skill |
| **distill** | recursive 5/3 summarization (launches @distill) |
| **tweet** | dense X/Twitter thread, no fluff |
| **visual** | render → inspect → adjust (launches @visual) |

## Working with skills

- Each `SKILL.md` has YAML frontmatter (`name`, `description`,
  optional `user-invocable: true`)
- `user-invocable: true` exposes the skill as `/<name>` slash command
- Auto-activation matches the `description` field — make it specific
- See `wisdom/SKILL.md` for the writing rules
