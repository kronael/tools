# Hermes Agent — what we should and shouldn't copy

Hermes Agent (Nous Research) is a long-running coding agent with a built-in **Curator** that periodically reviews skills and memory. The popular framing is "auto-improving agent", which is misleading on two counts: (a) the trigger is **inactivity**, not per-turn, and (b) the live-edit-without-approval behavior is contested upstream.

## Sources

- [Hermes Curator docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator) — official spec of triggers, scope, and tool whitelist
- [Hermes background-review source](https://github.com/NousResearch/hermes-agent/blob/main/agent/background_review.py) — `spawn_background_review_thread` and the three review prompts
- [Hermes issue #18373](https://github.com/NousResearch/hermes-agent/issues/18373) — open request for dry-run / approval before auto-archival
- [BSWEN writeup, April 2026](https://docs.bswen.com/blog/2026-04-07-hermes-ai-overwrites-skills/) — independent critique with examples of Hermes overwriting manual customizations

## What Hermes actually does

- **Trigger**: idle ≥2h since last user message, OR scheduled weekly cycle. Not per-turn (we misread this in v1 of our spec).
- **Fork**: spawns a daemon thread, snapshots conversation messages, installs a thread-level tool whitelist (memory + skills only).
- **Review prompts**: three module-level strings — memory, skill, combined. The skill prompt biases toward updating currently-loaded skills first, then umbrella skills, then creating new skills.
- **Scope**: agent-authored skills only. Bundled / hub-installed skills stay read-only — Hermes treats them as the canonical baseline.
- **Provenance**: skills written by the background fork get `write_origin="background_review"`, distinguishable from foreground / human edits.

## What goes wrong (BSWEN's findings)

- "Agent almost always thinks it performed well, even when it didn't" — the review's self-assessment is congratulatory by default, and that feeds into the edits.
- Manual customizations get overwritten with worse versions. Issue #18373 is the documented complaint.
- No dry-run mode at time of writing — edits land directly in the skill store.

## What we keep

- The **scope guardrail**: bundled skills are read-only. Adapt to our world: skills shipped in this repo (`skills/*/SKILL.md`) are the source of truth and edits land via PR, not via runtime mutation.
- The **idle trigger**: per-turn is wrong. Wait until the user is done.
- The **multi-prompt approach**: a separate prompt for memory vs skills vs both.

## What we don't copy

- **Runtime auto-edit without approval**. Library Drift findings + BSWEN's evidence make this a known failure mode. Quarantine + explicit approval mandatory.
- **Self-rated confidence**. Hermes's bias is documented; we need a separate evaluator (eval set), not the same LLM judging itself.
- **Per-turn anything**. Even if we reused the trigger, the review fires on inactivity, not on each Stop.

## Implication for our spec

We're not building a Hermes clone. We're building an **offline eval loop for the bundled skill library** in this repo. The output is PRs against `skills/*/SKILL.md`, not runtime mutations of `~/.claude/skills/`.
