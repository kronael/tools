---
name: coding-oracle
description: Ask fable (its code capabilities) for an adversarial second opinion on code — review, bug-hunt, design critique, architecture decision. NOT for creative critique (use creative-oracle). NOT for routine lookups (use grep/read/recall-memories).
when_to_use: "code review, second opinion on code, find the bug, tricky algorithm, unfamiliar library, sanity check a design, architecture decision, disagreement after reasoning on code, ask oracle about code"
user-invocable: true
---

# Coding Oracle

Non-creative code critique routes to **fable** (Claude, its code-review
capabilities) — NOT codex. Use this skill whenever the ask is: review this
code, hunt for bugs, critique a design/architecture, sanity-check an
algorithm, or get a second opinion on anything code-shaped.

For creative work (naming, prose, narrative, novel ideation) use
`creative-oracle` instead, which routes to codex.

## Invoke

Launch a background `fable` agent (Agent tool, `subagent_type: "fable"`,
`run_in_background: true`) — see the `fable` skill for the exact call
shape. The fable agent definition sets high effort; do not substitute a
default/medium agent for code second opinions. NEVER use a raw `Agent(...)`
call without going through this routing when you need a code second opinion.

```
Agent({
  subagent_type: "fable",
  run_in_background: true,
  description: "<short task>",
  prompt: "Goal: <X>. Find the flaw in <code/design>. <entry points: files, symbols, error output>."
})
```

## Adversarial framing

fable is a peer reviewer, not a rubber stamp — but framing still matters:

- ALWAYS attack your own conclusion: "Find the flaw in X", "Why would this
  break?", "What did I miss?"
- NEVER ask "is X correct?" / "does this look right?" — primes a yes.
- ALWAYS state the goal in one line ("Goal: <X>").
- For targeted questions: hand it entry points (file paths, symbols, error
  output).
- For open-ended research: state the goal and desired output format — skip
  prescribed steps, let fable explore.
- NEVER paste your full reasoning chain or conclusions — biases the second
  opinion.

## Output

Treat the answer as advisory. ALWAYS verify fable's claim against the
codebase before acting. NEVER implement blindly. Discard with a one-line
reason if wrong; cite when acting.

## Relationship to other skills

- `oracle` is a legacy alias — it now points here (coding is the default,
  non-creative case).
- `codex` / `pi` remain the underlying second-opinion CLIs used by
  `creative-oracle` for creative critique. They are not deprecated —
  just no longer the default for code review.
