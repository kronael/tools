---
name: learn
description: /learn — extract patterns into skills from session history, and evaluate the session for memory-worthy content. NOT for writing skills from scratch (use wisdom). NOT auto-triggered by the word "learn" in a prompt — invoke explicitly or via the low-frequency memory_nudge hook (PreCompact/Stop).
when_to_use: "learn from this session, save this pattern, extract reusable patterns, evaluate session for memory, session memory check"
user-invocable: true
---

Launch the @learn agent (Task tool, subagent_type: learn) to analyze conversation history, evaluate it for memory-worthy content, and create or update skills.

## Two capabilities, one skill

1. **Memory evaluation** (usually the low-effort pass, often nudge-triggered):
   review the session for corrections, confirmed decisions, project facts, or
   reference pointers and save them via the auto-memory mechanism
   (`~/.claude/projects/<slug>/memory/`, frontmatter
   `name`/`description`/`metadata.type` of `user`/`feedback`/`project`/
   `reference`, indexed in `MEMORY.md`). This does not require user
   back-and-forth — save what clearly qualifies, skip what doesn't.
2. **Pattern/skill extraction** (heavier pass, always user-invoked): read
   conversation history, identify recurring themes, and propose new/updated
   skills for the user to approve (see agent process).

Run memory evaluation first when triggered by the nudge; run full extraction
when the user explicitly asks to learn from a session.

## Rules for extracted skills
- ALWAYS read the session transcript and identify the specific failure/decision being captured BEFORE drafting (path: see global skill startup protocol).
- NEVER promote a single-session story to a skill — need pattern in 2+ distinct sessions; otherwise record in .diary/.

## Rules for memory evaluation
- ALWAYS distinguish the four memory types (user/feedback/project/reference) per the auto-memory format — don't dump everything into one bucket.
- NEVER save routine operations or one-off trivia — only durable, reusable facts or confirmed corrections.
- ALWAYS update `MEMORY.md`'s one-line index when adding an entry.
- NEVER invoked by the bare word "learn" appearing in a user prompt — that keyword route was removed deliberately (see hooks/README.md). Only the slash command and the `memory_nudge.py` hook trigger it.
