---
name: codex
description: Run the codex CLI for a second opinion. NOT for routine lookups (use grep/read/recall-memories). NOT a Claude Agent — this is the OpenAI codex CLI.
when_to_use: second opinion, tricky algorithm, unfamiliar library, sanity check, architecture decision, disagreement after reasoning, ask codex, oracle
user-invocable: true
---

# Codex

Runs `codex exec` as a subprocess for a one-shot second opinion.
NEVER use a raw `Agent(...)` call when you need a second opinion — ALWAYS use this skill instead.

## Invoke

We're inside dockbox (a container); codex's inner bwrap sandbox is unnecessary and
will fail on kernels that block unprivileged user namespaces. Always pass
`-s danger-full-access` to skip it.

```bash
# Auth check first
if ! codex login status >/dev/null 2>&1 \
   && [ -z "${CODEX_API_KEY:-}${OPENAI_API_KEY:-}" ]; then
  echo "codex unavailable — no auth configured"
  exit 0
fi

# -s danger-full-access: skip bwrap (container is the real perimeter)
# </dev/null is REQUIRED — without it codex blocks waiting for additional stdin
codex exec -s danger-full-access "Goal: <X>. Find the flaw in..." </dev/null
```

## Model — ALWAYS the newest, at high effort

- ALWAYS run on `~/.codex/config.toml`'s default model — codex pins the
  newest there and auto-migrates via its model-migration notices (currently
  `model = "gpt-5.5"`, `model_reasoning_effort = "high"`).
- NEVER pass `-m` with an older model — that silently downgrades the second
  opinion. Omit `-m` to inherit the newest default.
- To force max reasoning regardless of config, add
  `-c model_reasoning_effort="high"`.
- If `codex exec` errors that the model "requires a newer version of Codex",
  the CLI is stale — `bun add -g @openai/codex@latest` (or npm), then retry.

## Auth — two paths

**Path A — host `~/.codex` mount (preferred).** dockbox bind-mounts `~/.codex` from the host.
```bash
codex login status   # "Logged in using ChatGPT" / "Logged in using API key"
```

**Path B — env var.** dockbox forwards `OPENAI_API_KEY` and `CODEX_API_KEY` from the host env.

If unavailable, tell the user "codex isn't configured" and continue without it. NEVER crash the turn.

## Rules

codex is a peer agent — has tools, sees the repo. Give it the goal and entry points,
then let it explore freely. NEVER pre-chew the answer or walk it through steps;
that defeats the point. For open-ended tasks (doc improvements, architecture
reviews, broad audits) give a high-level goal and let codex decide how to research
it — it will read files, run grep, follow imports on its own.

### Adversarial framing

codex is sycophantic — confirming questions get confirming answers. Frame as the opposing side.

- ALWAYS attack your own conclusion: "Find the flaw in X", "Why would this break?", "What did I miss?"
- NEVER ask "is X correct?" / "does this look right?" — primes a yes.

### Prompt contents

- ALWAYS state the goal in one line ("Goal: <X>").
- For targeted questions: hand it entry points (file paths, symbols, error output).
- For open-ended research: state the goal and the output format — skip the steps.
- NEVER paste session transcript, your reasoning chain, or your conclusions — biases the second opinion.

ALWAYS verify codex's claim against the codebase before acting. NEVER implement blindly. Discard with one-line reason if wrong; cite when acting.

## Output

`codex exec "<prompt>"` writes the final message to stdout. `--json` emits JSON Lines. `--ephemeral` skips session persistence.
Treat the answer as advisory. Cite when acting on it.
