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
| Code review, bug hunt, algorithm/design critique | `fable` subagent, high effort |
| Planning critique, release plan, architecture plan | `fable` subagent, xhigh |
| Security, red-team, exploitability, deep audit | `fable` subagent, xhigh |
| Naming, prose, narrative, product copy, ideation | `codex` CLI, high effort |
| Ambiguous but touches code or operations | `fable` subagent, high effort |
| Explicit "ask codex" / "use codex" | `codex` CLI, high effort |

## Fable Route

Launch a background `fable` agent. Include the goal, target files/dirs, and
what to return. Frame adversarially:

```text
Goal: <X>. Find the flaw in <code/design/plan>. Entry points: <files, symbols,
error output>. Return findings only, with file:line or concrete trace.
```

Rules:

- Use high effort by default.
- Use xhigh only for planning and security/deep-audit routes, or when the user
  explicitly asks for maximum effort.
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
