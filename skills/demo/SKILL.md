---
name: demo
description: Terminal demo GIF recordings for READMEs (asciinema + agg). NOT for general Makefile targets (use software's ci.md) or GUI screenshots (use visual).
when_to_use: "record a demo, make demo, demo gif, asciinema, agg, terminal recording for README"
---

# Terminal demo recordings

Standard recipe: `asciinema` records a driven terminal session to a
`.cast` file, `agg` renders that to a `.gif` committed under the repo
and embedded in `README.md`.

## Makefile targets

Real file targets with real prerequisites — never one phony blob, so
`make demo` skips the recording when the cast is already fresh and only
re-renders the gif:

```makefile
.PHONY: demo

tmp/demo.cast: demo/run.ts
	mkdir -p tmp
	COLUMNS=80 LINES=30 asciinema rec tmp/demo.cast --overwrite --cols 80 --rows 30 -c 'bun run demo/run.ts'

demo/demo.gif: tmp/demo.cast
	agg --theme solarized-light --font-size 16 \
	    --cols 80 --rows 30 \
	    --idle-time-limit 3 --last-frame-duration 8 \
	    tmp/demo.cast demo/demo.gif

demo: demo/demo.gif
```

Reference implementation: `rig/Makefile`.

- ALWAYS drive the recording from a checked-in script (`demo/run.ts`,
  `demo/script`), never manual typing — reproducible and re-runnable.
- ALWAYS put the `.cast` intermediate in `tmp/` (gitignored); ALWAYS
  commit the final `.gif` under `demo/` next to its driving script.
- NEVER flatten `demo` into one phony target — split cast-recording from
  gif-rendering as separate file targets so Make can skip either.
- ALWAYS match `--cols`/`--rows` between `asciinema rec` and `agg` — a
  mismatch crops or letterboxes the gif.
- NEVER copy `--idle-time-limit`/`--last-frame-duration` verbatim —
  ALWAYS tune per demo, they trim dead pauses in the recording.
