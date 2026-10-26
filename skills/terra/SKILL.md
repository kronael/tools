---
name: terra
description: "/terra — Codex worker for the Sonnet lane, at high effort. NOT for docs rounds, refines or reviews (use dispatch § Tiers), mapping (use /luna), second opinions (use /oracle) or design calls (use /opus)."
when_to_use: "terra, Codex workhorse, cross-model implementation, cross-model investigation, cross-model code step"
user-invocable: true
---

# Terra

Terra is the Codex worker for the `/sonnet` lane. Its model ID is `gpt-5.6-terra`,
and its default effort is `high`. `dispatch` § Tiers owns its task assignments.

## Invoke

With a prompt after `/terra`, ALWAYS launch the worker in the background.
ALWAYS report what was launched and continue on non-overlapping work.

- ALWAYS use native `spawn_agent` only when its exposed model choices include
  `gpt-5.6-terra` and it supports explicit effort selection.
  ALWAYS set `model: "gpt-5.6-terra"`, `reasoning_effort: "high"`, and
  `fork_turns: "none"`. Otherwise, ALWAYS use the CLI route below.
  A `model` parameter alone does not establish support for Terra.
- ALWAYS apply an explicit owner effort override per WISDOM § Agents to
  either launch route; NEVER silently replace the requested model or effort.
- For CLI workers, ALWAYS apply only `astra`'s Model and Auth checks from
  `../astra/SKILL.md`. ALWAYS use the shell tool's background mode.
- ALWAYS set `-C` to the CLI worker's designated directory.
- ALWAYS use `--dangerously-bypass-approvals-and-sandbox` per `astra` § Invoke.
  The invocation is:

```bash
codex exec --ephemeral --dangerously-bypass-approvals-and-sandbox -C "<worker directory>" \
  -m gpt-5.6-terra -c model_reasoning_effort="high" \
  "<self-contained brief>" </dev/null
```

- ALWAYS use `dispatch` § Brief, including its Codex opening.
- ALWAYS ask the worker to return changed files, commands and outputs, and
  deviations. ALWAYS inspect its result before using it.
- ALWAYS follow `worktree` for editing workers.
- NEVER assign docs rounds, refines or review judgments to Terra — ALWAYS
  follow `dispatch` § Tiers.
- NEVER use Terra for a routine lookup, a mapping sweep or a bounded mechanical
  edit — ALWAYS a lookup in direct tools, the rest on `/luna`.

## Plan, then execute

For a change above Sonnet's size gate, ALWAYS follow `sonnet` § Plan, then
execute. ALWAYS check `dispatch` § Tiers before substituting Terra for a step.
NEVER duplicate that workflow here.
