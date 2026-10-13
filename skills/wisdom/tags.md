# Tags and conditional loading in a CLAUDE.md

Read from `SKILL.md` § CLAUDE.md (project) when a file uses XML wrappers
or a conditional-loading mechanism.

## Tags describe content; the harness controls loading

- ALWAYS treat `<important if="condition">…</important>` as a local prompt
  convention. The sources below do not document special priority, a parsed
  `if` condition, or an override of a system reminder for this wrapper.
- When XML helps separate content, ALWAYS choose consistent, descriptive
  names: `<instructions>`, `<context>`, `<input>`, or `<examples>` containing
  `<example>` blocks. Custom names such as `<testing_rules>` can replace or
  complement `<important>` as semantic labels. They are not priority levels.
- ALWAYS nest tags only to express a natural content hierarchy. NEVER infer
  stronger authority from a tag name or nesting; ALWAYS state the rule itself.
- For task-dependent guidance, ALWAYS state the condition in ordinary text:
  "When editing tests, ...". This works inside a tag or under a Markdown
  heading. An `if` attribute is a model-facing cue, not a documented loader.
- ALWAYS keep one narrow trigger per task-specific block as a local convention.
  NEVER combine unrelated triggers; ALWAYS split testing and API rules when
  their conditions differ.
- ALWAYS leave project identity, directory maps, the stack, and common commands
  unconditional. ALWAYS keep global wisdom free of project task wrappers as a
  local convention, not because global context has special XML semantics.
- For glob-based conditional loading in Claude Code, ALWAYS use the documented
  `.claude/rules/*.md` YAML `paths` mechanism. Matching file access loads those
  rules; rules without `paths` load unconditionally. Nested `CLAUDE.md` files
  also load on demand when Claude reads, writes, or edits files in their subtree.
- ALWAYS distinguish loading from enforcement. Loaded instructions guide the
  model; client settings or hooks enforce supported restrictions. NEVER present
  XML as enforcement or context filtering; ALWAYS verify loading separately.
  ALWAYS test claimed adherence or performance benefits on the target tasks.

Sources: [Anthropic prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags)
and [Academy XML lesson](https://academy.claude.com/courses/claude-with-amazon-bedrock/structure-with-xml-tags)
support descriptive delimiters. [Claude Code memory](https://code.claude.com/docs/en/memory)
documents Markdown organization, file loading, and enforcement limits.
