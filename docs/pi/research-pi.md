# Research: the "pi" coding-agent CLI (for a codex-style `/pi` skill)

Goal: identify the `pi` / "pi agent" / π CLI the user means, and document it
precisely enough to wrap it like our `codex` skill (one-shot, non-interactive,
text on stdout).

## What pi is (+confidence)

**Confidence: high (~90%).** "pi" is the **Pi Coding Agent** by Mario Zechner
(GitHub handle `badlogic`) — a minimal, extensible, terminal-first AI coding
agent. Canonical monorepo: `github.com/badlogic/pi-mono`, package
`packages/coding-agent`; public mirror `github.com/earendil-works/pi`; homepage
`pi.dev` ([repo README][readme], [earendil mirror][mirror], [pi.dev][home]).
It ships four built-in tools (read, write, edit, bash) plus a ~300-word system
prompt, and self-extends at runtime via TypeScript extensions, skills, prompt
templates and themes ([README][readme], [LLMReference][llmref]). It is BYOK and
multi-provider (Anthropic, OpenAI, Google, xAI, Groq, plus Claude Pro / ChatGPT
Plus / Copilot subscriptions) ([README][readme]). It is a very close structural
analog of the OpenAI `codex` CLI and Claude Code — same "one binary, agent loop,
tools" shape ([Pinggy roundup][pinggy]).

**Ranked alternatives (rejected):**
1. **Inflection AI's "Pi"** — a consumer *emotional-support chatbot*
   ("personal intelligence"), web/iOS/WhatsApp only, explicitly **cannot code**
   and has **no CLI**; most of the team was absorbed by Microsoft in 2024.
   Definitely not it ([IEEE Spectrum][ieee], [Fortune][fortune], [pi.ai][piai]).
2. **`oh-my-pi`** (`github.com/can1357/oh-my-pi`) — a heavier fork of the same Pi
   agent (LSP, browser, subagents). A variant of the same tool, not a different
   product ([oh-my-pi][ohmypi]).
3. **`pi_agent_rust`** (dicklesworthstone) — a Rust reimplementation of the same
   agent. Same family ([agentskills][piarust]).

All serious candidates converge on the **same** Pi coding agent. Only Inflection
is a true false-positive, and it fails on every axis (no CLI, no code, cloud
chatbot). I'm confident the user means the badlogic/earendil Pi.

## Install

```bash
# curl installer (recommended)
curl -fsSL https://pi.dev/install.sh | sh
# or npm (global)
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```
Node/npm or the curl script; no cloud account required ([README][readme],
[pi.dev usage][usage]). Mirror package `@mariozechner/pi-coding-agent` exists on
npm ([npm][npm]). Binary name after install: `pi`.

## Non-interactive invocation (the `codex exec` analog)

Codex analog: `codex exec -s danger-full-access "<prompt>" </dev/null`.
Pi equivalent ([usage][usage], [README][readme]):

```bash
pi -p "Your prompt here"                 # print mode: run, emit text, exit
cat file.md | pi -p "Summarize this"     # prompt via stdin pipe (merged in)
pi --mode json "Your prompt"             # JSON-lines event stream (structured)
pi --mode rpc                            # headless JSON-RPC over stdin/stdout
```

- **Prompt input:** positional arg, piped stdin, or `@file.md` file references
  ([usage][usage]).
- **`-p` / print mode** is the direct one-shot analog: single prompt in, text
  answer on stdout, process exits ([usage][usage]).
- **`--mode json`** emits every event as JSON lines if we want structured output
  instead of plain text ([usage][usage], [rpc docs][rpc]).
- **`--mode rpc`** is for long-lived IDE embedding — not needed for a one-shot
  wrapper ([rpc docs][rpc]).

## Auth

BYOK via env var or interactive login ([README][readme], [usage][usage]):

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # then: pi -p "..."
pi --api-key <key> ...                # per-run key flag
pi        # then /login  → pick provider (Claude Pro / ChatGPT Plus / Copilot)
```
- Only `ANTHROPIC_API_KEY` is named explicitly in the docs; other providers use
  the standard `<PROVIDER>_API_KEY` pattern or `--api-key` / `/login`
  ([README][readme]).
- Config/state: global `~/.pi/agent/settings.json`, project `.pi/settings.json`,
  context files `AGENTS.md` / `CLAUDE.md`, custom prompt `.pi/SYSTEM.md`
  ([usage][usage]).
- **No documented non-interactive `login status` command** (unlike
  `codex login status`). `/login` and `/logout` are interactive-only
  ([usage][usage]). See Blockers.

## Model / effort flags

```bash
pi --provider openai --model gpt-4o "..."   # provider + model
pi --model openai/gpt-4o "..."              # provider/id shorthand
pi --model sonnet:high "..."                # model:effort shorthand
pi --thinking high "..."                    # off|minimal|low|medium|high|xhigh
pi --list-models [search]                   # discover model ids
```
Reasoning levels: `off, minimal, low, medium, high, xhigh` ([usage][usage]).
To mirror codex's "newest model at high effort," pick the top model from
`--list-models` and pass `--thinking high` (or `--model <id>:high`).

## Blockers for a codex-style wrapper

**Verdict: essentially none — pi is a *better* fit than codex.** Key finding:
pi runs **"YOLO mode by default"** — "No permission prompts for file operations
or commands... Full filesystem access. Can execute any command with your user
privileges" ([author blog][blog]). So the codex `-s danger-full-access` sandbox
override is **built-in and needs no flag**; `pi -p "..."` already auto-runs
bash/edit/write non-interactively ([README][readme], [blog][blog]). It is
open-source, local, no paid-cloud lock-in — it passes the kronael "local only"
bar (BYOK key, same as codex). Minor caveats, none blocking:

1. **No non-interactive auth-probe command.** Can't replicate `codex login
   status` directly. Workaround: check that `ANTHROPIC_API_KEY` (or chosen
   provider key) is set, or a cached credential exists under `~/.pi/`, before
   invoking; optionally a trivial `pi -p "ok"` smoke probe.
2. **Runs with full host privileges by default** — fine (desirable) inside a
   container, but the wrapper should note it, mirroring our codex danger-mode
   caveat. To *restrict* instead, `--tools read,grep,find,ls` or
   `--exclude-tools` narrows capabilities ([README][readme]).
3. **Node/npm (or curl) dependency** to install — acceptable, same class as
   codex.
4. `--approve`/`-a` and `--no-approve`/`-na` govern *project-local file trust*
   (extensions/settings), **not** tool-execution gating — don't confuse them
   with a sandbox flag ([usage][usage]).

## Proposed `/pi` skill sketch

Mirror the `codex` skill shape:

```bash
# one-shot second opinion, danger-mode is the default (no flag needed)
pi -p "<adversarial second-opinion prompt>" </dev/null
# pin newest model + high effort, e.g.:
pi --model <newest-from-list-models>:high -p "<prompt>" </dev/null
```
- **Auth check:** verify `ANTHROPIC_API_KEY` (or configured provider key) is
  present; if not, tell the user to `export …_API_KEY` or run `pi` + `/login`
  once. (No `login status` command to shell out to.)
- **Model/effort:** default to the top-ranked model from `--list-models` at
  `--thinking high` (or `xhigh`) to match codex's "newest at high effort."
- **Prompt framing:** same adversarial "find the flaw / second opinion" framing
  as the codex skill; pass via arg or stdin.
- **Output:** plain text by default (`-p`); add `--mode json` only if the skill
  needs to parse structured events.
- **Isolation:** already YOLO — safe to run inside the tool container; document
  that it has full host access exactly like the codex danger flag.

[home]: https://pi.dev/
[usage]: https://pi.dev/docs/latest/usage
[readme]: https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md
[mirror]: https://github.com/earendil-works/pi
[rpc]: https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md
[npm]: https://www.npmjs.com/package/@mariozechner/pi-coding-agent
[blog]: https://mariozechner.at/posts/2025-11-30-pi-coding-agent/
[llmref]: https://www.llmreference.com/agents/pi
[pinggy]: https://pinggy.io/blog/best_open_source_cli_coding_agents/
[ohmypi]: https://github.com/can1357/oh-my-pi
[piarust]: https://agentskills.so/skills/dicklesworthstone-pi_agent_rust-interactive-shell
[ieee]: https://spectrum.ieee.org/inflection-ai-pi
[fortune]: https://fortune.com/2023/05/03/inflection-ai-deepmind-cofounder-mustafa-suleyman-pi-chatbot/
[piai]: https://pi.ai/
