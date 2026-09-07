# Refactor stack

Re-ship an unreviewable branch as dated feature branches that each stand
alone. The project's own doc holds its commands; this file is the rules and
why each exists.

## Order

- ALWAYS land every test improvement before any refactor. A test that ships
  after the code it measures records a result; it cannot prove the change safe.
- ALWAYS order production layers deletions → moves → defaults → injection →
  bundling → collapsing → behaviour changes. A behaviour change ships alone
  on its own evidence — NEVER inside a refactor.
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
- ALWAYS measure the survivor's arms after a consolidation: arm each alone
  and count the tests it fails. An arm no test fails is a branch no test
  runs; an arm that fails tests only by raising is one a silent drop passes.
- NEVER assert a method became a function — prove it. Apply the renames to
  the parent's body as an AST transform — `self.x` to the parameter that
  carries it, `self.helper(a)` to `helper(pre…, a)` — and compare with the
  new body's AST: identical, or it is a behaviour change. A rename is
  legitimate only when both names denote the same runtime object, and a
  prepended argument is a bare name, so the original arguments keep their
  evaluation order. Drop one rename and watch the proof fail before trusting it.
- For a file no suite reaches — a line trace says which — that proof is the
  whole evidence; a green gate and an unmoved golden say nothing there.
- NEVER trust the linter on where an import points. A name imported from a
  module that lacks it lints clean — imported and used is all it checks —
  and fails only the type checker. Run both on the destination, and grep
  each name the destination defines: a move can carry in a copy of a type
  that lives elsewhere.
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
- ALWAYS derive the whole rule or none of it. A table over a type's field
  names is usually several — which keys are allowed, and what each key's value
  must be. Deriving the first alone deletes the error that forced the second to
  be kept in step, so a new field is accepted and falls through to the loosest
  check. Derive from `f.type` too, and raise on a declared type no rule covers.
- NEVER fold a table on shared field names. Ask what question it answers; a
  seed table for a search is not a default table.
- NEVER delete an indirection before asking what it delays. A forwarder that
  only calls a function defined further down exists because `default_factory`
  resolves at class creation; without it the module is a `NameError` at import.
- A seam is finished when no read carries a literal, every name table is
  derived, and the armed run counts zero on every suite. Each remaining
  fallback is its own seam.

## Injecting

- A component reads nothing from disk or the environment below its entry
  point. The caller that builds it reads and hands in, and every
  construction site — production, harness, test — reads at its own entry
  point.
- NEVER treat it as a deletion, a move or a default. Every read keeps its
  reader and its value, so no consumer oracle applies; the signature changes
  at every site, so nothing is byte-neutral. It is read-neutral — the same
  reads, in the same order, from the frame above — and each half is proved
  on its own.
- ALWAYS prove the component's half with a guard: build it and run one cycle
  under a fixture that fails on every file and environment call, then run
  the loader under the same fixture and expect the raise. A guard nothing
  trips is green on nothing.
- ALWAYS arm the guard hole by hole. It is a list of names, and a name it
  lacks is a hole a read passes through as proof of absence. Plant each call
  in the guarded code and see it trip; a call that runs green is a hole.
  List the holes left open, each with why, and name the tripping call from
  the run, not from reading.
- NEVER raise an `Exception` from a guard. A handler on the path catches it
  and logs it, and formatting the traceback reads source from disk, so the
  guard fires inside its own report. Raise a `BaseException` subclass.
- ALWAYS write down what the guarded run runs. A near-empty cycle proves
  construction and that cycle touch nothing, not that a busy one does.
- NEVER quote a green suite or an unmoved golden for a statement no test
  executes. Force the moved block to return nothing and count the failures;
  zero means the gate is blind there. Record what stands in — the statements
  no test runs, from a line trace, and the statement-by-statement comparison
  against the block they came from — as a bug, not a pass.
- What leaves a class leaves its logger. Every line the loader writes carries
  the new name; grep for consumers of the old one — parsers, tests that tune
  a logger — before the commit.
- The leak runs both ways. A component that finds its own data cannot be
  built in a test without it, so tests build the smallest object that
  compiles, and a fake then justifies a production branch — a `hasattr` on a
  mandatory field that exists so the fake can skip it. Injection lets the test
  build the real object; the branch goes with the fake, never before it.
- NEVER assume the fake's branch is load-bearing. Arm it to raise to see it is
  reached at all, then force it off to see what fails. A branch that is
  reached and whose removal breaks nothing is dead to the suite, which is a
  different fact from one the suite depends on.
- NEVER read a factory's claim about disk — measure it under the guard.
  "Empty paths, so nothing loads" held until the loader's fallback to the
  packaged data was traced.

## Bundling

- Tunables scattered over a class become one slotted object every read and
  every override reaches by one name. Neither a deletion, a move, a default
  nor an injection: every value keeps its reader and its definition, and the
  path changes at every site. Value-neutral by construction: compare the new
  type's fields, defaults and order against the attributes they replace
  through `fields()`, not by eye.
- The failure to fear is not a wrong value but an override that stops
  applying. An assignment to the old name on an object with a `__dict__`
  binds a fresh attribute nobody reads, and the test passes while testing
  nothing. The type checker names it where its config looks; a linter cannot
  see it at all — the line is valid code. For the directories the type
  checker excludes, rewrite mechanically and sweep: grep every tunable name
  used as an attribute, drop those reaching the bundle, and name each
  survivor with what feeds it. A homonym fed from a different tunable, or a
  snapshot taken at construction, is where "the same name" changes a value
  with no gate noticing.
- ALWAYS declare the bundle with slots. It refuses a name it does not
  declare, so the next stale override raises where the old class swallowed it.
- NEVER assume an override the harness sets is measured. Freeze: make the
  bundle ignore every write after construction except a set read at import,
  run every gate, count. What fails is load-bearing; what stays green can
  stop applying with every suite green. Then mutate one default per run and
  count again. Record what neither run sees as a bug, not a pass.
- The instrument is under the same guard as the code. Read its configuration
  at import; an environment read in `__post_init__` is below the entry point.
- The seam is finished when the sweep returns only named homonyms and no
  default has a second copy — a policy hard-coding four of them, a module
  global a harness mutates, a field with no reader are each their own seam.

## Collapsing

- A parameter list unpacked from objects the caller already holds becomes
  those objects. Neither a deletion, a move, a default, an injection nor a
  bundle: every value keeps its reader and its definition, and the call
  site stops naming it. It is binding-neutral — each call site, each
  parameter, the same value from the same place — and that is proved by
  resolution, not by reading.
- The danger is not the signature but the defaults. A function default and
  the field it becomes are two definitions of one value, and a caller that
  omits the parameter silently receives the other one. ALWAYS enumerate
  every disagreement between the two before the first edit — the signature
  against `fields()` — and make every caller that omitted one say what it
  was getting.
- ALWAYS resolve, on both branches, the value every moved parameter receives
  at every call site — the argument, or whichever default applies — and
  compare by value, by type and by provenance. Value-equal is not
  type-equal: a float spelled at the site and an int inherited from the
  field compare equal and are not the same binding.
- NEVER drop an argument because it equals the new default. It is
  value-neutral and moves the binding from visible to inherited, which
  couples the test to a production default it never named. Measure it:
  retune that default and count the tests that fail where the branch below
  stays green. A value the site spells out, it keeps spelling out.
- A parameter the signature declares and the body never loads vanishes in
  the collapse. That is a deletion riding inside a move — count the name's
  loads, say it in the commit, and name the field it leaves with no reader.
- NEVER quote the green suite for this layer. Measure it: perturb one moved
  parameter at one call site per run and count the runs that survive. A
  site every perturbation survives checks nothing it passes; a parameter
  that survives at every site is checked nowhere. The resolution is the
  evidence; the run is not.
- An optional that stays is one whose `None` the code reads differently
  from empty. A `None` that logs where a dict rate-limits stays; one read as
  `.get(k, 0)` behind `is not None` with an else of `0` is the empty dict,
  and folds as its own edit.

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
- ALWAYS know what the type gate excludes. Its 0 errors cover the directories
  its config includes; a defect in the rest — a test tree, an untyped
  package — needs the sweep.

## Reporting

- NEVER quote the total diffstat. Split `git diff --numstat` by kind —
  fixtures, docs, tests, config, production — and say what each bucket is. A
  net deletion under a hundred thousand lines of recorded fixtures reads as a
  rewrite when only the total is shown.
