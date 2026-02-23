---
name: wisdom
description: Creating SKILL.md and CLAUDE.md. ALWAYS/NEVER statements, skill creation, project instructions, YAML frontmatter, wisdom files.
---

# Wisdom Skill

Guidelines for writing effective SKILL.md and CLAUDE.md files.

## Writing Good SKILL.md

```yaml
---
name: short-name
description: Specific trigger context. When to activate. What file types or keywords.
---
```

- Description is critical - semantic matching activates skills
- Content: ALWAYS/NEVER rules, patterns, code examples
- NEVER prose, ALWAYS statements or examples
- Under 200 lines, link to supporting files if larger

## Writing Good CLAUDE.md

- Project-specific only (skills handle general knowledge)
- Architecture, state machines, external systems
- Under 200 lines
- ALWAYS/NEVER statements or examples, not prose

## Format Rules

- ALWAYS use ALWAYS/NEVER/MUST/SHOULD statements
- NEVER write paragraphs of explanation
- ALWAYS include concrete examples when helpful
- NEVER duplicate content between skills
- ALWAYS keep files under line limits (skills: 200, CLAUDE.md: 200)

## Structure

```
SKILL.md structure:
1. YAML frontmatter (name, description)
2. One-line summary
3. Rules as bullet points
4. Examples (code blocks or inline)

CLAUDE.md structure:
1. TL;DR (one line)
2. Sections with bullet points
3. Examples for non-obvious patterns
```

## Anti-patterns

- NEVER write "This skill helps you..." marketing prose
- NEVER duplicate global wisdom in project CLAUDE.md
- NEVER use vague descriptions like "general utilities"
- NEVER exceed line limits (refactor to separate files)
