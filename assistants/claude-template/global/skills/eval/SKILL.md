---
name: eval
description: Evaluate agent responses. Use when asked to evaluate, review, grade, or assess agent output quality.
---

# Eval

Evaluate agent responses and save structured assessments.

## When to Use

- User asks to evaluate/review an agent's response
- User asks "did X do this correctly?"
- Quality assessment of agent output

## Storage

Save evaluations to `eval/<topic>/YYYYMMDD.md` (project-local).

Create topic directories as needed (e.g., `3dprint/`, `research/`, `code/`).

## Evaluation Template

```markdown
# Evaluation: <Topic> (<agent>/<instance>)

**Date**: YYYYMMDD
**Agent**: <agent name> (<instance>)
**Task**: <one-line summary>

## User Request

> <quote the original request>

## What Agent Did

1. <action 1>
2. <action 2>
...

## Evaluation

### Correct

- <what worked well>

### Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| <issue> | Critical/Medium/Low | <details> |

### Verdict

**PASS/FAIL** — <one-line summary>

## Score

| Dimension | Score | Notes |
|-----------|-------|-------|
| Task completion | X/10 | |
| Accuracy | X/10 | |
| Presentation | X/10 | |
| Honesty | X/10 | |
| **Overall** | **X/10** | |
```

## Dimensions

- **Task completion**: Did it do what was asked?
- **Accuracy**: Is the output correct/valid?
- **Presentation**: Is it well-formatted, clear?
- **Honesty**: Did it admit limitations vs hallucinate?

## Severity Levels

- **Critical**: Blocks user, incorrect output, security issue
- **Medium**: Missing functionality, unverified claims
- **Low**: Minor gaps, style issues, nice-to-haves

## Process

1. Read the agent's conversation/logs
2. Verify claims (check files exist, URLs work, code runs)
3. Score each dimension
4. Write evaluation to file
5. Report verdict to user
