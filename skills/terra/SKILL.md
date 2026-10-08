---
name: terra
description: "/terra — GPT-6.1 Sol workhorse subagent for investigation, coding, pre-review, and settled plan steps. NOT for second opinions or maximum-reasoning design work (use /astra or /opus)."
when_to_use: "terra, use terra, spawn terra, terra subagent, GPT-6.1 Sol worker, Codex workhorse, delegate to Sol, cross-model implementation, cross-model investigation"
user-invocable: true
---

# Terra

Terra is the Codex-native counterpart to `/sonnet`. It runs `gpt-6.1-sol` at
high effort as an independent workhorse. It is a skill alias, not a model name.

## Invoke

With a prompt after `/terra`, launch the worker in the background, report what
was launched, and continue on non-overlapping work.

- In Codex, ALWAYS use the native `spawn_agent` tool with
  `model: "gpt-6.1-sol"`, `reasoning_effort: "high"`, and
  `fork_turns: "none"`.
- In Claude Code, ALWAYS read `../astra/SKILL.md` and apply its Model, Auth,
  and Rules sections. ALWAYS launch this command with the shell tool's
  background mode:

```bash
codex exec --ephemeral --dangerously-bypass-approvals-and-sandbox \
  -m gpt-6.1-sol -c model_reasoning_effort="high" \
  "<self-contained brief>" </dev/null
```

- ALWAYS brief per `dispatch`: state the goal, context, scope, boundaries, and
  required evidence. NEVER pass the parent agent's reasoning or conclusions.
- ALWAYS ask the worker to return changed files, commands and outputs, and
  deviations. ALWAYS inspect its result before using it.
- NEVER run two writers in one worktree. ALWAYS isolate an editing worker with
  `worktree`, or run writers one at a time.
- NEVER use Terra for a routine lookup or bounded mechanical edit. ALWAYS use
  direct tools or `/haiku` for those tasks.

## Plan, then execute

For a change above Sonnet's size gate, ALWAYS follow `sonnet` § Plan, then
execute. Substitute Terra for a Sonnet worker only when a separate Codex model
adds value. NEVER duplicate that workflow here.
