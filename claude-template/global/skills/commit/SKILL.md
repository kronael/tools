---
name: commit
description: Git commits. git status, git diff, git add, staging files, commit messages, [section] format.
user-invocable: true
---

# Commit

Run the git commit workflow directly (no subagent).

## Optional Markers

If args contains a marker, use the corresponding format:
- `[checkpoint]` - prefix: `[checkpoint] Message`
- `[refined]` - suffix: `[section] Message [refined]`
- (none) - default: `[section] Message`

Section names: `fix`, `feat`, `refactor`, `docs`, `test`, `chore`, `perf`, `style`

## Workflow

1. Run `git status` (NEVER use -uall flag)
2. Run `git diff` to see staged and unstaged changes
3. Run `git log --oneline -5` to see recent commit style
4. If no changes exist, stop and report "nothing to commit"
5. Analyze changes and draft a commit message:
   - Summarize the nature (feature, fix, refactor, etc.)
   - Use the FORMAT matching the marker above
   - Focus on "why" not "what"
   - Keep it concise (1-2 sentences)
6. Stage relevant files with `git add` (avoid secrets like .env)
7. Create the commit using HEREDOC format:
   ```
   git commit -m "$(cat <<'EOF'
   Your message here
   EOF
   )"
   ```
8. Run `git status` to verify success

## Rules

- NEVER use git commit --amend
- NEVER add Co-Authored-By lines
- NEVER skip pre-commit hooks
- If pre-commit fails and reformats, retry the commit once

## Examples

User: `/commit` -> regular commit with `[section] Message`
Internal: `Skill(commit, "[checkpoint]")` -> `[checkpoint] Message`
Internal: `Skill(commit, "[refined]")` -> `[section] Message [refined]`
