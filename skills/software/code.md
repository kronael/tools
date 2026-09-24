# Code — the engineering baseline

The language-agnostic base every language skill builds on. `go`, `rs`, `py`,
`ts`, `sh`, and `sql` read this first — they say so in their body — then apply
their language-specific overlay.
Nothing here is language-specific; if a rule only holds for one language it
belongs in that language's skill, not here.

## Naming

Shorter is better. Omit prefixes and suffixes the context already makes clear —
`parse_tokens(symbol)`, not `parse_tokens_from_symbol()`. The entrypoint is
always `main`. Use short file extensions (`.jl`, not `.jsonl`) and short CLI
flags.

Single-letter and short variable names are fine where the scope is small and the
meaning is obvious: `n`, `k`, `r`, `i`, `j`, `x`, `y`, `z`, `m`, `g`, `f`, `h`;
doubled forms for nested or plural (`kk`, `vv`); and short descriptive words
(`data`, `msg`). Never use the visually ambiguous singles `o`, `O`, `l`, `I` —
they read as `0` and `1`. But those singles are for generic values — indices,
counts, math. A value that stands for a specific concept keeps that concept's
name (`url`, `slot`, `epoch`), never collapsed to its bare initial.

Never rename something that already has a name — aliases, intermediate bindings,
import renames. A rename erases where the value came from and forces the reader
to hold two names for one thing.

Discard with a bare `_`, never a named `_prefix` binding — `|(_, account)|`, not
`|(_withdraw, account)|`. The name labels a value you are throwing away; it is
clutter the reader still has to parse.

Inherit names; never invent one when the surrounding code already has it.
Before naming a function, parameter, field, type, test helper, or
commit-message term, check what the code, the schema, the domain, and
existing callers already call that thing, and reuse it exactly. A new word is
a claim that no existing name fits, and it has to be earned. Name a parameter
or local after its own type or the domain concept it holds, not after a role
you invented — a `&WithdrawerTracker` parameter is `tracker`, not `scope`. Use
the domain's word, not a synonym you prefer — if the column and the
surrounding code say `withdrawer`, the accessor is `withdrawers_of`, never
`owners_of`. An API-visible function — anything `pub`/`pub(crate)`, called
across modules, or that reads as part of the surface — is named by a verb
phrase: the verb is the action, the type it returns is the verb's object —
`filter_resolved_snapshots(...)`, not the value-shaped noun
`snapshots_with_resolved_withdraw(...)` that reads like the thing returned
rather than the act. A small local or inline helper may instead take the noun of
the type it returns, not a structure it builds internally or a nearby map.
Either way, `is_`/`has_` for predicates, `to_`/`into_` for conversions. If an
existing name is genuinely wrong,
change it everywhere — never coin a second name that competes with it. A
rename is not licence to rewrite prose: the same word can be a variable in
code and a domain term in a comment, and a blind rename corrupts the comment.

## Layout and formatting

One import per line; it keeps diffs clean. Keep code at 80 columns or under and
prose at 100, with 120 the hard ceiling reserved for the rare line that genuinely
hurts to wrap (a long URL, a table row).

Never nest a long or multi-line expression inside an `if`/`if let` condition —
a condition the reader cannot take in at a glance divorces the test from the
`{` that answers it. Bind the expression to a name, then branch on that name:
`let sent = retry_with_backoff(...).await;` then `if let Err(err) = sent`.

Utility files are named `*_utils.*`.

A script runs from a fixed working directory with simple relative paths — NEVER
`basename $0`, `__dirname`, or complex path resolution.

For user-facing output, lowercase informational messages and Capitalize errors
(`"checking..."` vs `"Failed: ..."`), and follow the Unix log format:
`Sep 18 10:34:26 INFO subsystem: message`.

Services and CLI entrypoints write logs to stdout/stderr only. Never install
file log handlers or pass log-file paths through application code — let the
supervisor, container runtime, CI, or top-level runner persist logs. If the
whole orchestration stack is Python, implement artifact capture/compression in
that top-level Python runner instead of requiring shell redirection.

## Comments

NEVER write a comment. Intent travels in names, types and structure; a comment
is not a fallback for code that failed to carry it. The ONE general exception is
a doc comment on a PUBLIC API item — an exported function, type, struct, module
— and it states only what a caller cannot see from the signature: contract,
units, ownership, error conditions. A private item gets none. A line inside a
body gets none.

Three narrow exceptions beyond it, each owned by the skill that states it and
valid only on the construct it names: a test's scenario-to-outcome intro
(`testing.md`), a `// SAFETY:` invariant on an `unsafe` block (`rs`), and the
WHY on a deliberate error suppression (`go`). Nothing else inside a body.

ALWAYS sweep the WHOLE file when you touch it, not only the lines you edit:
read every comment standing there and delete the ones this section bans.
Leaving one standing is a defect, not a no-op.

Redundancy test — delete the comment if it fails: NEVER leave standing a
comment whose content is already visible in adjacent code, INCLUDING a log,
warn, or error message on a neighbouring line. Paraphrasing that message in a
comment above it is the canonical redundant comment.

- NEVER stack `//`, `#`, `///` or `/** */` lines inside a function body — the
  ban is on the comment, not merely its length. A public-API doc comment MAY
  span lines when the caller's contract needs the room.
- NEVER a source line number in a comment (`// see line 200`, `// as in L42`),
  and NEVER a diff-gutter number (`255 +`) — point to a file and/or function
  name instead.
- NEVER a ticket number or issue ID in a comment.
- NEVER a comment about past state, a prior design, or backwards compat — the
  `writing` skill's no-history rule covers comments too; history lives in `.diary/`.

## Design

Reach for a struct or object only when you need to hold state or inject
dependencies; otherwise plain functions in modules compose better and leak less.
Model states as explicit enum variants rather than implicit boolean flags, and
always validate input before it reaches persistence. Name a variant by what
happens at the use site — the action or effect — never an interpretive label
the reader has to decode: `Notify::Send`/`Notify::Skip`, not
`Notify::Partners`/`Notify::Silent`.

A function-typed field in a struct is a jump, not an abstraction. The call site
names the field; the value is whatever another file assigned, and that value is
a literal with no name, so no other code can refer to it. An interface method is
the same seam with a name on each destination: the implementations are types,
and the language server lists them. Five-second test — from the call site, can
you name every assignment of this field without a search? If not, it is a jump:
write an interface with one method, or call the function directly. The test
double is the usual reason for the field and fails the test the same way; a
one-method interface with a fake type is as short and stays findable.

A function value is right where the reader sees it created: passed as an
argument (`sort.Slice`), adapted to the library's own interface
(`http.HandlerFunc`), or assigned in one wiring site because the caller holds a
package function and the callee must not import that package. Cost: arizuko,
2026-09-23 — 82 exported func fields in 14 files, and `Authorize` is a function
in one package, a method in a second and a func field in a third, so a grep for
the field answers about the wrong one.

## System changes

- **No duplication — amend the original.** Before adding a mechanism (guard,
  helper, table, log site, config), grep for an existing one. If it exists,
  fix/extend the ORIGINAL; NEVER add a parallel second path — two paths drift.
  If the original is wrong, fix it or call it out; NEVER route around it.
- **Fail loud, fail to the user.** An error on a user-facing path MUST surface
  to the user (thrown / returned non-2xx / delivered to the chat), not just
  logged — a logged-but-invisible failure is still silent. NEVER swallow
  (`_ = err`, `if err == nil { use }` with no else); ALWAYS handle-and-surface.
- **Retry ONLY transient errors** — remote/network calls and DB busy/locked.
  Everything else (misconfig, missing data, programming errors) throws
  immediately: no retry, no fallback, no best-effort continue past a failed
  precondition.
- **Fix causes, not symptoms.** A loud log is a symptom patch; the cause fix is
  the redesign that makes the bad state impossible-by-construction (gate the
  precondition, funnel to one renderer, guard at the boundary). ALWAYS prefer
  the cause fix.
- **Redesigns need sign-off.** When a fix is a redesign (new contract, changed
  control flow, cross-cutting), RECORD it in `BUGS.md` as a proposal FIRST
  (`bugs` skill); the user signs off BEFORE you ship. Only symptom-level
  loud-logging ships inline.
- ALWAYS build/test/lint every ~50 lines — errors cascade.

## Boring code

Prefer the boring solution. Debugging is twice as hard as writing, so leave
yourself mental headroom — write code simpler than you are capable of, and choose
clarity over cleverness. When two constructs are equivalent, pick the one that
takes the least mental model to read (a plain `for` loop over a combinator chain
when the body is non-trivial).

Before you add a branch, a fallback, or a config knob, check whether an existing
parameter, path, or environment variable can make the edge case normal. Reframe
first; branch only when no existing mechanism can express it. Good taste
eliminates the special case by redesigning so the edge *is* the normal path — one
code path beats ten.

Every line is a liability, so deletion lowers cost while premature abstraction
freezes the wrong shape in place. Copy a thing two or three times before you
abstract it, and design for replaceability. When you do abstract, the helper has
to reduce *total* complexity, not just line count: if it introduces concepts that
aren't at the call sites — function pointers, closures, generics, combinator
chains — it is not simpler. Judge by cognitive overhead, not diff size. A simple
solution that is mostly right beats a complex one that is fully correct, because
the simple one spreads and evolves while embedded complexity can never be removed.

Spend your roughly three innovation tokens where they buy competitive advantage.
Every new technology is an unknown failure mode; boring, documented tech is a
solved one. Don't spend a token on fashion.

Watch for complecting — if you cannot understand component A without tracking B's
state, they are braided together, and braided code grows combinatorially while
separated code composes linearly. State is the usual culprit: if `f(x)` returns
different results over time, that complexity escapes to every caller. Values
compose; stateful objects leak. Minimize state and make what remains explicit.
Prefer information as plain data over objects — ten data structures and ten
functions give a hundred composable operations; a hundred classes with ten
methods each give a thousand operations and no composition. Encapsulate I/O,
expose information.

## Grug rules

Three reminders from grugbrain.dev that the above doesn't already cover:

Match the tool to the weight of the task. If the scaffolding — subagents,
generated machinery, a lookbehind regex — is bigger than the change it serves,
it's the wrong tool. Small task, small tool.

Prefer locality of behavior: put the code on the thing that does the thing, and
don't scatter understanding across files just to honor separation of concerns.

Respect Chesterton's fence. Never delete or "simplify" code you don't yet
understand — the ugliness often encodes a real constraint. Understand it first.
