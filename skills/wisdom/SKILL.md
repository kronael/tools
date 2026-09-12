---
name: wisdom
description: Write or edit SKILL.md, CLAUDE.md, AGENTS.md. NOT for general code (use go/rs/py/ts), mining history (use learn), or researching/codifying public best practice into a skill (use scavenge).
when_to_use: "creating a new skill, adding a rule to CLAUDE.md, fixing a skill description, writing ALWAYS/NEVER statements, does this rule earn its context, cut what the model already knows, trim an always-loaded file"
---

# Wisdom Skill

## SKILL.md frontmatter

```yaml
---
name: short-name          # must match intended slash command slug if user-invocable
description: <one-line summary>. NOT for <case> (use <other-skill>).
when_to_use: <trigger phrases — natural requests users would say>
user-invocable: true      # optional — exposes skill as /name slash command in the UI
---
```

- ALWAYS keep `description` minimal — short summary + NOT clause only.
- ALWAYS pack `when_to_use` with retrieval keywords: error messages, symptom words, tool/library names, synonyms.
- `description` + `when_to_use` share a 1,536-char budget — both shown to Claude for routing.
- NEVER write description as workflow summary ("summarizes X via Y") — Claude shortcuts past skills whose description states the process.
- ALWAYS add `NOT for <case> (use <other-skill>)` in `description` — disambiguates neighbors.
- NEVER write "This skill helps you…" or marketing prose.
- NEVER use vague terms like "general utilities", "various tools".
- NEVER use trigger words shared with a sibling skill's primary trigger — causes routing races.

## Body patterns

- **Mode-toggle** (fin/explore style): concise `## Behavior` block, no other sections.
- **Agent-launcher** (visual/readme style): single sentence: "Launch the @X agent (Task tool, subagent_type: X) to…"
- **Runbook** (ship/merge/release style): numbered steps, each closing on a
  `Completion criterion:` line — an observable pass/fail condition, not "done
  when it looks right". Close with `## Review Checklist` restating the file's
  ALWAYS rules as checkable bullets, and, only where one recurring wrong-but-
  plausible shortcut exists, an `## Anti-Patterns` list naming it.

## SKILL.md body

- ALWAYS use ALWAYS/NEVER; NEVER use SHOULD (too soft).
- ALWAYS pair NEVER with ALWAYS: "NEVER X — ALWAYS Y instead."
- ALWAYS keep under 200 lines; skills persist in context all session. No exceptions — overflow goes to sibling files, never a longer SKILL.md.
- NEVER add obvious code examples LLMs already know.
- NEVER duplicate content between skills or with the global wisdom file.
- ALWAYS push overflow (anything >50 lines — API docs, tables, deep dives) into adjacent sibling files linked from the SKILL.md, loaded on demand; SKILL.md stays workflow-only. The SKILL.md MAY tell the LLM to force-read a sibling when it's mandatory, not optional.

- For example/context-budget and subagent effort defaults, follow
  `skills/CLAUDE.md`; keep this skill as the compact writing checklist.

## Router skills

- Router = one `SKILL.md` (the only preloaded file) + sibling cold data `.md` files read on demand (`create/`, `software/`).
- ALWAYS make a router instead of N sibling skills when they share an audience and are rarely invoked — N preloaded descriptions collapse to 1.
- Router body = explicit dispatch table mapping trigger keywords → data file; NEVER prose links alone.
- Router frontmatter MUST carry every folded mode's retrieval keywords within the 1,536-char budget — `/resolve` routes on them.
- Light content lives flat (`<mode>.md`); heavy ported trees keep their subtree intact at `<mode>/<slug>/`.
- NEVER name a data file `SKILL.md` — that is what makes it preload.
- Maintenance procedure: `skills/CLAUDE.md`.

## CLAUDE.md (project)

- Project-specific only — skills carry general knowledge.
- ALWAYS document architecture, state machines, external systems.
- Put critical rules at the top or bottom — middle content is least reliably attended to.
- ALWAYS wrap task-specific sections (testing conventions, API patterns, state
  management, i18n) in `<important if="condition">…</important>` with one
  narrow, single-trigger condition per block — Claude Code's own system
  reminder tells the model project context "may or may not be relevant,"
  and the tag overrides that framing so the block gets attention when its
  condition actually matches, instead of being skimmed past by default.
- NEVER wrap onboarding context relevant to 90%+ of tasks (project identity,
  directory map, tech stack, the commands table) — leave those bare; gating
  foundational context behind a narrow `if` starves it of attention on the
  tasks that need it most.
- NEVER give one `<important if>` block two unrelated trigger conditions —
  split "testing + API conventions" into two blocks so a task matching only
  one doesn't pull in the other's rules.
- This does NOT apply to this repo's own installed `~/.claude/CLAUDE.md`
  (the global wisdom file) — that file is always-loaded outside the
  per-project relevance gate, so the tag has nothing to cut through there.


## Minimize — does a rule earn its context?

A rule in an always-loaded file costs every session. It earns that only when
the model would not already behave that way. Measure it: put the topic to a
model that cannot see the rule, and compare.

- Reproduced by the clean model → candidate CUT, not a verdict. See below.
- Contradicted by it → KEEP, highest value. Overriding a strong prior is the
  one thing guidance can do that training cannot.
- Produced by neither → KEEP.

**Reproduction measures knowledge, not compliance.** A model will write a rule
out cleanly and then break it unprompted, so a reproduced rule is only free if
the model also FOLLOWS it by default. ALWAYS settle a candidate cut with a
second question to the clean room — ask the model to describe how it actually
behaves on a task with no instructions, its real defaults including the wrong
ones — and KEEP anything it confesses to violating. Models report writing
comments that narrate the change, declaring a task done on a green test run,
softening a partial result into language that reads complete, trusting a
subagent's summary unchecked, and cleaning up adjacent code nobody asked about
— every one of those is a rule they can also recite. A rule a model states and
breaks belongs in the file, stressed, not cut.

ALWAYS scope this to normative content — wisdom, style, judgment. A workflow
runbook encodes a chosen procedure and is not measurable this way.

**NEVER measure with a subagent.** It is handed `~/.claude/CLAUDE.md` and every
applicable project `CLAUDE.md` before its first token, so "do not read any
files" removes nothing and it paraphrases the rule back as its own. The tell is
specificity: a clean model gives the field default, a contaminated one returns
this repo's exact paths, counts and separators.

ALWAYS use `clean-room.sh <model> <prompt-file>` — a throwaway `HOME` so no
wisdom file loads, an empty working directory so no project `CLAUDE.md` is
discoverable. Export `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` first; a
clean `HOME` puts OAuth and the keychain out of reach. ALWAYS run two models —
one agreeing is a signal, two is a verdict.

ALWAYS verify the room before trusting a run: ask a probe this repo answers
unusually (branch naming, worktree placement, line width) and confirm the reply
gives the field default. Discard the whole run when repo-specific detail comes
back.

NEVER quote or paraphrase our text in the prompt — ask for the guidance itself,
never for a critique of ours. This includes the list of sub-topics: a "cover X,
Y, Z" line built from our own section headings is our table of contents, and a
model completing it proves only that it can write to a spec. Name the DOMAIN
alone and let the model decide what belongs in it; a rule it never thought to
mention is the finding. Before sending, read the prompt back and strike any
phrase you could locate in the file being measured.

Findings go to `BUGS.md` as a proposal naming which model produced what. NEVER
cut an always-loaded rule on sight — it changes every future session.
