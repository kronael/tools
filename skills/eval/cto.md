# CTO Eval

Dispatch:

- Technical adoption / due diligence: read `cto/checklist.md`.
- SLA-bet / source audit: read `cto/code-audit.md`.

Rules:

- ALWAYS run build + test first for adoption evaluations.
- ALWAYS produce a verdict using the selected mode's template.
- ALWAYS anchor "production-ready" to an explicit target: what load, what
  availability objective, what failure budget (SRE production-readiness-review
  discipline). An unanchored readiness claim is an opinion.
- NEVER skip maintenance burden. Impressive code with one maintainer is still
  a liability.
- NEVER open a browser or run the UI for the code lens — read source, specs,
  tests, commit history. If judging correctness *requires* the running system,
  that gap IS a finding ("the code isn't auditable from source alone").
- If the evidence is unclear because the system may break under hostile input,
  corrupted state, replay, concurrency, or exploit-like conditions, run the
  red lens (`red.md`) as a separate deeper pass instead of stretching CTO
  scope.
- A "DISPUTED" or "CONFIRMED" verdict in this lens's own report is the sub's
  self-check; it does not exempt the caller from re-deriving a claim whose
  direction matters (e.g. which side of a ratio is baseline).
