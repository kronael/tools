# Install reference — tool commands + prune list

Cold lookup data for `SKILL.md`. Read the section named by a step when that
step runs; the decision logic stays in `SKILL.md`.

## External tool commands (step 6)

Run `which <tool>` first; skip if present and recent.

**Core** — ask once, install as a batch:

| Tool | Command | Skills |
|------|---------|--------|
| `ship` | `uv tool install git+https://github.com/kronael/ship` | /ship |
| `agent-browser` | `bun install -g agent-browser` | /browse |
| `codex` | `bun install -g @openai/codex` | /codex /oracle |
| `pi` | `bun install -g @mariozechner/pi-coding-agent` | /pi |
| `pyright` | `bun install -g pyright` | /py /ts /tsx |
| `typescript-language-server` | `bun install -g typescript typescript-language-server` | /ts /tsx |
| `pre-commit` | `uv tool install pre-commit` | all (hooks) |
| `ast-grep` | `uv tool install ast-grep-cli && rm -f ~/.local/bin/sg` | /astgrep |

**Security audit** — ask separately (large, optional):

| Tool | Command | Skills |
|------|---------|--------|
| `bandit` | `uv tool install bandit` | /hacker-eval |
| `pip-audit` | `uv tool install pip-audit` | /hacker-eval |
| `semgrep` | `uv tool install semgrep` | /hacker-eval |
| `govulncheck` | `go install golang.org/x/vuln/cmd/govulncheck@latest` | /hacker-eval |
| `trufflehog` | `go install github.com/trufflesecurity/trufflehog/v3@latest` | /hacker-eval |
| `gitleaks` | download from github.com/gitleaks/gitleaks releases | /hacker-eval |

**Video rendering** — ask separately (heavy, rarely needed):

| Tool | Command | Skills |
|------|---------|--------|
| `faster-whisper` | library, no CLI — the render script pulls it via `uv run --with faster-whisper`; NEVER `uv tool install` it (no entrypoints) | /create (video render) |

## CLI tools (step 7)

Install the repo's standalone CLI tools so their `~/.local/bin` binaries track
the repo (a stale binary is the failure this prevents). ONLY when the tool's
source dir exists at the source root (clone/manual path; the Codex marketplace
snapshot carries them too). A plugin-only snapshot omits them — say so and
point to `cd <tool> && make install` from a clone. Each Makefile is idempotent,
so ALWAYS (re)install to refresh a stale binary. NEVER fail the whole install if
one toolchain is missing — report that tool skipped and continue.

| Tool | Command | Notes |
|------|---------|-------|
| `rig` | `cd rig && make install` | git helpers: rig + rip/rco/rir/rim/riq |
| `udfix` | `cd udfix && make install` | needs a Go toolchain |
| `clp` | `cd clp && make install` | sourceable bash; prints how to source it |
| `dockbox` | `cd dockbox && make install` | builds a Docker image — needs Docker; ask separately |

## Removed kronael skills to prune (step 2)

AFTER backup (step 1), delete these dirs from `~/.claude/skills/` if present —
consolidated into the `create/` router or renamed. Orphans keep preloading
their descriptions, defeating the router:

`create-architecture-diagram`, `create-ascii-art`, `create-ascii-video`,
`create-claude-design`, `create-code-presentation`, `create-design-md`,
`create-excalidraw`, `create-humanizer`, `create-manim-video`, `create-p5js`,
`create-popular-web-designs`, `create-pretext`, `create-sketch`,
`create-video-render`, `create-video-script`,
`sub` (renamed to `dispatch` in v0.3.23 — the model skills haiku/sonnet/opus/
fable were briefly removed in v0.3.22 then restored; both land together),
`software-engineering` (folded into `software/code.md`; language skills point
at it in-body), `gh-review`, `gh-fix` (folded into the `review` router —
`/review give gh` and `/review take gh`), `con`, `cont` (renamed to
`continue`), `merge-trivial` (renamed to `merge`, which now also covers rebase
+ cherry-pick), `docs-audit` (removed in the skills cleanup pass — deliberately
dropped, not folded).

NEVER delete `create-eval` (still bundled), `codex` or `oracle` (both bundled —
`codex` is canonical, `oracle` its alias; the v0.3.26 codex→oracle rename was
reverted), or any dir not on this list — user-added skills stay.
