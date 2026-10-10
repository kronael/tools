# Confessed defaults — hunt these first

Asked in isolation, models name these as their own defaults while being able to
recite the rule against each. Knowing a rule and following it differ; this is
where the gap shows.

- **Errors** — a broad catch that logs and continues; a fallback `None`/`[]`/`0`
  letting callers proceed on bad data; graceful degradation where crashing is
  cheaper than corrupted output; a guard on a path the caller already
  guarantees; a second logging or helper path because the first was never
  grepped for.
- **Scope** — adjacent code tidied unasked; the reported instance patched while
  sibling cases that fail the same way are left.
- **Tests** — mocks stacked until the test proves nothing; the assertion edited
  when a broken test is annoying; a guessed test command reported green.
- **Comments** — a comment above almost every block, half restating the code;
  docstrings added reflexively to a repo that has none; verbose names where the
  repo is terse.
- **Reporting** — done declared on a green run without exercising the path; a
  partial result softened into language that reads complete; a subagent's
  summary repeated without opening its diff.
