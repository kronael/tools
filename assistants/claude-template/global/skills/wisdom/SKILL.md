---
name: wisdom
description: Creating SKILL.md and CLAUDE.md. ALWAYS/NEVER statements, skill creation, project instructions, YAML frontmatter, wisdom files.
---

# Wisdom Skill

## SKILL.md Format

```yaml
---
name: short-name
description: Specific trigger context. Keywords and file types for activation.
---
```

- Description is critical — semantic matching activates skills
- ALWAYS/NEVER rules and examples, NEVER prose paragraphs
- Under 200 lines, link to supporting files if larger
- NEVER add obvious code examples LLMs already know

## CLAUDE.md Format

- Project-specific only (skills handle general knowledge)
- Under 200 lines, ALWAYS/NEVER statements
- Architecture, state machines, external systems

## Anti-patterns

- NEVER "This skill helps you..." marketing prose
- NEVER duplicate content between skills or with global CLAUDE.md
- NEVER vague descriptions like "general utilities"
