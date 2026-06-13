---
name: install
description: Install (or update) the Kronael toolkit into ~/.claude/. Copies skills, agents, hook scripts; merges hook wiring and recommended settings; installs the wisdom skill body as ~/.claude/CLAUDE.md. USE when the user says "install kronael", "install kronael tools", "install" (in this repo), or runs /kronael:install. NOT for installing the CLI tools dockbox/rig/clp (use their own Makefile).
---

# Install Kronael toolkit

Deploy the bundle into `~/.claude/` so skills, agents, and hooks live in the user's persistent config and work bare (no `kronael:` prefix).

## Source location

- **Plugin path**: `${CLAUDE_PLUGIN_ROOT}`.
- **Manual path**: current working directory (user opened Claude Code at the repo root and said "install").

ALWAYS verify these exist at the source root before proceeding:
- `skills/` — bundle of skills
- `agents/` — bundle of agents
- `hooks/` — hook scripts (prompt_nudge.py, pretool_nudge.py, local.py, reclaude.py, stop.py)
- `settings-recommended.json` — recommended permissions, sandbox, env, hook wiring
- `RECLAUDE.md` — re-injection template for the `reclaude` hook

If missing, you're in the wrong directory — stop and ask.

## Steps

1. **Backup**. ALWAYS copy current `~/.claude/{skills,agents,hooks,CLAUDE.md,settings.json,RECLAUDE.md}` to `~/.claude/backup/<timestamp>/` before overwriting.

2. **Copy assets** (replace strategy):
   - `skills/*` → `~/.claude/skills/` **but skip `skills/global/`** — its body is the wisdom file, deployed in step 3. Copying it as a skill would duplicate the always-loaded content.
   - `agents/*` → `~/.claude/agents/`
   - `hooks/*.py`, `hooks/*.sh`, `hooks/lib/` → `~/.claude/hooks/`
   - **Prune renamed hooks**: delete `~/.claude/hooks/nudge.py` and `~/.claude/hooks/extnudge.py` if present (renamed to `prompt_nudge.py` / `pretool_nudge.py`). Backup first per step 1.
   - **Prune removed kronael skills**: AFTER backup (step 1), delete these dirs from `~/.claude/skills/` if present — consolidated into the `create/` router or renamed (`create-humanizer` → `humanize`). Orphans keep preloading their descriptions, defeating the router:
     `create-architecture-diagram`, `create-ascii-art`, `create-ascii-video`, `create-claude-design`, `create-design-md`, `create-excalidraw`, `create-humanizer`, `create-manim-video`, `create-p5js`, `create-popular-web-designs`, `create-pretext`, `create-sketch`, `create-video-render`, `create-video-script`.
     NEVER delete `create-eval` (still bundled) or any skill dir not on this list — user-added skills stay.
   - `RECLAUDE.md` → `~/.claude/RECLAUDE.md`
   - NEVER delete user-added files not in source.

3. **Install wisdom**. The `global` skill body (file: `skills/global/SKILL.md`, minus YAML frontmatter) becomes `~/.claude/CLAUDE.md`. Single destination — NEVER also write to `~/.claude/skills/global/`. If `~/.claude/CLAUDE.md` already has content, show diff and ask before overwriting. Extract any local paths / repo names / secrets references into `~/.claude/LOCAL.md` (auto-injected by `local.py`).

4. **Merge settings**. Read `settings-recommended.json` and merge into `~/.claude/settings.json`:
   - **Hooks block** (UserPromptSubmit, PreToolUse, PostToolUse, Stop, PreCompact) — replace existing matching events with the recommended wiring (paths use `~/.claude/hooks/*.py`).
   - **Permissions, sandbox, env** — show diff, ask which restrictions to apply.
   - NEVER overwrite `~/.claude/settings.local.json`.

5. **External tools** — run `which <tool>` to detect; skip if present and recent.

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

6. **Report**: summary — X skills, Y agents, Z hooks, RECLAUDE.md, settings merged, W external tools. `/commit`, `/ship`, `/refine` etc. invocable bare. Suggest running `/recall-memories` once to verify the recall flow.

## Rules

- ALWAYS backup before overwriting
- NEVER delete files in `~/.claude/` not in source (org overlays, user customizations live there)
- NEVER touch `~/.claude/settings.local.json`, `~/.claude/LOCAL.md`, `~/.claude/CLAUDE.local.md`
- ALWAYS replace skills/hooks with current versions on name conflict
- NEVER sync `skipDangerousModePermissionPrompt` from user back into the template

## Update flow

Re-run `/kronael:install` (or "say install" in this repo) after `claude /plugin update`. Same steps; backup directory grows.
