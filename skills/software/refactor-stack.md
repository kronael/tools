# Refactor stack

Re-ship an unreviewable branch as dated feature branches that each stand
alone. The project's own doc holds its commands; this file is the rules and
why each exists.

## Order

- ALWAYS land every test improvement before any refactor. A test that ships
  after the code it measures records a result; it cannot prove the change safe.
- ALWAYS order production layers deletions → moves → defaults → behaviour
  changes. A behaviour change ships alone on its own evidence — NEVER inside
  a refactor.
- NEVER let a branch lean on a later one. Each is green on the branch below it.

## The dividing criterion

- A change is a test improvement iff it passes on the merge base with no
  production edit. ALWAYS check it — cherry-pick onto the base and run — NEVER
  judge it.
- ALWAYS expect to re-implement. Tests written against refactored signatures
  do not apply to the base; rewrite them there from the shipped test as a
  template, and re-record fixtures from the base.

## Proof per test

- NEVER claim a test improved without its mutation: the production change that
  should fail it, quoted failing on the branch and surviving on the base. A
  test that survives a mutation of the thing it names is not testing it.
- NEVER count an added assertion as a gain until the old one is re-checked.
  Two assertions can be jointly met by something neither names — a filtered
  count of 4 plus "all four agree" is met by the unfiltered length, and the
  filter is unfalsifiable.
- Shapes that pass on nothing: `<=` met by equality; a pure function compared
  with a second call of itself; `all()` or a `for` over an empty list; an
  input derived from the constant under test; a fixture whose cases cannot be
  told apart; a scenario that exits at a gate before the one named; a test
  double missing the field the production path reads.

## Four passes

Port, harden, adversarial review, close. The reviewer is a reader who did not
write the branch — a different model or person — and attacks every test the
branch added or strengthened. The fourth pass is the one that matters: a suite
built to be provable was still a third short until someone attacked it.

## Deleting

- NEVER delete on one oracle. A thing is dead when the unit suite, the
  configuration and deployed artifacts, and every generator that emits config
  — what it `setdefault`s, not only what it declares — all say no.
- ALWAYS measure a dynamic-attribute fallback instead of reading it: wrap
  `getattr`/`hasattr` to log each fallback with the owning test, run the
  suite. A fallback taken only under a test double is held up by the double;
  one taken under a real object is live. Neither is dead.
- ALWAYS append a cut record before the commit — name, readers, files and
  lines, commit — so the cut reverts from the record alone.

## Moving

- ALWAYS lint the destination module before committing a move. A name the old
  module's namespace supplied — an import used only on a rare branch —
  vanishes silently: the type checker follows the imports it can see, the
  suite covers the branches it runs, only the linter reads every line.
- NEVER consolidate two helpers on the claim they are identical — ALWAYS diff
  them normalised for comments, docstrings and formatting. An empty diff is a
  move; anything else is a behaviour change.
- NEVER consolidate across packages without checking for an import edge. A
  package that imports nothing from the other is a boundary, and its own copy
  of a helper is the boundary's cost.
- NEVER let a move change a value at any site. Rewriting inline spellings into
  the helper, or dropping a parameter nothing reads from N signatures, is a
  behaviour or signature change — record it, leave it.
- NEVER commit formatter churn inside a refactor — ALWAYS format through the
  project's pinned hook, and revert files the refactor did not touch.
- NEVER give a worktree two writers — ALWAYS commit after every edit, so a
  stray revert or a commit from a dirty tree costs one edit, not the branch.

## Defaults

- A default is defined once, in the type. `getattr(x, 'name', literal)` on a
  declared field is a second definition; on a mandatory field the literal is
  the only one. A hand-written table of a type's field names is the same
  defect one level up — derive it from the type.
- NEVER treat it as a deletion or a move. The fallback has a reader, so no
  consumer oracle applies; the direct read is not byte-neutral. It must be
  value-neutral: nothing reaching the seam lacks the name, and the type's
  default equals the literal.
- ALWAYS measure both halves. A parameter typed `Any` hides what arrives:
  enumerate every class that reaches the seam and compare their fields and
  defaults against each other and against each literal — a disagreement is a
  behaviour change. Then arm: replace each fallback with a probe that raises
  when the name is absent, run every suite that drives the seam, count zero.
  A literal cannot be armed in place — the default argument is evaluated
  first — hence the probe.
- ALWAYS arm the whole seam in one run. A run costs the same for one arm or
  all, and one population of objects reaches them, so the set is one number;
  per-site arming is the same evidence at N times the cost, and per-site
  reading is blind to the second class.
- NEVER accept a blocker a spec records without re-measuring it. It is dated
  to its writing.
- NEVER fold a table on shared field names. Ask what question it answers; a
  seed table for a search is not a default table.
- NEVER delete an indirection before asking what it delays. A forwarder that
  only calls a function defined further down exists because `default_factory`
  resolves at class creation; without it the module is a `NameError` at import.
- A seam is finished when no read carries a literal, every name table is
  derived, and the armed run counts zero on every suite. Each remaining
  fallback is its own seam.

## Gates

- Each branch moves no golden. A moved pinned hash means the change leaves the
  branch — NEVER re-pin on a refactor branch.
- ALWAYS record counts, never "green": passed and deselected before and after,
  per branch, and the arithmetic reconciles.
- ALWAYS prove a gate can fail before trusting its pass; empty input is the
  usual way a gate passes on nothing.
- ALWAYS run the gates before each commit, not each branch. The one defect
  that reached a stack tree was named by both the linter and the type
  checker; it landed from a commit made without them.

## Reporting

- NEVER quote the total diffstat. Split `git diff --numstat` by kind —
  fixtures, docs, tests, config, production — and say what each bucket is. A
  net deletion under a hundred thousand lines of recorded fixtures reads as a
  rewrite when only the total is shown.
