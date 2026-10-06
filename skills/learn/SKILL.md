---
name: learn
description: /learn — turn session history into memory entries, skills, or lint rules. NOT for writing a skill from scratch (use wisdom). NOT triggered by the word "learn" in a prompt — only the slash command or the memory_nudge hook (PreCompact/Stop) invokes it.
when_to_use: "learn from this session, save this pattern, extract reusable patterns, evaluate session for memory, session memory check, save memory, remember this, make this correction a rule"
user-invocable: true
---

# Learn — session history into memory, skills and lints

## Where it runs

The memory pass runs where the nudge lands — in the main thread, or in an
`Agent(subagent_type: learn)`, the thin agent that loads this skill, told to
"run the memory pass for <transcript path>". The skill and lint passes ask
the user to approve each item, so they ALWAYS run in the main thread.

## Sources

- `~/.claude/projects/<slug>/*.jsonl` — per-project transcripts (slug = cwd
  with `/` → `-`); reading recipe in `recall-memories` §1.
- `~/.claude/history.jsonl` — global prompt history.
- `~/.claude/projects/<slug>/memory/` — existing memory files and the
  `MEMORY.md` index.

## Three passes

- **Memory** — the nudge, or "save memory": read the current transcript; pick
  user corrections, confirmed decisions, durable project facts and reference
  pointers; write each as a file under `~/.claude/projects/<slug>/memory/`
  with frontmatter `name`, `description` and `metadata.type`
  (`user`/`feedback`/`project`/`reference`) plus a one-line `MEMORY.md`
  entry. No user round-trip: save what qualifies, skip the rest, report what
  was saved or that nothing qualified.
- **Skill** — user-invoked: grep the transcripts for corrections,
  ALWAYS/NEVER statements and recurring themes; present each candidate as a
  question — context, proposed skill, approve/reject/modify; enter plan mode
  to detail the approved ones; write only after sign-off and report what was
  written.
- **Lint** — user-invoked: the same structural, pattern-matchable correction
  on one language across 2+ sessions → an ast-grep rule in
  `skills/<lang>/lints/rules.yml` (`id`, `rule`, `message` naming the fix plus
  `See skill:<lang>`, `severity: warning`, `note:` citing the skill), a
  `<rule-id>.bad.<ext>` and `<rule-id>.good.<ext>` fixture proven by
  `make lints`, and the id under that skill's `## Lints`.

The nudge runs the memory pass. "Learn from this session" runs the skill
pass, then the lint pass.

## What qualifies

User corrections ("no, use X not Y"), explicit rules ("ALWAYS do X"),
patterns that worked, domain-specific knowledge, and a repeated structural
mistake on one language — a lint candidate.

## Rules

- ALWAYS locate the specific failure or decision in the transcripts BEFORE
  drafting anything.
- NEVER promote one session to a skill or a lint — the same pattern in 2+
  distinct sessions; a single session goes to `.diary/`.
- NEVER lint judgment (whether a name fits, minimality, "boring code") — a
  false positive trains `--no-verify`. A mechanical shape is lintable, such as
  a bool-returning function without an `is_`/`has_`/`can_` prefix. Only the
  user promotes a lint to `error`.
- ALWAYS write a skill per `wisdom` (frontmatter keys, `NOT for`,
  ALWAYS/NEVER, length) and pass `make skills-frontmatter`; NEVER carry a
  second copy of those rules here.
- NEVER save routine operations or one-off trivia — durable, reusable facts
  only.
