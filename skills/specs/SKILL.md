---
name: specs
description: Router for the spec workflow — the case against building, spec file conventions, and spec-first code changes. NOT for in-flight execution tracking (use ship) or README/ARCHITECTURE prose (use readme).
when_to_use: "write a spec, design doc, RFC, ADR, proposal, SPEC.md, specs/ directory, spec numbering, specs index, spec status frontmatter, spec before coding, spec-first change, code contradicts the spec; is this worth building, prior art check, already solved, talk me out of it, devil's advocate, over-engineered for its payoff, kill this idea, teardown"
user-invocable: true
---

# Specs — spec workflow router

Only this file preloads. ALWAYS read the ONE matched file below — plus
`format.md` whenever the work creates or edits a spec file, since that is
where its shape is defined. Paths are relative to this directory.

| If you need | Read |
|---|---|
| the case AGAINST building it at all — prior-art sweep, residue after subtracting it, cost vs payoff, one `don't build` / `build if` verdict in `.claude/plans/critique-useless-*.md` | `useless.md` |
| to create or update a spec file — `status:` lifecycle values, `NN-topic.md` numbering, `index.md` row, what belongs in the body and what never does, the post-ship trim | `format.md` |
| to change code a spec governs — find the governing spec, reconcile code↔spec drift, spec an unspecced design in the same pass | `spec-first.md` |

Order of the workflow: `useless.md` gates whether a spec is worth writing,
`format.md` writes it, `spec-first.md` keeps the code answering to it.
ALWAYS pass the gate before writing a spec for anything not already approved.
