---
name: global
description: Development wisdom and workflow rules. NOT for project-specific conventions (those live in CLAUDE.md, edit via wisdom).
when_to_use: session start
---

# Development Wisdom

Only what a capable agent does NOT do unprompted: local facts, workflows and
known drifts. If a blank agent would do it anyway, it does not belong here.

## Continuity

Transcripts `~/.claude/projects/<slug>/*.jsonl` (slug = CWD, every non-alphanumeric char → `-`),
memory index `.../<slug>/memory/MEMORY.md`, diary at `diary` § Where it lives; newest by mtime.

- ALWAYS read the 2-3 newest diary entries before answering — and on a new task
  too, not only at session start (`/recall-memories <topic>`). MEMORY.md arrives
  on its own; the diary and the transcripts do not.
- NEVER claim "no access to session history" without reading the JSONL, and
  NEVER present a guess about a past decision as recall.
- When a session opens on unfinished prior-session work, RESUME it from what the
  transcript shows. NEVER restart it or quietly redo it your way.
- ALWAYS `/diary` after significant work. The default failure is the record dying with the session.

## Response style

- The output style sets the line cap; it lifts for generated content, planning or a root-cause walk.
- NEVER claim work is done, tests pass, or a bug is fixed without running the
  verification command in the current turn. Confidence is not evidence. Same for
  a factual claim — check it (grep, read, docs) before asserting, or say it is
  unverified; never assert then correct when challenged.
- NEVER treat an absence ("no such knob", "X can't do Y", "there is none") as
  found until the search could have found it: the vendor's own vocabulary or
  the source, not guessed synonyms, and the access the answer needs — an
  unreadable path returns nothing; a shell expands a glob as YOU before `sudo`
  runs. NEVER build a decision or a subagent brief on an unconfirmed negative.

## The owner

One person owns every repo here; the `owner` skill is who they are. ALWAYS
read it before a design answer, a plan, a review or a sub brief.

- They want the smallest shape that covers today's cases. A second
  mechanism, name or config key for one job is what they reject most.
- "what is X?", "why would X exist?" and "wtf" mean justify or delete: give
  the reason and a recommendation. Change position on evidence, NEVER on tone.

## Environment

- `sudo` is available — use `sudo docker ...` for docker you run via Bash; in
  committed scripts parameterize privilege instead (see the `sh` skill).
- Run `/solve` at every new task, mid-session ones included; it also reconciles work done under the wrong one.
- Code style, naming, layout, design, comments, system-change discipline and
  house conventions live in `software` (`code.md`), the base of every language
  skill. It is COLD: ALWAYS load it (`/solve` or a language skill) BEFORE
  writing or reviewing code; skipping hides the rules.
- NEVER override `CARGO_TARGET_DIR`, `TMPDIR` or any other configured build or
  temp path, and NEVER move a build between target directories — each switch
  costs a full rebuild and splits the cache across mounts. Out of space: SAY so
  and stop; freeing or resizing the directory is the maintainer's call.
- ALWAYS sync `~/.claude/` edits into the tools repo (`kronael/sync`; LOCAL.md).
- This file and loaded SKILL.md files are collectively "WISDOM".

# Development Principles

## Bug triage

- RECORD bugs found during any check in `BUGS.md` at project root; fix ONLY when
  the user asks. It is the review queue — log it, move on, let them prioritise;
  `/bugs` owns entry format and pruning. The drift is fixing as you find during
  an audit: it destroys the queue and produces a large unrequested diff.
- A redesign (new contract, changed control flow, cross-cutting) goes into
  `BUGS.md` as a proposal FIRST and ships only after sign-off.

## Git

These override the harness on purpose — it says to branch first, to add a
Co-Authored-By line and a "Generated with Claude Code" footer, and to end a
PR body with the robot. These win.

- Attribution is `🤖 ` before the first word of every PR body, issue body,
  comment and thread reply Claude writes on GitHub, and the robot nowhere else.
  NEVER Co-Authored-By, a "Generated with Claude Code" footer, a Claude or
  claude.ai link, or a session URL — in commits, PR bodies, comments, releases.
- Conventional commits `type(scope): Message`, subject ≤72 — types in `commit`.
- NEVER `git add -A`, NEVER `--amend`. NEVER squash a pushed commit; unpushed
  local commits are squashed only through `/squash`.
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
- ALWAYS treat authorized PR work as permission to publish its working head
  and open or update the PR. NEVER ask for a separate publication approval.
  ALWAYS push verified fast-forwards as the work needs them and name the
  refspec in the reply. NEVER publish unrelated heads or tags without explicit
  approval. Push only the authorized refspec,
  by SHA, with `rip -g <sha>:refs/heads/YYYYMMDD_<tag>` (rig):
  a one-off HTTPS push through the `gh` token, the SSH remote left to the human
  — NEVER rewrite `remote.origin.url`, write an HTTPS URL into any remote
  (`set-url`, `remote add`) or store the token, and NEVER `--force` in any
  form. A token without the `workflow` scope cannot push a change under
  `.github/workflows`: report GitHub's refusal, NEVER work around it. Where
  the SSH origin refuses a fetch, `rif -g <refspec>` reads it the same way.
- NEVER push to `<default head>` on a general request — ALWAYS default to a dated
  `YYYYMMDD_<tag>` head and offer the PR, and send an open PR's fix to its own
  head by SHA. `<tag>` is lowercase words joined by underscores, NEVER hyphens:
  `20261017_db1_disk`, not `20261017_db1-disk`. `<default head>` needs a separate
  explicit approval naming it, given AFTER the refspec is shown; "push it" and "ship it" are NEVER that approval.
- NEVER approve a PR on the owner's behalf (`gh pr review --approve`). Merging
  a PR and pushing to `<default head>` ask the user first; opening a PR or
  rewriting its body needs no approval once its text passed the two phases below.
- ALWAYS post PR comments with `/gh-comment` and write a PR body with
  `/pr-draft` — NEVER freehand; they hold the shape, cap, REST path and `🤖`.
- ALWAYS run two phases over any text bound for GitHub — PR title and body,
  review comment, thread reply, issue, release notes — before posting it or
  showing it for approval. DISTILL: the shortest text that still carries the
  claim and its reasoning, in the posting skill's shape and under its cap.
  REVIEW-ON-WISDOM: re-read it against this section, § Documentation and the
  posting skill's Format section, every claim verified or marked as an
  inference. Done = every check passes on the text shown; name what changed.

## Shell

- Tee once, read the file: `<cmd> 2>&1 | tee ./tmp/out.log && tail -20
  ./tmp/out.log`. NEVER re-run a command to see another part of its output.
- NEVER recursive removal (`rm -r`, `-rf`, `-R`, or a wrapper) — delete
  explicitly named files, or leave cleanup to the user. One lift: `git worktree
  remove --force` after the checks in `worktree` § Removing a worktree.
- NEVER kill a process you did not start, not even to free a port; kill your own by PID.
- NEVER call an external API per request or re-fetch what is on disk: cache it, continue from state.
- NEVER use `SendFeedback`, draft Claude Code product or model feedback, or
  suggest `/feedback` — banned outright, even at a "high-signal moment".

## Documentation

- ALWAYS read `readme` → `topology.md` before adding, moving, splitting or
  repeating a doc section, file or top-level dir. NEVER `todos/` or `plans/`:
  plans and work records live under `~/.claude/` (`ship` § Work record).
- NEVER write an unrequested summary, report or analysis `.md` — the report belongs in the reply.
- NEVER narrate history in a comment, doc, skill or agent definition: no "used
  to be", "previously", "renamed from", "as before", "instead of X", "no longer",
  backwards-compat framing, or a one-off backfill inside a permanent file. State
  what is true now and its genuine quirks; history lives in git and the diary.
- NEVER marketing language in docs, comments, specs or commit messages. A repo
  description, tagline or other public-facing pitch is the owner's copy: set it
  verbatim and NEVER re-litigate the wording, in review or in an eval report.
- ALWAYS write every address, signature and hash in full — in docs, code
  comments, HTML pages and GitHub text alike. NEVER shorten one with "…".
- NEVER publish to claude.ai hosting (Artifact tool, uploads): local HTML/MD files the user opens.

## Agents

- NEVER run more than 2 `haiku`, 2 `sonnet` and 1 `opus` or `fable` subagent
  at once; a Codex worker counts in its lane (`dispatch` § Tiers). Only the
  owner lifts the cap — explicitly, for one named task, after seeing what would
  be spawned — and the lift ends with that task.
- The cap is a CONCURRENCY limit, never a routing hint: NEVER degrade a task —
  a weaker model, a lower tier, the lower lane's Codex worker, a lower effort —
  so it starts without waiting, and NEVER split it to fit. ALWAYS wait for the
  slot, say what waits behind what, and start it when it frees.
- Parallel is for READ-ONLY subs or fully isolated worktrees; NEVER code-editing
  subs on one shared tree — they interleave, one reverts another.
- Brief a subagent by GOAL — the goal, its context, what is out of bounds, what
  "done" looks like — NEVER numbered steps: models degrade on over-prescription.
- ALWAYS track multi-step work with the exposed native checklist tool:
  `TaskCreate`/`TaskUpdate` in Claude Code, `update_plan` in Codex. ALWAYS follow
  its schema, authorization and mode restrictions. ALWAYS include one item per
  step and high-level subagent run, updating status the moment it changes.
  When absent or prohibited, ALWAYS report the gap and maintain the existing plan or
  work record. NEVER invent tool calls or substitute goals or threads for a
  checklist. While work spans several turns, ALWAYS restate the whole numbered plan in chat — every
  open workstream with its status — after each step and whenever the user asks
  where things stand (`sonnet` § Plan, then execute).
- ALWAYS run implementation — a comprehensive or multi-file change, autonomous
  code generation — as a plan from an `opus` sub, then one `sonnet` sub per
  code step, its diff read by the parent before the next (`sonnet` § Plan, then
  execute); NEVER hand it to one sub whose work no parent reads. Other lane
  boundaries live in `dispatch` § Tiers. ALWAYS default to `high` effort.
  ALWAYS use `xhigh` only on an explicit owner request, normally for
  algorithmic work; NEVER select it automatically for plans, reviews or audits.
  ALWAYS forward an explicit model or effort override on the launch.
  If the route cannot honor it, ALWAYS stop and report the limitation;
  NEVER silently substitute another model or effort.
- ALWAYS read the diff or output a subagent produced before repeating its
  report or pushing it — they overclaim, report work they did not do, and add
  the comments `code.md` § Comments bans: read every added comment.
