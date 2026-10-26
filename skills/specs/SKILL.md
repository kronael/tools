---
name: specs
description: Router for the spec workflow — the case against building, spec file conventions, spec-first code changes. NOT for execution tracking (use ship) or README/ARCHITECTURE prose (use readme).
when_to_use: "speclint, spec lint, retire implemented specs; write a spec, design doc, RFC, ADR, proposal, SPEC.md, specs/ directory, spec numbering, spec status frontmatter, spec before coding, code contradicts the spec; is this worth building, prior art check, talk me out of it, kill this idea, teardown"
user-invocable: true
---

# Specs — spec workflow router

Only this file preloads. ALWAYS read the ONE matched file below — plus
`format.md` whenever the work creates or edits a spec file, since that is
where its shape is defined. Paths are relative to this directory.

| If you need | Read |
|---|---|
| the case AGAINST building it at all — prior-art sweep, residue after subtracting it, cost vs payoff, one `don't build` / `build if` verdict in the record dir's `critique-useless-*.md` | `useless.md` |
| to create, lint, implement or retire a spec — status, numbering, index, body, one-way links, tests and review | `format.md` |
| to change code a spec governs — find the governing spec, reconcile code↔spec drift, spec an unspecced design in the same pass | `spec-first.md` |

Order of the workflow: `useless.md` gates whether a spec is worth writing,
`format.md` writes it, `spec-first.md` keeps the code answering to it.
ALWAYS pass the gate before writing a spec for anything not already approved.
