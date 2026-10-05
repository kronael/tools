---
name: readme
description: Update readme, docs, documentation, architecture files.
when_to_use: update readme, update docs, update architecture, sync documentation, README outdated, ARCHITECTURE.md needs updating, new project docs, docs out of date
tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch
---

# Document Agent

ALWAYS load the `writing` skill before drafting or editing documentation.
ALWAYS read `~/.claude/skills/readme/topology.md` before editing any file — it
is the house layout: which file answers which question, what each one holds,
the numbers ledger and what `make lint` checks. NEVER edit a fact into a file
whose question it does not answer.

## Protocol

### 1. Read current state

Every file `topology.md` lists that exists here, `CHANGELOG.md` where the repo
keeps one, and the project structure (ls/tree).

### 2. Move explanation out of CLAUDE.md

Explanation in a CLAUDE.md moves to the file whose question it answers.
CLAUDE.md keeps what `wisdom` § CLAUDE.md (project) allows — NEVER remove a
project-specific invariant or gotcha from it.

### 3. Update each file as `topology.md` lays it out

For ASCII component/flow diagrams, follow the `diagrams` skill: draw with Unicode box-drawing chars and pipe through `udfix` to correct junctions. NEVER hand-draw junction chars (┬ ┴ ├ ┤ ┼) — let `udfix` fix them.

### 4. Verify claims against code

NEVER trust existing doc text — ALWAYS grep every referenced function/variable/constant/test name/path to confirm it exists and behaves as described, and check every result a doc cites against the newest run. ALWAYS fix doc to match code, NEVER the reverse. A number changes only by re-running its ledger command, then `make lint`.

## Rules

- NEVER call a spec (`specs/`, `SPEC.md`) "documentation" — it is a specification
- NEVER duplicate content across files — ALWAYS link instead
