---
name: specs
description: Router for the spec workflow — the case against building, the spec file and its body as the architecture document of the system after the change, spec-first code changes. NOT for execution tracking (use ship) or README/ARCHITECTURE prose (use readme).
when_to_use: "speclint, spec lint, retire implemented specs; write a spec, review a spec, spec body, spec diagrams, figure of the change, new changed removed, code excerpt in a spec, open questions, design doc, RFC, ADR, proposal, SPEC.md, specs/ directory, spec numbering, spec status frontmatter, spec before coding, code contradicts the spec; is this worth building, prior art check, talk me out of it, kill this idea, teardown"
user-invocable: true
---

# Specs — spec workflow router

Only this file preloads. ALWAYS read the ONE matched file below. Paths are
relative to this directory.

| If you need | Read |
|---|---|
| the case AGAINST building it at all — prior-art sweep, residue after subtracting it, cost vs payoff, one `don't build` / `build if` verdict in the record dir's `critique-useless-*.md` | `useless.md` |
| to draft, review, lint or retire a spec — status, numbering, index; the body as the architecture document after the change: the sections in order, figures marked `(new)`, `(changed)`, `(removed)`, when a table earns its place, the current and proposed code excerpts, open questions with the case and a recommendation, the `readme`, `writing` and `diagrams` rules it follows; one-way links, retirement and speclint | `format.md` |
| to implement or change code a spec governs — find the governing spec, reconcile code↔spec drift, spec an unspecced design in the same pass | `spec-first.md` |

Order of the workflow: `useless.md` gates whether a spec is worth writing,
`format.md` writes it, `spec-first.md` keeps the code answering to it.
ALWAYS pass the gate before writing a spec for anything not already approved.
