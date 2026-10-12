---
name: oracle
description: One second-opinion router for code, planning, security/deep audit, and creative critique. NOT for routine lookups (use grep/read/recall-memories) or fire-and-forget work (use dispatch).
when_to_use: "oracle, second opinion, sanity check, ask oracle, planning oracle, plan critique, code critique, creative critique, security audit critique, red team critique, disagreement after reasoning"
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
| Naming, prose, narrative, product copy, ideation | `astra` skill, high effort |
| Ambiguous but touches code or operations | `fable` subagent |
| Explicit "ask codex" / "use codex" | `astra` skill, high effort |
| Explicit Astra or Sol request | `astra` skill; for Sol, its § Sol variant |

## Fable Route

Launch a background agent with `subagent_type: "fable"` — `agents/fable.md`
pins it at xhigh, so every fable route runs at xhigh; the opus fallback
(`agents/opus.md`) runs at high. Include the goal, target files/dirs, and
what to return. Frame adversarially:

```text
Goal: <X>. Find the flaw in <code/design/plan>. Entry points: <files, symbols,
error output>. Return findings only, with file:line or concrete trace.
```

Rules:

- NEVER set effort in the prompt text — ALWAYS rely on the agent file's pin.
- Never ask "does this look right?" Ask what breaks, what is missing, or why the
  plan fails.
- Verify claims against the repo before acting.
- When fable cannot run (a usage limit), ALWAYS take the same route on
  `subagent_type: "opus"` — NEVER skip the opinion.

## Astra Route

Load the `astra` skill and follow its runbook. Use it for creative critique and
explicit Codex or Astra requests. Keep the prompt adversarial and high-level; do not
paste your full reasoning chain.

For an explicit Sol opinion, ALWAYS run `astra` § Sol (`gpt-6.1-sol`,
ephemeral) under the same `astra` § Rules; NEVER answer a Sol request on the
Astra model silently.

When the Astra CLI call cannot run (revoked auth, missing CLI), ALWAYS report
the failure and take the Fable Route, on opus when fable cannot run either.
For a missing pinned model, ALWAYS follow the named skill's stop-and-report
rule; NEVER substitute an engine without the user's choice.

## Output

Treat every oracle answer as advisory. Cite the finding when acting; discard
wrong claims with a one-line reason.
