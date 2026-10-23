---
name: terra
description: "/terra — GPT-6.1 Sol workhorse subagent, the Codex counterpart of /sonnet. NOT for mapping or a bounded mechanical edit (use /luna), second opinions (use /oracle) or design calls (use /opus)."
when_to_use: "terra, GPT-6.1 Sol worker, Codex workhorse, delegate to Sol, cross-model implementation, cross-model investigation, cross-model plan step"
user-invocable: true
---

# Terra

Terra is the Codex-native counterpart to `/sonnet`. It runs `gpt-6.1-sol` at
high effort, reviews included; `xhigh` only for a security review. It is a skill alias, not a model name.

## Invoke

With a prompt after `/terra`, ALWAYS launch the worker in the background.
ALWAYS report what was launched and continue on non-overlapping work.

- If Codex's native `spawn_agent` supports explicit model and effort selection,
  ALWAYS use `model: "gpt-6.1-sol"`, `reasoning_effort` at that level, and
  `fork_turns: "none"`. Otherwise, ALWAYS use the CLI route below.
- For CLI workers, ALWAYS apply only `astra`'s Model and Auth checks from
  `../astra/SKILL.md`. ALWAYS use the shell tool's background mode.
- ALWAYS set `-C` to the CLI worker's designated directory.
- Outside dockbox, ALWAYS use `--sandbox read-only` for read-only workers
  or `--sandbox workspace-write` for editing workers.
- Only in an externally isolated dockbox, ALWAYS replace the sandbox option with
  `--dangerously-bypass-approvals-and-sandbox` per `astra` § Invoke.
  The read-only invocation is:

```bash
codex exec --ephemeral --sandbox read-only -C "<worker directory>" \
  -m gpt-6.1-sol -c model_reasoning_effort="<high; xhigh only for a security review>" \
  "<self-contained brief>" </dev/null
```

- ALWAYS brief per `dispatch`.
- ALWAYS ask the worker to return changed files, commands and outputs, and
  deviations. ALWAYS inspect its result before using it.
- ALWAYS follow `worktree` for editing workers.
- NEVER use Terra for a routine lookup, a mapping sweep or a bounded mechanical
  edit — ALWAYS a lookup in direct tools, the rest on `/luna`.

## Plan, then execute

For a change above Sonnet's size gate, ALWAYS follow `sonnet` § Plan, then
execute. ALWAYS substitute Terra only when a separate Codex model adds value.
NEVER duplicate that workflow here.
