# Syncing docs to the code

Bring README, ARCHITECTURE and CLAUDE.md back in line with what the code does.
Doc prose follows the `writing` skill. Which file owns a fact is `topology.md`
in this directory — ALWAYS check it before editing; a fact edited into the
wrong file is doc rot even when the fact is right.

## Where it runs

A pass over a whole doc set runs in a subagent — `Agent(subagent_type:
readme)`, the thin agent that loads the `readme` skill, prompt opening with
"read its `sync.md`", then one line per changed behaviour. A one-fact fix
runs inline. A subagent that loaded this skill runs the pass itself.

## Protocol

1. **Read the current state** — README.md, ARCHITECTURE.md, CLAUDE.md,
   CHANGELOG.md where kept, and the tree (`ls`/`tree`).
2. **Move content out of CLAUDE.md** — installation, usage, examples and
   getting started belong in README; system design, component relationships,
   data flows and state machines in ARCHITECTURE. CLAUDE.md keeps only the
   shocking, counter-intuitive patterns and production gotchas unique to the
   project; NEVER remove those.
3. **README** — ALWAYS open with what → why → how, in that order, before
   anything else appears on the page:
   1. What it is — one sentence a 13-year-old understands; no jargon,
      acronyms or domain terms. A reader who stops here still knows what the
      thing is. Directly under it, whenever anything is unaudited,
      unreleased, unpublished or not yet run on the real network, ONE status
      line says so ("Not audited. Use it at your own risk."). ALWAYS word it
      the same on the README, the docs landing page and the first guide page,
      and change the three together; NEVER leave the status to a Limitations
      section the reader who stops at the pitch never reaches.
   2. Why use it — the gap it fills: what someone does instead today and what
      that costs them. Concrete, not adjectival. Then what adopting costs,
      in fees, storage, compute and overhead per run, as a formula in the
      project's units plus one worked figure a test or bench measured
      ("(header + payload bytes) × rent per byte; the getting-started example
      locks 2,153,920 lamports"). NEVER "cheap" or "low overhead" without
      both.
   3. How to start — a runnable copy-paste block that produces visible output.
   Every domain term that survives into the body gets a plain-English
   definition at first use. Then Installation, Usage (copy-paste examples),
   Running, Configuration (required only), and a closing **"How to read
   this"** section naming which file answers which question — or, when a
   docs site exists, the hub shape in `topology.md` § README as a docs-site
   hub. Technical detail
   — validation, retry logic, integration patterns — goes to ARCHITECTURE.
   NEVER document how the service is deployed — base image, Dockerfile, CI,
   k8s manifests, deploy steps; the README says how to RUN it, deploy detail
   goes to the ops/infra repo.
4. **ARCHITECTURE** — the audience is a senior engineer who has to change this
   code: depth, not breadth. NEVER re-explain what the project is; that is the
   README's job. Sections: Overview, Components (table, one-line purpose per
   file), Data Flow, State Management, External Systems, Invariants,
   Architectural Decisions — ALWAYS name the alternative each decision rejected
   and why. Diagrams are mandatory, not decoration: at minimum a component
   diagram and a data-flow diagram for the primary write path and the primary
   read path. A structure that exists only as prose is undocumented; a sequence
   whose order matters is drawn in order. ASCII diagrams follow the `diagrams`
   skill — Unicode box-drawing piped through `udfix`; NEVER hand-draw junction
   chars (┬ ┴ ├ ┤ ┼).
5. **Verify claims against code** — NEVER trust existing doc text. ALWAYS grep
   every referenced function, variable, constant, test name and path to confirm
   it exists and behaves as described, and check every cited result against
   the newest run. ALWAYS fix the doc to match the code, NEVER the reverse.

## Rules

- ALWAYS keep README under 150 lines, ARCHITECTURE under 300, CLAUDE.md under
  200.
- NEVER duplicate content across files — ALWAYS reference the owning file.
- ALWAYS take a doc's code from a file a test or build compiles and runs — a
  region include (`<<< @/../examples/start.ts#connect` over a
  `// #region connect` block) or a block a script generates. NEVER hand-type a
  snippet into a doc set that has a build: it compiles once, when written, and
  drifts silently after. Without a build, ALWAYS cite beside the snippet the
  runnable example file it came from and the test that runs it.
- NEVER call SPEC.md "documentation" — it is a specification.
- NEVER mention how a feature was arrived at, internal plan names, goal
  codenames or project history — docs describe what the code does. ALWAYS
  write as if the reader has no prior context on the project's decisions.
- Language-specific patterns belong to the language skills (`rs`, `py`,
  `sql`), NEVER to a project's docs.
