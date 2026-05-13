---
name: wisdom
description: Write or edit SKILL.md, CLAUDE.md, AGENTS.md. NOT for general code (use go/rs/py/ts) or mining history (use learn).
when_to_use: creating a new skill, adding a rule to CLAUDE.md, fixing a skill description, writing ALWAYS/NEVER statements
---

# Wisdom Skill

## SKILL.md frontmatter

```yaml
---
name: short-name          # must match intended slash command slug if user-invocable
description: <one-line summary>. NOT for <case> (use <other-skill>).
when_to_use: <trigger phrases — natural requests users would say>
user-invocable: true      # optional — exposes skill as /name slash command in the UI
---
```

- ALWAYS keep `description` minimal — short summary + NOT clause only.
- ALWAYS pack `when_to_use` with retrieval keywords: error messages, symptom words, tool/library names, synonyms.
- `description` + `when_to_use` share a 1,536-char budget — both shown to Claude for routing.
- NEVER write description as workflow summary ("summarizes X via Y") — Claude shortcuts past skills whose description states the process.
- ALWAYS add `NOT for <case> (use <other-skill>)` in `description` — disambiguates neighbors.
- NEVER write "This skill helps you…" or marketing prose.
- NEVER use vague terms like "general utilities", "various tools".
- NEVER use trigger words shared with a sibling skill's primary trigger — causes routing races.

## Body patterns

- **Mode-toggle** (fin/explore style): concise `## Behavior` block, no other sections.
- **Agent-launcher** (visual/readme style): single sentence: "Launch the @X agent (Task tool, subagent_type: X) to…"

## SKILL.md body

- ALWAYS use ALWAYS/NEVER; NEVER use SHOULD (too soft).
- ALWAYS pair NEVER with ALWAYS: "NEVER X — ALWAYS Y instead."
- ALWAYS keep under 200 lines; skills persist in context all session.
- NEVER add obvious code examples LLMs already know.
- NEVER duplicate content between skills or with the global wisdom file.
- ALWAYS move reference material (>50 lines: API docs, tables) to sibling files; SKILL.md is workflow only.

## CLAUDE.md (project)

- Project-specific only — skills carry general knowledge.
- ALWAYS document architecture, state machines, external systems.
- Put critical rules at the top or bottom — middle content is least reliably attended to.
