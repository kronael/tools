# Code — the engineering baseline

The language-agnostic base every language skill reads before its first edit; a
rule that holds for one language only lives in that language's skill. The
rules sessions break most come first; pairs read wrong → right. ALWAYS re-scan
your diff against every `##` heading here before calling an edit done.

## Naming

- ALWAYS name a predicate `is_`/`has_`/`can_`/`should_` and a conversion
  `to_`/`into_`: `valid()` → `is_valid()`, camelCase `isValid()`. The
  `<lang>-bool-fn-prefix` lint flags the miss in Rust, Python and TypeScript
  (`.ts`, not `.tsx`); no lint covers any other language.
- ALWAYS reuse the name the code, the schema, the domain and existing callers
  already give a thing — function, parameter, field, type, test helper,
  commit-message term. A new word claims that no existing name fits; earn it.
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

- NEVER write a comment. Intent travels in names, types and structure; a
  comment is no fallback for code that failed to carry it.
- ALWAYS limit the one general exception to a doc comment on a PUBLIC API item
  — exported function, type, struct, module — stating only what a caller cannot
  see from the signature: contract, units, ownership, error conditions. NEVER
  one on a private item, NEVER one on a line inside a body.
- NEVER leave a comment whose content adjacent code already shows, a log, warn
  or error message on a neighbouring line included — paraphrasing that message
  above it is the canonical redundant comment:
  `// load failed` over `error!("load failed")` → delete the comment.
- ALWAYS sweep the WHOLE file you touch, not only the lines you edit: read
  every comment standing there and delete the ones this section bans. One left
  standing is a defect, not a no-op.
- NEVER stack `//`, `#`, `///` or `/** */` lines inside a function body — the
  ban is on the comment, not its length. A public-API doc comment MAY span
  lines when the caller's contract needs the room.
- NEVER a source line number or a diff-gutter number (`255 +`) in a comment —
  point to a file or function: `see line 200` → `see parse_header`.
- NEVER a ticket number or issue ID in a comment.
- ALWAYS confine comments inside a body to three narrow exceptions, each owned
  by the skill that states it and valid only on the construct it names: a
  test's scenario-to-outcome intro (`testing.md`), a `// SAFETY:` invariant on
  an `unsafe` block (`rs`), and the WHY on its own line above a deliberately
  unhandled error — a Go error suppression (`go`), a Rust `.unwrap()` (`rs`).
  NEVER anything else, and NEVER one trailing a code line.
- NEVER count a machine-read marker as a comment: a `// #region <name>` doc
  include anchor (`readme` skill) or a lint or type pragma (`//nolint:`,
  `# noqa`, `# type: ignore`, `// @ts-expect-error`) is read by a tool, so it
  stays.

## Boring code

- ALWAYS choose the boring solution: debugging is twice as hard as writing, so
  write simpler than you are capable of, clarity over cleverness.
- ALWAYS pick the construct that takes the least mental model when two are
  equivalent: a combinator chain with a non-trivial body → a plain `for` loop.
- ALWAYS copy a thing two or three times before you abstract it. Every line is
  a liability, deletion lowers cost, and a premature abstraction freezes the
  wrong shape in place. ALWAYS design for replaceability.
- NEVER call an abstraction simpler when it brings concepts the call sites do
  not have — function pointers, closures, generics, combinator chains. It has
  to cut TOTAL complexity; judge by cognitive overhead, not diff size.
- ALWAYS reframe before adding a branch, a fallback or a config knob: check
  whether an existing parameter, path or environment variable makes the edge
  case normal. Branch only when no existing mechanism can express it — one code
  path beats ten.
- ALWAYS prefer a simple solution that is mostly right over a complex one that
  is fully correct — the simple one spreads and evolves, embedded complexity
  never leaves.
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
- ALWAYS validate input before it reaches persistence.
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
  and `code-blocks` false, worktrees and generated files excluded) and a pinned
  `rumdl` (`bun add -d --exact rumdl`, or the PyPI package); `make fmt` runs
  `rumdl fmt .`, `make lint` runs `rumdl check .`, and the `md_format` hook
  runs it on every `.md` you write — when it says the file changed, Read it
  again before the next Edit. A repo with no config is never rewrapped.
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
