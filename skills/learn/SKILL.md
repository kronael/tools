---
name: learn
description: /learn — extract patterns into skills from session history. NOT for writing skills from scratch (use wisdom).
when_to_use: "learn from this session", "save this pattern", extract reusable patterns
user-invocable: true
---

Launch the @learn agent (Task tool, subagent_type: learn) to analyze conversation history and create or update skills.

## Rules for extracted skills
- ALWAYS read the actual session transcript (~/.claude/projects/<slug>/*.jsonl) and identify the specific failure/decision being captured BEFORE drafting.
- ALWAYS write the new skill's description as triggers ("Use when…"), NEVER as workflow summary.
- NEVER promote a single-session story to a skill. Need pattern in 2+ distinct sessions; otherwise record in .diary/.
