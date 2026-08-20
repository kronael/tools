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
3. **Lint-rule extraction** (heavier pass, user-invoked): when the session
   shows a repeated deterministic, language-specific correction, propose an
   ast-grep lint rule so the next session is enforced, not re-reminded.

Run memory evaluation first when triggered by the nudge; run full extraction
when the user explicitly asks to learn from a session.

## Rules for extracted skills
- ALWAYS read the session transcript and identify the specific failure/decision being captured BEFORE drafting (path: see global skill startup protocol).
- NEVER promote a single-session story to a skill — need pattern in 2+ distinct sessions; otherwise record in .diary/.

## Rules for extracted lint rules
- ALWAYS gate on structure: only a pattern-matchable mistake becomes a lint.
  Judgment (naming, minimality, "boring code") stays a skill — NEVER lint
  judgment; a false positive trains the agent to reach for `--no-verify`.
- ALWAYS co-locate and prove: write the rule into `skills/<lang>/lints/rules.yml`
  with bad+good fixtures, `severity: warning`, `note:` citing the skill; add the
  id to that skill's `## Lints`; prove it with `make lints`.
- ALWAYS propose, NEVER auto-promote to `error` — the user promotes after review.
- NEVER extract from a single session — need the same correction in 2+ sessions.

## Rules for memory evaluation
- ALWAYS distinguish the four memory types (user/feedback/project/reference) per the auto-memory format — don't dump everything into one bucket.
- NEVER save routine operations or one-off trivia — only durable, reusable facts or confirmed corrections.
- ALWAYS update `MEMORY.md`'s one-line index when adding an entry.
- NEVER invoked by the bare word "learn" appearing in a user prompt — that keyword route was removed deliberately (see hooks/README.md). Only the slash command and the `memory_nudge.py` hook trigger it.
