---
name: wisdom
description: Write or edit SKILL.md, CLAUDE.md, AGENTS.md — skill descriptions, ALWAYS/NEVER rules, frontmatter, project instructions. USE when creating a new skill, adding a rule, updating project guidance, or fixing a skill description. NOT for general code (use the matching language skill).
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

### Description is routing, not metadata

The description field is how Claude decides *when* to invoke the skill — it reads the description against the user's request. This is the only routing mechanism. Implications:

- Include 4–6 natural phrases users would actually say, not category labels.
- Overlapping descriptions cause races — two skills mentioning "changes" or "commit" will fight. NEVER use words shared with a sibling skill's primary trigger.
- Write in declarative form ("summarizes X") not imperative ("summarize X") — describe what the skill does, not what to do.

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
