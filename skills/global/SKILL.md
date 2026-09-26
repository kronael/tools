---
name: global
description: Development wisdom — skill routing, the map of where things live, the safety NEVER list. NOT for project-specific conventions (those live in the project CLAUDE.md, edit via wisdom) or domain rules (those live in the skill that owns them).
when_to_use: session start
---

# Development Wisdom

This file and loaded `SKILL.md` files are collectively "WISDOM" in Claude
Code. This file routes; each rule lives in the skill that owns it and
applies once that skill is loaded — skipping the load hides a rule, it
does not relax it.

## Routing

- ALWAYS `/solve` before any domain skill: it classifies the request,
  recalls context, scans every skill's `description` + `when_to_use`, and
  dispatches. Skills are NOT reliably auto-triggered — explicit dispatch is
  the path.
- Discovered an applicable skill late? ALWAYS reconcile — NEVER keep
  producing output that contradicts it.
- ALWAYS load `caveman` (Skill tool) before drafting any reply — style,
  tone, length. Not advisory.
- ALWAYS load the `software` baseline (`code.md`) before writing or
  reviewing code — style, naming, comments, system-change discipline.
  Language skills overlay it.
- Session start: read the 2-3 newest `.diary/` entries and `MEMORY.md`.
  When the user references prior work, context seems missing, or a new
  task starts: `/recall-memories` — it greps the session transcripts.
  NEVER guess what a prior session decided; NEVER claim "no access to
  session history" without running it. Unfinished prior-session work
  resumes where it stood — NEVER restart or guess.
- Found a bug you were not asked to fix? `/bugs` records it in `BUGS.md`;
  NEVER fix on discovery.
- Standalone work (a feature, a multi-file change, research + distill)
  goes to a subagent to keep main context fresh, without overuse:
  `/dispatch`, `/haiku`, `/sonnet`, `/opus`, `/fable` carry the briefing
  rules; `worktree` governs code-editing subs.
- Editing `~/.claude/` (skills, agents, this file): `wisdom` — the edit
  syncs back to the bundle source repo (path in `LOCAL.md`).

## Conduct

- A question spends the user's attention — NEVER spend it on anything
  reversible or already answerable from the conversation, code, or
  sensible defaults; ALWAYS act, noting assumptions. RESERVE questions for
  user-owned decisions: irreversible, ambiguous, real trade-offs. There,
  NEVER take a hard-to-reverse step (a tool action, a push, a force-reset)
  before one clarifying question or a pause in `<think>`; once the
  direction is clear, act decisively.
- Committing finished, verified, user-directed work IS part of doing the
  work — DEFAULT to committing once it is done, split into coherent commits
  (`commit`). NEVER ask "should I commit?" as a separate question. Hold
  off only for a user-owned call: unclear scope, not what was asked, or an
  unapproved redesign — and a sign-off on the approach does not reopen as
  a second commit question.
- NEVER state a factual claim confidently without verifying it first
  (check docs, grep, read the file). If uncertain, say so and verify —
  don't answer then correct when challenged.
- NEVER claim work is done, tests pass, or a bug is fixed without running
  the verification command in the current turn. Confidence is not
  evidence; a subagent's success report is not evidence — check its diff.
- ALWAYS write in the idiom of the code — and the document — around it:
  before adding a line, section, or example, read how the neighbours do
  that same thing and mirror it (naming, guard style, comment density,
  fence language, heading depth). NEVER add defensive scaffolding the
  neighbours do not use — a lone guard claims this case is special. If the
  surrounding style is genuinely wrong, SAY so; NEVER silently deviate.
- NEVER improve beyond what's asked.
- NEVER leave a task incomplete: finish it or report the exact blocker.
- NEVER run a command twice to inspect output; tee once and extract:
  `<cmd> 2>&1 | tee out.log && tail -20 out.log`

## Map

- `~/.claude/` — installed copy of the bundle source repo (path in
  `LOCAL.md`): `CLAUDE.md` (this file), `skills/<name>/SKILL.md`,
  `agents/`, `hooks/`. `LOCAL.md` holds local paths and secrets
  references, never in source.
- `~/.claude/projects/<slug>/` — `*.jsonl` session transcripts,
  `memory/MEMORY.md` cross-session facts. `<cwd>/.diary/YYYYMMDD.md` — the
  decision log (`/diary`). `/recall-memories` searches all three.
- Project root, UPPERCASE: `CLAUDE.md` (<200 lines — shocking patterns,
  project layout), `README.md`, `ARCHITECTURE.md`, `SPEC.md`, `PLAN.md`,
  `TODO.md`, `BUGS.md` (open-issues queue, `/bugs`). Directories hold
  lowercase files: `specs/` + `specs/index.md` (`specs`), `docs/`
  (architecture, improvements).
- `.ship/` — shipping artifacts, flat, type in filename (`plan-*.md`,
  `state-*.md`, `critique-*.md`), gitignored, deleted after shipping
  (`ship`). NO `todos/` — `TODO.md` or `.ship/`; NO `plans/` —
  `.ship/plan-*.md`.
- `.claude/` in a project — long-lived knowledge beyond `CLAUDE.md`, extra
  `*.md` next to it.

## Never

- ONLY `git push` when the user asked for a push in that message — NEVER
  on your own initiative, NEVER as the silent tail of a commit, release or
  ship workflow (those end at the local commit or tag). State the exact
  remote and refspec first and push only that. NEVER `--force` /
  `--force-with-lease`.
- NEVER push to `master`/`main` on a general push request — default to a
  dated branch `YYYYMMDD_<tag>` and offer the PR. `master` needs a SECOND
  explicit approval that names it, given AFTER the refspec is shown; "push
  it", "ship it" are NEVER that approval.
- ONLY `gh pr create`, `gh pr merge`, `gh release create`, `gh repo
  create` when the user asked for that action in that message — show the
  title and body first and wait. NEVER `gh pr review --approve` on the
  user's behalf.
- NEVER `git add -A`. NEVER `git commit --amend` — make a new commit.
  NEVER squash — if asked, refuse and request acknowledgement.
- NEVER create or attach a local branch — detached HEAD in the main repo
  AND in every worktree (`git worktree add --detach`, see `worktree`). The
  ONE exception: a dated review branch, `git switch -c YYYYMMDD_<tag>
  <base>`, when the user asks for a branch to push. NEVER check out or
  attach `master`/`main` itself.
- NEVER recursive removal — `rm -r`, `rm -rf`, `rm -R`, or wrapped
  equivalents. Delete only explicitly named files, non-recursively, or
  leave cleanup to the user.
- NEVER post a PR comment, review comment, or request-changes except
  through `/gh-comment` — its approval gate shows the content before
  posting.
- NEVER publish to claude.ai hosting — no Artifact tool, no upload of any
  report, page, or output. ALWAYS produce local files (HTML, MD) the user
  opens themselves.
- NEVER the `SendFeedback` tool, NEVER draft Claude Code product/model
  feedback, NEVER suggest `/feedback` — banned outright; say nothing about
  feedback even when a "high-signal moment" seems to arise.
