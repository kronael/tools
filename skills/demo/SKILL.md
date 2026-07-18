---
name: demo
description: Terminal demo GIF + MP4 recordings for READMEs and social (asciinema + agg + ffmpeg). NOT for general Makefile targets (use software) or GUI screenshots (use visual).
when_to_use: "record a demo, make demo, demo gif, demo mp4, demo video, asciinema, agg, terminal recording for README or twitter"
---

# Terminal demo recordings

Standard recipe: `asciinema` records a driven terminal session to a
`.cast` file, `agg` renders that to a `.gif` committed under the repo
and embedded in `README.md`. For social (Twitter/X), also transcode the
gif to an `.mp4` — autoplays, far smaller, and the only format some
platforms accept.

## Type the commands (self-narrating demos)

The strongest demos show *how* each result is produced: echo a shell
prompt and the command being typed, then run it, with a one-line `#`
comment before each step saying why. A viewer should be able to reproduce
the whole thing from the recording alone. Pattern (bash driver):

```bash
type_run() {                       # print "$ ", type the command, run it
	printf '\033[1;32m$ \033[1;37m'
	local i; for ((i=0; i<${#1}; i++)); do printf '%s' "${1:i:1}"; sleep 0.028; done
	printf '\033[0m\n'; sleep 0.9; eval "$1"
}
note() { printf '\n\033[1;36m# %s\033[0m\n' "$*"; }   # cyan narration
```

Gate the per-char delay behind an env var (`DEMO_TYPE=1`) so `make demo`
runs instantly for humans but types out char-by-char when recording.
Keep background scaffolding (starting mocks/servers) narrated, not typed —
type only the commands that are the point.

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

demo/demo.mp4: demo/demo.gif
	ffmpeg -y -i demo/demo.gif -movflags faststart -pix_fmt yuv420p \
	    -vf 'scale=trunc(iw/2)*2:trunc(ih/2)*2' demo/demo.mp4

demo: demo/demo.mp4
```

`-pix_fmt yuv420p` and the even-dimension `scale` are mandatory — most
players (and Twitter) reject odd dimensions or non-4:2:0 chroma. Commit
both `demo.gif` (README embed) and `demo.mp4` (social upload).

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
- If the narrative claims an API exposes something, show a real `curl`
  request to that endpoint and its result. Filtering with `jq`, `grep`, or a
  small named helper is fine when the raw response is too large, but do not
  replace real endpoints with invented demo objects.
