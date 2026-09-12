# Code — the engineering baseline

The language-agnostic base every language skill builds on. `go`, `rs`, `py`,
`ts`, `sh`, and `sql` read this first (they say so in their body and
carry a `requires: software` hint), then apply their language-specific overlay.
Nothing here is language-specific; if a rule only holds for one language it
belongs in that language's skill, not here.

## Naming

The entrypoint is always `main`. Use short file extensions (`.jl`, not `.jsonl`) and short CLI
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

## Layout and formatting

One import per line; it keeps diffs clean. Keep code at 80 columns or under and
prose at 100, with 120 the hard ceiling reserved for the rare line that genuinely
hurts to wrap (a long URL, a table row).

Utility files are named `*_utils.*`.

For user-facing output, lowercase informational messages and Capitalize errors
(`"checking..."` vs `"Failed: ..."`), and follow the Unix log format:
`Sep 18 10:34:26 INFO subsystem: message`.

Services and CLI entrypoints write logs to stdout/stderr only. Never install
file log handlers or pass log-file paths through application code — let the
supervisor, container runtime, CI, or top-level runner persist logs. If the
whole orchestration stack is Python, implement artifact capture/compression in
that top-level Python runner instead of requiring shell redirection.

## Comments

When a comment earns its place, at most ONE short line.

Redundancy test — delete the comment if it fails: NEVER write a comment whose
content is already visible in adjacent code, INCLUDING a log, warn, or error
message on a neighbouring line. Paraphrasing that message in a comment above it
is the canonical redundant comment.

- NEVER a multi-line comment block — no `///`, no `/** */`, no stacked `//`. A
  comment spanning more than one line is a bug; cut it to one line or drop it.
- NEVER a source line number in a comment (`// see line 200`, `// as in L42`),
  and NEVER a diff-gutter number (`255 +`) — point to a file and/or function
  name instead.

## Design

A simple solution that is mostly right beats a complex one that is fully correct,
because the simple one spreads and evolves while embedded complexity can never
be removed.

You get roughly three innovation tokens; don't spend one on fashion.

Braided code grows combinatorially while separated code composes linearly.
Prefer information as plain data over objects — ten data structures and ten
functions give a hundred composable operations; a hundred classes with ten
methods each give a thousand operations and no composition.
