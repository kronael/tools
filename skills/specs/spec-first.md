# Spec-first changes

The spec is the source of truth; code conforms. Every non-trivial change starts here.

- ALWAYS find the governing spec BEFORE editing code — `specs/index.md`, or grep `specs/` for the topic.
- ALWAYS reconcile code↔spec: when they disagree, the divergence IS the bug — fix both in one pass, never just the code.
- When the design is unspecced, ALWAYS draft the MINIMAL spec edit in the same change; code that adds an unspecced structure is incomplete.
- ALWAYS read neighboring specs first; NEVER contradict them — keep cross-references and status consistent.
- NEVER drift a spec unless the drift makes the code more minimal/orthogonal/simpler.
- ALWAYS leave code more minimal, orthogonal, and simpler than before — "it works" is not "done".
