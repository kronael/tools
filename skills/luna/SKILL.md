---
name: luna
description: "/luna — GPT-6 Luna fan-out subagent, the Codex counterpart of /haiku. NOT for investigation or a code step (use /terra), docs rounds or reviews (use dispatch § Tiers), second opinions (use /oracle) or design calls (use /opus)."
when_to_use: "luna, GPT-6 Luna worker, Codex fan-out, cheap Codex sub, delegate to Luna, cross-model mapping, cross-model mechanical edit"
user-invocable: true
---

# Luna

Luna is the Codex-native counterpart to `/haiku`. It runs `gpt-6-luna` at
high effort for read-only fan-out — mapping, grep surveys, one-file lookups —
and a bounded mechanical edit with a clear spec. Its catalog description is
"Fast and affordable model for easier tasks."

## Invoke

With a prompt after `/luna`, ALWAYS launch the worker in the background.
ALWAYS report what was launched and continue on non-overlapping work.

- If native `spawn_agent` exposes `gpt-6-luna` and explicit effort selection,
  ALWAYS use `model: "gpt-6-luna"`, `reasoning_effort: "high"`, and
  `fork_turns: "none"`. Otherwise, ALWAYS use the CLI route below.
- ALWAYS apply explicit owner effort overrides per WISDOM § Agents to either route.
- For CLI workers, ALWAYS apply only `astra`'s Model and Auth checks from
  `../astra/SKILL.md`. ALWAYS use the shell tool's background mode.
- ALWAYS set `-C` to the CLI worker's designated directory.
- ALWAYS use `--dangerously-bypass-approvals-and-sandbox` per `astra` § Invoke.
  The invocation is:

```bash
codex exec --ephemeral --dangerously-bypass-approvals-and-sandbox -C "<worker directory>" \
  -m gpt-6-luna -c model_reasoning_effort="high" \
  "<self-contained brief>" </dev/null
```

- ALWAYS use `dispatch` § Brief, including its Codex opening.
- ALWAYS ask the worker to return changed files, commands and outputs, and
  deviations. ALWAYS inspect its result before using it.
- ALWAYS follow `worktree` for editing workers.
- NEVER accept multi-step reasoning, an ambiguous spec or a cross-file refactor
  — ALWAYS choose the worker through `dispatch` § Tiers.
  A routine lookup stays in direct tools; a codemod stays in the
  parent (`sonnet` § Plan).
