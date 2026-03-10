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
5. Validate if commit is needed:
   - If user explicitly invoked /commit: ALWAYS proceed
   - If auto-suggested (from hook): check if changes form cohesive chunk:
     * Single feature, fix, or refactor (not multiple unrelated changes)
     * Related files (not scattered across unrelated modules)
     * Complete work (not half-implemented or broken state)
   - If NOT cohesive: report analysis and stop
   - If cohesive: proceed to commit
6. Analyze changes and draft a commit message:
   - Summarize the nature (feature, fix, refactor, etc.)
   - Use the FORMAT matching the marker above
   - Focus on "why" not "what"
   - Keep it concise (1-2 sentences)
7. Stage relevant files with `git add` (avoid secrets like .env)
8. Create the commit using HEREDOC format:
   ```
   git commit -m "$(cat <<'EOF'
   Your message here
   EOF
   )"
   ```
9. Run `git status` to verify success

## Rules

- ALWAYS commit when explicitly invoked by user
- ONLY commit auto-suggestions if changes form cohesive chunk
- Cohesive chunk = single feature, fix, or refactor; related files; complete work
- NEVER use git commit --amend
- NEVER add Co-Authored-By lines
- NEVER skip pre-commit hooks
- If pre-commit fails and reformats, retry the commit once

## Examples

User: `/commit` -> regular commit with `[section] Message`
Internal: `Skill(commit, "[checkpoint]")` -> `[checkpoint] Message`
Internal: `Skill(commit, "[refined]")` -> `[section] Message [refined]`
