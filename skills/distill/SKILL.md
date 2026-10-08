---
name: distill
description: /distill — Use when compressing a long document, transcript, or codebase into its essence. NOT for skill creation (use learn) or recall (use recall-memories).
when_to_use: "long article, codebase audit, multi-page spec, chat transcript, research dump; what is this in 5 words, give me the gist, boil this down"
user-invocable: true
---

# Distill — the 5/3 approach

Compression reveals truth: noise falls away, essence emerges. All state lives
in `.distill/` under the project root, so a run resumes from wherever it
stopped.

## Where it runs

A distillation reads a whole codebase or research set. Invoked in the main
thread, ALWAYS run it in a background `Agent(subagent_type: distill)`, the thin
agent that loads this skill, with the subject and scope; present `.distill/final.md` when it returns. A subagent
that loaded this skill runs the phases itself.

## Start here — read the state, pick the phase

| `.distill/` holds | Phase |
|---|---|
| nothing | 1 — decompose |
| `areas.md`, no `breadth/` | 2 — breadth research |
| `breadth/` populated, no `L1.md` | 3 — compress each area |
| `L1.md`, no `L2.md` | 4 — cross-compress |
| `L2.md`, no `final.md` | 5 — final output |
| `final.md` | present it |

## Phase 1 — decompose → `areas.md`

Read the codebase or topic. Identify 5 major areas of roughly equal weight and
decide per area whether it needs web research, codebase reading or both —
NEVER force one source on every area.

```markdown
# Areas
1. [Name] - [description] - [source: code|web|both]
```

## Phase 2 — breadth → `breadth/01-name.md` …

Per area, gather ~500 words of raw findings: read files and grep patterns for
`code`; WebSearch/WebFetch for context, state of the art and comparisons for
`web`; both for `both`. No compression yet. Run areas sequentially and save
after each.

## Phase 3 — compress each area → `L1.md`

Per area, three levels, each shorter than the last:

```markdown
## [Area Name]

### Detailed (~200 words)
[What it does, why it exists, key decisions]

### Summary (~50 words)
[One paragraph]

### Essence (3-5 words)
**[Core of this area]**
```

## Phase 4 — cross-compress → `L2.md`

From the five essences and summaries:

```markdown
# Cross-Area Analysis

## Patterns (~100 words)
[Trade-offs, architectural decisions, recurring themes]

## Summary (~30 words)
[One paragraph for the whole]

## Essence (3-5 words)
**[What this IS]**
```

## Phase 5 — final → `final.md`

```markdown
# Distillation: [Subject]

## Essence
**[3-5 words]**

## Summary
[One paragraph from L2]

## Patterns
[Cross-cutting from L2]

## By Area

### [Area 1]: [3-5 word essence]
[Summary from L1]
```

Present it. Done.

## Rules

- ALWAYS read the existing state before starting and save to `.distill/`
  after each phase.
- NEVER compress without reading the source first.
- NEVER repeat a phrase between compression levels; ALWAYS make each level
  shorter than the previous.
- ALWAYS make the essence quotable and true. No marketing language.
