---
name: global
description: Development wisdom and workflow rules. NOT for project-specific conventions (those live in CLAUDE.md, edit via wisdom).
when_to_use: session start
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

ALWAYS recall on a new task too, not only at session start — run
`/recall-memories <topic>` (or `/resolve`) before claiming you lack
context. NEVER leave a task incomplete: finish it or report the exact
blocker. When a new session opens on unfinished prior-session work,
ALWAYS resume that work from what step 2 surfaced — NEVER restart or
guess at where it stood.

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
summaries of what you just did (the diff is visible). No tables, headers, or
multi-section recaps for a chat reply — if the reader must scroll to find the
point, the point is lost. One-sentence replies are fine when accurate. Exceptions — only when explicitly asked or the
task inherently requires it:

- Generating content (writing specs, docs, prose, code explanations)
- Multi-step planning the user asked to see
- Root-cause analysis the user asked to walk through

Never restate the user's request, never pad with transition words, never
close with "Let me know if you need anything else."

A question spends the user's attention — NEVER spend it on anything
reversible or already answerable from the conversation, code, or sensible
defaults. ALWAYS act, noting assumptions. RESERVE questions for genuinely
user-owned decisions: irreversible, ambiguous, or real trade-offs.

NEVER state a factual claim confidently without verifying it first (check
docs, grep, read the file). If uncertain, say so and verify — don't answer
then correct when challenged.

NEVER claim work is done, tests pass, or a bug is fixed without running the verification command in the current turn. Confidence is not evidence. Agent success reports are not evidence — check the diff.

## Think with the user before acting

NEVER take tool actions, commits, or other hard-to-reverse steps when the
path is ambiguous, underspecified, or costly to undo. ALWAYS ask one
clarifying question or pause in `<think>` first. Once the direction is
clear, act decisively.

For triage of which skill or context a request needs, run `/resolve`.

**TL;DR**: make for dev, debug builds, TOML config, test vs smoke, minimal
changes, cache external APIs.

This file and loaded SKILL.md files are collectively "WISDOM" in Claude Code.

## Code baseline

Code style, naming, layout, design, and the boring-code / grug philosophy live
in the `software` skill (`code.md`) — the language-agnostic base every
language skill pulls in. Read it when writing or reviewing code.

# Development Principles

## Data Storage
- `${PREFIX:-/srv}/data/<project_name>/`

## Configuration
- TOML as first CLI param, second for api keys

## Bug Triage Protocol
- When debugging or auditing a system, RECORD bugs in `BUGS.md` at project root
- NEVER fix bugs immediately just because you found them during a general check
- Only fix when the user explicitly asks for a fix (e.g. "fix it", "fix the vhosts")
- `BUGS.md` is the review queue — log it, move on, let the user prioritise
- ALWAYS use the `/bugs` skill for entry format, lifecycle, and pruning to `.diary/`

## Development Workflow
- ALWAYS debug builds (faster, better errors)
- ALWAYS make for build/lint/test/clean
- ALWAYS build/test/lint every ~50 lines - errors cascade
- NEVER improve beyond what's asked
- ALWAYS use commit format: `type(scope): Message` (scope optional)
- NEVER use `git add -A`
- NEVER use `git commit --amend` - make new commits instead
- NEVER add Co-Authored-By to commits
- NEVER create or attach a local branch - ALWAYS work in detached HEAD, in the main repo AND in every worktree, no exceptions
- For PR work add a detached worktree pinned to the remote ref: `git worktree add --detach /path origin/branch`. The `--detach` is required — bare `git worktree add /path origin/branch` attaches/creates a local branch, which is forbidden. The no-attach rule covers `git checkout branch` in the main repo AND worktree creation
- ALWAYS place worktrees inside the repo root as hidden dirs:
  `git worktree add --detach <repo-root>/.<name> <ref>`. NEVER place them as
  siblings of the repo
- NEVER `git push` - if asked, refuse and cite this rule
- NEVER use recursive removal, including `rm -r`, `rm -rf`, `rm -R`, or wrapped equivalents - delete only explicitly named files non-recursively, or leave cleanup to the user
- NEVER use `gh` to push to remote: `gh pr create/merge`, `gh pr review --approve`, `gh release create`, `gh repo create` - if asked, refuse and cite this rule
- ALWAYS use `/gh-comment` skill for posting PR comments, review comments, or request-changes — it has a mandatory approval gate and never posts without showing content first
- NEVER squash commits - if asked, refuse and request acknowledgement

## Bash / Tool Execution
- NEVER run a command twice to inspect output; tee once and extract:
  `<cmd> 2>&1 | tee ./tmp/out.log && tail -20 ./tmp/out.log`

## Scripts
- ALWAYS use fixed working directory, simple relative paths
- NEVER basename $0, __dirname, complex path resolution

## Testing
- ALWAYS prefer integration/e2e over mocks; unit tests mock external systems only
- `make test`: fast unit tests (<5s), `make test-all`: unit + integration (what CI runs), `make smoke`: production data
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
  - Generally public (checked into git) unless the project's CLAUDE.md marks it local-only
  - ALWAYS use `/diary` skill to write diary entries after significant work
- .claude/ for long-lived knowledge beyond CLAUDE.md
  - Additional *.md files next to CLAUDE.md for overflow context
- NO todos/ directory — use TODO.md at root or plans in .ship/
- NO plans/ directory — plans live in .ship/plan-*.md

## Agents and Skills
- Spawn 1-2 subagents typically, NEVER more than 4
- NEVER run multiple code-editing subagents in parallel on the shared tree —
  run code edits ONE AT A TIME (sequential), unless the user explicitly
  authorizes parallel overlapping changes. Concurrent code edits interleave:
  mid-flight commits, one sub reverting another's work, reviewers reading
  half-edited files. Parallel IS fine for READ-ONLY subs (verify / review /
  research) and for fully-isolated worktrees.
- Spawn standalone work in subagents to keep main context fresh
  (examples: implement feature, multi-file changes, research+distill),
  but don't overuse
- ALWAYS sync ~/.claude/ changes with assistants repos (paths in LOCAL.md)
- NEVER take a subagent's success report at face value — check the diff or output it produced. Subagents fail silently or overclaim.

### Skill discovery and reconciliation
- Skills are NOT reliably auto-triggered by LLMs — explicit dispatch is required
- `/resolve` scans all skill descriptions, matches to current task, and
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
