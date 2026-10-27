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

- `dispatch` § Task routing owns task definitions and the single model/effort
  matrix; its Capacity section owns concurrency. ALWAYS point there from
  workflow skills, never repeat the policy in a launcher or workflow.
- `claude` and `codex` own provider launch mechanics. Native agent files are
  execution bindings, not task routers. ALWAYS keep their model and effort
  compatible with dispatch's selections and any explicit owner override.
- NEVER rely on prompt text such as "think harder" to set effort. ALWAYS use
  a supported launch parameter or a matching native binding.

## Agent definitions

- `agents/` holds minimal native Claude bindings: `fable`, `opus`, `sonnet`
  and `haiku`, plus `spec` for Opus/xhigh where a native launch lacks an effort
  override. ALWAYS keep them as frontmatter-only model/effort bindings.
  NEVER put task policy or workflow knowledge in an agent body or description.
- An agent without `effort:` inherits the parent session's effort. ALWAYS pin
  it and have the `claude` runbook verify the binding matches the selection.
  An owner override still needs a supported control; a different prompt is not
  an effort override.
- Codex models launch through `codex`, using native controls or the CLI.
  NEVER create Claude agent files for Codex models.
- This section owns the agent-file convention. ALWAYS point here from other
  files rather than repeating the inventory.
- A skill that needs isolation says so in its own body (`## Where it runs`).
  ALWAYS select its task through `dispatch` and use the provider runbook;
  NEVER add a same-named agent for every workflow or use an inherited
  `general-purpose` default as a substitute for explicit model and effort.

## Earning a rule's place

- ALWAYS run `wisdom` § The subtraction test before adding or trimming a rule.

## Prompt examples and context

- ALWAYS treat examples as steering tokens, not neutral documentation.
- ALWAYS prefer an explicit rule over an example when the rule can be stated
  directly.
- ALWAYS keep examples scarce, ordinary, and representative; label what
  property should generalize.
- NEVER keep an example merely as history or proof of dogfooding. It primes
  future runs and spends context.
- ALWAYS move example galleries, research notes, and test cases to cold
  references; keep preloaded skills as decision surfaces.
- ALWAYS give an illustrative absolute path a one-character account segment
  (`/home/u/app/x`). The leak lint reads a longer one as a real machine path
  and errors (`skill-local-path` in `hooks/skill_frontmatter_lint.py`). A file
  whose point is the real-looking path — what to strip, where a slug comes
  from — opts out with `<!-- lint: allow skill-local-path -->` on a line of
  its own.

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
