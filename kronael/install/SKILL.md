---
name: install
description: Install (or update) the Kronael toolkit into ~/.claude/ and bridge it into Codex. Copies skills, agents, hook scripts; merges Claude hook wiring; installs Codex hook wiring; installs the wisdom skill body as ~/.claude/CLAUDE.md; offers the standalone CLI tools (rig, udfix, clp, dockbox). First-time installs get an explained questionnaire. USE when the user says "install kronael", "install kronael tools", "install" (in this repo), or runs /kronael:install.
---

# Install Kronael toolkit

Deploy the bundle into `~/.claude/` so skills, agents, and hook scripts live
in the user's persistent config and work bare (no `kronael:` prefix). When
running from Codex, also bridge the installed skills and hook wiring into
Codex's `~/.agents/skills` and `~/.codex/hooks.json` surfaces.

## Source location

- **Plugin path**: `${CLAUDE_PLUGIN_ROOT}`.
- **Manual path**: current working directory (user opened Claude Code at the repo root and said "install").

ALWAYS verify these exist at the source root before proceeding:
- `skills/` — bundle of skills
- `agents/` — bundle of agents
- `hooks/` — hook scripts (codex_hook.py, prompt_nudge.py, pretool_nudge.py, local.py, reclaude.py, stop.py)
- `codex-hooks.json` — Codex lifecycle hook wiring that calls `hooks/codex_hook.py`
- `settings-recommended.json` — recommended permissions, sandbox, env, hook wiring
- `RECLAUDE.md` — re-injection template for the `reclaude` hook

If missing, you're in the wrong directory — stop and ask.

## Sync protocol

Install is a fast copy only when installed source-owned files are unchanged.
When local installed edits exist, install becomes a merge workflow.

- ALWAYS run a quiet checksum/`cmp` drift check before backup/copy.
- NEVER run recursive diffs on the happy path.
- **Determine direction automatically** for every differing file — compare
  content (`cmp`) AND mtime (installed vs source):
  - **source-newer** (installed mtime ≤ source, content differs): this is a
    normal update where the repo advanced. Overwrite silently — do NOT ask.
    A uniform installed mtime across the differing set (one prior-install
    timestamp) confirms no hand-edits.
  - **installed-newer** (installed mtime > source): a real local edit may
    exist. ONLY here show a diff summary and ask: sync back to repo,
    overwrite from source, or skip that path.
- NEVER treat a backup as permission to discard installed-side edits.
- NEVER touch installed-only files except the explicit prune list below.

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
  - **External tools** — ship, agent-browser, codex, pyright, LSP servers,
    pre-commit (step 6 core batch).
  - **CLI tools** — rig, udfix, clp (step 7).
  - **dockbox** — dockerized Claude Code sandbox; needs Docker (step 7).
  - **Heavy/optional** — security-audit + video tools (step 6 separate asks).
  Run ONLY the opted-in groups. ALWAYS still back up (step 1) before any write.
- **Update**: skip the questionnaire. Proceed with the per-step asks the steps
  already define (settings and tools still confirm before installing). NEVER
  replay the full questionnaire on every re-run.

## Steps

0. **Skill lint preflight**. ALWAYS run `make skills-frontmatter` when available.
   If it reports files, run `make skills-frontmatter-fix` before copying skills.

0. **Fast drift preflight**. Follow the sync protocol for
   `~/.claude/{skills,agents,hooks,CLAUDE.md,RECLAUDE.md}` and
   `~/.codex/hooks.json` before backup/copy.

1. **Backup**. ALWAYS copy current
   `~/.claude/{skills,agents,hooks,CLAUDE.md,settings.json,RECLAUDE.md}` and
   `~/.codex/{config.toml,hooks.json}` to `~/.claude/backup/<timestamp>/`
   before overwriting.

2. **Copy assets** (replace strategy):
   - `skills/*` → `~/.claude/skills/` **but skip `skills/global/`** — its body is the wisdom file, deployed in step 3. Copying it as a skill would duplicate the always-loaded content.
   - `agents/*` → `~/.claude/agents/`
   - `hooks/*.py`, `hooks/*.sh`, `hooks/lib/` → `~/.claude/hooks/`
   - **Prune renamed hooks**: delete `~/.claude/hooks/nudge.py` and `~/.claude/hooks/extnudge.py` if present (renamed to `prompt_nudge.py` / `pretool_nudge.py`). Backup first per step 1.
   - **Prune removed kronael skills**: AFTER backup (step 1), delete these dirs from `~/.claude/skills/` if present — consolidated into the `create/` router or renamed (`create-humanizer` → `humanize`). Orphans keep preloading their descriptions, defeating the router:
     `create-architecture-diagram`, `create-ascii-art`, `create-ascii-video`, `create-claude-design`, `create-design-md`, `create-excalidraw`, `create-humanizer`, `create-manim-video`, `create-p5js`, `create-popular-web-designs`, `create-pretext`, `create-sketch`, `create-video-render`, `create-video-script`,
     `sub` (renamed to `dispatch` in v0.3.23 — the individual model skills haiku/sonnet/opus/fable were also briefly removed in v0.3.22 then restored; both changes land together here).
     NEVER delete `create-eval` (still bundled) or any skill dir not on this list — user-added skills stay.
   - `RECLAUDE.md` → `~/.claude/RECLAUDE.md`
   - NEVER delete user-added files not in source.

3. **Install wisdom**. The `global` skill body (file: `skills/global/SKILL.md`, minus YAML frontmatter) becomes `~/.claude/CLAUDE.md`. Single destination — NEVER also write to `~/.claude/skills/global/`. If `~/.claude/CLAUDE.md` already has content, show diff and ask before overwriting. Extract any local paths / repo names / secrets references into `~/.claude/LOCAL.md` (auto-injected by `local.py`).

4. **Merge settings**. Read `settings-recommended.json` and merge into `~/.claude/settings.json`:
   - **Hooks block** (UserPromptSubmit, PreToolUse, PostToolUse, Stop, PreCompact) — replace existing matching events with the recommended wiring (paths use `~/.claude/hooks/*.py`).
   - **Permissions, sandbox, env** — show diff, ask which restrictions to apply.
   - NEVER overwrite `~/.claude/settings.local.json`.

5. **Install Codex bridge**. When running from Codex, or when the user asks
   for Codex support, install both bridges:
   - Ensure `project_doc_fallback_filenames` in `~/.codex/config.toml`
     contains `CLAUDE.md`.
   - Ensure `~/.agents/skills` points at `~/.claude/skills` (symlink when
     possible; per-skill symlinks only when `~/.agents/skills` is already a
     directory).
   - Copy `codex-hooks.json` → `~/.codex/hooks.json` after the drift
     preflight. This file wires Codex `UserPromptSubmit`, `PreToolUse`,
     `PostToolUse`, `Stop`, and `PreCompact` into
     `~/.claude/hooks/codex_hook.py`, which normalizes Codex payloads before
     delegating to the installed Kronael hook scripts. The wrapper also
     suppresses Claude-style context-only output for Codex `PreCompact`, where
     Codex only accepts block decisions.
   - Tell the user to open `/hooks` in the next Codex TUI session and trust
     the changed hooks. For one-shot verification only, use
     `--dangerously-bypass-hook-trust`; do not make that the normal path.

6. **External tools** — run `which <tool>` to detect; skip if present and recent.

   **Core** — ask once, install as a batch:
   | Tool | Command | Skills |
   |------|---------|--------|
   | `ship` | `uv tool install git+https://github.com/kronael/ship` | /ship |
   | `agent-browser` | `bun install -g agent-browser` | /browse |
   | `codex` | `bun install -g @openai/codex` | /codex |
   | `pyright` | `bun install -g pyright` | /py /ts /tsx |
   | `typescript-language-server` | `bun install -g typescript typescript-language-server` | /ts /tsx |
   | `pre-commit` | `uv tool install pre-commit` | all (hooks) |

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
   | `faster-whisper` | `uv tool install faster-whisper` | /create (video render) |

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
   RECLAUDE.md, Claude settings merged, Codex bridge installed/skipped,
   W external tools, CLI tools installed/skipped. `/commit`, `/ship`,
   `/refine` etc. invocable bare. In Codex, remind the user that hook
   commands require `/hooks` trust after install/update.

## Rules

- ALWAYS backup before overwriting
- NEVER delete files in `~/.claude/` not in source (org overlays, user customizations live there)
- NEVER touch `~/.claude/settings.local.json`, `~/.claude/LOCAL.md`, `~/.claude/CLAUDE.local.md`
- ALWAYS replace skills/hooks with current versions on name conflict only after drift preflight clears installed-side edits
- NEVER sync `skipDangerousModePermissionPrompt` from user back into the template
- NEVER copy Kronael skills into `~/.codex/skills`; Codex uses
  `~/.agents/skills`

## Update flow

Re-run `/kronael:install` (or "say install" in this repo) after `claude /plugin update`. Same steps; backup directory grows.
