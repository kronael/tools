---
name: wisdom
description: Write or edit SKILL.md, CLAUDE.md, AGENTS.md. NOT for general code (use go/rs/py/ts) or mining history (use learn).
when_to_use: creating a new skill, adding a rule to CLAUDE.md, fixing a skill description, writing ALWAYS/NEVER statements
---

# Wisdom Skill

## SKILL.md frontmatter

```yaml
---
name: short-name
description: <one-line summary of what the skill does>. NOT for <case> (use <other-skill>).
when_to_use: <trigger phrases — natural requests users would say to invoke this skill>
---
```

- ALWAYS put the one-line summary in `description`; put trigger phrases in `when_to_use`.
- `description` + `when_to_use` share a 1,536-character budget — both shown to Claude for routing.
- ALWAYS add `NOT for <case> (use <other-skill>)` in `description` — disambiguates closest neighbors.
- NEVER omit the NOT clause — the harness has no other way to handle overlapping skills.
- NEVER write "This skill helps you…" or any marketing prose.
- NEVER use vague terms like "general utilities", "various tools".
- Description is what the harness matches against — every word earns its place.

### Routing mechanics

Claude matches user requests against the combined `description` + `when_to_use` text. Keep `description` as a declarative summary ("summarizes X", not "summarize X"); put natural trigger phrases in `when_to_use`.

- Overlapping `when_to_use` causes races — NEVER use trigger words shared with a sibling skill's primary trigger.
- `description` + `when_to_use` share a 1,536-char budget — trim ruthlessly.

## SKILL.md body

- ALWAYS use ALWAYS/NEVER statements; never SHOULD (too soft).
- ALWAYS pair NEVER with ALWAYS: "NEVER X. ALWAYS Y instead." — prohibitions without direction are half a rule.
- ALWAYS keep under 200 lines; skills persist in context all session (every line = recurring token cost per turn).
- NEVER add obvious code examples LLMs already know.
- NEVER duplicate content between skills or with the global wisdom file.

## CLAUDE.md (project)

- Project-specific only — skills carry general knowledge.
- ALWAYS under 200 lines. The system prompt already uses ~50 of the ~200-instruction budget; beyond 150 rules, compliance degrades uniformly.
- ALWAYS/NEVER statements. Positive framing ("ALWAYS X") gets higher compliance than negative ("NEVER not-X").
- ALWAYS document architecture, state machines, external systems.
- NEVER restate language or workflow conventions that live in skills.
- Put critical rules at the top or bottom — middle content is least reliably attended to.
