---
name: bugs
description: >
  The `BUGS.md` open-issues queue — the record-don't-fix policy, its two
  sections (open defects, and what was ruled not a defect), entry format,
  pruning. NOT for resolved-bug history (that lives in git and /diary), NOT
  for feature backlog (use TODO.md/specs).
when_to_use: "log this bug, open issues, what's broken, what's the queue, prune BUGS.md, audit-record-only, debugging-but-not-fixing-now"
---

# Bugs

`BUGS.md` at the project root holds exactly two things:

1. **Defects that are still true of the code.**
2. **Things that were reported as defects and are not** — so the next audit
   does not re-report them.

Nothing else. It is NOT a log of audits, reviews, sessions or sweeps: no
"Status — <date> — <what I checked>" blocks, no lead paragraphs describing a
review pass, no counts of what was verified. That narrative belongs in
`.diary/`. A reader opens `BUGS.md` to learn what is broken, not what someone
did.

(Filename is uppercase `BUGS.md`. Some projects use lowercase — match what the
project already has.)

## Record, don't fix

- When debugging or auditing a system, RECORD bugs in `BUGS.md` at project root
- NEVER fix bugs immediately just because you found them during a general check
- Only fix when the user explicitly asks for a fix (e.g. "fix it", "fix the vhosts")
- `BUGS.md` is the review queue — log it, move on, let the user prioritise

## When NOT to record

- NEVER record when the user is currently driving a fix — just fix
- NEVER record trivial / one-shot issues a code comment covers
- NEVER record feature requests — those go in `TODO.md` or a new spec
- NEVER duplicate — when an open entry covers the same root cause, append
  context to it instead
- NEVER record what you did. An entry describes the defect, not the pass that
  found it. Provenance is at most one clause inside the entry (`CONFIRMED at
  HEAD <date>`), never a section.

## Structure

Group by **subject** — the component or surface the defects live in — not by
when they were found:

```markdown
## Code bugs (in source/SQL, not the tests)
## Coverage gaps (edge cases / untested branches)
## <component or subsystem>
```

An existing section that fits takes the entry; only add a section when no
current one covers the subject. A defect dated in its own entry is enough —
the file needs no dated scaffolding around it.

## Entry format

One **bullet** per bug: bold UPPERCASE-KEBAB id, a `(SEVERITY, type)` tag, an
em-dash, then the body.

```markdown
- **COMPONENT-SHORT-NAME** (SEVERITY, type) — <what's broken>, at `file:line`;
  <why / failure mode>. **Fix:** <sketch>.
```

- **ID** — `COMPONENT-DESCRIPTIVE-NAME`, UPPERCASE-KEBAB, component-prefixed
  and self-describing (`ME-SNAPSHOT-NO-INDEX-DEDUP-REBUILD`,
  `GW-OUTBOUND-UNBOUNDED`), not a short opaque code.
- **SEVERITY** — `CRITICAL | HIGH | MED | LOW` (or `MED-HIGH`).
- **type** — one word for the class: `latency`, `correctness`, `docs`,
  `design`, `duplication`, `perf`, `ops`, `config`, `resource/DoS`,
  `hardening`, `traceability`.
- **body** — concrete `file:line` cites, the failure/why, and often a
  **Fix:** sketch. Multi-line prose is fine for a hard one.
- **status** — inline, as a clause: `CONFIRMED at HEAD <date>`,
  `open (record only)`, `deferred — <why>`, `needs sign-off`. A fix that
  changes behaviour says so, with what was measured.
- A redesign proposal (new contract, changed control flow, cross-cutting)
  is an entry with `needs sign-off` and the options sketched; the user
  signs off on the approach BEFORE it is built.

## Not-a-defect section

A permanent section — the project may already name it `## Design invariants —
intentional, do not re-report` — holds one compressed line per ruling:
what was reported, and why it is correct behaviour. These are NEVER deleted;
they exist to stop the same finding coming back. A refuted finding (premise
was false) goes here too, with the evidence that refuted it.

## Pruning

A fixed defect leaves the file. Its history is the commit that fixed it, so
delete the entry once the fix is committed — do not mark it fixed and keep it.
Deferred entries stay as-is. Not-a-defect lines stay forever.

Invoke with `prune` to sweep entries whose defect no longer holds. ALWAYS
re-verify against the current code before deleting — an entry's own status
line is a claim, not evidence.

## Aggregation (optional)

If a project accumulates issue reports in multiple scratch files, consolidate
into root `BUGS.md` on request (`aggregate`): enumerate the scratch entries
read-only, fold them into the subject sections above, and note in each scratch
file "Consolidated to root `BUGS.md` <date>". The owner wipes the scratch
files after the merge.
