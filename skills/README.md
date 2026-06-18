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
- **recall-memories**: explicit search across diary + memory + recent
  session transcripts. Memory and diary don't auto-fire on relevant
  prompts — recall-memories is the "look it up" verb.

## Multi-pass refinement (refine, improve, readme)

LLMs drift from CLAUDE.md and codestyle on a single pass. Even when
the rules are loaded, a long generation introduces noise: extra
comments, inconsistent naming, broken imports, stale doc counts.
Refinement is a deliberate second pass that re-reads the rules with
the diff visible.

- **improve**: DO → CRITICIZE → EVALUATE → IMPROVE on changed code
- **readme**: sync README/ARCHITECTURE/CHANGELOG with what shipped
- **refine**: orchestrates both, validates build/test, commits `[refined]`

Reach for these when: about to PR, after a feature lands, after a
long generation pass.

## Shortcuts (fin, sub)

Macros for instructions you'd otherwise type out every time:

- **fin**: "finish all pending tasks without stopping for confirmation"
- **sub**: "spawn this prompt as a background subagent and continue"

These don't add new behavior — they're aliases. The win is muscle
memory: `/fin` is faster than retyping the rule.

## Discovery nudging (hooks, not skills)

Skills auto-activate by description match, but in practice the LLM
often misses the right one. Hooks add explicit nudges: keyword →
skill/agent routing on prompt submit, file extension → language skill
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
- **Domain** (e.g. `cli`, `service`, `data`, `ops`, `trader`,
  `testing`, `browse`, `diagrams`) — patterns for a kind of program.
  They compose with language skills: a Rust CLI loads `rs` + `cli`.
- **Workflow** (e.g. `commit`, `diary`, `refine`, `review`, `ship`,
  `release`, `specs`, `merge`, `bugs`, `recall-memories`, `wisdom`,
  `scavenge`, `codex`) — multi-pass refinement, git flow, memory,
  scaffolding, second opinions, codifying public best practice.
- **Escalation** (`haiku`, `sonnet`, `opus`, `fable`, `dispatch`, `fin`) — model
  routing and macro aliases. Each model tier has its own skill; `dispatch` is
  fire-and-forget at default model.
- **Evaluation lenses** (e.g. `hacker-eval`, `credits`, `eye-13yo`) —
  judge a codebase or practice from a fixed perspective.
- **Routers** (`create/`, `software/`) — one preloaded `SKILL.md`
  dispatching to cold data files read on demand. `create/` holds the
  creative artifact generators (HTML, SVG, ASCII, video), mostly ported
  from
  [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/tree/main/skills/creative)
  and **local-only** — generators needing paid APIs, cloud accounts, or
  external apps were dropped; local CLI deps (ffmpeg, manim) are fine.
  `software/` holds engineering runbooks extracted from `ops`. Structure
  rules: [`CLAUDE.md`](CLAUDE.md) in this directory.
- **Shared prose references** (`writing`, `humanize`) — copy rules and
  the de-slop pass, cited by `tweet`, `pr-draft`, `readme`, `diary`.
- **`global`** — special case, not installed as a skill: its body
  becomes the wisdom file `~/.claude/CLAUDE.md` at install.

## Skill workflow diagram

Skills cluster into phases. Main spine: orientation → planning → coding → quality → output.
Side-channels (escalation, communication) fire at any stage.

┌─ orientation ───────────────┐
│ resolve recall-memories     │
│ explore                     │
└──────────────┬──────────────┘
               │
┌─ planning ───▼──────────────┐
│ specs ship                  │
└──────────────┬──────────────┘
               │
┌─ coding ─────▼──────────────┐
│ go rs py ts tsx sh sql cli  │         ┌─ escalation ────────┐
│ service data trader         ├────────►│ haiku sonnet opus   │
└──────────────┬──────────────┘         │ fable dispatch fin  │
               │                        └─────────────────────┘
┌─ quality ────▼──────────────┐
│ review code-review improve  │
│ refine visual testing bugs  │
└──────────────┬──────────────┘
               │
┌─ output ─────▼──────────────┐         ┌─ communication ─────┐
│ commit pr-draft release     │         │ diary readme wisdom │
│ gh-comment                  ├────────►│ learn tweet         │
└─────────────────────────────┘         └─────────────────────┘

**orientation** — load context before acting. `resolve` is the universal entry point;
`recall-memories` searches diary/memory/sessions; `explore` answers without modifying.

**planning** — `specs` for design docs; `ship` for multi-session work tracking.
Skip for one-off tasks.

**coding** — language skills (go, rs, py, ts, tsx, sh, sql) carry per-language rules;
shape skills (cli, service, data, trader) carry patterns for what you're building.
They compose: a Rust CLI loads `rs` + `cli`.

**quality** — `review`/`code-review` for finding issues; `improve`/`refine` for fixing
them; `visual` for UI; `testing` for test patterns; `bugs` for the record-don't-fix queue.

**output** — `commit`, `pr-draft`, `release`, `gh-comment`. Use once work is verified.

**communication** — fires after milestones at any stage. `diary` logs decisions;
`readme` syncs docs; `wisdom` edits skills; `learn` mines history; `tweet` drafts threads.

**escalation** — route to the right model/mode from any stage. `/haiku` → `/sonnet` → `/opus` → `/fable`
for increasing capability. `/dispatch` for fire-and-forget at default model. `fin` for no-confirmation runs.

## Working with skills

- Each `SKILL.md` has YAML frontmatter (`name`, `description`,
  optional `user-invocable: true`)
- `user-invocable: true` exposes the skill as `/<name>` slash command
- Auto-activation matches the `description` field — make it specific
- See `wisdom/SKILL.md` for the writing rules
