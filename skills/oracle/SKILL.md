---
name: oracle
description: Independent critique of code, plans, products or claims. NOT for routine lookups (use direct tools) or execution work (use dispatch).
when_to_use: "oracle, second opinion, sanity check, plan critique, code critique, creative critique, security audit critique, red team critique"
user-invocable: true
---

# Oracle

This skill owns second-opinion framing and verification. `dispatch` owns task
selection, models, effort, capacity and overrides; `claude` and `codex` own
provider launches. ALWAYS pass the owner's requested model, provider and effort
through unchanged. “Ask Codex” selects a provider, not an audit model.

## Select the task

ALWAYS select the task from `dispatch` by the requested output. A code or plan
critique uses review; a broad adversarial, security or systemic critique uses
audit. Creative critique follows the same distinction. Product specification
and implementation are separate tasks, not implicit parts of an opinion.

ALWAYS preserve a required fresh reviewer or auditor. A provider's same-model
inline shortcut applies only to an ordinary opinion without an independence
requirement. NEVER use it to bypass `review`, `refine` or their whole-change
audit. For an explicit Pi request, use `pi` and preserve its actual engine
choice; NEVER substitute it for a selected Claude or Codex route silently.

## Brief

ALWAYS use `dispatch` § Brief. Give the goal, target artifacts, entry points,
house rules, boundaries and required evidence. Frame the request adversarially:
“Find what breaks this claim” or “Find the flaw in this plan.”

- NEVER ask “is this correct?” or “does this look right?” Those questions
  invite confirmation. ALWAYS ask what breaks, what is missing or why it fails.
- NEVER provide your own suspected weaknesses or reasoning chain. ALWAYS let
  the reviewer choose the attack from the goal and source artifacts.
- ALWAYS give an implementation-plan reviewer the accepted requirements and
  current plan as artifacts, not the author's defense of its choices.
- ALWAYS require findings with `file:line`, a concrete trace or a command and
  its output. A summary without evidence does not support a change.

## Settle the result

ALWAYS verify each claim against the source before acting. Cite the evidence
when applying a finding; give a one-line reason when discarding it. NEVER
implement an opinion blindly or treat the model's confidence as proof.

On unavailable credentials, model, effort or usage capacity, ALWAYS report the
exact selected route and limitation. Continue independent preparation; NEVER
silently substitute an engine. Dispatch owns explicit owner-approved alternatives.
