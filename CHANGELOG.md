# Changelog

## [v0.3.1] — 20260525

> kronael v0.3.1 — dockbox image hardened, hooks bulletproofed, eval-loop research bundle
>
> Follow-up patch release after v0.3.0's UID-agnostic image. The dockbox base swaps to `debian:forky` (fresher packages, dodges the bookworm GPG-mirror flap); `gh` arrives via cli.github.com's signed apt repo; `yq` and `bc` are bundled; `node` comes only from nvm so `.nvmrc` works per project. `dockbox-init` now sanitizes `DOCKBOX_USER` against `/etc/passwd` injection, defaults CMD to `/bin/zsh` when none is passed, surfaces chown failures to stderr, and `DISABLE_AUTOUPDATER=1` is baked in so claude-code never tries to self-update inside the sandbox. Hooks get a real test rig: `pretool_nudge.py` swallows every exception in production and ships 59 pytest cases covering every extension mapping and payload shape. `make test` runs them from the repo root. specs/2 pivots away from a Hermes clone to a DSPy-MIPROv2-style offline eval loop (PR-only, no runtime mutation of `~/.claude/skills/`), and a new `research/` directory documents the literature behind that decision (Library Drift, MIPROv2, A-MEM, Reflexion, Anthropic skills guidance, multi-agent failure modes, eval-set construction).
>
> • dockbox image is now stable across all host UIDs, includes `yq`/`bc`/`gh`, never auto-updates claude inside the sandbox
> • `pretool_nudge.py` will never crash a tool call again — every exception is suppressed in production; pytest covers the logic
> • `make test` at the repo root runs hook tests across all subdirs
> • New `research/` hub: 8+ topic md files with sources behind the skill-eval-loop design
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `yq`, `bc` packages in the dockbox image; `gh` via github-cli signed apt repo
- `DISABLE_AUTOUPDATER=1` + `CLAUDE_CODE_DISABLE_AUTOUPDATE=1` env in image — claude-code never self-updates inside dockbox
- `dockbox-init` registers the runtime user in `/etc/passwd`, defaults CMD to `/bin/zsh`, surfaces chown failures
- `make test` at repo root + `hooks/Makefile`; 59 pytest cases for `pretool_nudge.py`
- `research/` directory with 8 topic markdown files documenting the skill auto-improvement design's sources
- `specs/2-hermes-skill-autoimprove.md` rewritten to the bundle eval loop architecture (DSPy MIPROv2 style)

### Changed
- Base image: `node:lts` → `debian:forky`. Node now comes from nvm only, symlinked to `/usr/local/bin` so build-time npm/npx work without sourcing `nvm.sh`
- All dev-tool homes moved to `/opt/dev-tools/{cargo,rustup,nvm,bun,goroot,go,sdkman,uv}/` (world-readable; portable across UIDs)
- `pretool_nudge.py` refactored into orthogonal `skill_for` / `extract_path` / `process` functions; top-level swallow-all wrapper
- `DOCKBOX_USER` is sanitized inside `dockbox-init` (only `[A-Za-z0-9_-]` allowed) — prevents `/etc/passwd` injection

### Fixed
- `dockbox-init`: `gosu` no longer errors when CMD is empty (defaults to `/bin/zsh`)
- `dockbox-init`: chown failures now print warnings to stderr instead of being silent
- `pretool_nudge.py`: hook can no longer block a tool call by raising a Traceback (top-level except in `main`)

## [v0.3.0] — 20260525

> kronael v0.3.0 — one dockbox image for every host user
>
> Until v0.2.8 the image baked a `claude` user with the build-time UID; it only worked for whoever ran `make image`, and a UID mismatch (cross-host pulls, multi-user boxes, sudo invocations) silently broke `pnpm install` and friends with EACCES. v0.3.0 drops the baked user entirely: tools move into `/opt/dev-tools/` (world-readable), the image has no `USER` directive, and `dockbox-init` registers the host invoker in `/etc/passwd` at start, chowns `$HOME` (a tmpfs at `/home/dockbox`) plus every overmount, and `gosu`-drops to the host UID/GID. One image, every host UID, no rebuild.
>
> • Image is UID-agnostic — pushable to a registry, pullable on any host, works for alice/bob/ondra without per-user builds
> • Bind mounts move from `/home/claude/*` to `/home/dockbox/*`; the runtime user gets a real `/etc/passwd` entry so `whoami`, prompts, `ls -l` all show the host username
> • Tools (cargo, nvm, bun, rustup, sdkman, go, uv, pre-commit, ship, nushell, claude-code, codex, pi, agent-browser, pyright) all install to `/opt/dev-tools/`
>
> Rebuild your image (`cd dockbox && make install`) once after upgrading. Existing containers must be removed (`dockbox rm`) — they're frozen on old paths.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Changed
- `dockbox/Dockerfile` rewritten: no `ARG UID`, no `useradd`, no `USER` directive. Tools install to `/opt/dev-tools/{cargo, rustup, nvm, bun, go, sdkman, uv}/`, `npm-global` stays at `/usr/local/share/npm-global/`. Final `chmod -R a+rwX /opt/dev-tools` makes everything usable by any runtime UID.
- `dockbox-init` (image-baked) now reads `$DOCKBOX_UID`, `$DOCKBOX_GID`, `$DOCKBOX_USER` to register `/etc/passwd` + `/etc/group` entries, top-level-chown `$HOME` and every `$DOCKBOX_EPH_PATHS` entry, then `exec gosu $UID:$GID "$@"`.
- `dockbox` script always passes `--user 0:0` and the UID/GID/USER env vars; always mounts a tmpfs `$HOME` at `/home/dockbox`; bind-mount destinations switched from `/home/claude/*` to `/home/dockbox/*`.
- `dockbox/Makefile` drops the `UID` build arg. Only `TZ` remains.
- `claude` wrapper script moved from `/home/claude/.local/bin/claude` to `/usr/local/bin/claude`; reads `$HOME` instead of hardcoded path.
- System-wide `/etc/zsh/zshrc` replaces the per-user oh-my-zsh setup — fzf bindings + `HISTFILE` only.
- `dockbox/README.md` and `CLAUDE.md` updated to describe the new model.

### Breaking
- Old containers must be removed (`dockbox rm`) before upgrading; their bind-mount paths (`/home/claude/*`) no longer exist in the new image.
- Anything outside the dockbox script that references `/home/claude/...` paths inside the container (`.dockboxrc` extras, custom skills) must move to `/home/dockbox/...`.

## [v0.2.8] — 20260525

> kronael v0.2.8 — dockbox ephemeral overmounts: one chown path for both backends
>
> v0.2.7 had two ownership paths: tmpfs used `uid=` at mount, volume used start-as-root + chown via `dockbox-init` + `gosu` drop. The split made it possible for a stale tmpfs mount or a subtle host/container UID mismatch to leave something un-`claude`-owned and break `pnpm install`. Now both backends share the same flow: container always starts as root, `dockbox-init` chowns every overmount listed in `$DOCKBOX_EPH_PATHS` to `claude:claude`, `gosu` drops, then your command runs. Backend choice is purely the mount type — tmpfs (default, RAM) or anonymous Docker volume (`-T`, disk).
>
> • pnpm/npm/bun installs inside dockbox no longer trip over root- or ondra-owned overmount paths — every path is claude-owned before user code runs
> • Same ownership logic regardless of `-T`, fewer corners to debug
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Changed
- dockbox always passes `--user 0:0` and `DOCKBOX_EPH_PATHS` to the container when any ephemeral overmounts are active; `dockbox-init` chowns then `gosu`-drops to `claude` regardless of backend
- tmpfs overmounts mount with plain `--tmpfs <path>` (no `uid=`/`gid=`) — ownership is set by the entrypoint chown, not the mount option
- `dockbox/README.md` and `CLAUDE.md` updated to describe the unified ownership flow

## [v0.2.7] — 20260523

> kronael v0.2.7 — dockbox ephemeral mounts: tmpfs by default, volume on `-T`
>
> Builds inside dockbox no longer fight with the host UID. The default backend is now a kernel `tmpfs` per ephemeral dir, mounted with `uid` set so the container's `claude` user owns it from the first byte. Pass `-T` to switch to anonymous Docker volumes — the container then starts as root, a new `dockbox-init` entrypoint chowns each volume to `claude`, and `gosu` drops privilege before your command runs. Either way you stop seeing EACCES.
>
> • Default tmpfs is RAM-backed — fast for `node_modules`/`.next`/`.turbo` (lots of small files), at the cost of RAM
> • `dockbox -T` uses disk-backed Docker volumes when you'd rather not pay RAM for artifacts
> • Image grows by `gosu` + a tiny `/usr/local/bin/dockbox-init` script
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `dockbox -T` — disk-backed anonymous Docker volume backend for ephemeral overmounts (default is tmpfs)
- Dockerfile: `gosu` package and `/usr/local/bin/dockbox-init` entrypoint that chowns paths listed in `DOCKBOX_EPH_PATHS` (when running as root) then drops to `claude`

### Changed
- dockbox ephemeral overmounts default to kernel tmpfs (`--tmpfs <path>:uid=...,gid=...,mode=0755`) — no host footprint, owned by container user at mount, gone with the container
- v0.2.6 host-stash mechanism (`/tmp/dockbox-eph/<name>/`) removed; not needed since both new backends own the mount correctly
- `dockbox/README.md` "Ephemeral builds" section: two-backend model documented, trade-offs spelled out

## [v0.2.6] — 20260522

> kronael v0.2.6 — dockbox ephemeral overmounts actually writable
>
> Default-on ephemeral overmounts in v0.2.4 used anonymous Docker volumes, which are root-owned and broke `pnpm install` (and any other writer) with EACCES inside the container. Now uses a per-container host stash under `/tmp/dockbox-eph/<name>/` bind-mounted in — owned by the host user, matching the container's `claude` UID. The stash is removed by an EXIT trap when dockbox returns. Put `/tmp` on tmpfs for RAM-backed speed.
>
> • dockbox: ephemeral `node_modules`/`.next`/`dist`/`build`/`.turbo`/`.cache` are now writable by the container user (EACCES gone)
> • Stash lives at `/tmp/dockbox-eph/<container>/` on host, cleaned up on exit
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Fixed
- dockbox: anonymous-volume overmounts (v0.2.4) were owned by root, breaking `pnpm install` and similar with EACCES — switched to host-side stash dirs at `/tmp/dockbox-eph/<container>/` bind-mounted in, owned by the host user (UID-matched with container `claude`)

### Changed
- dockbox script no longer `exec`s docker; runs in foreground so an `EXIT` trap can clean up the stash
- `dockbox/README.md` "Ephemeral builds" section updated to describe the new bind-mount mechanism

## [v0.2.5] — 20260522

> kronael v0.2.5 — clippy and rustfmt in dockbox
>
> The image now installs `clippy` and `rustfmt` alongside `rust-analyzer`. Required for any serious Rust work and for the pre-commit hooks most Rust projects use. Rebuild the image to pick this up.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- dockbox: `rustup component add clippy rustfmt` (alongside existing rust-analyzer)

## [v0.2.4] — 20260522

> kronael v0.2.4 — ephemeral builds in dockbox by default
>
> Builds inside dockbox now stay inside dockbox, with zero flags. Rust and Python uv auto-redirect to a container-only cache via `CARGO_TARGET_DIR` and `UV_PROJECT_ENVIRONMENT`. For everything else, dockbox walks the workdir and overmounts every `node_modules`, `.next`, `dist`, `build`, `.turbo`, `.cache` (recursive — monorepo workspaces handled) with anonymous Docker volumes, gone on `--rm`. Opt out per-run with `dockbox -P` or `--no-ephemeral`.
>
> • dockbox: builds never write to your host workdir, no flag required
> • `dockbox -P` — opt-out for when you need host build dirs visible
> • global: ban `gh pr create/merge`, `gh pr review --approve`, `gh release create`, `gh repo create` — same protection as `git push`
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- Dockerfile envs: `CARGO_TARGET_DIR=/home/claude/.cache/cargo-target` and `UV_PROJECT_ENVIRONMENT=/home/claude/.cache/uv-venv` — Rust and uv builds now go to container-ephemeral paths
- dockbox: default-on ephemeral overmount for `node_modules .next dist build .turbo .cache` — recursive under workdir, anonymous Docker volumes, gone on `--rm`
- `dockbox -P` / `--no-ephemeral` opt-out flag to bind-mount build dirs from host instead
- `dockbox/README.md` — "Ephemeral builds" section explaining the model + trade-offs + first-run surprise

### Changed
- global skill: ban `gh` push-to-remote (`gh pr create/merge`, `gh pr review --approve`, `gh release create`, `gh repo create`) alongside existing `git push` ban
- `settings-recommended.json` deny rules: same `gh` commands hard-blocked at the harness level, not just by skill text

## [v0.2.3] — 20260521

> kronael v0.2.3 — fresher dockbox, gh-token shortcut
>
> Dockbox image now pulls latest Node/pnpm/bun/rust/nushell on rebuild, and a new `-g` flag forwards your GH token into the container.
>
> • `dockbox -g` — forwards `GH_TOKEN`/`GITHUB_TOKEN` so `gh` works inside the container
> • dockbox rebuild: latest Node stable via nvm, plus bumped git-delta / nvm / zsh-in-docker / nushell pins
> • `tg-fetch users.py` — snapshots Telegram group participants to JSONL
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `dockbox -g` flag forwards `GH_TOKEN` and/or `GITHUB_TOKEN` from host env
- `tg-fetch/users.py` — group participants snapshot to JSONL

### Changed
- dockbox: `nvm install node` (latest stable, was pinned `22`)
- dockbox pinned-tool bumps: git-delta 0.18.2 → 0.19.2, nvm 0.40.1 → 0.40.4, zsh-in-docker 1.2.0 → 1.2.1, nushell 0.110.0 → 0.112.2
- dockbox auto-latest tools (pnpm, bun, rustup, go, gopls, uv, claude-code, codex, pi-coding-agent, agent-browser, pyright, typescript, ship, playwright, puppeteer) now rebuild against current upstream

## [v0.2.2] — 20260520

> kronael v0.2.2 — merge origin/master skill quality pass + browse rename
>
> • Merged v0.2.1 skill quality pass (21 skills refined against 10 external repos)
> • browse skill (renamed agent-browser) — no more Agent subagent type confusion
> • ops: container hardening rules (USER non-root, HEALTHCHECK, dumb-init)
> • oracle + explore skills from origin

### Added
- oracle skill: codex CLI second-opinion
- explore skill: read-only codebase exploration mode
- ops: container hardening (USER non-root, HEALTHCHECK, `--init`/dumb-init)

### Changed
- `agent-browser` skill renamed to `browse` — CLI is still `agent-browser`, skill name is not
- All changes from v0.2.1 skill quality pass (see below)

## [v0.2.1] — 20260513

### Changed
- Skill quality pass: 21 skills refined against 10 top-tier external repos (anthropics/skills, obra/superpowers, wshobson, voltagent, hesreallyhim, qdhenry, 0xfurai, alirezarezvani, lst97). Every change filtered through 2+ source corroboration + codex (oracle) critique + wisdom-skill terseness pass.
- meta (wisdom, global, learn, specs, sub): description=triggers; offload heavy content to references/; completion claims need evidence; verify subagent results; transcript reading + N≥2 rule for skill extraction; specs anti-pattern list + self-review checklist; sub never bare prompt.
- workflow (ship, refine, fin, recall-memories, distill, testing): refine triage substep; recall-memories freshness check; testing verify-failure-for-right-reason; distill trigger-form description; fin grind-harder framing.
- language (ts, sh, py, rs, tsx): ts satisfies/branded/discriminated/exhaustive/unknown/import-type; sh strict mode + mktemp+trap + NUL-safe iter; py Protocol over ABC; rs MIRI for unsafe + adapter DTOs.
- domain (service, data, ops, browse, oracle, cli, create-eval, diary): service correlation-IDs + stable error shape; data idempotent upsert + schema versioning + validate before persist; ops SLO+burn-rate alerts + runbook URL; browse wait-before-snapshot + locator priority + error screenshot; oracle targeted context + verify before adopting; create-eval programmatic assertions.
- visual: broadened triggers (components, landing pages, dashboards).
- improve: NOT-for-explain in description; expanded triggers.
- explore: `allowed-tools` frontmatter for mechanical read-only enforcement.

## [v0.2.0] — 20260512

> kronael v0.2.0 — plugin-first install, flat layout, sharper skills
>
> Install by cloning to /tmp and saying "install" — Claude reads CLAUDE.md and runs the procedure.
>
> • Plugin renamed kronael-tools → kronael — shorter install command
> • Flat layout: skills/, agents/, hooks/ at repo root (no more assistants/ nesting)
> • "Say install" elevated as primary path — git clone + cd + claude + "install"
> • skills/global/ no longer copied as a skill — body goes only to ~/.claude/CLAUDE.md
> • browse skill replaces agent-browser — clearer name, no Agent subagent confusion
> • All 35 skills carry USE/NOT descriptions for unambiguous dispatch

### Added

- `when_to_use` frontmatter field across skills — routing triggers separate from `description`
- oracle skill: codex CLI second-opinion, dual auth (host `~/.codex` mount or API key env)
- explore skill: read-only mode toggle (`/explore`), no code modifications
- `browse` skill (renamed from `agent-browser`) — browser automation via CLI, never as subagent type
- `COOKBOOK.md` — detached-HEAD workflow recipes with rig
- `skills/README.md` — skill families rationale
- `ARCHITECTURE.md` § Why hybrid — evolvability and LLM-coordinated merge rationale
- Full Codex install runbook in `AGENTS.md`
- `ops` skill: uvx single-file scripts, Python+uv Makefile/Dockerfile patterns, container hardening

### Changed

- Plugin renamed `kronael-tools` → `kronael`; trigger phrases: "install kronael" + "install kronael tools"
- Flat repo layout: bundle at root instead of `assistants/`
- `skills/global/` skipped during install copy — body goes only to `~/.claude/CLAUDE.md`
- README: `git clone /tmp/kronael + claude + "install"` as primary install path
- All 35 skill descriptions rewritten in USE/NOT format
- `release` skill: monorepo version files, distill blockquote broadcast format, first-release handling
- `INSTALL.md` dropped — `kronael/install/SKILL.md` is the single source of truth
- `description` trimmed to noun-phrase + NOT clause only — routing triggers moved to `when_to_use`
- dockbox: base image `node:lts`, `pnpm@latest`; NVM + Node 22 pre-installed; `~/.codex` mount
- settings: dropped sandbox block (per-env, not toolkit's call)

### Fixed

- `agent-browser` no longer spawnable as `Agent(subagent_type=...)` — renamed to `browse` + description clarified
- `ops` skill: dropped duplicate Makefile blocks; resolved lint/uvx contradictions

## [v0.1.2] — earlier

## [v0.1.1] — earlier

## [v0.1.0] — earlier
