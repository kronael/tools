---
name: global
description: Development wisdom and workflow rules. NOT for project-specific conventions (those live in CLAUDE.md, edit via wisdom).
when_to_use: session start
---

# Development Wisdom

Only what a capable agent does NOT do unprompted: local facts, workflows, and
the known drifts. Generic good practice is deliberately absent — if a blank
agent would do it anyway, it does not belong here.

## Continuity

Transcripts `~/.claude/projects/<slug>/*.jsonl` (slug = CWD with `/` → `-`),
memory index `.../<slug>/memory/MEMORY.md`, diary `<cwd>/.diary/*.md`. Newest by
mtime.

- ALWAYS read the 2-3 newest diary entries before answering — and on a new task
  too, not only at session start (`/recall-memories <topic>`). MEMORY.md arrives
  on its own; the diary and the transcripts do not.
- NEVER claim "no access to session history" without reading the JSONL, and
  NEVER present a guess about a past decision as recall.
- When a session opens on unfinished prior-session work, RESUME it from what the
  transcript shows. NEVER restart it or quietly redo it your way.
- ALWAYS `/diary` after significant work. The default failure is the record
  dying with the session.

## Response style

- The line cap and answer-first shape come from the output style. What it does
  not cover: the cap lifts for content you were asked to generate, planning you
  were asked to show, or a root cause you were asked to walk through.
- NEVER claim work is done, tests pass, or a bug is fixed without running the
  verification command in the current turn. Confidence is not evidence. Same for
  a factual claim — check it (grep, read, docs) before asserting, or say it is
  unverified; never assert then correct when challenged. An absence claim ("no
  such knob", "X can't do Y") is only as strong as the search behind it — a
  self-designed grep for guessed synonyms can miss the vendor's own word for it,
  so verify the vendor's actual vocabulary (or read the source) before asserting
  the negative.

## Environment

- `sudo` is available — use `sudo docker ...` for docker you run via Bash; in
  committed scripts parameterize privilege instead (see the `sh` skill).
- Run `/resolve` to pick the skill for a task — it also reconciles work already
  produced under the wrong one.
- Code style, naming, layout, design and comments live in the `software` skill
  (`code.md`), the base every language skill pulls in. That content is COLD —
  invisible until loaded, and skipping the load hides the rules rather than
  relaxing them. ALWAYS load it (`/resolve`, or a language skill) BEFORE writing
  or reviewing code.
- ALWAYS sync `~/.claude/` changes into the tools repo (paths in LOCAL.md).
- This file and loaded SKILL.md files are collectively "WISDOM".

# Development Principles

## House conventions

- Data: `${PREFIX:-/srv}/data/<project_name>/`
- Config: prefer flags + env vars for anything simple — a short flag where a
  human types it (`-u`), a long name with an env var where the deploy sets it
  (`RPC_URL`). Reach for a file only when the shape is genuinely nested: TOML as
  first CLI param, api keys as second
- `make` for build/lint/test/clean, debug builds, build/test/lint every ~50 lines
- `make test` = fast unit (<5s); `make test-all` = unit + integration, what CI
  runs; `make smoke` = production data
- Pre-commit reformats on first run — ALWAYS retry the commit (2 attempts).
  NEVER skip the checks

## Bug triage

- RECORD bugs found during any check in `BUGS.md` at project root; fix ONLY when
  the user asks. It is the review queue — log it, move on, let them prioritise.
  Use `/bugs` for entry format and pruning.
- The drift is fixing as you find during an audit: it destroys the queue and
  produces a large unrequested diff.

## System-change discipline

- Grep for the existing mechanism (guard, helper, table, log site, config)
  before adding one, and extend the ORIGINAL. NEVER a parallel second path — two
  paths drift. If the original is wrong, fix it or say so; NEVER route around it.
- Fail loud, to the user: an error on a user-facing path MUST surface (thrown,
  non-2xx, delivered), not just logged. NEVER swallow it, and NEVER add
  retry/fallback/best-effort as "robustness" — that turns a visible failure into
  an invisible one. Retry ONLY the transient: network, DB busy/locked.
- Prefer the cause fix to the loud log — make the bad state impossible by
  construction.
- A redesign (new contract, changed control flow, cross-cutting) goes into
  `BUGS.md` as a proposal FIRST and ships only after sign-off.
- No abstraction until there are 2-3 real call sites.

## Git

The first four rules here contradict the harness on purpose (it says to branch
first, to use `gh` for GitHub work, and to append a Co-Authored-By line). These win.

- Conventional commits: `type(scope): message` —
  fix/feat/docs/test/chore/refactor, `merge:`/`release:` for those. Subject ≤72.
- Invoking /refine, /ship, /commit, /release IS the ask to commit.
- NEVER `git add -A`, NEVER `--amend`, NEVER squash, NEVER Co-Authored-By.
- ALWAYS detached HEAD — NEVER create or attach a local branch, in the main repo
  or in any worktree. For PR work:
  `git worktree add --detach <repo-root>/.<name> <ref>` — bare `git worktree add`
  attaches a branch, and worktrees live inside the repo root as hidden dirs,
  never as siblings.
- NEVER `git push`; NEVER let `gh` write to a remote (`pr create/merge`,
  `pr review --approve`, `release create`, `repo create`) — refuse, cite this
  rule, and hand over the `! <command>`.
- Both push rules are defaults a repo can lift, but only in writing and in that
  repo (its `CLAUDE.md`, its `.claude/`, or a project memory naming it), and only
  for what the grant names. An in-session ask is not a grant.
- ALWAYS use `/gh-comment` for PR comments — it has an approval gate.
- `git status`'s "up to date with origin/main" only means the local
  remote-tracking ref is current, not the live remote — it will say this even
  months after the real upstream moved on. ALWAYS `git fetch` (or check the
  host directly) before trusting it, not only at session start.

## Shell

- Tee once, read the file: `<cmd> 2>&1 | tee ./tmp/out.log && tail -20
  ./tmp/out.log`. NEVER re-run a command to see another part of its output.
- NEVER recursive removal (`rm -r`, `-rf`, `-R`, or a wrapper) — delete
  explicitly named files, or leave cleanup to the user.
- NEVER `killall`/`pkill` by name — kill by PID. ALWAYS handle SIGINT/SIGTERM in
  anything long-running.
- NEVER hit an external API per request, and NEVER re-fetch what is already on
  disk — cache it, continue from last state.
- NEVER use the `SendFeedback` tool, NEVER draft Claude Code product or model
  feedback, and NEVER suggest `/feedback` — banned outright, and say nothing
  about feedback even when a "high-signal moment" seems to arise.

## Documentation

- UPPERCASE at root: CLAUDE.md, README.md, ARCHITECTURE.md, SPEC.md, PLAN.md,
  TODO.md. CLAUDE.md under 200 lines: shocking patterns and project layout.
- `specs/` for design docs (`specs/index.md` the master index), `docs/` for
  project documentation, `.ship/` for shipping artifacts (flat, type in the
  filename, ephemeral), `.diary/YYYYMMDD.md` for the shipping log. NO `todos/`,
  NO `plans/`.
- ALWAYS root-anchor the gitignore rules for local working dirs: `/.ship/`,
  `/.diary/`, `/specs/`, `/BUGS.md`. The bare `.ship/` form matches at every
  depth and swallows a real `src/specs/`.
- NEVER write an unrequested summary/report/analysis `.md` — the report belongs
  in the reply.
- NEVER reference an earlier version, prior design or counterfactual in a
  comment, doc, skill or agent definition — no "used to be", "previously",
  "renamed from", "as before", "instead of X", "no longer", or backwards-compat
  framing. Same bar for temporary-inside-permanent: never narrate a transient
  artifact (a one-off backfill) into a permanent one. State what is true now and
  its genuine quirks; history lives in git and `.diary/`.
- Comments earn their place only by saying what the code cannot: why a choice was
  made, or what is surprising. NEVER restate the code or a name.
- NEVER marketing language.
- NEVER publish to claude.ai hosting — no Artifact tool, no uploads. Produce
  local files (HTML, MD) the user opens themselves.

## Agents

- 1-2 subagents typically, NEVER more than 4.
- Parallel is for READ-ONLY subs, or fully isolated worktrees. NEVER run
  code-editing subs in parallel on a shared tree — they interleave, one reverts
  another, reviewers read half-edited files.
- ALWAYS check the diff or output a subagent produced before repeating its
  report — they overclaim, and occasionally report work they did not do.
