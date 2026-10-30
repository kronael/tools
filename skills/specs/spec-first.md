# Spec-first changes

A spec in flight (`planned`, `partial`) governs the code it names. A shipped
spec governs nothing; the docs hold the state.

- ALWAYS check `specs/index.md` for an in-flight spec on the topic BEFORE
  editing code.
- ALWAYS treat a code↔spec disagreement as the bug — fix both in one pass,
  NEVER just the code.
- ALWAYS write the minimal spec first, shaped by `format.md`, when a change
  adds a structure no spec covers; the code without it is incomplete.
- NEVER contradict a neighbouring in-flight spec — ALWAYS read them first.
