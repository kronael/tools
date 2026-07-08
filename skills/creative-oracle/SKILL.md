---
name: creative-oracle
description: Ask codex for an adversarial second opinion on creative work — naming, prose, narrative, novel ideation, brainstorming. NOT for code review/bug-hunt/design critique (use coding-oracle).
when_to_use: "creative critique, naming ideas, prose review, narrative feedback, brainstorm alternatives, second opinion on copy, sanity check an idea, disagreement after reasoning on non-code work"
user-invocable: true
---

# Creative Oracle

Creative critique routes to **codex** — naming, prose, narrative structure,
novel ideation, brainstorming alternatives, anything where the output is
words/ideas rather than code correctness.

For code review, bug-hunting, or architecture critique use `coding-oracle`
instead, which routes to fable.

The full invocation runbook (auth checks, sandbox flags, model pinning,
adversarial framing, output handling) lives in the `codex` skill — load
that skill and follow it. This skill exists to make the routing decision:
creative work goes to codex, not fable.

## When to reach for this

- Naming a project, skill, artifact, or product
- Reviewing/tightening prose, copy, or narrative
- Ideating alternatives for a creative direction
- Sanity-checking a pitch, tagline, or story beat

## Rules

- ALWAYS frame adversarially: "Find the flaw in this name/story/copy",
  "why would this fall flat?" — NEVER "does this sound good?" (primes a
  yes; codex is sycophantic).
- ALWAYS treat the answer as advisory — cite when acting on it, discard
  with a one-line reason when not.
- For a second, non-Claude cross-check on the same creative question, `pi`
  is available alongside codex (see the `pi` skill).
