---
name: oracle
description: One second-opinion router for code, planning, security/deep audit, and creative critique. NOT for routine lookups (use grep/read/recall-memories) or fire-and-forget work (use dispatch).
when_to_use: "oracle, second opinion, sanity check, ask oracle, planning oracle, plan critique, code critique, creative critique, security audit critique, red team critique, disagreement after reasoning"
user-invocable: true
---

# Oracle

One router for second opinions. User text wins: if the user explicitly asks for
codex, fable, creative, code, planning, or security routing, follow that route.

## Dispatch

| Request | Route |
|---|---|
| Code review, bug hunt, algorithm/design critique | `fable` subagent |
| Planning critique, release plan, architecture plan | `fable` subagent |
| Security, red-team, exploitability, deep audit | `fable` subagent |
| Naming, prose, narrative, product copy, ideation | `codex` CLI, high effort |
| Ambiguous but touches code or operations | `fable` subagent |
| Explicit "ask codex" / "use codex" | `codex` CLI, high effort |

## Fable Route

Launch a background agent with `subagent_type: "fable"` — `agents/fable.md`
pins it at xhigh, so every fable route runs at xhigh. Include the goal,
target files/dirs, and what to return. Frame adversarially:

```text
Goal: <X>. Find the flaw in <code/design/plan>. Entry points: <files, symbols,
error output>. Return findings only, with file:line or concrete trace.
```

Rules:

- NEVER set effort in the prompt text — only the agent file sets it.
- Never ask "does this look right?" Ask what breaks, what is missing, or why the
  plan fails.
- Verify claims against the repo before acting.

## Codex Route

Load the `codex` skill and follow its runbook. Use it for creative critique and
explicit Codex requests. Keep the prompt adversarial and high-level; do not
paste your full reasoning chain.

## Output

Treat every oracle answer as advisory. Cite the finding when acting; discard
wrong claims with a one-line reason.
