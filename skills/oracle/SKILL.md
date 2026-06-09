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

**!!  ALWAYS pass `--dangerously-bypass-approvals-and-sandbox` inside dockbox  !!**

Codex layers its own sandbox on top of dockbox's. The default `read-only`
mode silently swallows file reads and reports "no findings"; even
`workspace-write` cannot read paths outside its declared workspace.
Dockbox is the real sandbox — codex's inner one is duplicate machinery
that costs you findings.

`--dangerously-bypass-approvals-and-sandbox` is **only safe inside
dockbox** because dockbox is the perimeter. The flag's documentation
explicitly says it is "intended solely for running in environments that
are externally sandboxed" — that's us.

> **NEVER use this flag on the host.** Codex will execute model-generated
> shell commands with no approval and no isolation. Only fire it through
> dockbox where the perimeter holds.

```bash
# Short prompt
codex exec --dangerously-bypass-approvals-and-sandbox \
  "is there a stdlib equivalent of Python's bisect in Go?"

# Multi-line context via stdin
cat <<'EOF' | codex exec --dangerously-bypass-approvals-and-sandbox -
Review this CRDT merge function for ordering bugs:
<paste code>
EOF

# Pipe another command's output as context
go test ./... 2>&1 | codex exec --dangerously-bypass-approvals-and-sandbox \
  "summarize the failure and propose the smallest fix"
```

If you ever see codex citing sandbox blocks, the flag wasn't applied —
re-check the invocation, do not silently fall back to `-s read-only`.

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
# </dev/null is REQUIRED when passing prompt as argument — without it codex blocks on stdin
codex exec "$prompt" </dev/null
```

Tell the user "oracle isn't configured" and continue without it. NEVER
crash the turn.

## Rules

codex is a peer agent — has tools, sees the repo. ALWAYS let it explore; NEVER pre-chew the answer.

### Adversarial framing

codex is sycophantic — confirming questions get confirming answers. Frame as the opposing side so a flaw report carries signal.

- ALWAYS attack your own conclusion: "Find the flaw in X", "Why would this break?", "What did I miss?"
- NEVER ask "is X correct?" / "does this look right?" — primes a yes.

### Prompt contents

- ALWAYS state the goal in one line ("Goal: <X>").
- ALWAYS hand it entry points: file paths, symbols, verbatim error/test output, binding constraints (language version, perf budget, forbidden deps).
- OPTIONAL: short listing or excerpt when it saves a redundant search — NEVER as substitute for codex looking.
- NEVER paste session transcript, your reasoning chain, or your conclusions — biases the second opinion.

ALWAYS verify codex's claim against the codebase before acting. NEVER implement blindly. Discard with one-line reason if wrong; cite when acting.

## Output

`codex exec "<prompt>"` writes the final message to stdout. With
`--json` it emits JSON Lines — terminal event has the full answer.
Treat the answer as advisory. Cite when acting on it ("codex flagged
that this loop allocates per iteration; adjusted to reuse the buffer").
