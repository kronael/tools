---
name: sol
description: "Ask the codex CLI on gpt-5.6-sol for a second opinion. NOT for routine lookups (use grep/read/recall-memories). NOT a Claude Agent — this is the OpenAI codex CLI."
when_to_use: "ask sol, /sol, sol second opinion, second opinion from the sol model"
user-invocable: true
---

# Sol

The codex CLI pinned to `gpt-5.6-sol`, at high effort. Its catalog description
is "Older generation workhorse model." It gives the same kind of second opinion
as `astra`, from a different Codex model. This is a subprocess, NEVER a Claude
`Agent(...)` type.

Use it only when the user explicitly asks for Sol; `oracle` routes to it only on
such a request.

## Invoke

ALWAYS follow `astra` § Invoke, § Model, § Auth, § Rules and § Output, with two
differences: select `gpt-5.6-sol` in the catalog check and the command, and run
`codex exec --ephemeral` instead of `resume --last`. `resume --last` picks the
working directory's latest session, which is Astra's thread after an Astra call,
and Sol must answer without having read Astra's prompt and answer.

```bash
codex exec --ephemeral --dangerously-bypass-approvals-and-sandbox \
  -m gpt-5.6-sol -c model_reasoning_effort="high" \
  "Goal: <X>. Find the flaw in..." </dev/null
```
