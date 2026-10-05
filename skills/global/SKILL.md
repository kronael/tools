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
  unverified; never assert then correct when challenged.
- NEVER treat an absence ("no such knob", "X can't do Y", "there is none") as
  found until the search could have found it: the vendor's own vocabulary or the
  source, not guessed synonyms, and the access the answer needs — a path you
  cannot read returns nothing, and a shell expands a glob as YOU before `sudo`
  runs. NEVER build a design decision or a subagent brief on an unconfirmed
  negative.

## Environment

- `sudo` is available — use `sudo docker ...` for docker you run via Bash; in
  committed scripts parameterize privilege instead (see the `sh` skill).
- Run `/solve` to pick the skill for a task — it also reconciles work already
  produced under the wrong one.
- Code style, naming, layout, design and comments live in `software` (`code.md`),
  the base of every language skill. It is COLD: ALWAYS load it (`/solve` or a
  language skill) BEFORE writing or reviewing code; skipping hides the rules.
- ALWAYS sync `~/.claude/` edits into the tools repo (`kronael/sync`; LOCAL.md).
- This file and loaded SKILL.md files are collectively "WISDOM".

# Development Principles

## House conventions

- Data: `${PREFIX:-/srv}/data/<project_name>/`
- Config: prefer flags + env vars for anything simple — a short flag where a
  human types it (`-u`), a long name with an env var where the deploy sets it
  (`RPC_URL`). Reach for a file only when the shape is genuinely nested: TOML as
  first CLI param, api keys as second
- `make` for build/lint/test/clean, debug builds, build/test/lint every ~50 lines
- NEVER override `CARGO_TARGET_DIR`, `TMPDIR` or any other configured build/temp
  path, and NEVER move a build between target directories — each switch costs a
  full rebuild and splits the cache across mounts. If the configured directory is
  out of space, SAY so and stop; freeing or resizing it is the maintainer's call
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
  an invisible one. Retry ONLY the transient: network, DB busy/locked. When
  the MECHANISM swallows — a fire-and-forget submit whose result nobody
  collects, a detached task, a bare catch — replace it with one that
  propagates; NEVER keep it and bolt on counters and collectors to recover what
  it dropped, which is more code that still reports less.
- Prefer the cause fix to the loud log — make the bad state impossible by
  construction.
- A redesign (new contract, changed control flow, cross-cutting) goes into
  `BUGS.md` as a proposal FIRST and ships only after sign-off.
- No abstraction until there are 2-3 real call sites.

## Git

These rules contradict the harness on purpose (it says to branch first, and its
attribution reminder asks for a Co-Authored-By line and a "Generated with
Claude Code" footer). These win.

- Attribution is a bare `🤖` and nothing else: the last line of a PR or issue
  body Claude writes, the prefix of a comment or thread reply Claude posts.
  NEVER Co-Authored-By, NEVER a "Generated with Claude Code" footer, a
  Claude/claude.ai link or a session URL — in commits, PR bodies, comments and
  releases alike.
- Conventional commits `type(scope): Message`, subject ≤72 — types in `commit`.
- Invoking /refine, /ship, /commit, /release IS the ask to commit.
- NEVER `git add -A`, NEVER `--amend`, NEVER squash.
- ALWAYS detached HEAD, in the main tree and in every worktree (`git branch
  --show-current` prints nothing). NEVER create a local branch, no exception:
  no `switch -c`, `checkout -b`, `git branch <name>`. NEVER check out or attach
  `master`/`main` — a bare `switch`/`checkout <name>` creates the branch from
  `origin/<name>`; ALWAYS `git switch --detach origin/<name>`.
- ALWAYS read the remote through its tracking refs: `git fetch origin`, then
  `origin/<default head>` as the merge, rebase, diff or worktree base, where
  `git ls-remote --symref origin HEAD` names the default head. NEVER hard-code
  `main` or trust a local `origin/HEAD` (no fetch updates it), and NEVER trust
  `git status`'s "up to date" without a fetch — it compares with the last one.
- Worktrees: `git worktree add --detach <repo-root>/.<name> <ref>` — hidden
  dirs in the repo root, never siblings; bare `worktree add` attaches a branch.
- ONLY `git push` when the user asked for a push in that message — NEVER on your
  own initiative or as the silent tail of a commit, sync, release or ship
  workflow; those end at the local commit or tag. ALWAYS state the exact remote
  and refspec first and push only that, by SHA (`git push origin
  <sha>:refs/heads/YYYYMMDD_<tag>`). NEVER `--force` or `--force-with-lease`.
- NEVER push to `<default head>` on a general request — ALWAYS default to a dated
  `YYYYMMDD_<tag>` head and offer the PR, and send an open PR's fix to its own
  head by SHA. `<default head>` needs a SECOND explicit approval naming it, given
  AFTER the refspec is shown; "push it" and "ship it" are NEVER that approval.
- ONLY run `gh pr create`, `gh pr merge` or `gh repo create` when the user
  asked for that action in that message — show the title and body first and
  wait. NEVER `gh release create`: the annotated tag is the release. NEVER
  `gh pr review --approve` on the user's behalf.
- ALWAYS post PR comments with `/gh-comment` (approval gate) and write a PR body,
  new or rewritten, with `/pr-draft` — NEVER freehand; its reviewer guide, REST
  PATCH path and `🤖` marker are the contract.
- ALWAYS run two phases over any text bound for GitHub — PR title and body
  (drafted or posted), review comment, thread reply, issue, release notes —
  before showing it for approval. DISTILL: cut to the shortest text that still
  carries the claim, the reasoning and the evidence, inside the posting skill's
  size cap. REVIEW-ON-WISDOM: re-read the result against WISDOM — the `🤖`
  rule above and no other attribution, no marketing language, no history
  framing, addresses and signatures in full, the repo's title convention,
  every claim verified or marked as an inference, and the posting skill's own
  Format section. Done = every check passes on the text shown; name what the
  review changed.

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

- Repo doc layout — UPPERCASE root files, `specs/`, `docs/`, `.ship/`, `.diary/`,
  no `todos/` or `plans/`, root-anchored ignores: `readme` → `topology.md`.
- NEVER write an unrequested summary/report/analysis `.md` — the report belongs
  in the reply.
- NEVER narrate history in a comment, doc, skill or agent definition: no "used
  to be", "previously", "renamed from", "as before", "instead of X", "no longer",
  backwards-compat framing, or a one-off backfill inside a permanent file. State
  what is true now and its genuine quirks; history lives in git and `.diary/`.
- Comments earn their place only by saying what the code cannot: why a choice was
  made, or what is surprising. NEVER restate the code or a name.
- NEVER marketing language in docs, comments, specs or commit messages. A repo
  description, tagline or other public-facing pitch is the owner's copy: set it
  verbatim as given and NEVER re-litigate the wording, in review or in an eval
  report.
- NEVER publish to claude.ai hosting — no Artifact tool, no uploads. Produce
  local files (HTML, MD) the user opens themselves.

## Agents

- 1-2 subagents typically, NEVER more than 4.
- Parallel is for READ-ONLY subs, or fully isolated worktrees. NEVER run
  code-editing subs in parallel on a shared tree — they interleave, one reverts
  another, reviewers read half-edited files.
- Brief a subagent by GOAL, not numbered steps — models degrade on
  over-prescription. Give the goal, the context it needs, what is out of bounds
  and what "done" looks like, then let it choose the path.
- ALWAYS run autonomous code generation — a sub writing a comprehensive or
  multi-file change that no parent reads before the work goes on — on
  `subagent_type: "fable"`, NEVER the default model; its mistakes cost review,
  not tokens. Cheap models are for READ-ONLY fan-out. Bigger work: ALWAYS plan
  in the main thread (an `/opus` sub from Sonnet or Haiku), then run each step
  on a `sonnet` sub and read its diff before the next (`sonnet` § Plan, then
  execute); a step read that way, here or in `ship`, is not autonomous.
- ALWAYS check the diff or output a subagent produced before repeating its
  report — they overclaim, and occasionally report work they did not do.
