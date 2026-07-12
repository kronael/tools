---
name: install
description: Install (or update) the Kronael toolkit into ~/.claude/ and bridge it into Codex. Copies skills, agents, hook scripts; merges Claude hook wiring; installs Codex hook wiring; installs the wisdom skill body as ~/.claude/CLAUDE.md; offers the standalone CLI tools (rig, udfix, clp, dockbox). First-time installs get an explained questionnaire. USE when the user says "install kronael", "install kronael tools", "install" (in this repo), or runs /kronael:install.
---

# Install Kronael toolkit

Deploy the bundle into `~/.claude/` so skills, agents, and hook scripts live
in the user's persistent config and work bare (no `kronael:` prefix). When
running from Codex, also bridge the installed skills and hook wiring into
Codex's global guidance, `~/.agents/skills`, and `~/.codex/hooks.json` surfaces.

## Source location

Source root: `CLAUDE_PLUGIN_ROOT` if set and assets exist there; else CWD.
Stop if neither has assets — report which path to use.

Check `~/.claude/plugins/installed_plugins.json` for `kronael@*`: if absent,
note that `Skill("kronael:install")` won't resolve — user must say "install" here.

ALWAYS verify these exist at the source root before proceeding:
- `skills/` — bundle of skills
- `agents/` — bundle of agents
- `hooks/` — hook scripts (codex_hook.py, prompt_nudge.py, pretool_nudge.py, local.py, reclaude.py, stop.py, memory_nudge.py)
- `codex-hooks.json` — Codex lifecycle hook wiring that calls `hooks/codex_hook.py`
- `settings-recommended.json` — recommended permissions, sandbox, env, hook wiring
- `RECLAUDE.md` — re-injection template for the `reclaude` hook

If missing, you're in the wrong directory — stop and ask.

## Sync protocol

Install is a fast copy only when installed source-owned files are unchanged.
When local installed edits exist, install becomes a merge workflow.

- Manifest path: `~/.claude/kronael-install-manifest.json`.
- ALWAYS run a quiet checksum/manifest drift check before backup/copy.
- NEVER run recursive diffs on the happy path.
- Per source-owned path, compare source / installed / manifest sha256, then
  **determine direction automatically**:
  - installed == manifest → source-only update: overwrite silently.
  - source == manifest → local edit: show diff, ask (sync back / overwrite / skip).
  - neither == manifest → conflict: show diff, ask; NEVER overwrite silently.
  - no manifest entry + content differs → treat as local edit: ask, don't guess.
- ALWAYS write/update the manifest after a successful copy, recording the
  installed path and the source hash just installed.
- NEVER treat a backup as permission to discard installed-side edits.
- NEVER touch installed-only files except the explicit prune list below.
- **Installed-only skills are NOT auto-captured into source.** An installed skill
  with no source counterpart may be an org/local skill (arizuko/dashd/ant/routd,
  local paths, secrets) that must NOT enter public source. Reverse-sync
  (installed → repo) ONLY on the user's explicit ask: flag each installed-only
  skill, exclude or genericize the org-specific ones, add only the generic ones
  the user opts into.

## Plan & consent

Detect first-time vs update: a **new install** = neither `~/.claude/CLAUDE.md`
nor `~/.claude/skills/` exists yet. An **update** = either already exists.

- **New install**: BEFORE any copy, explain what install does in 2-3 lines,
  then present a questionnaire so the user opts into each group. On Claude use
  AskUserQuestion (multiSelect); on Codex list numbered options and ask the
  user to reply with their picks. Groups:
  - **Bundle** (skills + agents + hooks + wisdom file → `~/.claude/`) — the
    core; default on. Nothing else is useful without it.
  - **Settings restrictions** — permissions, sandbox, env (step 4).
  - **External tools** — ship, agent-browser, codex, pi, pyright, LSP servers,
    pre-commit (step 6 core batch).
  - **CLI tools** — rig, udfix, clp (step 7).
  - **dockbox** — dockerized Claude Code sandbox; needs Docker (step 7).
  - **Heavy/optional** — security-audit + video tools (step 6 separate asks).
  Run ONLY the opted-in groups. ALWAYS still back up (step 1) before any write.
- **Update**: skip the first-time questionnaire, but ALWAYS still run steps 6–7
  — NEVER silently skip tools or dockbox on a re-run (a stale binary or an
  un-offered dep is the failure this prevents). Detect external tools + install
  missing core, ask once for the heavy security/video batch, offer CLI-tools +
  dockbox (re)install. Settings still confirm before applying.

## Steps

0. **Preflight**. Run `make skills-frontmatter` (then `-fix` if it reports files)
   before copying skills. Then run the sync-protocol drift check for
   `~/.claude/{skills,agents,hooks,CLAUDE.md,RECLAUDE.md}`, the Kronael-managed
   block in `~/.codex/AGENTS.md`, and `~/.codex/hooks.json`.

1. **Backup**. ALWAYS copy current
   `~/.claude/{skills,agents,hooks,CLAUDE.md,settings.json,RECLAUDE.md}` and
   `~/.codex/{AGENTS.md,AGENTS.override.md,config.toml,hooks.json}` to
   `~/.claude/backup/<timestamp>/`
   before overwriting.

2. **Copy assets** (replace strategy):
   - `skills/*` → `~/.claude/skills/` **but skip `skills/global/`** — its body is the wisdom file, deployed in step 3. Copying it as a skill would duplicate the always-loaded content.
   - `agents/*` → `~/.claude/agents/`
   - `hooks/*.py`, `hooks/*.sh`, `hooks/lib/` → `~/.claude/hooks/`
   - `output-styles/*` → `~/.claude/output-styles/`
   - Merge the block between `<!-- kronael:start -->` and
     `<!-- kronael:end -->` from `codex/AGENTS.md` into
     `~/.codex/AGENTS.md` when running from Codex. Replace only an existing
     Kronael block; otherwise append it. NEVER overwrite content outside the
     markers. This makes Codex load Claude guidance in addition to AGENTS
     guidance and applies the selected terse response policy.
   - **Prune renamed hooks**: delete `~/.claude/hooks/nudge.py` and `~/.claude/hooks/extnudge.py` if present (renamed to `prompt_nudge.py` / `pretool_nudge.py`). Backup first per step 1.
   - **Prune removed kronael skills**: AFTER backup (step 1), delete these dirs from `~/.claude/skills/` if present — consolidated into the `create/` router or renamed (`create-humanizer` → `humanize`). Orphans keep preloading their descriptions, defeating the router:
     `create-architecture-diagram`, `create-ascii-art`, `create-ascii-video`, `create-claude-design`, `create-code-presentation`, `create-design-md`, `create-excalidraw`, `create-humanizer`, `create-manim-video`, `create-p5js`, `create-popular-web-designs`, `create-pretext`, `create-sketch`, `create-video-render`, `create-video-script`,
     `sub` (renamed to `dispatch` in v0.3.23 — the individual model skills haiku/sonnet/opus/fable were also briefly removed in v0.3.22 then restored; both changes land together here),
     `software-engineering` (folded into the `software` router as `software/code.md`; language skills point at it in-body),
     `gh-review`, `gh-fix` (folded into the `review` router — `/review give gh` and `/review take gh`),
     `con`, `cont` (renamed to `continue`).
     NEVER delete `create-eval` (still bundled), `codex` or `oracle` (both
     bundled again — `codex` is the canonical second-opinion skill, `oracle`
     is its alias; the v0.3.26 codex→oracle rename was reverted), or any
     skill dir not on this list — user-added skills stay.
   - `RECLAUDE.md` → `~/.claude/RECLAUDE.md`
   - NEVER delete user-added files not in source.

3. **Install wisdom**. The `global` skill body (file: `skills/global/SKILL.md`, minus YAML frontmatter) becomes `~/.claude/CLAUDE.md`. Single destination — NEVER also write to `~/.claude/skills/global/`. If `~/.claude/CLAUDE.md` already has content, show diff and ask before overwriting. Extract any local paths / repo names / secrets references into `~/.claude/LOCAL.md` (auto-injected by `local.py`).

4. **Merge settings**. Read `settings-recommended.json` and merge into `~/.claude/settings.json`:
   - **Hooks block** (UserPromptSubmit, PreToolUse, PostToolUse, Stop, PreCompact) — replace existing matching events with the recommended wiring (paths use `~/.claude/hooks/*.py`).
   - **`cleanupPeriodDays`** — ALWAYS apply the recommended value, never ask. The 30-day default silently deletes session transcripts at startup; the toolkit keeps all history. If the user's value is lower, raise it to the recommended one; never lower it.
   - **`outputStyle`** — set live `~/.claude/settings.json` `outputStyle` to the recommended value (`80% caveman`). Without this key the style file in `output-styles/` is defined but never activated (the style silently does nothing).
   - **Permissions, sandbox, env** — show diff, ask which restrictions to apply.
   - NEVER overwrite `~/.claude/settings.local.json`.

5. **Install Codex bridge**. When running from Codex (or the user asks for Codex
   support), install every bridge:
   - Global wisdom: if neither `~/.codex/AGENTS.override.md` nor
     `~/.codex/AGENTS.md` exists, symlink `~/.codex/AGENTS.md` →
     `~/.claude/CLAUDE.md` (leave it if already resolved). Any other existing
     global Codex guidance is a conflict — show and ask. NEVER rely on project
     fallback names for global guidance.
   - `~/.codex/config.toml`: ensure top-level `project_doc_fallback_filenames`
     contains `CLAUDE.md` (before the first `[table]`; NEVER under `[tui]` etc.).
   - Symlink `~/.agents/skills` → `~/.claude/skills` (per-skill symlinks only if
     it is already a directory). If pi is installed, symlink
     `~/.pi/agent/AGENTS.md` → `~/.claude/CLAUDE.md` (skip if a real file exists).
   - Copy `codex-hooks.json` → `~/.codex/hooks.json` (after the drift preflight).
     It wires Codex's lifecycle events into `~/.claude/hooks/codex_hook.py`, which
     normalizes Codex payloads before delegating to the Kronael hooks (and drops
     context-only output for Codex `PreCompact`, which only accepts block decisions).
   - Tell the user to open `/hooks` in the next Codex TUI session and trust the
     changed hooks. One-shot verify only: `--dangerously-bypass-hook-trust`.

6. **External tools** — run `which <tool>` to detect; skip if present and recent.

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

7. **CLI tools** — install the repo's standalone CLI tools so their binaries
   in `~/.local/bin` track the repo (a stale binary is the failure this step
   prevents). ONLY possible when the tool's source dir exists at the source
   root (the cloned/manual path; the Codex marketplace snapshot has them too).
   A plugin-only snapshot omits them — then say so and point to
   `cd <tool> && make install` from a clone. For each opted-in tool run its
   Makefile — idempotent, so ALWAYS (re)install to refresh a stale binary:

   | Tool | Command | Notes |
   |------|---------|-------|
   | `rig` | `cd rig && make install` | git helpers: rig + rip/rco/rir/rim/riq |
   | `udfix` | `cd udfix && make install` | needs a Go toolchain |
   | `clp` | `cd clp && make install` | sourceable bash; prints how to source it |
   | `dockbox` | `cd dockbox && make install` | builds a Docker image — needs Docker; ask separately |

   NEVER fail the whole install if one tool's toolchain is missing — report
   that tool as skipped and continue.

8. **Report**: summary — fast drift result, X skills, Y agents, Z hooks,
   RECLAUDE.md, **pruned dirs/hooks** (name every stale skill/hook removed per
   step 2 — renamed, consolidated, or dead; say "pruned: none" when nothing
   matched so the user knows removal ran), Claude settings merged, Codex global
   guidance + skills + hooks bridge
   installed/skipped, W external tools, CLI tools installed/skipped. Claude skills are invocable
   bare (`/commit`, `/ship`, `/refine`, ...). Codex bridged skills are
   invocable as `@commit`, `@ship`, `@refine`, ...; remind the user that hook
   commands require `/hooks` trust after install/update.

## Rules

- ALWAYS backup before overwriting
- NEVER delete files in `~/.claude/` not in source (org overlays, user customizations live there)
- NEVER touch `~/.claude/settings.local.json`, `~/.claude/LOCAL.md`, `~/.claude/CLAUDE.local.md`
- ALWAYS replace skills/hooks with current versions on name conflict only after drift preflight clears installed-side edits
- NEVER sync `skipDangerousModePermissionPrompt` from user back into the template
- NEVER copy Kronael skills into `~/.codex/skills`; Codex uses
  `~/.agents/skills`
- NEVER duplicate global wisdom into Codex — symlink it, or surface a conflict

## Update flow

Re-run `/kronael:install` (or "say install" in this repo) after `claude /plugin update`. Same steps; backup directory grows.
