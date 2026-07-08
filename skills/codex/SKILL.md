---
name: codex
description: Ask the codex CLI for a second opinion. NOT for routine lookups (use grep/read/recall-memories). NOT a Claude Agent — this is the OpenAI codex CLI. Invoked by creative-oracle for creative critique; for code critique see coding-oracle (fable) instead.
when_to_use: "codex, second opinion, tricky algorithm, unfamiliar library, sanity check, architecture decision, disagreement after reasoning, ask codex. NOT for routine lookups"
user-invocable: true
---

# Codex

Runs `codex exec` as a subprocess for a one-shot second opinion.
NEVER use a raw `Agent(...)` call when you need a second opinion — ALWAYS use this skill instead.

Routing: creative critique (naming, prose, narrative, ideation) → `creative-oracle`,
which uses this skill for mechanics. Code critique (review, bug-hunt, design) →
`coding-oracle` (fable), not this skill. `oracle` is a legacy alias that now
points to `coding-oracle` by default.

## Invoke

We're inside dockbox (a container); codex's inner bwrap sandbox is unnecessary.
On kernels that block unprivileged user namespaces, bwrap fails with
`No permissions to create a new namespace` — and `-s danger-full-access` does NOT
help, because it still spins up bwrap (in full-access mode), so every shell
command codex runs dies before executing. The ONLY reliable skip is the flag
`--dangerously-bypass-approvals-and-sandbox`, which disables bwrap entirely.
NEVER use `-s read-only` for an audit either — it sandboxes the network too, so
codex's backend lookups fail (`failed to lookup address information`).

```bash
# Auth check first
if ! codex login status >/dev/null 2>&1 \
   && [ -z "${CODEX_API_KEY:-}${OPENAI_API_KEY:-}" ]; then
  echo "codex unavailable — no auth configured"
  exit 0
fi

# --dangerously-bypass-approvals-and-sandbox: skip bwrap (container is the real
#   perimeter; -s danger-full-access still runs bwrap, fails on no-userns kernels)
# --ephemeral: skip session-rollout files (a long batch loop fills the disk otherwise)
# </dev/null is REQUIRED — without it codex blocks waiting for additional stdin
codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral \
  -c model_reasoning_effort="high" \
  "Goal: <X>. Find the flaw in..." </dev/null
```

NEVER `pkill -f codex` to clean up — it matches your own shell's command line
(which contains "codex") and kills the harness. Kill codex by numeric PID
(`ps -eo pid,args | grep -F 'codex exec' | grep -v grep | grep -v zsh`).

## Model — ALWAYS the newest, at high effort

- ALWAYS run on `~/.codex/config.toml`'s default model — codex pins the
  newest there and auto-migrates via its model-migration notices.
- NEVER pass `-m` with an older model — that silently downgrades the second
  opinion. Omit `-m` to inherit the newest default.
- ALWAYS pass `-c model_reasoning_effort="high"` for second-opinion work.
  Do not trust a lower local config default.
- If `codex exec` errors that the model "requires a newer version of Codex",
  the CLI is stale — `bun add -g @openai/codex@latest` (or npm), then retry.

## Auth — two paths

**Path A — host `~/.codex` mount (preferred).** dockbox bind-mounts `~/.codex` from the host.
```bash
codex login status   # "Logged in using ChatGPT" / "Logged in using API key"
```

**Path B — env var.** dockbox forwards `OPENAI_API_KEY` and `CODEX_API_KEY` from the host env.

If unavailable, ALWAYS tell the user "codex isn't configured". NEVER crash the turn.

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
