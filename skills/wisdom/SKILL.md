---
name: wisdom
description: Write or edit SKILL.md, CLAUDE.md, AGENTS.md. NOT for general code (use go/rs/py/ts), mining history (use learn), or researching/codifying public best practice into a skill (use scavenge).
when_to_use: "creating a new skill, adding a rule to CLAUDE.md, fixing a skill description, writing ALWAYS/NEVER statements, skill not triggering, skill frontmatter, when_to_use, skill lint failed"
---

# Wisdom Skill

## SKILL.md frontmatter

```yaml
---
name: short-name              # the /name slug and the Skill tool name
description: <one-line summary>. NOT for <case> (use <other-skill>).
when_to_use: <trigger phrases — what a user would say>
user-invocable: false         # optional — hides /name from the menu; Claude can still invoke it
argument-hint: "<question>"   # optional — shown after /name
---
```

- ALWAYS include `name`, `description`, `when_to_use` — lint: skill-keys (hard fail).
- NEVER invent a key — Claude Code reads `name`, `description`, `when_to_use`, `user-invocable`, `disable-model-invocation`, `argument-hint`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `shell`, `context`, `agent`, `paths`, `hooks`; any other key (`arg:`) is silently ignored.
- ALWAYS keep `description` minimal — short summary + NOT clause only.
- ALWAYS pack `when_to_use` with retrieval keywords: error messages, symptom words, tool/library names, synonyms.
- The listing shows `description - when_to_use`, cut at 1,536 chars — lint: skill-budget (warn). A keyword past the cap never routes; ALWAYS put the key use case first.
- The whole listing has a budget (1% of the context window). When it overflows, the skills with the least recent use drop to a bare name — a skill nobody invokes loses its description first. `/skill-doctor` shows cost and use per skill.
- NEVER write description as workflow summary ("summarizes X via Y") — Claude shortcuts past skills whose description states the process.
- ALWAYS add `NOT for <case> (use <other-skill>)` in `description` — disambiguates neighbors; lint: skill-notfor (warn).
- NEVER write "This skill helps you…" or marketing prose.
- NEVER use vague terms like "general utilities", "various tools".
- NEVER use trigger words shared with a sibling skill's primary trigger — causes routing races.
- ALWAYS test reachability before committing: write the request the way a user types it and `grep -il '<its key word>' skills/*/SKILL.md` — the hit is this skill and no sibling's primary trigger. A skill reachable only by its name is unreachable from a description match.

## Body patterns

- **Mode-toggle** (fin/explore style): concise `## Behavior` block, no other sections.
- **Agent-launcher** (visual/readme style): single sentence: "Launch the @X agent (Task tool, subagent_type: X) to…"

## SKILL.md body

- ALWAYS use ALWAYS/NEVER for every directive, never the soft 'should' form — lint: skill-should (hard fail).
- ALWAYS pair NEVER with ALWAYS: "NEVER X — ALWAYS Y instead."
- ALWAYS keep under 200 lines; a body loads in full on every invocation. No exceptions — overflow goes to sibling files, never a longer SKILL.md. Lint: skill-length (warn; workflow/runbook skills up to 500).
- NEVER add obvious code examples LLMs already know.
- NEVER duplicate content between skills or with the global wisdom file — one rule lives in the skill that owns it; the others point.
- ALWAYS push overflow (anything >50 lines — API docs, tables, deep dives) into adjacent sibling files linked from the SKILL.md, loaded on demand; SKILL.md stays workflow-only. The SKILL.md MAY tell the LLM to force-read a sibling when it's mandatory, not optional.
- ALWAYS run `make skills-frontmatter` (repo root) after an edit; pre-commit runs the same lint.
- For example/context-budget and subagent effort defaults, follow
  `skills/CLAUDE.md`; keep this skill as the compact writing checklist.

## Router skills

- Router = one `SKILL.md` (the only preloaded file) + sibling cold data `.md` files read on demand (`create/`, `software/`).
- ALWAYS make a router instead of N sibling skills when they share an audience and are rarely invoked — N preloaded descriptions collapse to 1.
- Router body = explicit dispatch table mapping trigger keywords → data file; NEVER prose links alone.
- Router frontmatter MUST carry every folded mode's retrieval keywords within the 1,536-char budget — `/solve` routes on them.
- Light content lives flat (`<mode>.md`); heavy ported trees keep their subtree intact at `<mode>/<slug>/`.
- NEVER name a data file `SKILL.md` — that is what makes it preload; lint: skill-router (warn).
- Maintenance procedure: `skills/CLAUDE.md`.

## Installed copy vs source

- `~/.claude/` is an install of the assistants repos (paths in `LOCAL.md`) —
  ALWAYS sync a `~/.claude/` change to them; NEVER let install and source drift.

## CLAUDE.md (project)

- Project-specific only — skills carry general knowledge.
- ALWAYS document architecture, state machines, external systems.
- Put critical rules at the top or bottom — middle content is least reliably attended to.
