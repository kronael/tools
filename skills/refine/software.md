# Refine lenses — software

What a refine pass hunts for against the language-agnostic baseline. Read WITH
`../software/code.md` (write-time rules), NEVER as a substitute — each lens names
the section that holds the rule. Every language skill requires `software`, so
every code context reads this file. Each lens carries the tag refine step 6
reads to pick the agent type.

## Coined and drifted names `simplify`

- ALWAYS grep the tree for every identifier the change introduces — function,
  parameter, field, type, test helper. A new word standing beside an existing
  name for the same thing (the column, the caller, the schema) is a finding;
  so is a synonym for the domain's word. Rule: `code.md` § Naming.
- ALWAYS grep the diff for the rebinding shapes: an import alias (`as`), a
  single-use `let x = y`, a named discard (`_foo`), a concept held in a bare
  initial (`u` for a URL), a `_from_<arg>` suffix the parameter already says.
- ALWAYS read each new or renamed function body against its verb — a `get_`
  that writes, an `is_` that mutates, a `finish_` that cancels is a finding,
  and a `simplify` fix is the rename, never a comment explaining the verb.
  Read its callers too: an argument that inverts the verb
  (`subscribe(…, op=UNSUBSCRIBE)`) is a second function wearing the first's
  name. A verb that names no operation —
  `rg -n 'def (process|handle|poll|run|manage|do)\b'` — is a finding: say what
  it does (`read_stats`).
- ALWAYS count the diff's repeated assemblies: the same two names glued at
  three or more sites —
  `git diff <range> | rg '^\+[^+]' | rg -o "f'[^']*\{\w+\.\w+\}[^']*\{\w+\.\w+\}[^']*'" | sort | uniq -c`
  — is one value the design never named (§ Design: a format's version is a
  name, written once).
- ALWAYS compare added/renamed module and package names with their main symbol or job;
  ALWAYS flag generic/partial names or utility basenames violating § Layout and formatting.
  A module named for a category that holds one source (`streaming/chats.py` holding
  Telegram) is named for what it holds (`telegram.py`).
- ALWAYS read one thing's name across every layer the range touches — table
  column, wire field, code, docs, config key, log key. Two words for it
  (`client` in the schema, `receiver` in the code) is a finding, renamed
  everywhere in this change; NEVER kept on one layer "for compatibility".

## Comments the baseline bans `simplify`

- ALWAYS list every comment in each touched FILE, not only in the hunks
  (`grep -nE '^\s*(//|#|--|/\*|\*)'`), in every component the range touches,
  `lib/` and test files included; ALWAYS flag those outside § Comments'
  exceptions. A sweep scoped to the hunks or to one component is itself a
  finding: rerun it over the whole touched set.
- ALWAYS read a surviving doc comment against its item: on a private item, or
  restating the signature, it is a finding.
- ALWAYS check the comment directly above a log, warn or error call — a
  paraphrase of that message is the most common miss. So are line numbers,
  ticket IDs and history notes (`was`, `old`, `legacy`).

## Abstraction that does not pay `simplify`

- ALWAYS count the call sites of each helper, interface, generic, wrapper and
  config knob the change adds — `rg -n '<name>'`, a `Protocol` declared so
  one reader at the edge (health, a status page) can take several concrete
  classes included. One or two sites is a finding: inline it (§ Boring
  code). Count production and test callers apart (`rg -n '<name>' -g
  '!**/test*'`): zero production callers is test-only code, moved to the
  tests or deleted. Application code only: a `table_verb` SQL function with
  one caller is the `sql` § Functions design; shared helpers follow § Second path beside the first.
- ALWAYS open every function the range adds (`git diff <range> | rg
  '^\+\s*(async )?def '`) whose body is one or two statements: one that only
  forwards its arguments to one call and wraps or renames the result
  (`read_catalog` = `get_markets(…)` then `Catalog(…)`) is a finding: inline
  it at its callers (§ Boring code). One that takes five or more parameters
  says the type it feeds bundles too much: pass the record (`py.md` § Data).
- ALWAYS grep the added lines for a callable chosen then called
  (`f = a if cond else b` followed by `f(…)`, a `download = …` indirection):
  write the `if`/`else` with the two calls (§ Boring code).
- ALWAYS name the reader for every hash, fingerprint, checksum, version
  constant, provenance field or registry the range adds (`rg -n -i
  'hash|fingerprint|checksum|provenance|VERSION|registry|register\('` over
  the added lines). No reader in the tree today is a finding: compare the
  fields, write the version in the module name (§ Design), delete the rest.
  A registry filled by import side effects or decorators is explicit
  assembly in `main` respelled; wire the instances where the reader sees them.
- ALWAYS trace consumers of each runtime or test asset the range adds
  (`git diff --name-only --diff-filter=A <range>`): search its name, then check
  glob discovery, directory scans and configuration. An asset with no consumer
  is a finding, deleted (`testing.md` § Scope and layout). Documentation is
  read by people; NEVER infer an unused asset from a missing basename match.
- ALWAYS list every function the range adds that assigns to or appends on its
  first parameter (`def add_trade(klines, …)` writing `klines.x`): an
  aggregator's updates are its methods (§ Design) — move it onto the type.
- ALWAYS name, for every fan-out the range adds (`gather`, `TaskGroup`,
  `errgroup`, `join_all`), the resource each awaitable takes — a lock, a
  one-in-flight bucket, a connection. All serialized on one is a loop dressed
  as concurrency; none bounded is a flood that wants a semaphore.
- ALWAYS read every added scan over a mapping's values for a field
  (`next(m for m in xs.values() if m.address == …)`, a `find_<x>` helper):
  the callers hold the key the map lacks — key the map by it.
- ALWAYS test each added mechanism against § Boring code: identify the unmet
  requirement and why subtraction or model, view and state simplification
  cannot satisfy it. Missing evidence is a finding.
- ALWAYS grep for function-typed struct fields the change adds (`func(` inside
  a Go struct, `Box<dyn Fn`, a `Callable` attribute) and for every map whose
  values are functions (`dict[str, Callable`, `map[string]func`, a
  `{'kind': handler}` literal): keyed by a string the wire carries, it is the
  `match` on a kind string respelled (§ Design); run § Design's five-second
  test on the rest.
- ALWAYS flag two or more booleans that together encode one state — § Design
  wants the enum.
- ALWAYS read each new construct against the plain version: a clever or novel
  construct — a one-liner trick, a pattern the codebase does not use, a
  generic or macro — where a plain `if` or loop does the job is a finding,
  rewritten plain (§ Boring code).

## Checks that guard nothing `simplify`

- ALWAYS list every check the range adds — `git diff <range> | rg '^\+' |
  rg -n 'if not |raise |assert |re\.(fullmatch|match)|\.exists\(|ge=|le=|
  max_|_limit|_cap\b|timeout|enabled'` — and, for each, name the production
  input that reaches it. A condition the types, the boundary parser or the
  real call already reject, or that no caller can produce, is a finding:
  delete it (`code.md` § Boring code: a check that never fires reads as a
  requirement). A start-up probe for a tool or login the first real call
  would fail on, a byte or length cap with no measured need, an `IF EXISTS`
  guard inside a transactional migration: the same finding.
- ALWAYS read each config key, flag, default, docker or unit parameter the
  range adds against its callers: a value no deployment sets to a second
  value today is a constant or a deletion, NEVER a knob (§ Boring code: a knob
  is the owner's decision). A feature is switched by the presence of its
  config section, NEVER an `enabled` flag or an empty-list default (`code.md`
  § House conventions). A required value gets no default in code.

## Second path beside the first `simplify`

- ALWAYS grep the tree for the mechanism each new guard, helper, table, log
  site or config key duplicates — same verb, same table, same env var. A
  second path where the original could be extended is a finding
  (`software/code.md` § System changes).
- ALWAYS grep the added lines and the PR text for the kept-old-path words —
  `rg -n -i 'legacy|backward|compat|fallback|rollback|deprecated|_old\b|old_|
  before-'` — each is a finding: delete the old path and move forward only;
  git holds every version (WISDOM § Documentation, `owner` § The smallest
  shape wins).
- ALWAYS list every unit, container, service, database, schema, CLI entry or
  process the range adds (`git diff --name-only <range> | rg
  'ansible|Dockerfile|\.service|migrations|main\.py'`): one beside an
  existing component that owns the same data or loop is a finding unless a
  privilege boundary forces it — a loop joins the owning process as a
  coroutine, a table joins the owning schema (`code.md` § System changes).
- ALWAYS treat a parsing or validation helper set the range adds beside the
  project's codec or boundary pydantic (`validation_utils.py`, `to_int`,
  `to_money`) as a second structurer: a finding, replaced by the codec.
- ALWAYS grep shared-library public names and maintained upstream dependencies already in use; replace helpers they provide.
- ALWAYS compare function bodies across components; put a helper two components need in the shared library once.
- ALWAYS compare new layers with a sibling's framework, routes, config loader, logging and `main`;
  ALWAYS flag departures or dependencies duplicating a role (§ System changes).
- ALWAYS check a fix that changes a contract or control flow across modules
  for its `BUGS.md` proposal; none is a finding, routed to `BUGS.md`, never
  applied.
- ALWAYS list every encoder the range adds beside a record (`rg -n 'def
  (encode|to_row|to_wire|as_row)'` over the added files): a record copied
  field by field into the row it is stored as is two shapes of one record
  (§ Design: the row is the record).

## Component moves change the code `correctness`

- ALWAYS diff each copy raw against its source revision/path; ALWAYS flag missing evidence or differences
  without a listed destination constraint (§ System changes).

## Feature PRs change runtime or deployment `correctness`

- ALWAYS inspect the whole PR for runtime/deployment changes listed in § System changes;
  ALWAYS flag changes bundled with features or lacking owner sign-off.

## Component builds diverge from the repo `simplify`

- ALWAYS require new build files to copy a sibling's Makefile, Dockerfile extension and manifests; diff the Makefiles.
- ALWAYS list `Dockerfile.ext` lines and check each against the base template and its preparation path;
  ALWAYS flag extensions or manual downloads for tools the base image or package manager already provides.

## Tests that prove nothing `simplify`

- ALWAYS list, per test file the range adds, the production modules it
  exercises: trace imports, helpers, subprocesses and service calls. A test
  whose subject is only a library or test helper is a finding; a helper that
  drives production is allowed (`testing.md` § Scope and layout).
- ALWAYS grep each added test's expected values for the module under test
  (`rg -n 'assert .*== *<module>\.'`) and its patches for the project's own
  modules (`rg -n "patch\('<project>"`): a mirror assertion or a mocked own
  module proves nothing (`testing.md` § What an assertion proves).
- ALWAYS grep added tests for assertions on source text, file names,
  migration numbers or fixture provenance (`rg -n "read_text\(|\.sql'|00[0-9]-|
  provenance"`): each is a finding (`testing.md` § Scope and layout, § What
  an assertion proves).
- ALWAYS break the subject of one added or converted test per module —
  invert its condition or revert the fix — and run the test: green both ways
  proves nothing, and a conversion that stays green on the broken subject
  weakened the test it replaced.
- ALWAYS list every production parameter, kwarg or `None` default the range
  adds that only tests pass (`rg -n '<param>=' -g '!**/test*'` returns no
  production caller): a finding, patched at the use site instead (`py`
  § Testing).

## Swallowed, softened and retried errors `correctness`

- ALWAYS grep the diff for the swallow shapes: `_ = err`, `if err == nil {`
  with no else, `except …: pass` or log-and-continue, an empty `catch`,
  `.ok()`/`unwrap_or_default()`/`?? []` on a user-facing path, a fallback
  `None`/`[]`/`0` the caller proceeds on. Each must reach the user
  (`software/code.md` § System changes).
- ALWAYS read every retry loop's body: anything but a network call or DB
  busy/locked inside it — a parse, a config read, a precondition — is a
  finding.

## External contract read from a summary `correctness`

- ALWAYS trace a client of another team's service to the provider's spec at
  its default head; a parameter name or formula sourced from an in-repo
  summary or a stub branch is a finding. ALWAYS recompute a derived formula on
  the spec's own worked examples (§ System changes).
- ALWAYS read each config key the range adds against that spec: a fact the
  provider fixes — a step, a sequence rule, an interval, a format — is a
  constant or a client fix, NEVER a knob the deploy sets (§ Boring code: a
  knob is the plan's or the owner's decision).
- ALWAYS compare each record type the range adds or narrows for an external
  source against a real row or sample of it: positions skipped (`Post(row[0],
  row[1], row[3], row[4])` of eight) or columns dropped because nothing reads
  them yet are findings (`data` § State Management).

## Layout drift `simplify`

- ALWAYS measure, never eyeball: `awk 'length > 80'` over the changed code
  lines, a multi-line expression inside an `if` condition, two imports on one
  line, a file log handler or log-file path in application code, and over the
  added lines `rg -n '__file__|__dirname|basename \$0'` — a path derived from
  the module's or binary's location where configuration or the test runner's
  root should hold it (§ Layout and formatting).
- ALWAYS inspect changed component trees for same-name nesting, redundant `api/` wrappers and nested utility modules.
  ALWAYS flag wrappers violating `readme/topology.md` § Files.

## Changes the ask cannot explain `simplify`

- ALWAYS group `git diff --stat <range>` by top-level directory and read every
  file against the nouns of the ask: a touched sibling component, `lib/` or
  `ansible/` the ask never named, an added `__init__.py`, a formatted file the
  change did not need, a regenerated workflow — each is a finding, reverted or
  parked (`code.md` § System changes: no drive-by). State the added-line count
  beside the ask's size; "why is it 16k lines" is the owner's next question.
- ALWAYS list every `.md` the range adds (`git diff --name-only
  --diff-filter=A <range> -- '*.md'`): one outside README, ARCHITECTURE,
  CHANGELOG, `specs/` and `BUGS.md` — a plan, report, summary or analysis —
  is a finding, deleted (WISDOM § Documentation).
- ALWAYS check an open PR that holds one job: a second PR or branch opened for
  the same job, or a copy of files in place of a change to them, is a finding.

## Deleted without being understood `correctness`

- ALWAYS check every deletion or "simplification" of code the change did not
  author for a stated reason the removed constraint does not hold — none
  stated is a finding (§ Grug rules, Chesterton's fence).
