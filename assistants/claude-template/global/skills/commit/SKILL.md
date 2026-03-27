---
name: commit
description: Git commits. git status, git diff, git add, staging files, commit messages, [section] format.
user-invocable: true
---

# Commit

Run the git commit workflow directly (no subagent).

## Markers

If args contains a marker, use the corresponding format:
- `[checkpoint]` - prefix: `[checkpoint] Message`
- `[refined]` - suffix: `[section] Message [refined]`
- (none) - default: `[section] Message`

Section names: `fix`, `feat`, `refactor`, `docs`, `test`, `chore`, `perf`, `style`

## Workflow

1. `git status` (NEVER -uall), `git diff`, `git log --oneline -5`
2. If no changes, stop: "nothing to commit"
3. Cohesion check (skip if user explicitly invoked /commit):
   - Single feature/fix/refactor, related files, complete work -> proceed
   - Disparate changes -> list them, suggest separate commits, stop
4. Draft message: format per marker, focus on "why", 1-2 sentences
5. `git add` relevant files, commit with HEREDOC:
   ```
   git commit -m "$(cat <<'EOF'
   Your message here
   EOF
   )"
   ```
6. `git status` to verify

## Rules

- NEVER use git commit --amend
- NEVER add Co-Authored-By lines
- If pre-commit fails and reformats, retry once

## Examples

User: `/commit` -> regular commit with `[section] Message`
Internal: `Skill(commit, "[checkpoint]")` -> `[checkpoint] Message`
Internal: `Skill(commit, "[refined]")` -> `[section] Message [refined]`
