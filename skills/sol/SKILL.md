---
name: sol
description: "Ask the codex CLI on gpt-5.6-sol for a second opinion. NOT for routine lookups (use grep/read/recall-memories). NOT a Claude Agent — this is the OpenAI codex CLI. Usually routed through oracle."
when_to_use: "sol, ask sol, use sol, second opinion from sol, quick codex opinion, sanity check, disagreement after reasoning. NOT for routine lookups"
user-invocable: true
---

# Sol

The codex CLI pinned to `gpt-5.6-sol`, at high effort. Its catalog description
is "Older generation workhorse model." It gives the same kind of second opinion
as `astra`, from a different Codex model. This is a subprocess, NEVER a Claude
`Agent(...)` type.

Routing lives in `oracle`. Use this skill directly only when the user
explicitly asks for Sol or when `oracle` dispatches to it.

## Invoke

ALWAYS follow `../astra/SKILL.md` for every rule of the call: Invoke, Model,
Auth, Rules and Output. ALWAYS select `gpt-5.6-sol` in the catalog check and
the command; NEVER inherit Astra's slug from its example.

```bash
codex exec resume --last --dangerously-bypass-approvals-and-sandbox \
  -m gpt-5.6-sol -c model_reasoning_effort="high" \
  "Goal: <X>. Find the flaw in..." </dev/null
```

ALWAYS serialize Sol and Astra calls in one working directory: they share its
latest session, so `--last` would pick the other call's thread.
