<!-- kronael:start -->
# Kronael

- ALWAYS read `~/.claude/CLAUDE.md` when it exists.
- ALWAYS read every applicable `CLAUDE.md` from the project root to the current
  directory, even when `AGENTS.md` is loaded.
- ALWAYS read the project's `.claude/CLAUDE.md` when it exists: Codex never
  loads it, because `project_doc_fallback_filenames` entries are matched as
  bare file names in each directory.
- Before reading or editing a file, ALWAYS check from the project root through
  its directory for a closer `CLAUDE.md` and read it first.
- NEVER choose between `AGENTS.md` and `CLAUDE.md`; apply both.

## Work record

Plans, the ship record and critiques live in the main tree's
`.claude/plans/` — plan mode's directory, pinned by `plansDirectory` in
`.claude/settings.json` and ignored by the root-anchored `/.claude/plans/`
line. ALWAYS reuse the active change's record where it is; `ship` § Work record
owns the rule.

## Response style

ALWAYS apply the Response Style section in `~/.claude/CLAUDE.md` and read
`~/.claude/output-styles/caveman.md` when it exists. The installed output
style is the source of the caveman response rules for both agents.
<!-- kronael:end -->
