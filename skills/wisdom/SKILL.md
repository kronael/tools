---
name: wisdom
description: Creating SKILL.md and CLAUDE.md. ALWAYS/NEVER statements, YAML frontmatter, skill descriptions, project instructions. USE when writing or editing a SKILL.md, project CLAUDE.md, or AGENTS.md. NOT for general code (use the matching language skill).
---

# Wisdom Skill

## SKILL.md frontmatter

```yaml
---
name: short-name
description: <one-line summary>. USE <when>. NOT for <case> (use <other-skill>).
---
```

- ALWAYS lead with a one-line summary of what the skill is for.
- ALWAYS append `USE <when>` — concrete trigger: file extension, prompt keyword, task type.
- ALWAYS append `NOT for <case> (use <other-skill>)` — disambiguate the closest neighbor.
- NEVER omit USE/NOT — the harness has no other way to disambiguate overlapping skills.
- NEVER write "This skill helps you…" or any marketing prose.
- NEVER use vague terms like "general utilities", "various tools".
- Description is what the harness matches against — every word earns its place.

## SKILL.md body

- ALWAYS use ALWAYS/NEVER statements; never SHOULD (too soft).
- ALWAYS keep under 200 lines; link to supporting files if larger.
- NEVER add obvious code examples LLMs already know.
- NEVER duplicate content between skills or with the global wisdom file.

## CLAUDE.md (project)

- Project-specific only — skills carry general knowledge.
- ALWAYS under 200 lines, ALWAYS/NEVER statements.
- ALWAYS document architecture, state machines, external systems.
- NEVER restate language or workflow conventions that live in skills.
