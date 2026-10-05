---
name: astra
description: "Ask the codex CLI on gpt-6-astra (or gpt-5.6-sol, the Sol variant) for a second opinion. NOT for routine lookups (use grep/read/recall-memories). NOT a Claude Agent — this is the OpenAI codex CLI. Usually routed through oracle."
when_to_use: "astra, ask astra, codex, ask codex, sol, ask sol, /sol, second opinion, tricky algorithm, unfamiliar library, sanity check, architecture decision, disagreement after reasoning. NOT for routine lookups"
user-invocable: true
---

# Astra

The codex CLI pinned to `gpt-6-astra`, at high effort. Its catalog description
is "Frontier intelligence for the most demanding work." This is a subprocess,
NEVER a Claude `Agent(...)` type — ALWAYS use the CLI invocation below.

Routing lives in `oracle`. Use this skill directly only when the user
explicitly asks for Astra, Codex or Sol, or when `oracle` dispatches to the
Astra route.

## Invoke

ALWAYS complete the Model and Auth checks below before this invocation.
A Sol call shares these rules except the model and the session: see § Sol.

In dockbox, the container provides isolation; codex's inner bwrap sandbox is unnecessary.
On kernels that block unprivileged user namespaces, bwrap fails with
`No permissions to create a new namespace` — and `-s danger-full-access` does NOT
help, because it still spins up bwrap (in full-access mode), so every shell
command codex runs dies before executing. The ONLY reliable skip is the flag
`--dangerously-bypass-approvals-and-sandbox`, which disables bwrap entirely.
NEVER use `-s read-only` for an audit on this path — ALWAYS use the bypass
flag; sandboxed backend lookups can fail (`failed to lookup address information`).

ALWAYS launch via the `resume` subcommand so codex continues this project's
existing thread instead of starting cold every call. `--last` picks the most
recent session for the current cwd (`--all` disables that cwd filter); with no
prior session it cold-starts cleanly (fresh id, exit 0, no error), so
`resume --last` is the ONE universal invocation — no first-call special case.

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
# --dangerously-bypass-approvals-and-sandbox: skip bwrap (container is the real
#   perimeter; -s danger-full-access still runs bwrap, fails on no-userns kernels)
# </dev/null is REQUIRED — without it codex blocks waiting for additional stdin
codex exec resume --last --dangerously-bypass-approvals-and-sandbox \
  -m gpt-6-astra -c model_reasoning_effort="high" \
  "Goal: <X>. Find the flaw in..." </dev/null
```

NEVER combine `resume` with `--ephemeral` — ephemeral skips persistence, so
there is nothing to resume next call. Use plain `codex exec --ephemeral …`
(no `resume`) ONLY for a genuinely isolated batch loop where each item must NOT
inherit the others' context; everything else uses `resume --last`.

NEVER `pkill -f codex` to clean up — it matches your own shell's command line
(which contains "codex") and kills the harness. Kill codex by numeric PID
(`ps -eo pid,args | grep -F 'codex exec' | grep -v grep | grep -v zsh`).

## Sol

`/sol` is the same second opinion from `gpt-5.6-sol` (catalog description
"Older generation workhorse model"), at high effort. Use it only when the user
explicitly asks for Sol; `oracle` routes to it only on such a request. Two
differences from the Astra invocation: select `gpt-5.6-sol` in the catalog
check and the command, and run `codex exec --ephemeral` instead of `resume
--last`. `resume --last` picks the working directory's latest session, which is
Astra's thread after an Astra call, and Sol must answer without having read
Astra's prompt and answer.

```bash
codex exec --ephemeral --dangerously-bypass-approvals-and-sandbox \
  -m gpt-5.6-sol -c model_reasoning_effort="high" \
  "Goal: <X>. Find the flaw in..." </dev/null
```

## Model — fixed by the variant asked for

- ALWAYS pin `gpt-6-astra` for Astra and `gpt-5.6-sol` for Sol. The request
  names the variant; reading this runbook NEVER changes that choice.
- ALWAYS confirm the selected slug exists with the check below before the
  call; exit 0 means present. NEVER pick the model by the configured default or by priority.
- If the cache is missing, unreadable, or lacks the slug, ALWAYS stop the
  launch and report the exact missing model. ALWAYS ask the user to refresh
  the Codex catalog or explicitly choose another model; NEVER silently substitute.
- ALWAYS pass `-c model_reasoning_effort="high"` for second-opinion work, in
  both variants; NEVER trust a lower local config default.
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
