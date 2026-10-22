---
name: pi
description: Ask the pi coding-agent CLI for a second opinion — badlogic's `pi`, a distinct model that complements /astra. NOT for routine lookups (use grep/read/recall-memories).
when_to_use: "pi, ask pi, second opinion from pi, cross-check Astra"
user-invocable: true
---

# Pi

Runs `pi -p` as a subprocess for a one-shot second opinion. `pi` is the Pi
coding agent (badlogic/earendil, `pi.dev`) — same shape as codex: one binary,
agent loop, its own tools (read/bash/edit/write). Methodology + citations:
`docs/pi/research-pi.md` in the bundle source repo.

Why alongside `/astra`: pi answers from a **different model** than this Claude
harness (configurable to Gemini/GPT/Claude), so it's a real second opinion.
Use it to cross-check Astra or when you want a non-Claude view. NEVER use a raw
`Agent(...)` for a second opinion — use this skill or `/astra`.

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
# --thinking high: match Astra's high effort
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
  auth can reach.
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
  ChatGPT Plus / Copilot, directly or through a local proxy). Presence of that
  file = probably logged in; confirm only via an actual `-p` call.
- **BYOK env var** — `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`,
  etc., or `--api-key <key>` per run.

If neither is present, tell the user to `export <PROVIDER>_API_KEY` or run `pi`
once and `/login`. ALWAYS report "pi isn't configured" and continue. NEVER crash.

## Rules

pi is a peer agent with tools and repo access, as codex is: `astra` § Rules
owns the briefing rules — goal and entry points, adversarial framing, no
reasoning chain pasted in, every claim verified before acting — and they
apply to pi unchanged.

To restrict what pi can touch (read-only-ish review): `--tools read,grep,find,ls`
or `--no-tools`. `-a/--approve` govern project file-trust, NOT tool gating.

## Output

`pi -p "<prompt>"` writes the final text to stdout. `--mode json` emits a
JSON-lines event stream; `--mode rpc` is for IDE embedding (not for one-shots).
Treat the answer as advisory. Cite when acting on it.
