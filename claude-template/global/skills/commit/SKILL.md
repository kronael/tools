---
name: commit
description: Commit changes using haiku model
user-invocable: true
---

# Commit with Haiku

Use the Task tool to spawn a haiku subagent for git commits.

## Instructions

When this skill is invoked, IMMEDIATELY use the Task tool with:
- `subagent_type`: "Bash"
- `model`: "haiku"
- `prompt`: The full git commit workflow (see below)

## Optional Markers

If args contains a marker, include it in the commit format:
- `[checkpoint]` - prefix for checkpoint commits: `[checkpoint] Message`
- `[refined]` - suffix for refined commits: `[section] Message [refined]`

## Commit Workflow Prompt

Pass this prompt to the haiku agent, substituting FORMAT based on marker:

```
Perform a git commit with these steps:

1. Run `git status` (never use -uall flag)
2. Run `git diff` to see staged and unstaged changes
3. Run `git log --oneline -5` to see recent commit style
4. If no changes exist, stop and report "nothing to commit"
5. Analyze changes and draft a commit message:
   - Summarize the nature (feature, fix, refactor, etc.)
   - Format: FORMAT
   - Focus on "why" not "what"
   - Keep it concise (1-2 sentences)
6. Stage relevant files with `git add` (avoid secrets like .env)
7. Create the commit using HEREDOC format:
   git commit -m "$(cat <<'EOF'
Your message here
EOF
)"
8. Run `git status` to verify success

IMPORTANT:
- NEVER use git commit --amend
- NEVER add Co-Authored-By lines
- NEVER skip pre-commit hooks
- If pre-commit fails and reformats, retry the commit once
```

### FORMAT Values

| Marker       | FORMAT value                        |
|--------------|-------------------------------------|
| (none)       | `[section] Message`                 |
| [checkpoint] | `[checkpoint] Message`              |
| [refined]    | `[section] Message [refined]`       |

Section names: `fix`, `feat`, `refactor`, `docs`, `test`, `chore`, `perf`, `style`

## Examples

User: `/commit` -> regular commit with `[section] Message`
Internal: `Skill(commit, "[checkpoint]")` -> `[checkpoint] Message`
Internal: `Skill(commit, "[refined]")` -> `[section] Message [refined]`
