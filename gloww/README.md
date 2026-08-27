# gloww — glow at the terminal's real width

[glow](https://github.com/charmbracelet/glow) renders markdown in the
terminal, but it wraps each source line on its own. A file hard-wrapped at
76 columns keeps those breaks at every width, so a narrow terminal gets
ragged output and a wide one wastes half the screen.

`gloww` rejoins each paragraph into one line with
[mdformat](https://github.com/hukkin/mdformat) `--wrap no`, then lets glow
wrap it to fit. mdformat parses CommonMark, so code fences, lists, tables,
and frontmatter keep their own line breaks.

## Install

```sh
cd gloww && make install
```

Installs to `~/.local/bin/gloww`. Needs `glow` on `PATH`, plus either
`mdformat` or `uv` (the script falls back to `uvx mdformat`).

## Usage

```sh
gloww README.md              # paged, wrapped to the terminal width
gloww -w 60 README.md        # wrapped to 60 columns
cat README.md | gloww        # stdin
gloww README.md --style dark # further arguments pass through to glow
```

`GLOWW_WIDTH` sets the width from the environment. Output to a pipe is not
paged.
