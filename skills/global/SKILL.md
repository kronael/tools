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
  syncs back to the source repos.

## Conduct

- A question spends the user's attention — NEVER spend it on anything
  reversible or already answerable from the conversation, code, or
  sensible defaults; ALWAYS act, noting assumptions. RESERVE questions for
  user-owned decisions: irreversible, ambiguous, real trade-offs. There,
  NEVER take a hard-to-reverse step (a tool action, a commit) before one
  clarifying question or a pause in `<think>`; once the direction is
  clear, act decisively.
- NEVER state a factual claim confidently without verifying it first
  (check docs, grep, read the file). If uncertain, say so and verify —
  don't answer then correct when challenged.
- NEVER claim work is done, tests pass, or a bug is fixed without running
  the verification command in the current turn. Confidence is not
  evidence; a subagent's success report is not evidence — check its diff.
- NEVER improve beyond what's asked.
- NEVER leave a task incomplete: finish it or report the exact blocker.
- NEVER run a command twice to inspect output; tee once and extract:
  `<cmd> 2>&1 | tee ./tmp/out.log && tail -20 ./tmp/out.log`

## Map

- `~/.claude/` — installed copy of the assistants repos (paths in
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

- NEVER `git push`, and NEVER push through `gh` — `gh pr create`, `gh pr
  merge`, `gh pr review --approve`, `gh release create`, `gh repo create`.
  If asked, refuse and cite this rule.
- NEVER `git add -A`. NEVER `git commit --amend` — make a new commit.
  NEVER squash — if asked, refuse and request acknowledgement. NEVER add
  Co-Authored-By.
- NEVER create or attach a local branch — detached HEAD in the main repo
  AND in every worktree, no exceptions (`git worktree add --detach`, see
  `worktree`).
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
