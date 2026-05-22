# Changelog

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
