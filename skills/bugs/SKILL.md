---
name: bugs
description: >
  The `BUGS.md` review queue — entry format, dated grouping, inline resolution,
  pruning. NOT for the record-don't-fix policy (that's CLAUDE.md Bug Triage
  Protocol), NOT for resolved-bug history (that lives in git + CHANGELOG), NOT
  for feature backlog (use TODO.md/specs).
when_to_use: "log this bug, open issues, what's broken, what's the queue, prune BUGS.md, audit-record-only, debugging-but-not-fixing-now"
---

# Bugs

`BUGS.md` at the project root is the **review queue: OPEN and DEFERRED items
only.** Resolved bugs live in git (commit refs) and `CHANGELOG.md` — not here.
Complementary to `TODO.md` (forward-looking backlog: features, refactors).

(Filename is uppercase `BUGS.md`. Some projects may use lowercase `bugs.md` —
match whatever the project already has.)

**Policy is in CLAUDE.md "Bug Triage Protocol"** — record during audits, never
fix on discovery, let the user prioritise. This skill is the file mechanics
only; do not restate the policy.

## When NOT to record

- NEVER record when the user is currently driving a fix — just fix
- NEVER record trivial / one-shot issues a code comment covers
- NEVER record feature requests — those go in `TODO.md` or a new spec
- NEVER duplicate — when an open entry covers the same root cause, append
  context to it instead

## Structure

The file opens with the one-line purpose, then groups entries under **dated
status headers** — one block per audit / review / session:

```markdown
## Status — <YYYY-MM-DD> — <short title of the audit or finding>
```

Each block collects that one review's findings together. A short lead line
under the header can note provenance ("Record-only per triage; full evidence
in <report>. Do NOT fix without founder go.").

## Entry format

One **bullet** per bug: bold UPPERCASE-KEBAB id, a `(SEVERITY, type)` tag, an
em-dash, then the body.

```markdown
- **COMPONENT-SHORT-NAME** (SEVERITY, type) — <what's broken>, at `file:line`;
  <why / failure mode>. **Fix:** <sketch>.
```

- **ID** — `COMPONENT-DESCRIPTIVE-NAME`, UPPERCASE-KEBAB, component-prefixed
  and self-describing (`ME-SNAPSHOT-NO-INDEX-DEDUP-REBUILD`,
  `GW-OUTBOUND-UNBOUNDED`, `DOC-RT-FLOOR-DRIFT`), not a short opaque code.
- **SEVERITY** — `CRITICAL | HIGH | MED | LOW` (or `MED-HIGH`). A non-defect
  carries a marker instead: `(roadmap, not a defect)`, `(design — not a
  correctness bug)`.
- **type** — one word for the class: `latency`, `correctness`, `docs`,
  `design`, `duplication`, `perf`, `ops`, `config`, `bench`, `resource/DoS`,
  `hardening`, `traceability`.
- **body** — concrete `file:line` cites, the failure/why, and often a
  **Fix:** sketch. Multi-line prose is fine for a hard one.

## Resolution & pruning

Status is inline on the entry — appended after the tag or bolded at the top:

- `— CONFIRMED` — verified real, still open.
- `— FIXED <date> (<commitref>)` / `**Status: FIXED <date>.**` — fixed.
- `— Record-only per triage` — logged, not to be actioned yet.

When a whole dated block is fixed, a one-line `**RESOLVED <date> — all N
FIXED.**` cap with commit refs can precede its removal.

**Prune resolved entries out.** FIXED bugs live in git + CHANGELOG, not here —
once an entry is fixed and committed, delete it. DEFERRED and BY-DESIGN entries
stay as a standing record (with their marker). Invoke with `prune` to sweep
FIXED entries.
