# Skills

Auto-activating context for Claude Code. Each `<name>/SKILL.md` loads
when its description matches the current task. Some are user-invocable
as slash commands (`/refine`, `/diary`, ...).

## Why these exist

LLMs forget. Every conversation starts cold, every long generation
drifts from the rules, and the right skill rarely fires on its own.
Each skill in this directory addresses one of five problems:

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
- **recall-memories**: explicit search across diary + memory + Claude
  Code and Codex session records, down to single tool and agent results,
  so an earlier run is reused instead of repeated. `recall.py` beside the
  skill parses the records. Memory and diary don't auto-fire on relevant
  prompts — recall-memories is the "look it up" verb.

## Multi-pass refinement (refine, improve, readme)

LLMs drift from CLAUDE.md and codestyle on a single pass. Even when
the rules are loaded, a long generation introduces noise: extra
comments, inconsistent naming, broken imports, stale doc counts.
Refinement is a deliberate second pass that re-reads the rules with
the diff visible.

- **improve**: DO → CRITICIZE → EVALUATE → IMPROVE on changed code
- **readme**: sync README/ARCHITECTURE/CHANGELOG with what shipped
- **refine**: orchestrates both, validates build/test, commits `refa: …`

Reach for these when: about to PR, after a feature lands, after a
long generation pass.

## Shortcuts (fin, dispatch)

Macros for instructions you'd otherwise type out every time:

- **fin**: "finish all pending tasks without stopping for confirmation"
- **dispatch**: "spawn this prompt as a background subagent and continue"
- **next**: "park a discovered bug/TODO for later without stopping current work"
- **ans**: "answer-only read-only mode — explain, never edit files or run shell"
- **continue**: "resume every interrupted/paused task; if none, confirm the session is clean, suggest /recall-memories, and present where to go next"
- **sweep**: "dispatch a background audit for one bug category across the whole repo, filing each hit in BUGS.md"

These don't add new behavior — they're aliases. The win is muscle
memory: `/fin` is faster than retyping the rule.

## Discovery nudging (hooks, not skills)

Skills auto-activate by description match, but in practice the LLM
often misses the right one. Hooks add explicit nudges: keyword →
skill routing on prompt submit, file extension → language skill
on file touch, commit/diary checks on stop. Without them the LLM picks
the wrong skill or none. With them, common workflows surface
automatically. The hook list and wiring live in `../hooks/README.md`.

## Skill categories

A hand-maintained per-skill table drifts the moment a skill lands, so
there isn't one. **Run `ls skills/` for the full set** — each dir has a
`SKILL.md` whose frontmatter (`name`, `description`, `when_to_use`) is
the authoritative entry. The categories:

- **Languages** (`go`, `py`, `rs`, `sh`, `sql`, `ts`, `tsx`) —
  codestyle only: naming, idioms, test layout, build flags.
- **Domain** (e.g. `cli`, `service`, `data`, `ops`, `solana`,
  `browse`, `diagrams`, `show-me`, `astgrep`, `demo`, `ingest`, `emacs`) —
  patterns for a kind of program or tool. They compose with language skills: a
  Rust CLI loads `rs` + `cli`; a structural codemod loads `astgrep` + the target
  language. `ingest` (any file → Markdown via `uvx markitdown`; URL →
  transcript/audio/video via `yt-dlp`) is adapted from
  [steipete/agent-scripts](https://github.com/steipete/agent-scripts). `show-me`
  (opt-in `/show-me` — pseudocode/call-tree/mermaid/diff/local-HTML for the
  current conversation topic, distinct from `diagrams`' permanent ASCII docs)
  is ported from [humanlayer/skills](https://github.com/humanlayer/skills).
- **Workflow** (e.g. `solve`, `commit`, `diary`, `refine`, `review`, `ship`,
  `release`, `specs`, `merge`, `squash`, `bugs`, `recall-memories`, `wisdom`,
  `scavenge`, `astra`, `pi`) — triage, multi-pass refinement, git flow,
  memory, scaffolding, second opinions, codifying public best practice.
- **Escalation** (`sonnet`, `terra`, `opus`, `fable`, `dispatch`, `fin`) — model
  routing and macro aliases. Each model tier has its own skill; `dispatch` is
  fire-and-forget at default model. `terra` runs the Codex workhorse through
  a native subagent or the CLI. Model and effort pins follow
  [`CLAUDE.md` § Agent definitions](CLAUDE.md#agent-definitions).
- **Evaluation lenses** (`eval/` — CEO, CTO, red team, design craft, novice
  UX, hiring, or every lens at once) — judge a product, codebase, UI or
  engineer from a fixed perspective.
- **Routers** (`create/`, `software/`, `specs/`, `readme/`, `review/`,
  `research/`, `writing/`, `eval/`) — one preloaded
  `SKILL.md` dispatching to cold data files read on demand. `create/` holds the
  creative artifact generators (HTML, SVG, ASCII, video), mostly ported
  from
  [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/tree/main/skills/creative)
  and **local-only** — generators needing paid APIs, cloud accounts, or
  external apps were dropped; local CLI deps (ffmpeg, manim) are fine.
  `software/` holds engineering runbooks for code, tests, CI, typing, deploys,
  observability, and the attribution/NOTICE practice for ported work
  (`credits.md`); `specs/` the design record; `readme/` syncs docs after
  shipping and holds the doc file topology, single-page shape and the HTML
  pages (onepager, doc page); `review/` gives or takes a code review;
  `research/` holds the quantitative-research runbooks: method (evidence),
  layout (organisation), traps (silent wrong numbers). Structure rules:
  [`CLAUDE.md`](CLAUDE.md) in this directory.
- **Shared references** (`writing`, `humanize`) —
  `writing` owns the prose rules and, in its cold `page.md`, how a document or
  page is laid out; `humanize` is the AI-tells catalogue it finishes with; both
  cited by `tweet`, `pr-draft`, `readme`, `diary`. The response style itself is
  `../output-styles/caveman.md`, applied or reverted per session by
  `../commands/caveman.md`.
- **`global`** — special case, not installed as a skill: its body
  becomes the wisdom file `~/.claude/CLAUDE.md` at install.

## Skill workflow diagram

Skills cluster into phases. Main spine: orientation → planning → coding → quality → output.
Side-channels (escalation, communication) fire at any stage.

┌─ orientation ───────────────┐
│ solve recall-memories       │
│ ans                         │
└──────────────┬──────────────┘
               │
┌─ planning ───▼──────────────┐
│ specs ship                  │
└──────────────┬──────────────┘
               │
┌─ coding ─────▼──────────────┐
│ go rs py ts tsx sh sql cli  │         ┌─ escalation ────────┐
│ service data                ├────────►│ sonnet terra opus   │
└──────────────┬──────────────┘         │ fable dispatch fin  │
               │                        └─────────────────────┘
┌─ quality ────▼──────────────┐
│ review improve              │
│ refine visual software bugs │
└──────────────┬──────────────┘
               │
┌─ output ─────▼──────────────┐         ┌─ communication ─────┐
│ commit pr-draft release     │         │ diary readme wisdom │
│ gh-comment                  ├────────►│ learn tweet         │
└─────────────────────────────┘         └─────────────────────┘

**orientation** — load context before acting. `solve` is the universal entry point;
`recall-memories` searches diary/memory/sessions; `ans` answers without modifying.

**planning** — `specs` for design docs; `ship` to drive a change end to end, mostly unattended.
Skip for one-off tasks.

**coding** — language skills (go, rs, py, ts, tsx, sh, sql) carry per-language rules;
shape skills (cli, service, data) carry patterns for what you're building.
They compose: a Rust CLI loads `rs` + `cli`.

**quality** — `review` covers the whole loop: `review give` produces findings
(local diff, or a GitHub PR with `gh`), `review take` applies them (a local list
or a PR's comments); it supersedes the built-in `/code-review` for local work.
`improve` for a targeted fix; `refine` for the finalizing pass — read-only
subagents per context of the change, and every claim it makes re-derived
against the tree; `visual` for UI; `software` (`testing.md`) for test
patterns; `bugs` for the record-don't-fix queue.

**output** — `commit`, `pr-draft`, `release`, `gh-comment`, `gh-issue`. Use once work is verified.

**communication** — fires after milestones at any stage. `diary` logs decisions;
`readme` syncs docs; `wisdom` edits skills; `learn` mines history; `tweet` drafts threads.

**escalation** — route to the right model/mode from any stage. `/sonnet` →
`/opus` → `/fable` increases the Claude tier. `/terra` selects the
Codex workhorse. `/dispatch` uses the default model. `fin` runs without
confirmation stops.

## Working with skills

- Each `SKILL.md` has YAML frontmatter: `name`, `description` and
  `when_to_use` required (lint hard-fails without them), `user-invocable`
  optional
- Every skill is a `/<name>` slash command by default; `user-invocable: false`
  hides it from the `/` menu
- Auto-activation matches `description` + `when_to_use` — make them specific
- See `wisdom/SKILL.md` for the writing rules
