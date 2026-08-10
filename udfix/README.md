# udfix

Reads a box-drawing diagram from stdin, rewrites each junction and
segment character (`┌┐└┘├┤┬┴┼─│`) to match the neighbors that actually
connect to it, and writes the result to stdout.

Arrow heads (`►◄▼▲`) count as connections but are never rewritten.
Non-box characters, short/ragged lines, and the input's trailing-newline
state pass through unchanged.

## Install

```
make install
```

Installs to `$PREFIX/udfix` (default `~/.local/bin/udfix`).

## Use

```
udfix < diagram.txt > diagram_fixed.txt
```

## Lint

`-lint` checks instead of rewriting. It reads a diagram on stdin, prints `row:col: message` for
each defect, and exits non-zero if any — a gate for docs whose diagrams are hand-edited.

```
udfix -lint < diagram.txt    # exit 0 clean; exit 1 with defects listed
```

Rules:

- **Underspecified junction** — a glyph that fails to draw a segment actually touching it (a `┐`
  with a line entering from above) is flagged, with the expected glyph.
- **ASCII arrows** — `->` and `<-` are flagged; use `► ◄ ▲ ▼`.
- **Tolerated** — a glyph that draws *more* arms than connect (`want ⊂ have`) is left alone. That
  is a file-tree branch (`├──` with nothing above) or a deliberate stub, so `-lint` is safe on
  tree listings; the rewrite mode is not — it cornerises a tree's first `├` to `┌`.

Lint one diagram per invocation; to gate a whole document, pipe each fenced code block through it.
