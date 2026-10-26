---
name: astra
description: "Ask the codex CLI on gpt-6-astra (or gpt-6.1-sol, the Sol variant) for a second opinion, usually routed through oracle. NOT for routine lookups (use grep/read/recall-memories). NOT a Claude agent."
when_to_use: "astra, ask astra, codex, ask codex, sol, ask sol, second opinion, sanity check, disagreement after reasoning"
user-invocable: true
---

# Astra

The codex CLI pinned to `gpt-6-astra`, at high effort for a review. Its catalog description
is "Frontier intelligence for the most demanding work." This is a subprocess,
NEVER a Claude `Agent(...)` type — ALWAYS use the CLI invocation below.

Routing lives in `oracle`. Use this skill directly only when the user
explicitly asks for Astra, Codex or Sol, or when `dispatch`, `oracle` or
`refine` selects a route here.

## Invoke

For a second opinion from the model you are running on, ALWAYS answer directly
and NEVER launch this CLI. This shortcut does not apply to an isolated worker
selected through `dispatch` § Tiers. `refine` step 6 owns its native Codex launch.

ALWAYS complete the Model and Auth checks below before this invocation.
A Sol call shares these rules except the model, effort and session: see § Sol.
ALWAYS use `dispatch` § Brief, including its Codex opening, for both variants.

ALWAYS use `--dangerously-bypass-approvals-and-sandbox`: the owner requires no
inner sandbox. NEVER pass `--sandbox` or `-s`. The bypass disables approvals
and sandboxing, including namespace setup that can fail on restricted kernels.
A read-only worker is read-only by its brief, not by this flag.

From Claude Code, ALWAYS launch via `resume --last` to continue this project's
existing thread. `--last` picks the most recent session for the current cwd;
`--all` disables that cwd filter. With no prior session it starts a fresh one.
From Codex, ALWAYS use isolated `codex exec --ephemeral` with the same model,
effort and bypass flags below. NEVER resume a thread from a Codex worker.

```bash
# Auth check first — catches "never logged in" only. `codex login status`
# reads the stored credential without exercising it, so it prints "Logged in
# using ChatGPT" and exits 0 on a session whose refresh token has been revoked.
# The revocation surfaces only on a real call, as a wall of
# `Failed to refresh token: ... refresh_token_invalidated` and
# `auth error code: token_revoked`, with no model output.
if ! codex login status >/dev/null 2>&1 \
   && [ -z "${CODEX_API_KEY:-}${OPENAI_API_KEY:-}" ]; then
  echo "codex unavailable — no auth configured"
  exit 0
fi

# resume --last: continue this cwd's most recent codex session (cold-starts if
#   none). Repeated calls fold into ONE growing session file, not N rollout
#   files — so this is also the disk-friendly path, no --ephemeral needed.
# </dev/null is REQUIRED — without it codex blocks waiting for additional stdin
codex exec resume --last --dangerously-bypass-approvals-and-sandbox \
  -m gpt-6-astra -c model_reasoning_effort="high" \
  "<brief per dispatch § Brief>" </dev/null
```

NEVER combine `resume` with `--ephemeral`. ALWAYS use plain `codex exec --ephemeral …`
(no `resume`) for a Codex parent or an isolated batch loop whose items must NOT
inherit each other's context. Other Astra calls from Claude use `resume --last`.

NEVER `pkill -f codex` to clean up — it matches your own shell's command line
(which contains "codex") and kills the harness. Kill codex by numeric PID
(`ps -eo pid,args | grep -F 'codex exec' | grep -v grep | grep -v zsh`).

## Sol

Sol is the Codex worker for the `/opus` lane. Its model ID is `gpt-6.1-sol`,
and its effort is `xhigh`. `dispatch` § Tiers owns its work assignments;
`oracle` also selects it for an explicit Sol opinion.
ALWAYS apply § Invoke and its brief rule. For CLI calls, ALWAYS select
`gpt-6.1-sol` in the catalog check and use `codex exec --ephemeral`.
NEVER resume Astra's thread for Sol — ALWAYS give Sol an independent context.

```bash
codex exec --ephemeral --dangerously-bypass-approvals-and-sandbox \
  -m gpt-6.1-sol -c model_reasoning_effort="xhigh" \
  "<brief per dispatch § Brief>" </dev/null
```

## Model — fixed by the variant asked for

- ALWAYS pin `gpt-6-astra` for Astra and `gpt-6.1-sol` for Sol. The request
  names the variant; reading this runbook NEVER changes that choice.
- ALWAYS confirm the selected slug exists with the check below before the
  call; exit 0 means present. NEVER pick the model by the configured default or by priority.
- If the cache is missing, unreadable, or lacks the slug, ALWAYS stop the
  launch and report the exact missing model. ALWAYS ask the user to refresh
  the Codex catalog or explicitly choose another model; NEVER silently substitute.
- ALWAYS set `model_reasoning_effort` explicitly: Sol uses § Sol's pin;
  Astra uses `high`, with WISDOM § Agents setting its exceptions.
  NEVER trust the local config default.
- If `codex exec` errors that the model "requires a newer version of Codex",
  the CLI is stale — `bun add -g @openai/codex@latest` (or npm), then retry.

```bash
python3 - '<selected slug>' <<'PY'
import json
import os
import sys
from pathlib import Path

home = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex'))
catalog = json.loads((home / 'models_cache.json').read_text())
sys.exit(0 if any(m['slug'] == sys.argv[1] for m in catalog['models']) else 1)
PY
```

## Auth — two paths

**Path A — host `~/.codex` mount (preferred).** dockbox bind-mounts `~/.codex` from the host.
```bash
codex login status   # "Logged in using ChatGPT" / "Logged in using API key"
```

**Path B — env var.** dockbox forwards `OPENAI_API_KEY` and `CODEX_API_KEY` from the host env.

If unavailable, ALWAYS tell the user "codex isn't configured". NEVER crash the turn.

ALWAYS treat `token_revoked` or `401 Unauthorized` in the output as codex being
unavailable, whatever `login status` claimed, and ALWAYS hand the user
`! codex login` to run themselves — it is interactive and cannot be driven from
a tool call. NEVER retry the call: a revoked refresh token does not recover.

## Rules

Codex is a peer agent with tools and repo access. ALWAYS give it the goal and entry points,
then let it explore freely. NEVER pre-chew the answer or walk it through steps;
that defeats the point. For open-ended tasks (doc improvements, architecture
reviews, broad audits) give a high-level goal and let codex decide how to research
it — it will read files, run grep, follow imports on its own.

### Adversarial framing

codex is sycophantic — confirming questions get confirming answers. Frame as the opposing side.

- ALWAYS attack your own conclusion: "Find the flaw in X", "Why would this break?", "What did I miss?"
- NEVER ask "is X correct?" / "does this look right?" — primes a yes.
- NEVER hand it your own list of suspected weaknesses. An adversarial *frame*
  ("destroy this claim") is right; an adversarial *checklist* ("check whether
  the denominator is inflated, whether X only reacts to absurd values, whether
  Y is theatre") is pre-chewing wearing a hostile mask. You get your own
  hypotheses back, confirmed, and never learn what you failed to suspect —
  which is the entire reason to ask. State the claim, name the artifacts, and
  let it choose the attack.

### Prompt contents

- ALWAYS state the goal in one line ("Goal: <X>").
- For targeted questions: hand it entry points (file paths, symbols, error output).
- For open-ended research: state the goal and the output format — skip the steps.
- NEVER paste session transcript, your reasoning chain, or your conclusions — biases the second opinion.

ALWAYS verify codex's claim against the codebase before acting. NEVER implement blindly. Discard with one-line reason if wrong; cite when acting.

## Output

The invocation above writes the final message to stdout; `--json` emits JSON
Lines. `--ephemeral` skips persistence — see Invoke. Treat the answer as
advisory. Cite when acting on it.
