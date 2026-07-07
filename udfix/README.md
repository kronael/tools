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
