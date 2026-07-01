---
name: bugs
description: >
  The `bugs.md` open-issues queue — entry format, lifecycle, pruning to diary.
  NOT for the record-don't-fix policy (that's CLAUDE.md Bug Triage Protocol), NOT
  for resolved-bug history (use /diary), NOT for feature backlog (use TODO.md/specs).
when_to_use: "log this bug, open issues, what's broken, what's the queue, prune bugs.md, audit-record-only, debugging-but-not-fixing-now"
---

# Bugs

`bugs.md` at the project root is the **open-issues queue**. Complementary to
`.diary/` (the resolution log) and `TODO.md` (forward-looking backlog:
features, refactors).

**Policy is in CLAUDE.md "Bug Triage Protocol"** — record during audits, never
fix on discovery, let the user prioritise. This skill is the file mechanics
only; do not restate the policy.

## When NOT to record

- NEVER record when user is currently driving a fix — just fix
- NEVER record trivial / one-shot issues a code comment covers
- NEVER record feature requests — those go in `TODO.md` or a new spec
- NEVER duplicate — when an open entry covers the same root cause, append
  context to it instead

## Bug ID format

IDs use a short prefix + number, e.g. `D5`, `P2`. All characters must be
**base58-safe**: no `0` (zero), `O` (capital O), `I` (capital I), or `l`
(lowercase L). These are excluded from base58 because they are visually
ambiguous with each other and with digits.

## Entry format

H2 heading per entry. Date in parens; status appended once resolved.

```markdown
## <ID> — <one-line title> (<YYYY-MM-DD>[, open | partial | fixed])

<paragraph: what's broken, observed impact, suspected root cause>

- **Severity:** high | medium | low
- **Scope:** <subsystem / area>
- **Affected:** <component(s) or instance(s)>
- **Source:** <file:line OR log timestamp>
- **Status:** open | in-progress | resolved-not-yet-removed
- **Fix:** <commit SHA if fixed, else blank>
```

## Lifecycle

1. **Record** — add an entry when a bug surfaces and a fix isn't authorized.
2. **Mark in place** — when the fix ships, prepend `✅ FIXED <date>` to the
   title and fill the **Fix** line with the commit SHA. Keep the entry.
3. **Prune to diary** — periodically (per release, per refine pass) sweep
   ✅-marked entries: for each, write a one-line `.diary/YYYYMMDD.md` note
   citing the bug title + commit SHA (see `/diary`), then delete from
   `bugs.md`.

Remove an entry only after all three hold: fixed-in-code (or closed
won't-fix), referenced in the diary, and deployed to affected targets (or
marked not-deployed). Invoke with `prune` to sweep ✅-marked entries.

## Aggregation (optional)

If a project accumulates issue reports in multiple scratch files, consolidate
into root `bugs.md` periodically (per release, or on request via `aggregate`):

1. Enumerate post-date entries across the scratch files (read-only).
2. Synthesize into one root section grouped by cross-cutting pattern,
   debounced against prior aggregations.
3. Note in each scratch file: "Consolidated to root `bugs.md` <date>".

Scratch files stay as-is; the owner wipes them after merge.

