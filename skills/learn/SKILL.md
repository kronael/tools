---
name: learn
description: /learn — turn session history into memory entries, skills, or lint rules. NOT for writing a skill from scratch (use wisdom). NOT triggered by the word "learn" in a prompt — only the slash command or the memory_nudge hook (PreCompact/Stop) invokes it.
when_to_use: "learn from this session, save this pattern, extract reusable patterns, evaluate session for memory, session memory check, save memory, remember this, make this correction a rule"
user-invocable: true
---

Launch the @learn agent (Task tool, subagent_type: learn) and name the pass.

## Three passes

- **Memory** — the nudge, or "save memory": corrections, confirmed
  decisions, durable project facts, reference pointers →
  `~/.claude/projects/<slug>/memory/` plus a one-line `MEMORY.md` index
  entry. No user round-trip: save what qualifies, skip the rest.
- **Skill** — user-invoked: a theme that recurs across sessions → a
  proposed new or updated skill; the user approves each before it is written.
- **Lint** — user-invoked: the same structural, pattern-matchable
  correction on one language → an ast-grep rule in
  `skills/<lang>/lints/rules.yml`, so the next session is enforced, not reminded.

The nudge runs the memory pass. "Learn from this session" runs the skill
pass, then the lint pass.

## Rules

- ALWAYS locate the specific failure or decision in the transcripts
  (`~/.claude/projects/<slug>/*.jsonl`; recipe: `recall-memories` §1)
  BEFORE drafting anything.
- NEVER promote one session to a skill or a lint — the same pattern in
  2+ distinct sessions; a single session goes to `.diary/`.
- NEVER lint judgment (naming, minimality, "boring code") — a false
  positive trains `--no-verify`. A lint ships with bad+good fixtures,
  `severity: warning`, a `note:` citing the skill, its id in that skill's
  `## Lints`, and passes `make lints`. Only the user promotes it to `error`.
- ALWAYS write a skill per `wisdom` (frontmatter keys, `NOT for`,
  ALWAYS/NEVER, length) and pass `make skills-frontmatter`.
- NEVER save routine operations or one-off trivia — durable, reusable
  facts only, typed `user` / `feedback` / `project` / `reference`.
