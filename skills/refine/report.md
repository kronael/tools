# Change summary — the report that closes the run

ALWAYS end with a system-effect analysis and a verification checklist, NEVER a
list of edits:

- Direct dependencies — what imports or calls the changed code.
- Runtime behaviour — performance, error handling, side effects.
- Configuration — new env vars, changed defaults, breaking changes.
- Verified unaffected — the modules or services checked, and how.
- Tests pass, build succeeds, linter clean — each run in this turn.
- Assumptions or edge cases that still need attention.

Shape: "Decorator change affects 4 services. Consumer worker retry logic
separate (verified: uses different config path). All tests pass unmodified."
