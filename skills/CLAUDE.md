# skills/ — structure rules

How skills in this directory are organized. Router convention owned here;
repo CLAUDE.md links to this file.

## Flat skills vs router skills

- **Flat skill** = `skills/<name>/SKILL.md`. For frequently invoked verbs
  (`commit`, `refine`, `humanize`) and bare tech names (`rs`, `go`, `ops`).
- **Router skill** = one `SKILL.md` (the ONLY preloaded file) + sibling cold
  data `.md` files, read on demand. Current routers: `create/` (artifact
  generators), `software/` (engineering baseline + runbooks).
- Preload model (verified): Claude Code injects `name` + `description` +
  `when_to_use` per skill into the always-on listing; `when_to_use` is
  "appended to description" and the combined text is capped at 1,536 chars
  per entry (code.claude.com/docs/en/skills, frontmatter reference).
  Bodies load only on invocation. `when_to_use` is NOT free — trim it too.
  ALWAYS make a router when several rarely-invoked skills share an audience —
  N preloaded entries collapse to 1.

## Router anatomy

- `SKILL.md` — dispatch table: trigger keywords → data file. NEVER prose
  links alone. `description` = one-line summary + `NOT for…` clause — no
  keyword dump, no workflow text. `when_to_use` = trimmed keyword list,
  at least one anchor per folded mode, no synonyms — `/resolve` scans both
  fields.
- Light content lives flat: `<mode>.md`.
- Heavy content nests: `<mode>/<slug>.md` + `<mode>/<slug>/` keeping the
  ported tree intact (`references/`, `scripts/`, `templates/`).
- NEVER name a data file `SKILL.md` — that is exactly what makes it preload.
- Data-file frontmatter is inert provenance (author, license, tags) — keep
  it for attribution (NOTICE points at it), never trust it for routing.

## Naming law

- `create/` = makes artifacts; `software/` = engineering knowledge.
  Namespaces, not words you conjugate — no new `create-*` dirs.
- Bare verbs and tech names stay flat top-level.
- `writing`, `humanize` = shared references cited by prose skills
  (`tweet`, `pr-draft`, `readme`, `diary` → `writing` → `humanize`).

## Subagent effort defaults

- `opus` and `fable` subagents default to high effort. Do not make xhigh the
  default; reserve xhigh for explicit planning work and security/deep-audit
  work, or when the user explicitly asks for maximum effort.
- `sonnet` subagents default to high effort for investigations, bug hunts,
  pre-review, and implementation support. Use medium only when the task is
  clear enough that `haiku` could plausibly do it, but `sonnet` is chosen for
  slightly better judgment or context handling.
- `haiku` subagents are for cheap exploration, research, mapping, grep-style
  surveys, and mechanical bounded edits. Escalate once the work requires
  multi-step design judgment, cross-file architecture, or ambiguous tradeoffs.
- NEVER rely on prompt text like "think harder" to set effort. Encode the
  intended model/effort in the launcher skill or agent definition.

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
4. If a dir is removed/renamed, add it to the prune list in
   `../kronael/install/SKILL.md` so reinstalls delete orphans.
5. Per-router edit notes: `create/CLAUDE.md`, `software/CLAUDE.md`.
