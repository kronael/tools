# Development Wisdom

**TL;DR**: make for dev, debug builds, TOML config, test vs smoke, minimal
changes, cache external APIs.

## Boring Code Philosophy

**Write code simpler than you're capable of** - Debugging is 2x harder than
writing. Leave mental headroom for fixing problems later. Choose clarity
over cleverness.

**Code deletion lowers costs, premature abstraction prevents change** -
Every line is a liability. Copy 2-3 times before abstracting. Design for
replaceability.

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
- Short file extensions (.jl not .jsonl), short CLI flags
- Entrypoint is ALWAYS called main
- ALWAYS 80 chars, max 120
- Single import per line (cleaner git diffs)

### TypeScript
- Use const f (args): result => { ... } for functions instead of function keyword where this is sufficient
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
- Lowercase logging, capitalize error names only
- Unix log format: "Sep 18 10:34:26"

## Data Storage
- `${PREFIX:-/srv}/data/<project_name>/`

## Configuration
- TOML as first CLI param, second for api keys

## Development Workflow
- ALWAYS debug builds (faster, better errors)
- ALWAYS make for build/lint/test/clean
- ALWAYS build/test/lint every ~50 lines - errors cascade
- NEVER improve beyond what's asked
- ALWAYS use commit format: "[section] Message"
- NEVER use `git add -A`
- NEVER use `git commit --amend` - make new commits instead
- NEVER add Co-Authored-By to commits
- Detached HEAD ok (reflog keeps commits, branch when needed)

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
- UPPERCASE files: CLAUDE.md, README.md, ARCHITECTURE.md, TODO.md
- CLAUDE.md <200 lines: shocking patterns, project layout
- ARCHITECTURE.md: see readme agent
- CHANGELOG.md for historical notes
- NEVER marketing language, cut fluff
- Describe what code does, not its history (avoid "restores", "reverted" unless directly relevant)
- Allow splits/versions/directories:
  - SPEC* files or specs/* directory
  - TODO* files or todos/* directory
  - PLAN* files or plans/* directory
  - ARCHITECTURE* files (no architectures/ dir needed)
  - Examples: SPECv1.md, TODO_1.md, specs/subscriptions.md, plans/migration.md

## Agents and Skills
- Spawn 1-2 subagents typically, NEVER more than 4
- Spawn standalone work in subagents to keep main context fresh
  (examples: implement feature, multi-file changes, research+distill),
  but don't overuse
- ALWAYS sync ~/.claude/ changes with assistants repos (paths in LOCAL.md)
