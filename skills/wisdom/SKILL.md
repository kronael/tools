---
name: wisdom
description: Write or edit SKILL.md, CLAUDE.md, AGENTS.md. NOT for general code (use go/rs/py/ts), mining history (use learn), or researching/codifying public best practice into a skill (use scavenge).
when_to_use: "creating a new skill, adding a rule to CLAUDE.md, fixing a skill description, writing ALWAYS/NEVER statements, skill not triggering, skill frontmatter, when_to_use, skill lint failed, does this rule earn its context, cut what the model already knows, trim an always-loaded file, instruction tags, conditional instruction scoping"
---

# Wisdom Skill

## Treat skills as first-class

Skills are durable, DRY knowledge, explicitly dispatched — NOT auto-triggered
(see WISDOM), so `/solve` can only route what the frontmatter describes well.

- ALWAYS hold a skill to ONE concern; a sprawling skill matches everything and routes nothing.
- ALWAYS extend the right existing skill over spawning a near-duplicate — grep the skill list first; two skills on one concern race in `/solve` and drift out of sync.

## Pairing with /learn

`/learn` mines session history — it surfaces reusable patterns (2+ sessions) and
proposes new/updated skills, but hands the authoring off to wisdom.

- ALWAYS turn a `/learn` proposal into well-formed SKILL.md here (frontmatter + ALWAYS/NEVER body), not a rough draft left in a transcript.
- ALWAYS fold a surfaced pattern into the correct existing skill when one fits; author a new skill only when none does.
- NEVER let a single-session story become a skill — record it in .diary/ (learn's 2+ rule); persist genuine patterns via /learn → wisdom.

## SKILL.md frontmatter

```yaml
---
name: short-name              # the /name slug and the Skill tool name
description: <one-line summary>. NOT for <case> (use <other-skill>).
when_to_use: <trigger phrases — what a user would say>
user-invocable: false         # optional — hides /name from the menu; Claude can still invoke it
argument-hint: "<question>"   # optional — shown after /name
---
```

- ALWAYS include `name`, `description`, `when_to_use` — lint: skill-keys (hard fail).
- NEVER invent a key — Claude Code reads `name`, `description`, `when_to_use`, `user-invocable`, `disable-model-invocation`, `argument-hint`, `arguments`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `shell`, `context`, `agent`, `background`, `paths`, `hooks`, `metadata`, `license`, `compatibility`; any other key (`arg:`) is silently ignored here and rejected by other Agent Skills consumers — lint: skill-keys (hard fail). Provenance goes under `metadata`.
- ALWAYS keep `description` minimal — short summary + NOT clause only.
- ALWAYS pack `when_to_use` with retrieval keywords: error messages, symptom words, tool/library names, synonyms.
- The listing shows `description - when_to_use`, cut at 1,536 chars, and the whole listing has a context budget — `skills/CLAUDE.md` § Flat skills vs router skills owns both. ALWAYS put the key use case first (lint: skill-budget, warn).
- NEVER write description as workflow summary ("summarizes X via Y") — Claude shortcuts past skills whose description states the process.
- ALWAYS add `NOT for <case> (use <other-skill>)` in `description` — disambiguates neighbors; lint: skill-notfor (warn).
- NEVER write "This skill helps you…" or marketing prose.
- NEVER use vague terms like "general utilities", "various tools".
- NEVER use trigger words shared with a sibling skill's primary trigger — causes routing races.
- ALWAYS test reachability before committing: write the request the way a user types it and `grep -il '<its key word>' skills/*/SKILL.md` — the hit is this skill and no sibling's primary trigger. A skill reachable only by its name is unreachable from a description match.

## Body patterns

- **Mode-toggle** (fin/ans style): concise `## Behavior` block, no other sections.
- **Self-contained** (visual/improve style): the body carries the full
  instructions; a `## Where it runs` block names the agent to launch — rules
  in `skills/CLAUDE.md` § Agent definitions.
- **Runbook** (ship/merge/release style): numbered steps, each closing on a
  `Completion criterion:` line — an observable pass/fail condition, not "done
  when it looks right". Close with `## Review Checklist` restating the file's
  ALWAYS rules as checkable bullets, and, only where one recurring wrong-but-
  plausible shortcut exists, an `## Anti-Patterns` list naming it.

## SKILL.md body

- ALWAYS use ALWAYS/NEVER for every directive, never the soft 'should' form — lint: skill-should (hard fail).
- ALWAYS pair NEVER with ALWAYS: "NEVER X — ALWAYS Y instead."
- ALWAYS keep under 200 lines; a body loads in full on every invocation. No exceptions — overflow goes to sibling files, never a longer SKILL.md. Lint: skill-length (warn; workflow/runbook skills up to 500).
- NEVER add obvious code examples LLMs already know.
- NEVER duplicate content between skills or with the global wisdom file — one rule lives in the skill that owns it; the others point.
- ALWAYS push overflow (anything >50 lines — API docs, tables, deep dives) into adjacent sibling files linked from the SKILL.md, loaded on demand; SKILL.md stays workflow-only. The SKILL.md MAY tell the LLM to force-read a sibling when it's mandatory, not optional.
- ALWAYS run `make skills-frontmatter` (repo root) after an edit; pre-commit runs the same lint.
- For example/context-budget and subagent effort defaults, follow
  `skills/CLAUDE.md`; keep this skill as the compact writing checklist.

## The subtraction test — ALWAYS run it before writing or trimming

A rule in an always-loaded file costs every session; it earns that only when a
capable model would not already behave that way. NEVER judge that from memory
— measure it. `subtraction.md` in this directory owns the procedure: the clean
room, the prompts, the file order, the verdict table and where findings go.
ALWAYS read it before a measurement.

- Reproduced by the clean model → candidate CUT, not a verdict. See below.
- Contradicted by it, or marked `[NEEDS TELLING]` → KEEP, highest value.
  Overriding a strong prior is the one thing guidance can do that training
  cannot.
- Produced by neither → KEEP.
- Local facts it cannot guess (paths, house conventions, tool and skill
  names), workflows, and rules that deliberately OVERRIDE the harness → KEEP,
  the override labelled in place. ALWAYS scope the test to normative content —
  wisdom, style, judgment; a workflow runbook encodes a chosen procedure and is
  not measurable this way.
- A survivor the system prompt or the active output style already states → CUT.
- Real engineering content that is not always needed → MOVE to the skill that
  owns it, loaded on demand, after checking it is not already there; NEVER
  delete it.

**Reproduction measures knowledge, not compliance.** A model will write a rule
out cleanly and then break it unprompted. ALWAYS ask the clean room the
behaviour question too — how it actually behaves on a task with no
instructions, its real defaults including the wrong ones — and KEEP anything
it confesses to violating: comments that narrate the change, done declared on
a green test run, a partial result worded as complete, a subagent's summary
trusted unchecked. ALWAYS ask it per candidate rule, NEVER once for the whole
sweep: one confession list answers the rules it happens to name and says
nothing about the rest, and treating it as global licence cuts rules no
evidence ever covered.

**A self-report NEVER proves compliance.** A rule the clean room recites and
does not confess can still break in every session — it recites the `is_`/`has_`
prefix and "clarity over cleverness", and sessions break both. ALWAYS CUT only
on behavioural evidence: a search of real transcripts or diffs showing the
default followed, or the owner's report. ALWAYS KEEP a drift the owner
observes, whatever the clean room says, and stress it where code is checked —
a lint, a `refine` hunt — rather than cut it.

Empirically, almost nothing survives. Across error handling, testing and
comments, every freely reproduced rule was one the models confess to breaking:
swallowing an error whose recovery is unclear, degrading where crashing is
correct, a second logging path, over-mocking, a comment above every block.
EXPECT a nearly empty cut list; a long one means the evidence step was skipped.

When the criterion changes mid-sweep — and it will, because each pass exposes
how the last one was fooled — ALWAYS re-examine every cut already made under
the old criterion, including the ones that still look right. Correcting only
the convenient ones leaves the rest standing on reasoning you have abandoned.

A check that has never failed has not been tested. ALWAYS run a probe you
expect to FAIL before trusting one that passes — a clean room that cannot leak,
a linter that cannot flag, and a broken one look identical from a green run.

## Router skills

What a router is, when to make one, its dispatch table, file layout and the `SKILL.md` naming trap: `skills/CLAUDE.md` § Flat skills vs router skills, § Router anatomy, § Router invariants and § Editing a router.

## Installed copy vs source

`~/.claude/` is an install of the bundle source repo (path in `LOCAL.md`): ALWAYS sync an edit there back to source (WISDOM § Environment).

## CLAUDE.md (project)

- Project-specific only — skills carry general knowledge; where each CLAUDE.md
  sits (root, one per package) is `readme` → `topology.md`.
- NEVER repeat what README/ARCHITECTURE/docs say — architecture, state machines
  and external systems are ARCHITECTURE.md's. ALWAYS cut re-explanation to a
  one-line pointer; keep only the invariants, gotchas and syntax an editor must
  not get wrong.
- ALWAYS group related rules under clear Markdown headings and bullets.

### Tags describe content; the harness controls loading

- ALWAYS treat `<important if="condition">…</important>` as a local prompt
  convention. The sources below do not document special priority, a parsed
  `if` condition, or an override of a system reminder for this wrapper.
- When XML helps separate content, ALWAYS choose consistent, descriptive
  names: `<instructions>`, `<context>`, `<input>`, or `<examples>` containing
  `<example>` blocks. Custom names such as `<testing_rules>` can replace or
  complement `<important>` as semantic labels. They are not priority levels.
- ALWAYS nest tags only to express a natural content hierarchy. NEVER infer
  stronger authority from a tag name or nesting; ALWAYS state the rule itself.
- For task-dependent guidance, ALWAYS state the condition in ordinary text:
  "When editing tests, ...". This works inside a tag or under a Markdown
  heading. An `if` attribute is a model-facing cue, not a documented loader.
- ALWAYS keep one narrow trigger per task-specific block as a local convention.
  NEVER combine unrelated triggers; ALWAYS split testing and API rules when
  their conditions differ.
- ALWAYS leave project identity, directory maps, the stack, and common commands
  unconditional. ALWAYS keep global wisdom free of project task wrappers as a
  local convention, not because global context has special XML semantics.
- For glob-based conditional loading in Claude Code, ALWAYS use the documented
  `.claude/rules/*.md` YAML `paths` mechanism. Matching file access loads those
  rules; rules without `paths` load unconditionally. Nested `CLAUDE.md` files
  also load on demand when Claude reads, writes, or edits files in their subtree.
- ALWAYS distinguish loading from enforcement. Loaded instructions guide the
  model; client settings or hooks enforce supported restrictions. NEVER present
  XML as enforcement or context filtering; ALWAYS verify loading separately.
  ALWAYS test claimed adherence or performance benefits on the target tasks.

Sources: [Anthropic prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags)
and [Academy XML lesson](https://academy.claude.com/courses/claude-with-amazon-bedrock/structure-with-xml-tags)
support descriptive delimiters. [Claude Code memory](https://code.claude.com/docs/en/memory)
documents Markdown organization, file loading, and enforcement limits.
