---
name: pi
description: Ask the pi coding-agent CLI for a second opinion. NOT for routine lookups (use grep/read/recall-memories). NOT a Claude Agent and NOT codex — this is badlogic's `pi` CLI (a distinct model, complements /codex).
when_to_use: "pi, ask pi, second opinion from pi, tricky algorithm, unfamiliar library, sanity check, architecture decision, disagreement after reasoning, cross-check codex. NOT for routine lookups"
user-invocable: true
---

# Pi

Runs `pi -p` as a subprocess for a one-shot second opinion. `pi` is the Pi
coding agent (badlogic/earendil, `pi.dev`) — same shape as codex: one binary,
agent loop, its own tools (read/bash/edit/write). Methodology + citations:
`docs/pi/research-pi.md`.

Why alongside `/codex`: pi answers from a **different model** than this Claude
harness (its default here is `codex-serve/gpt-5.2-codex`; configurable to
Gemini/GPT/Claude), so it's a real second opinion. Use it to cross-check codex
or when you want a non-Claude view. NEVER use a raw `Agent(...)` for a second
opinion — use this skill or `/codex`.

## Invoke

pi runs in **YOLO / full-access mode by default** — no permission prompts, full
filesystem + shell. That's the codex `--dangerously-bypass-approvals-and-sandbox`
behavior built in, so NO sandbox flag is needed. The container is the perimeter.

```bash
# There is NO reliable static auth check (no `login status`; a
# ~/.pi/agent/settings.json can exist with defaultProvider but NO credentials —
# that alone does NOT mean logged in). The actual `-p` call IS the check:
# a `404 page not found` body or non-zero exit = not authed / endpoint down.

# --no-session: don't persist a rollout file (a batch loop fills the disk otherwise)
# --thinking high: match codex's "newest at high effort"
# </dev/null is REQUIRED — without it pi blocks waiting for more stdin
pi -p --no-session --thinking high "Goal: <X>. Find the flaw in..." </dev/null
```

ALWAYS treat a non-zero exit OR a body like `404 page not found` as
**pi unavailable** (its subscription serve endpoint can be down/expired) — say
so and continue WITHOUT crashing the turn. NEVER let a pi failure abort your work.

NEVER `pkill -f pi` to clean up — `pi` is a 2-char substring that matches
unrelated processes (and your own shell). Kill by numeric PID
(`ps -eo pid,args | grep -F 'pi -p' | grep -v grep`).

## Model — newest available, high effort

- Discover with `pi --list-models`; it prints the providers/models the current
  auth can reach (here: `claude-serve` haiku/sonnet, `codex-serve gpt-5.2-codex`).
- ALWAYS inherit pi's configured default (`defaultProvider`/`defaultModel` in
  `~/.pi/agent/settings.json`) unless you have a reason to switch — it pins the
  strongest configured model. Add `--thinking high` (or `xhigh`) for max reasoning.
- To force a specific tier: `--model sonnet:high`, or `--provider openai --model
  <id>`. `--model <provider>/<id>` and `--model <id>:<effort>` shorthands work.
- pi's OUT-OF-BOX default (fresh install, no login) is `google/gemini-2.5-flash`,
  which needs `GEMINI_API_KEY`. For a second opinion, a non-Claude model is a
  feature — pick the strongest one available.

## Auth — no status command

pi has NO non-interactive `login status` (unlike codex). Two working paths:

- **Subscription login** — cached in `~/.pi/agent/settings.json` (Claude Pro /
  ChatGPT Plus / Copilot via `codex-serve`/`claude-serve`). Presence of that
  file = probably logged in; confirm only via an actual `-p` call.
- **BYOK env var** — `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`,
  etc., or `--api-key <key>` per run.

If neither is present, tell the user to `export <PROVIDER>_API_KEY` or run `pi`
once and `/login`. ALWAYS report "pi isn't configured" and continue. NEVER crash.

## Rules

pi is a peer agent — it has tools and sees the repo. Give it the goal and entry
points, then let it explore. NEVER pre-chew the answer or walk it through steps.
For open-ended tasks give a high-level goal and let pi research it.

### Adversarial framing

Like any model, pi is sycophantic — confirming questions get confirming answers.

- ALWAYS attack your own conclusion: "Find the flaw in X", "Why would this break?"
- NEVER ask "is X correct?" / "does this look right?" — primes a yes.

### Prompt contents

- ALWAYS state the goal in one line ("Goal: <X>").
- Targeted questions: hand it entry points (file paths, symbols, error output).
- NEVER paste your reasoning chain or conclusions — biases the second opinion.

To restrict what pi can touch (read-only-ish review): `--tools read,grep,find,ls`
or `--no-tools`. `-a/--approve` govern project file-trust, NOT tool gating.

ALWAYS verify pi's claim against the codebase before acting. Discard with a
one-line reason if wrong; cite when acting.

## Output

`pi -p "<prompt>"` writes the final text to stdout. `--mode json` emits a
JSON-lines event stream; `--mode rpc` is for IDE embedding (not for one-shots).
Treat the answer as advisory. Cite when acting on it.
