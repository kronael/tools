---
name: learn
description: /learn — turn session history into memory entries, skills, or lint rules. NOT for writing a skill from scratch (use wisdom); the word "learn" in a prompt is no trigger.
when_to_use: "learn from this session, save this pattern, extract reusable patterns, session memory check, save memory, remember this, make this correction a rule, check whether the workflow ran, check recall routing"
user-invocable: true
---

# Learn — session history into memory, skills and lints

## Where it runs

The memory pass runs where the nudge lands — in the main thread, or in a
fact-gathering worker selected through `dispatch`, briefed to run the memory
pass for the given transcript path. The skill and lint passes ALWAYS run
in the main thread. ALWAYS honor approval already given in the session.

## Sources

- `~/.claude/projects/<slug>/*.jsonl` — per-project transcripts (slug: WISDOM
  § Continuity); reading recipe in `recall-memories` §1.
- `~/.claude/history.jsonl` — global prompt history.
- `~/.claude/projects/<slug>/memory/` — existing memory files and the
  `MEMORY.md` index.

## Check expected actions against the record

ALWAYS use `recall-memories` to locate evidence for each pass. ALWAYS inspect
the relevant task interval for expected workflow actions, even without user correction.
ALWAYS compare instructions applicable at that time with recorded skill reads
or invocations, routing reasons, tool calls, worker launches, results and follow-up verification.
ALWAYS identify each material gap by expected action, observed action, source
location and consequence. ALWAYS distinguish verified omissions from unavailable records.
NEVER infer hidden reasoning from a missing decision line. NEVER accept an
assistant's claim alone as proof of compliance.

The recall helper excludes recall calls from search. When checking recall use
or routing, ALWAYS inspect the relevant raw transcript interval. ALWAYS open
known call handles with `show` where possible. NEVER treat an empty helper search
as proof of non-use.

ALWAYS check whether the owning instruction already covers a gap. If so,
ALWAYS propose a repair to its trigger or workflow, never another copy of the rule.
ALWAYS require two distinct sessions for a newly inferred skill or lint pattern.
An explicit request to repair an existing workflow follows the authorization
already given for that repair.
ALWAYS keep a nudge within the memory pass. ALWAYS save only qualifying durable
facts or evidence pointers. A nudge does not authorize skill or lint edits.
ALWAYS apply the approval rules below to user-invoked skill and lint passes.

## Three passes

ALWAYS use the shared evidence check above in every pass.

- **Memory** — the nudge, or "save memory": read the current transcript; pick
  user corrections, confirmed decisions, durable project facts and reference
  pointers; write each as a file under `~/.claude/projects/<slug>/memory/`
  with frontmatter `name`, `description` and `metadata.type`
  (`user`/`feedback`/`project`/`reference`) plus a one-line `MEMORY.md`
  entry. No user round-trip: save what qualifies, skip the rest, report what
  was saved or that nothing qualified.
- **Skill** — user-invoked: inspect corrections, workflow gaps, successful
  choices, ALWAYS/NEVER statements and recurring themes. For each unapproved
  candidate, ALWAYS ask with context and the proposed skill: approve/reject/modify.
  ALWAYS detail approved items in plan mode and write within the approved scope.
  ALWAYS report what was written.
- **Lint** — user-invoked: the same structural, pattern-matchable correction
  across 2+ sessions → `wisdom`'s promotion procedure. `astgrep` → `lints.md`
  owns rule files, fixtures, bindings and project adoption.

The nudge runs the memory pass. "Learn from this session" runs the skill
pass, then the lint pass.

## What qualifies

User corrections, explicit rules, patterns that worked and domain knowledge
can qualify. Workflow omissions and successful tool or routing choices need
supporting evidence and must pass the durable, reusable filter below.
A repeated structural mistake on one language can qualify as a lint candidate.

## Rules

- ALWAYS locate the specific failure or decision in the transcripts BEFORE
  drafting anything.
- NEVER promote a newly inferred pattern from one session to a skill or lint.
  ALWAYS require the same pattern in two distinct sessions. A single session
  goes to the diary. Explicit workflow repairs use the authorization above.
  Implementing an approved rule as a lint follows `wisdom` without this discovery threshold.
- NEVER lint judgment (whether a name fits, minimality, "boring code") — a
  false positive trains `--no-verify`. A mechanical shape is lintable, such as
  a bool-returning function without an `is_`/`has_`/`can_`/`should_` prefix.
  Only the user promotes a lint to `error`.
- ALWAYS write a skill per `wisdom` (frontmatter keys, `NOT for`,
  ALWAYS/NEVER, length) and pass `make skills-frontmatter`; NEVER carry a
  second copy of those rules here.
- NEVER save routine operations or one-off trivia — durable, reusable facts
  only.
