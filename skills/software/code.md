# Code — the engineering baseline

The language-agnostic base every language skill reads before its first edit; a
rule that holds for one language only lives in that language's skill. The
rules sessions break most come first; pairs read wrong → right. ALWAYS re-scan
your diff against every `##` heading here before calling an edit done.

## Naming

- ALWAYS name a predicate `is_`/`has_`/`can_`/`should_` and a conversion
  `to_`/`into_`: `valid()` → `is_valid()`, camelCase `isValid()`. The
  `<lang>-bool-fn-prefix` lint flags a miss where it exists; the rule stands
  without it.
- ALWAYS name a function that wraps one external command `run_<command>`,
  after the program it runs; `run_process` is the generic form: a helper
  around `xz` is `run_xz()`, NEVER `compress()` or `store_file()`. The name
  says a subprocess starts; an effect name hides it.
- ALWAYS name a function that runs for the life of the process or of a
  connection `<what>_loop` (`consume_loop`, `seed_loop`), and one that does an
  operation once and classifies how it ended — returns, raises a retryable or a
  permanent error, records the outcome — `do_<what>` (`do_run`, `do_fetch`),
  with no retry inside: a retry wraps the `do_` call. NEVER `run`, `handle` or
  `_attempt` for either; the name tells the reader the function never returns,
  or that it is the one place a failure is sorted.
- ALWAYS reuse the name the code, the schema, the domain and the owner already
  give a thing — function, parameter, field, type, file, commit term — and
  carry one word through an endpoint's path, handler, module and models, the
  models named `<Word>Request` and `<Word>Response`: `/v1/react` → `react()`
  in `react.py`, `ReactRequest`, `ReactResponse`; NEVER `reactions.py`, NEVER
  `ReactIn`/`ReactOut`, NEVER a `stream()` on `/v1/ws`.
- ALWAYS use the domain's word, NEVER a synonym you prefer — the column and the
  surrounding code say `withdrawer`: `owners_of` → `withdrawers_of`.
- ALWAYS name a parameter or local after its own type or the domain concept it
  holds, NEVER a role you invented: `scope: &WithdrawerTracker` →
  `tracker: &WithdrawerTracker`.
- NEVER rename what already has a name — no alias, intermediate binding or
  import rename. A rename erases where the value came from and makes the reader
  hold two names for one thing.
- ALWAYS the shortest name the context leaves clear; drop the prefixes and
  suffixes it already supplies: `parse_tokens_from_symbol()` →
  `parse_tokens(symbol)`.
- ALWAYS make the verb match the behaviour, and rename the moment they diverge —
  a `finish_task()` that cancels, or a `get_*()` that mutates, is a lie.
- ALWAYS name an API-visible function — `pub`/`pub(crate)`, called across
  modules, or reading as part of the surface — by a verb phrase: the verb is
  the action, the type it returns is the verb's object.
  `snapshots_with_resolved_withdraw()` → `filter_resolved_snapshots()`.
- NEVER name a small local or inline helper after a structure it builds
  internally or a nearby map — it may take the noun of the type it returns.
- ALWAYS change a genuinely wrong name everywhere it occurs — NEVER coin a
  second name that competes with it.
- NEVER let a rename rewrite prose: the same word can be a variable in code and
  a domain term in a comment, and a blind rename corrupts the comment.
- ALWAYS discard with a bare `_`, NEVER a named binding — the name labels a
  value you throw away: `|(_withdraw, account)|` → `|(_, account)|`.
- ALWAYS short names for generic values — indices, counts, math — in a small
  scope: `n`, `k`, `r`, `i`, `j`, `x`, `y`, `z`, `m`, `g`, `f`, `h`; doubled
  forms for nested or plural (`kk`, `vv`); short words (`data`, `msg`).
- NEVER collapse a value that stands for a specific concept to its initial — it
  keeps the concept's name: `u` → `url`, `s` → `slot`, `e` → `epoch`.
- NEVER `o`, `O`, `l`, `I` — they read as `0` and `1`.
- ALWAYS `main` for the entrypoint.
- ALWAYS short file extensions and short CLI flags: `.jsonl` → `.jl`.

## Comments

- NEVER write a comment or docstring; intent travels in names, types and
  structure. ALWAYS sweep the WHOLE file you touch and delete every comment
  this section bans — one left standing is a defect, not a no-op.
- The one general exception: a doc comment on a PUBLIC API item stating what
  the signature cannot — contract, units, ownership, error conditions — NEVER
  what the body does: `"""The MD5 hex digest of repr(contents)."""` on
  `digest(contents)` restates the body → delete it. NEVER one on a private
  item.
- Inside a body, three exceptions only, each on the construct its skill names:
  a test's scenario-to-outcome intro (`testing.md`), `// SAFETY:` on `unsafe`
  (`rs`), the WHY above a deliberately unhandled error (`go`, `rs`) — a few
  words naming the reason; the full why goes in the commit message. NEVER one
  trailing a code line, NEVER a line number, ticket id or spec handle — a
  repo-relative path (`specs/4/6-agents.md`) when a pointer is needed.
- A machine-read marker is not a comment: a `// #region <name>` doc anchor
  (`readme` skill) and a lint or type pragma (`//nolint:`, `# noqa`,
  `# type: ignore`, `// @ts-expect-error`) stay.
- A config file is not code: the reason beside an entry — a lint `ignore`
  list, a CI matrix, host vars — stays, because the entry has no name, type
  or body to carry it. A sweep deletes nothing there.

## Boring code

- ALWAYS choose the boring solution: debugging is twice as hard as writing, so
  write simpler than you are capable of, clarity over cleverness.
- ALWAYS pick the construct that takes the least mental model when two are
  equivalent: a combinator chain with a non-trivial body → a plain `for` loop.
- ALWAYS copy a thing two or three times before you abstract it. Every line is
  a liability, deletion lowers cost, and a premature abstraction freezes the
  wrong shape in place. ALWAYS design for replaceability.
- ALWAYS extend what exists before writing anything new — the runner, the
  helper, the parameter, the test that creates the database and reads the
  result. A new module, stage, helper or knob is the plan's or the owner's
  decision, NEVER the executor's.
- NEVER call an abstraction simpler when it brings concepts the call sites do
  not have — function pointers, closures, generics, combinator chains. It has
  to cut TOTAL complexity; judge by cognitive overhead, not diff size.
- ALWAYS try subtraction first: remove unnecessary mechanisms, then simplify
  data models, views and state handling.
- ALWAYS preserve required behavior. Fewer lines alone do not prove a simpler
  solution.
- ALWAYS add code only for a measured unmet requirement that subtraction and
  those simplifications cannot satisfy.
- NEVER braid components: if A cannot be understood without tracking B's
  state, separate them — braided code grows combinatorially, separated code
  composes linearly. ALWAYS minimise state and make what remains explicit; an
  `f(x)` whose result changes over time leaks that complexity to every caller.
- ALWAYS hold information as plain data over objects; encapsulate I/O, expose
  information. Ten structures and ten functions give a hundred composable
  operations; a hundred classes of ten methods give a thousand and no
  composition.
- NEVER spend an innovation token on fashion — there are roughly three, for
  where they buy competitive advantage. Every new technology is an unknown
  failure mode; boring, documented tech is a solved one.

## Design

- ALWAYS model states as explicit enum variants, NEVER implicit boolean flags:
  `sent: bool, skipped: bool` → `enum Notify { Send, Skip }`.
- ALWAYS name a variant by what happens at the use site — the action or effect
  — NEVER an interpretive label the reader has to decode:
  `Notify::Partners`/`Notify::Silent` → `Notify::Send`/`Notify::Skip`.
- ALWAYS plain functions in modules; reach for a struct or object only to hold
  state or inject dependencies — functions compose better and leak less.
- ALWAYS compose a part of an object's behaviour that varies: a field holding
  an object of one interface, a do-nothing one where there is nothing to do.
  NEVER a base-class method a subclass overrides, NEVER an `isinstance` probe
  for an optional method — the type test that asks "can this object do X?".
- ALWAYS model a closed set of data variants — message types, sample kinds,
  events — as one named, frozen type per variant behind one small interface
  or base, and dispatch on the type: a Rust `match` on the enum, a Go type
  switch, Python `isinstance`/`match` on the class. NEVER on a `kind`/`type`
  string or a map key, and NEVER a map of untyped values (`dict[str, Any]`,
  `map[string]any`) as a data shape: external JSON is parsed into the variants
  where it enters, and nothing past that boundary sees the raw form.
- ALWAYS validate input before it reaches persistence, and ALWAYS compare a
  field once, against the value the code itself derives for it; NEVER a second
  check against a constant that repeats the first — the two drift apart.
- ALWAYS return an error from library code — a crate, a package, a module
  another program imports — and let only the top level, `main` or a test,
  decide to crash: a panic inside a library takes every caller down. Enforce
  it with the language's lints where they exist (`rs` § Unwrap Safety).
- ALWAYS handle SIGINT and SIGTERM in anything long-running — a service,
  daemon, worker or watch loop: stop taking new work, finish or cancel what is
  in flight, flush, and exit.
- NEVER a function-typed struct field: it is a jump, not an abstraction. The
  call site names the field, the value is a nameless literal another file
  assigned, and no other code can refer to it. Five-second test — from the call
  site, can you name every assignment of the field without a search? If not,
  write a one-method interface (its implementations are types the language
  server lists) or call the function directly. A test double fails the test the
  same way; a one-method interface with a fake type is as short and stays
  findable: `Authorize func(ctx) error` field →
  `type Authorizer interface { Authorize(ctx) error }`.
- ALWAYS keep a function value where the reader sees it created: passed as an
  argument (`sort.Slice`), adapted to the library's own interface
  (`http.HandlerFunc`), or assigned at one wiring site because the caller holds
  a package function the callee must not import. Cost: once one name is a
  function in one package, a method in a second and a func field in a third, a
  grep for the field answers about the wrong one.

## System changes

- ALWAYS grep for the existing mechanism (guard, helper, runner, table, log
  site, config) before adding one, and extend the ORIGINAL. NEVER a parallel
  second path, a stage beside it or a helper around it — two paths drift. If
  the original is wrong, fix it or say so; NEVER route around it.
- ALWAYS fail loud, to the user: an error on a user-facing path MUST surface
  (thrown, non-2xx, delivered), not just logged. NEVER swallow it, and NEVER
  add retry/fallback/best-effort as "robustness" — that turns a visible failure
  into an invisible one. Retry ONLY the transient: network, DB busy/locked.
  When the MECHANISM swallows — a fire-and-forget submit nobody collects, a
  detached task, a bare catch — replace it with one that propagates; NEVER keep
  it and bolt on counters and collectors to recover the drops: more code, less
  reported.
- ALWAYS prefer the cause fix to the loud log — make the bad state impossible
  by construction.
- A redesign (new contract, changed control flow, cross-cutting) ships only
  after sign-off on its `BUGS.md` proposal (WISDOM § Bug triage).
- NEVER improve beyond what the task asks — no drive-by cleanup, rename or
  feature in the same change; park it (`next`, `bugs`).
- ALWAYS retry inside a job or request only a failure that returns fast —
  refused or reset connection, a cut body, a rate-limit answer — on short
  delays (1, 1, 2, 5 s) under one deadline per call. NEVER retry a timeout
  there: it fails the unit of work, and the outer retry (the next claim, the
  caller) tries again. A test proves a timeout makes exactly one attempt.
- **An external contract is the provider's published spec.** ALWAYS build and
  re-check a client of another team's service against the provider's
  integrator guide or API spec at its default head, fetched fresh before you
  merge or ship — NEVER an in-repo summary, a stub branch, or a parameter name
  you assumed.
- ALWAYS check a formula derived from that spec against the spec's own worked
  examples; a derivation can drop a term the examples carry.
- ALWAYS build/test/lint every ~50 lines — errors cascade.
- NEVER edit source by running a script or `sed -i` that string-replaces it —
  ALWAYS edit the file directly, so the change is read as it is written and
  not after a blind substitution has landed. AST tools (`ruff --fix`, LibCST,
  ast-grep, a language server's rename) rewrite syntax nodes, not strings, and
  are not this.

## Layout and formatting

- NEVER nest a long or multi-line expression inside an `if`/`if let` condition
  — the reader loses the test before reaching the `{` that answers it. Bind it,
  then branch on the name: `if let Err(err) = retry_with_backoff(...).await` →
  `let sent = retry_with_backoff(...).await;` then `if let Err(err) = sent`.
- ALWAYS code at 80 columns or under and prose at 100; 120 is the hard ceiling,
  for the rare line that genuinely hurts to wrap (a long URL, a table row).
- ALWAYS let `rumdl` wrap Markdown, NEVER your hands: a repo opts in with a
  root `.rumdl.toml` (`[MD013] line-length = 100`, `reflow = true`, `tables`
  and `code-blocks` false; `exclude` names worktrees and generated files as
  `.name/` patterns — a root-anchored `/.*/` skips nothing when one file is
  named) and a pinned `rumdl` (`bun add -d --exact rumdl`, or the PyPI
  package); `make fmt` runs `rumdl fmt .`, `make lint` runs `rumdl check .`,
  and the PostToolUse hook runs it on every `.md` you write. A repo with no
  config is never rewrapped.
- ALWAYS one import per line — it keeps diffs clean.
- ALWAYS name utility files `*_utils.*`.
- ALWAYS run a script from a fixed working directory with simple relative
  paths — NEVER `basename $0`, `__dirname`, or complex path resolution.
- ALWAYS lowercase informational user-facing messages and Capitalize errors:
  `"checking..."`, `"Failed: ..."`.
- ALWAYS the Unix log format: `Sep 18 10:34:26 INFO subsystem: message`.
- ALWAYS write logs from services and CLI entrypoints to stdout/stderr only —
  NEVER a file log handler or a log-file path passed through application code;
  the supervisor, container runtime, CI or top-level runner persists them.

## House conventions

- Data: `${PREFIX:-/srv}/data/<project_name>/` for a service or daemon. A
  program a user runs keeps state, settings, cache and data in
  `$XDG_{STATE,CONFIG,CACHE,DATA}_HOME/<name>` (`~/.local/state/<name>` and so
  on), each overridable by one flag or env var.
- Config: prefer flags + env vars for anything simple — a short flag where a
  human types it (`-u`), a long name with an env var where the deploy sets it
  (`RPC_URL`). Reach for a file only when the shape is genuinely nested: TOML as
  first CLI param, api keys as second.
- `make` for build/lint/test/clean and debug builds: `make test` = fast unit
  (<5s), `make test-all` = unit + integration, what CI runs, `make smoke` =
  production data.

## Grug rules

Three reminders from grugbrain.dev the sections above do not cover.

- NEVER use a tool heavier than the task — scaffolding (subagents, generated
  machinery, a lookbehind regex) bigger than the change it serves is the wrong
  tool. Small task, small tool.
- ALWAYS keep locality of behaviour: put the code on the thing that does the
  thing. NEVER scatter understanding across files just to honour separation of
  concerns.
- NEVER delete or "simplify" code you do not yet understand (Chesterton's
  fence) — the ugliness often encodes a real constraint. Understand it first.
