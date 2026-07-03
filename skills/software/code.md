# Code — the engineering baseline

The language-agnostic base every language skill builds on. `go`, `rs`, `py`,
`ts`, `sh`, `sql`, and `mk` read this first (they say so in their body and
carry a `requires: software` hint), then apply their language-specific overlay.
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

## Layout and formatting

One import per line; it keeps diffs clean. Keep code at 80 columns or under and
prose at 100, with 120 the hard ceiling reserved for the rare line that genuinely
hurts to wrap (a long URL, a table row).

Utility files are named `*_utils.*`. Never write under `/tmp` — use `./tmp` in
the project root, with `./log` for debug and smoke logs and `./dist` or
`./target` for build artifacts.

For user-facing output, lowercase informational messages and Capitalize errors
(`"checking..."` vs `"Failed: ..."`), and follow the Unix log format:
`Sep 18 10:34:26 INFO subsystem: message`.

Services and CLI entrypoints write logs to stdout/stderr only. Never install
file log handlers or pass log-file paths through application code — let the
supervisor, container runtime, CI, or top-level runner persist logs. If the
whole orchestration stack is Python, implement artifact capture/compression in
that top-level Python runner instead of requiring shell redirection.

## Design

Reach for a struct or object only when you need to hold state or inject
dependencies; otherwise plain functions in modules compose better and leak less.
Model states as explicit enum variants rather than implicit boolean flags, and
always validate input before it reaches persistence.

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
