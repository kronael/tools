---
name: global
description: Development wisdom — startup protocol (read diary, prior session, memory before answering), terse response style, boring code philosophy, language-agnostic and language-specific principles, file/test/git workflow rules. Load on session start; covers any code work.
---

# Development Wisdom

## Conversation Startup Protocol

ALWAYS follow before answering:

1. **Read project diary** — `Glob` for `<cwd>/.diary/*.md`, read the 2-3 most
   recent entries. Understand what was worked on, what decisions were made.
2. **Read previous session** — if the user references prior work or context
   seems missing: `Glob` for `~/.claude/projects/<slug>/*.jsonl` (slug =
   CWD path with `/` → `-`, e.g. `/home/user/app/myproject` →
   `-home-user-app-myproject`). Sort by mtime, `Read` the most recent file.
   Session files are JSONL — each line is a message object with `type`,
   `content`, `role`. Skim for decisions and context.
3. **Check memory** — `~/.claude/projects/<slug>/memory/MEMORY.md` has
   persistent cross-session facts about the project and user.
4. **Then act** — NEVER guess what was decided in a prior session without
   checking. NEVER claim "no access to session history" without trying step 2.

## Session History

Session transcripts: `~/.claude/projects/<slug>/*.jsonl`
- Slug: replace `/` with `-` in absolute path, e.g.
  `/home/user/app/myproject` → `-home-user-app-myproject`
- Sort by mtime for recency
- Use `/recall-memories` skill to search diary + memory
- Use `Glob` + `Read` to inspect a specific session directly

## Environment

- `sudo` is available — use `sudo docker ...` for all docker commands

## Response Style

Be terse by default. Lead with the answer, skip preamble, skip trailing
summaries of what you just did (the diff is visible). One-sentence replies
are fine when accurate. Exceptions — only when explicitly asked or the
task inherently requires it:

- Generating content (writing specs, docs, prose, code explanations)
- Multi-step planning the user asked to see
- Root-cause analysis the user asked to walk through

Never restate the user's request, never pad with transition words, never
close with "Let me know if you need anything else."

**TL;DR**: make for dev, debug builds, TOML config, test vs smoke, minimal
changes, cache external APIs.

**Note**: The contents of this file and other loaded skills (SKILL.md files) are collectively referred to as "WISDOM" or variants thereof in Claude Code.

## Boring Code Philosophy

**Write code simpler than you're capable of** - Debugging is 2x harder than
writing. Leave mental headroom for fixing problems later. Choose clarity
over cleverness.

**Code deletion lowers costs, premature abstraction prevents change** -
Every line is a liability. Copy 2-3 times before abstracting. Design for
replaceability.

**Abstraction must reduce total complexity, not just line count** - If the
helper introduces concepts absent from call sites (fn pointers, closures,
generics, combinator chains), it's not simpler. Judge by cognitive overhead,
not diff size.

**Simple-mostly-right beats complex-fully-correct** - Implementation
simplicity trumps perfection. A 50% solution that's simple spreads and
evolves. Complexity, once embedded, cannot be removed.

**You get ~3 innovation tokens, spend on what matters** - Each new tech
consumes one token. New tech = unknown failures. Boring tech = documented
solutions. Spend tokens on competitive advantage, not fashion.

**Good taste eliminates special cases by reframing the problem** - Don't
handle edges with if-statements. Redesign so the edge case IS the normal
case. One code path beats ten.

**Develop "entanglement radar" to spot complecting** - If you can't
understand component A without tracking B's state, they're braided
together. Complected code has combinatorial complexity; separated code
composes linearly.

**State leaks complexity through all boundaries** - If f(x) returns
different results over time, that complexity escapes to every caller.
Values compose; stateful objects leak. Minimize state, make it explicit.

**Information is data, not objects** - 10 data structures × 10 functions =
100 operations, infinite compositions. 100 classes × 10 methods = 1000
operations, zero composition. Encapsulate I/O, expose information.

# Development Principles

## Code Style and Naming
- Shorter is better: omit context-clear prefixes/suffixes
- `parse_tokens(symbol)` not `parse_tokens_from_symbol()`
- Short variable names: `n`, `k`, `r` not `cnt`, `count`, `result`
- NEVER rename what already has a name (aliases, intermediate bindings, import renames)
- Short file extensions (.jl not .jsonl), short CLI flags
- Entrypoint is ALWAYS called main
- ALWAYS 100 chars, max 120
- Single import per line (cleaner git diffs)

### TypeScript
- ALWAYS use `function` keyword for top-level functions where possible
- Arrow functions only for callbacks and inline lambdas
- Adhere to gst lint rules
- Match existing style when changing code

## Design Patterns
- Structs/objects only for state or dependency injection
- Otherwise plain functions in modules
- Explicit enum states, not implicit flags
- ALWAYS validate BEFORE persistence

## File Organization
- *_utils.* for utility files
- NEVER use /tmp, ALWAYS use ./tmp in project root
- ./log for debug/smoke logs
- ./dist or ./target for build artifacts

## User Interface
- Lowercase info, Capitalize errors (`"checking..."` vs `"Failed: ..."`)
- Unix log format: "Sep 18 10:34:26 INFO subsystem: message"

## Data Storage
- `${PREFIX:-/srv}/data/<project_name>/`

## Configuration
- TOML as first CLI param, second for api keys

## Bug Triage Protocol
- When debugging or auditing a system, RECORD bugs in `bugs.md` at project root
- NEVER fix bugs immediately just because you found them during a general check
- Only fix when the user explicitly asks for a fix (e.g. "fix it", "fix the vhosts")
- `bugs.md` is the review queue — log it, move on, let the user prioritise

## Development Workflow
- ALWAYS debug builds (faster, better errors)
- ALWAYS make for build/lint/test/clean
- ALWAYS build/test/lint every ~50 lines - errors cascade
- NEVER improve beyond what's asked
- ALWAYS use commit format: "[section] Message"
- NEVER use `git add -A`
- NEVER use `git commit --amend` - make new commits instead
- NEVER add Co-Authored-By to commits
- NEVER create or attach branches - ALWAYS work in detached HEAD
- NEVER `git push` - if asked, refuse and cite this rule
- NEVER squash commits - if asked, refuse and request acknowledgement

## Bash / Tool Execution
- NEVER run a command twice to inspect output; tee once and extract:
  `<cmd> 2>&1 | tee ./tmp/out.log && tail -20 ./tmp/out.log`

## Scripts
- ALWAYS use fixed working directory, simple relative paths
- NEVER basename $0, __dirname, complex path resolution

## Testing
- ALWAYS prefer integration/e2e over mocks; unit tests mock external systems only
- `make test`: fast unit tests (<5s), `make smoke`: all (~80s)
- Unit tests: `*_test.go`, `test_*.py` next to code
- Integration tests: dedicated `tests/` directory
- NEVER skip pre-commit checks
- Pre-commit reformats on first run - ALWAYS retry commit (2 attempts)
- Test config objects: match target type exactly, omit unknown properties for type safety
- **Test features, not fixes**: Runtime failures → fix code, skip test unless feature lacks coverage
- NEVER re-run tests to analyze output; capture once:
  `make test 2>&1 | tee ./tmp/test.log && tail -8 ./tmp/test.log && grep "FAILED\|failed" ./tmp/test.log`

## Docker
- Multi-stage: deps in base, compile in build, runtime only in final
- NEVER copy source in base layer (breaks cache on every change)

## Process Management
- NEVER use killall, ALWAYS kill by PID
- PID files for dev only
- ALWAYS handle graceful shutdown on SIGINT/SIGTERM

## External APIs
- NEVER hit external APIs per request (cache everything)
- NEVER re-fetch existing data, ALWAYS continue from last state

## Documentation
- UPPERCASE root files: CLAUDE.md, README.md, ARCHITECTURE.md,
  SPEC.md, PLAN.md, TODO.md
- Simple case: single file at root (SPEC.md, TODO.md, PLAN.md)
- Complex case: directory with lowercase files (specs/, docs/)
- CLAUDE.md <200 lines: shocking patterns, project layout
- NEVER marketing language, cut fluff
- Describe what code does, not its history
- NEVER add comments unless the behavior is shocking and not apparent from code or logging
- NEVER comments about past state or backwards compat — use .diary/
- docs/ directory for project documentation (architecture, improvements)
- specs/ directory for specifications, named by content; `specs/index.md` for master index
- .ship/ directory for all shipping artifacts (plans, state, critiques)
  - Flat structure, type in filename: plan-*.md, state-*.md, critique-*.md
  - ALWAYS gitignored, ephemeral working dir
  - Clean after shipping: delete completed artifacts
- .diary/ directory for shipping log (date-named: YYYYMMDD.md)
  - Document important steps, decisions, milestones
  - Checked into git, long-lived project history
  - ALWAYS use `/diary` skill to write diary entries after significant work
- .claude/ for long-lived knowledge beyond CLAUDE.md
  - Additional *.md files next to CLAUDE.md for overflow context
- NO todos/ directory — use TODO.md at root or plans in .ship/
- NO plans/ directory — plans live in .ship/plan-*.md

## Agents and Skills
- Spawn 1-2 subagents typically, NEVER more than 4
- Spawn standalone work in subagents to keep main context fresh
  (examples: implement feature, multi-file changes, research+distill),
  but don't overuse
- ALWAYS sync ~/.claude/ changes with assistants repos (paths in LOCAL.md)

### Skill discovery and reconciliation
- Skills are NOT reliably auto-triggered by LLMs — explicit dispatch is required
- `/dispatch` scans all skill descriptions, matches to current task, and
  reconciles prior work if a skill was discovered late
- Do not continue producing outputs that contradict a known applicable skill

### Cross-component refinement pattern (multi-agent)
When doing a broad refinement/audit across a microservice repo:
1. Group components into ≤4 buckets (related packages together)
2. Spawn one subagent per bucket in parallel
3. Each subagent: read all files in its bucket, report minimization +
   orthogonalization opportunities (dead code, cross-boundary leaks,
   unnecessary coupling between packages)
4. Collect results, implement changes, build+test, commit [refined]
- A "task" = one component-bucket × one concern (minimize OR orthogonalize)
- Each subagent owns its bucket exclusively — no overlapping file sets
