---
name: oracle
description: One second-opinion router for code, planning, security/deep audit, and creative critique. NOT for routine lookups (use grep/read/recall-memories) or fire-and-forget work (use dispatch).
when_to_use: "oracle, second opinion, sanity check, ask oracle, plan critique, code critique, creative critique, security audit critique, red team critique"
user-invocable: true
---

# Oracle

One router for second opinions. User text wins: if the user explicitly asks for
astra, sol, fable, creative, code, planning, or security routing, follow that route.

## Dispatch

| Request | Route |
|---|---|
| Code review, bug hunt, algorithm/design critique | `fable` subagent |
| Planning critique, release plan, architecture plan | `fable` subagent |
| Security, red-team, exploitability, deep audit | `fable` subagent |
| Naming, prose, narrative, product copy, ideation | `astra` skill |
| Ambiguous but touches code or operations | `fable` subagent |
| Explicit "ask codex" / "use codex" | `astra` skill |
| Explicit Astra or Sol request | `astra` skill; for Sol, its § Sol variant |

## Fable Route

Launch a background agent with `subagent_type: "fable"`. Include the goal,
target files/dirs, and what to return. Frame adversarially:

```text
Goal: <X>. Find the flaw in <code/design/plan>. Entry points: <files, symbols,
error output>. Return findings only, with file:line or concrete trace.
```

Rules:

- NEVER set effort in the prompt text — ALWAYS the agent file's pin, or the launch's `effort` per WISDOM § Agents.
- Never ask "does this look right?" Ask what breaks, what is missing, or why the
  plan fails.
- Verify claims against the repo before acting.
- When Fable cannot run, ALWAYS follow `fable`'s usage-limit rule;
  NEVER substitute another model without the user's choice.

## Astra Route

Load the `astra` skill and follow its runbook. Use it for creative critique and
explicit Codex or Astra requests. Keep the prompt adversarial and high-level; do not
paste your full reasoning chain.

For an explicit Sol opinion, ALWAYS run `astra` § Sol (`gpt-6.1-sol`,
ephemeral) under the same `astra` § Rules; NEVER answer a Sol request on the
Astra model silently.

When the selected model cannot run (revoked auth, missing CLI or model),
ALWAYS report the failure and ask before selecting another model.
NEVER substitute an engine without the user's choice.

## Output

Treat every oracle answer as advisory. Cite the finding when acting; discard
wrong claims with a one-line reason.
