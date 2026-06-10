---
name: oracle
description: Ask codex CLI for a second opinion. NOT for routine lookups (use grep/read/recall-memories).
when_to_use: tricky algorithm, unfamiliar library, sanity check before committing to a non-obvious implementation, disagreement with self after reasoning
---

# Oracle

Drives `codex` CLI (`@openai/codex`) as a subprocess for a one-shot
second opinion. The binary is on `PATH` in dockbox; auth comes from
either a host `~/.codex` mount or an env-var API key.

## When to invoke

- A tricky algorithm where trade-offs aren't obvious
- A library/API surface you don't know well
- A sanity check on a non-obvious implementation before it ships
- Disagreement with self after a reasoning round

NEVER reach for oracle on routine uncertainty — `/recall-memories` + grep resolve most questions faster and without an external call.

## Call it

```bash
# Short prompt
codex exec "is there a stdlib equivalent of Python's bisect in Go?"

# Multi-line context via stdin
cat <<'EOF' | codex exec -
Review this CRDT merge function for ordering bugs:
<paste code>
EOF

# Pipe another command's output as context
go test ./... 2>&1 | codex exec "summarize the failure and propose the smallest fix"
```

Flags: `--json` for machine-readable output, `--ephemeral` to skip session persistence.

## Auth — two paths

**Path A — host `~/.codex` mount (preferred).** dockbox bind-mounts
`~/.codex` from the host at `/home/claude/.codex` (rw) when the dir
exists. codex reads `auth.json` from there — ChatGPT-OAuth, API key,
config. Single `codex login` on the host serves every dockbox session.

```bash
codex login status   # "Logged in using ChatGPT" / "Logged in using API key"
```

**Path B — env var.** dockbox forwards `OPENAI_API_KEY` and
`CODEX_API_KEY` from the host env when set.

## Missing-auth fallback

ALWAYS probe before using — fail gracefully:

```bash
if ! codex login status >/dev/null 2>&1 \
   && [ -z "${CODEX_API_KEY:-}${OPENAI_API_KEY:-}" ]; then
  echo "oracle unavailable — no codex auth configured"
  exit 0
fi
codex exec "$prompt"
```

Tell the user "oracle isn't configured" and continue without it. NEVER
crash the turn.

## Rules

- ALWAYS hand codex the specific question + minimal code/error — NEVER paste session transcript or your reasoning chain
- ALWAYS verify codex's claim against the codebase before acting. NEVER implement blindly. Discard with one-line reason if wrong; cite when acting

## Output

`codex exec "<prompt>"` writes the final message to stdout. With
`--json` it emits JSON Lines — terminal event has the full answer.
Treat the answer as advisory. Cite when acting on it ("codex flagged
that this loop allocates per iteration; adjusted to reuse the buffer").

## NEVER leak cost to the user

codex appends a cost/token summary to its own output (something like
`tokens used: 4321 ($0.11)` or a `total_cost_usd` field in `--json`
mode). That is **internal accounting**, not chat content.

- NEVER quote, paraphrase, or forward codex's cost/token line into a
  reply, status, file caption, or summary.
- NEVER mention dollar amounts, token counts, or "cost" sourced from
  codex output.
- Extract the answer (the model's actual message text) before you
  show anything to the user. Drop the trailing cost block.
- If you must reason about the cost, do so inside `<think>` only —
  never in visible output.

If the host exposes a cost-logging tool (e.g. `log_external_cost`),
that is the only sanctioned destination for the number.
