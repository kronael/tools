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

- `sudo` is available — use `sudo docker ...` for docker commands YOU run via
  the Bash tool (in authored/committed scripts, parameterize privilege instead
  — see the `sh` skill)

## Response Style

ALWAYS read `~/.claude/output-styles/caveman.md` when it exists and apply its
response rules.


## Think with the user before acting

For triage of which skill or context a request needs, run `/resolve`.

**TL;DR**: make for dev, debug builds, TOML config, test vs smoke, minimal
changes, cache external APIs.

This file and loaded SKILL.md files are collectively "WISDOM" in Claude Code.

## Code baseline

Code style, naming, layout, design, comments, and the boring-code / grug
philosophy live in the `software` skill (`code.md`) — the language-agnostic
base every language skill pulls in. This content is COLD: it is NOT in this
always-loaded file and stays invisible until the skill is invoked. ALWAYS load
it — run `/resolve`, or invoke the `software` skill (or a language skill that
requires it) — BEFORE writing or reviewing code. Skipping the load does not
relax those rules, it only hides them, so the comments policy and the style
baseline silently fail to apply.

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

## System-change discipline
- **Redesigns need sign-off.** When a fix is a redesign (new contract, changed control flow, cross-cutting), RECORD it in `BUGS.md` as a proposal FIRST; the user signs off BEFORE you ship. Only symptom-level loud-logging ships inline.

## Development Workflow
- ALWAYS debug builds (faster, better errors)
- ALWAYS make for build/lint/test/clean
- ALWAYS build/test/lint every ~50 lines - errors cascade
- NEVER improve beyond what's asked
- ALWAYS use conventional-commit format: "type(scope): message" —
  fix/feat/docs/test/chore/refactor (scope optional); "merge:"/"release:" for those
- Invoking /refine, /ship, /commit, /release IS the ask to commit (those
  workflows commit by design); otherwise commit only when the user asks
- NEVER add Co-Authored-By to commits
- ALWAYS work in detached HEAD, in the main repo AND in every worktree. The
  ONE exception is a dated feature branch for review: `git switch -c
  YYYYMMDD_<tag> <base>` when the user asks for a branch to push. NEVER check
  out or attach `master`/`main` itself.
- For PR work add a detached worktree pinned to the remote ref: `git worktree add --detach /path origin/branch`. The `--detach` is required — bare `git worktree add /path origin/branch` attaches/creates a local branch, which is forbidden. The no-attach rule covers `git checkout branch` in the main repo AND worktree creation
- ALWAYS place worktrees inside the repo root as hidden dirs:
  `git worktree add --detach <repo-root>/.<name> <ref>`. NEVER place them as
  siblings of the repo
- NEVER use recursive removal, including `rm -r`, `rm -rf`, `rm -R`, or wrapped equivalents - delete only explicitly named files non-recursively, or leave cleanup to the user
- ALWAYS use `/gh-comment` skill for posting PR comments, review comments, or request-changes — it has a mandatory approval gate and never posts without showing content first
- NEVER squash commits - if asked, refuse and request acknowledgement

## Bash / Tool Execution
- NEVER run a command twice to inspect output; tee once and extract:
  `<cmd> 2>&1 | tee out.log && tail -20 out.log`
- NEVER use the `SendFeedback` tool, NEVER draft Claude Code product/model
  feedback, and NEVER suggest the `/feedback` command — banned outright. Say
  nothing about feedback even when a "high-signal moment" seems to arise.

## Scripts
- ALWAYS use fixed working directory, simple relative paths
- NEVER basename $0, __dirname, complex path resolution

## Testing
- `make test`: fast unit tests (<5s), `make test-all`: unit + integration (what CI runs), `make smoke`: production data
- NEVER skip pre-commit checks
- Pre-commit reformats on first run - ALWAYS retry commit (2 attempts)
- Test config objects: match target type exactly, omit unknown properties for type safety
- NEVER re-run tests to analyze output; capture once:
  `make test 2>&1 | tee test.log && tail -8 test.log && grep "FAILED\|failed" test.log`

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
- NEVER marketing language, cut fluff
- NEVER publish to claude.ai hosting — do NOT use the Artifact tool or upload
  any report/page/output to claude.ai. ALWAYS produce local files (HTML, MD)
  the user opens themselves. Local HTML is fine; the online upload is not.
- NEVER reference an earlier version, prior design, or counterfactual in a
  comment, doc, skill, or agent definition — no "used to be", "previously",
  "renamed from", "as before", "instead of X", "no longer", "matching the old
  <name>", or backwards-compat framing. Same bar for temporary-inside-permanent:
  never narrate a transient artifact (a one-off backfill script) into a
  permanent one (a migration, a long-lived module) — that belongs in the
  transient file itself, if anywhere. State only what is true now and its
  genuine quirks; history lives in .diary/
- specs/ directory for specifications, named by content; `specs/index.md` for master index
- .ship/ directory for all shipping artifacts (plans, state, critiques)
  - Flat structure, type in filename: plan-*.md, state-*.md, critique-*.md
  - ALWAYS gitignored, ephemeral working dir
  - Clean after shipping: delete completed artifacts
- .diary/ directory for shipping log (date-named: YYYYMMDD.md)
  - Document important steps, decisions, milestones
  - Named companion `YYYYMMDD-<name>.md` beside the daily log for a standalone
    durable artifact — a report, an audit, a design analysis, a postmortem —
    that a future reader opens on its own; the daily log stays the default
    and the running narrative, and ALWAYS references the companion so it
    remains the index into the day
  - Generally public (checked into git) unless the project's CLAUDE.md marks it local-only
  - ALWAYS use `/diary` skill to write diary entries after significant work
- .claude/ for long-lived knowledge beyond CLAUDE.md
  - Additional *.md files next to CLAUDE.md for overflow context
- NO todos/ directory — use TODO.md at root or plans in .ship/
- NO plans/ directory — plans live in .ship/plan-*.md

## Agents and Skills
- ALWAYS sync ~/.claude/ changes with the bundle source repo (path in LOCAL.md)

### Skill discovery and reconciliation
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
