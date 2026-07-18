---
name: readme
description: Update readme, docs, documentation, architecture files.
when_to_use: update readme, update docs, update architecture, sync documentation, README outdated, ARCHITECTURE.md needs updating, new project docs, docs out of date
tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch
---

# Document Agent

## Protocol

### 1. Read current state

README.md, ARCHITECTURE.md, CLAUDE.md, CHANGELOG.md, project structure (ls/tree).

### 2. Extract from CLAUDE.md

- **README**: installation, usage, examples, getting started
- **ARCHITECTURE**: system design, component relationships, data flows, state machines

Keep in CLAUDE.md only: shocking/counter-intuitive patterns, production gotchas unique to the project.

### 3. Update README.md

Sections: title + problem statement (one sell sentence max), Installation, Usage (copy-paste examples), Running, Configuration (required only). End with pointers to SPEC.md / ARCHITECTURE.md.

NEVER sell past the opening sentence. Keep under 150 lines. Technical details (validation, retry logic, integration patterns) → ARCHITECTURE.md.

### 4. Update/Create ARCHITECTURE.md

Sections: Overview, Components, Data Flow, State Management, External Systems. Keep under 300 lines. Focus on relationships and flows, not implementation.

For ASCII component/flow diagrams, follow the `diagrams` skill: draw with Unicode box-drawing chars and pipe through `udfix` to correct junctions. NEVER hand-draw junction chars (┬ ┴ ├ ┤ ┼) — let `udfix` fix them.

### 5. Verify claims against code

NEVER trust existing doc text — ALWAYS grep every referenced function/variable/constant to confirm it exists and behaves as described. ALWAYS fix doc to match code, NEVER the reverse.

### 6. Route content

| Content | Where |
|---------|-------|
| Installation, usage, examples | README |
| Component design, data flows | ARCHITECTURE |
| Deployment, CI, container/k8s config | ops/infra repo |
| Language-specific patterns | skills (rs, py, sql) |
| Project gotchas, ALWAYS/NEVER rules | CLAUDE.md |

CLAUDE.md target: <200 lines.

## Rules

- NEVER remove non-obvious wisdom from CLAUDE.md — ALWAYS keep project-specific gotchas there
- NEVER duplicate content across files — ALWAYS reference instead
- NEVER use marketing language ("powerful", "flexible", "robust", "easy", "simple") — one sell sentence in README intro only
- NEVER call SPEC.md "documentation" — it's a specification
- NEVER document how the service is deployed in its README — container base image, Dockerfile, CI, k8s manifests, deploy steps — ALWAYS keep the README to how to RUN it (install, usage, running, config) and route deploy details to the ops/infra repo
- ALWAYS keep README under 150 lines, ARCHITECTURE under 300, CLAUDE.md under 200
- ALWAYS use concrete copy-paste examples in README
- ALWAYS fix doc to match code, NEVER the reverse
