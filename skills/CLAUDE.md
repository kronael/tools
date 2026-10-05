# skills/ — structure rules

How skills in this directory are organized. Router convention owned here;
repo CLAUDE.md links to this file.

## Flat skills vs router skills

- **Flat skill** = `skills/<name>/SKILL.md`. For frequently invoked verbs
  (`commit`, `refine`, `humanize`) and bare tech names (`rs`, `go`, `ops`).
- **Router skill** = one `SKILL.md` (the ONLY preloaded file) + sibling cold
  data `.md` files, read on demand. Current routers: `create/` (artifact
  generators), `software/` (engineering baseline + runbooks), `specs/` (spec
  workflow), `readme/` (documentation: sync, file topology, page shape),
  `review/` (give/take a code review — see `review/SKILL.md`), `eval/`
  (one evaluation lens per file, `all.md` runs every lens), `research/`
  (research baseline), `writing/` (prose rules hot, `page.md` for how a
  document or page is laid out).
- Preload model (verified): Claude Code injects `name` + `description` +
  `when_to_use` per skill into the always-on listing; `when_to_use` is
  "appended to description" and the combined text is capped at 1,536 chars
  per entry (code.claude.com/docs/en/skills, frontmatter reference).
  Bodies load only on invocation. `when_to_use` is NOT free — trim it too.
  ALWAYS make a router when several rarely-invoked skills share an audience —
  N preloaded entries collapse to 1.
- The listing has a SECOND cap the per-entry one hides: the whole listing gets
  1% of the context window at 4 chars/token — 8,000 chars at a 200k window.
  Over budget, every entry falls back to `- <name>` and descriptions are
  bought back in descending recency-weighted-use order, so a skill nobody
  invoked loses its description first and its keywords stop routing. Deleting
  an entry frees its name AND its claim on that pool; trimming a `when_to_use`
  under the 1,536 cap only frees the pool.

## Router anatomy

- `SKILL.md` — dispatch table: trigger keywords → data file. NEVER prose
  links alone. `description` = one-line summary + `NOT for…` clause — no
  keyword dump, no workflow text. `when_to_use` = trimmed keyword list,
  at least one anchor per folded mode, no synonyms — `/solve` scans both
  fields.
- Light content lives flat: `<mode>.md`.
- Heavy content nests: `<mode>/<slug>.md` + `<mode>/<slug>/` keeping the
  ported tree intact (`references/`, `scripts/`, `templates/`).
- NEVER name a data file `SKILL.md` — that is exactly what makes it preload
  (warned by lint: skill-router in `hooks/skill_frontmatter_lint.py`).
- Data-file frontmatter is inert provenance (author, license, tags) — keep
  it for attribution (NOTICE points at it), never trust it for routing.

## Router invariants

Hold these on every edit — each one is what keeps a router cheaper than the
skills it replaces.

- ALWAYS exactly one `SKILL.md` per router, at the router root. It is the only
  file that preloads and the only file that is invocable.
- A body file is NEVER separately invocable — `software/code.md` has no
  `/code`. ALWAYS reach it through its router; NEVER document or promise a
  slash command for one.
- ALWAYS make every dispatch row resolve to a file that exists, at a path
  relative to the router directory. NEVER point a row outside that directory —
  name the owning skill in prose instead.
- ALWAYS leave every `.md` under the router reachable: named by a row, or
  indexed by a file a row names. `CLAUDE.md` is the sole exemption — it is
  edit notes, not content.
- ALWAYS write the left cell so a reader picks the file WITHOUT opening any:
  name the concrete decisions, artifacts and file names inside it. NEVER a
  bare topic word — a row a reader cannot match against makes them read two
  files, which is the cost the router exists to remove.
- ALWAYS tell the body to read exactly ONE matched file. NEVER let a router
  invite a bulk read of its subtree.

## Naming law

- `create/` = makes artifacts; `software/` = engineering knowledge;
  `specs/` = the design record; `readme/` = the docs a project ships.
  Namespaces, not words you conjugate — no new `create-*` dirs.
- A router is named for its drawer, NEVER for one of its modes — the mode
  keeps its own name as the body file (`specs/useless.md`).
- Bare verbs and tech names stay flat top-level.
- A verb skill may route its own modes under its own name (`readme/`,
  `review/`).
- `writing` = the one owner of the prose and page rules (router, `page.md`
  cold); `humanize` = the AI-tells catalogue it finishes with. Cited by prose
  skills (`tweet`, `pr-draft`, `readme`, `diary` → `writing` → `humanize`);
  every other skill, agent or file points there in one line, NEVER restates.

## Subagent effort defaults

- The agent files in `agents/` pin each tier, and the launcher skills quote
  them: `sonnet` = Sonnet 5.5 at high, `opus` = Opus 5.5 at high, `fable` =
  xhigh, `haiku` = model only (Haiku 4.5 rejects `effort`). ALWAYS change an
  agent file and every skill that quotes it in one commit.
- `sonnet` runs investigations, bug hunts, pre-review, and the steps of a
  written plan (`sonnet` § Plan, then execute). `opus` takes design calls and
  plan steps that need judgment. `fable` takes unattended multi-file code,
  `ship` plans, and security or deep audits.
- `haiku` subagents are for cheap exploration, research, mapping, grep-style
  surveys, and mechanical bounded edits. Escalate once the work requires
  multi-step design judgment, cross-file architecture, or ambiguous tradeoffs.
- NEVER rely on prompt text like "think harder" to set effort. Encode the
  intended model/effort in the launcher skill or agent definition.

## Agent definitions

- `agents/` holds model and effort pins — `fable`, `opus`, `sonnet`, `haiku`,
  with no body — and thin skill agents whose body only loads the same-named
  skill. `visual`, `readme`, `improve` (pins Sonnet 5.5 at high), `learn` and
  `distill` are each launched from their skill's `## Where it runs`
  (`readme/sync.md` for `readme`). `refine` runs in the main thread by design;
  its agent serves only an explicit dispatch of a whole refine pass.
  Knowledge lives in the skill that owns the concern, NEVER in an agent body.
- This section owns the agents rule. ALWAYS point here in one line from any
  other file; NEVER restate the list.
- A skill that needs isolation or a model says so in its own body (`## Where
  it runs`): ALWAYS its thin same-named agent where one fits, else
  `general-purpose` or a model pin (`fable`/`opus`/`sonnet`/`haiku`) told to
  load the skill. NEVER write a content-bearing agent definition, and NEVER reduce
  a skill body to one "launch agent X" line.

## Earning a rule's place

- ALWAYS run the `wisdom` skill's subtraction test before adding or trimming
  rules: a fresh sub writes its defaults for the topic, and whatever it produces
  unprompted does not go in. Only drifts, unguessable local facts, workflows and
  deliberate harness overrides survive.

## Prompt examples and context

- Treat examples as steering tokens, not neutral documentation.
- Prefer explicit rules over examples when the rule can be stated directly.
- Keep examples scarce, ordinary, and representative; label what property
  should generalize.
- Do not keep examples merely as history or proof of dogfooding. They prime
  future runs and spend context.
- Move example galleries, research notes, and test cases to cold references;
  keep preloaded skills as decision surfaces.

## Editing a router

1. Add/keep content in the cold data file (size is irrelevant — it loads
   only on dispatch).
2. Update the router dispatch table row.
3. Add the mode's trigger keywords to router `when_to_use` if missing
   (keep trimmed — it preloads).
4. If a dir is removed or renamed, add its old name to `RETIRED` in
   `../kronael/sync/reference.md` § Classify, so a sync moves the installed
   copy aside without asking the owner about it.
5. Per-router edit notes: `create/CLAUDE.md`, `software/CLAUDE.md`.
