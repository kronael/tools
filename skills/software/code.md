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
  carry one word through an endpoint's path, handler, module and model:
  `/v1/react` → `react()` in `react.py`, `ReactIn`; NEVER `reactions.py`,
  NEVER a `stream()` on `/v1/ws`.
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

## Boring code

- ALWAYS choose the boring solution: write simpler than you are capable of,
  and take the construct with the least mental model when two are equivalent
  (a combinator chain with a non-trivial body → a plain `for` loop).
- ALWAYS extend what exists before writing anything new — the runner, the
  helper, the parameter, the test that creates the database and reads the
  result — and copy a thing two or three times before you abstract it. A new
  module, stage, helper or knob is the plan's or the owner's decision, NEVER
  the executor's; NEVER call an abstraction simpler when it brings concepts
  the call sites lack (closures, generics, predicate parameters) — it has to
  cut TOTAL complexity, judged by cognitive overhead, not diff size.
- ALWAYS prefer a simple solution that is mostly right over a complex one that
  is fully correct; NEVER braid components — if A cannot be understood without
  B's state, separate them; ALWAYS hold information as plain data over
  objects: encapsulate I/O, expose information.
- NEVER spend an innovation token on fashion: a new technology is an unknown
  failure mode; boring, documented tech is a solved one.

## Design

- ALWAYS model states as explicit enum variants, NEVER implicit boolean flags:
  `sent: bool, skipped: bool` → `enum Notify { Send, Skip }`.
- ALWAYS name a variant by what happens at the use site — the action or effect
  — NEVER an interpretive label the reader has to decode:
  `Notify::Partners`/`Notify::Silent` → `Notify::Send`/`Notify::Skip`.
- ALWAYS plain functions in modules; reach for a struct or object only to hold
  state or inject dependencies — functions compose better and leak less.
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

- ALWAYS hold every change to WISDOM § System-change discipline: amend the
  original, fail loud to the user, retry only the transient, fix the cause,
  redesign only after sign-off.
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
