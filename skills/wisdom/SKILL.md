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

- ALWAYS put the one-line summary in `description`; put trigger phrases in `when_to_use`.
- `description` + `when_to_use` share a 1,536-character budget — both shown to Claude for routing.
- ALWAYS keep `description` as a declarative summary ("summarizes X", not "summarize X").
- ALWAYS add `NOT for <case> (use <other-skill>)` in `description` — disambiguates closest neighbors.
- NEVER omit the NOT clause — the harness has no other way to handle overlapping skills.
- NEVER write "This skill helps you…" or any marketing prose.
- NEVER use vague terms like "general utilities", "various tools".
- Overlapping `when_to_use` causes races — NEVER use trigger words shared with a sibling skill's primary trigger.

## Body patterns

- **Mode-toggle** (fin/explore style): concise `## Behavior` block, no other sections.
- **Agent-launcher** (visual/readme style): single sentence: "Launch the @X agent (Task tool, subagent_type: X) to…"

## SKILL.md body

- ALWAYS use ALWAYS/NEVER statements; never SHOULD (too soft).
- ALWAYS pair NEVER with ALWAYS: "NEVER X. ALWAYS Y instead." — prohibitions without direction are half a rule.
- ALWAYS keep under 200 lines; skills persist in context all session (every line = recurring token cost per turn).
- NEVER add obvious code examples LLMs already know.
- NEVER duplicate content between skills or with the global wisdom file.

## CLAUDE.md (project)

- Project-specific only — skills carry general knowledge.
- ALWAYS document architecture, state machines, external systems.
- Put critical rules at the top or bottom — middle content is least reliably attended to.
