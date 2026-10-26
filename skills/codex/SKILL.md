---
name: codex
description: Run a selected model through native Codex workers or the Codex CLI. NOT for task selection (use dispatch) or second-opinion framing (use oracle).
when_to_use: "Codex provider, ask codex, use codex, run codex, ask Astra, ask Sol, Codex CLI auth, Codex model catalog, Codex worker launch"
user-invocable: true
---

# Codex

This runbook executes a selected Codex route. ALWAYS obtain the task, model
and effort from `dispatch` before launching. NEVER infer the selection from
this skill's name or the local configuration default.

## 1. Select the launch method

ALWAYS use native `spawn_agent` when its exposed model choices include the
selected model and it supports explicit effort. ALWAYS set `model` and
`reasoning_effort` to the selection and `fork_turns: "none"`. A model parameter
alone does not prove the model is available. Native workers need no CLI
catalog or auth check. Otherwise, ALWAYS use the CLI checks below.

For a same-model second opinion, ALWAYS answer directly unless the owner asks
for isolation or independence. NEVER apply that shortcut to a worker selected
by dispatch: it needs a separate context even on the parent's model.

ALWAYS use `dispatch` for the brief, capacity and launch report. A read-only
worker is read-only by its brief, not by a CLI sandbox flag. Editing isolation
follows `worktree`; ALWAYS launch in the designated directory.

Completion criterion: one supported launch method and an explicit model,
effort, directory and context policy are recorded.

## 2. Check the CLI and model

ALWAYS check `codex --version` and its relevant help before relying on flags.
If the CLI is absent or reports that a model requires a newer version,
ALWAYS report the missing capability. Installation or upgrade needs the
applicable authorization; NEVER silently replace the model.

ALWAYS run this check with the selected model ID and effort before a CLI
launch. Success proves local catalog membership, not live entitlement.

```bash
python3 - '<selected model ID>' '<selected effort>' \
  "${CODEX_HOME:-$HOME/.codex}/models_cache.json" <<'PY'
import json
import sys
from pathlib import Path

model, effort, catalog_path = sys.argv[1:]
try:
    catalog = json.loads(Path(catalog_path).read_text())
    supported = any(
        entry['slug'] == model
        and any(level['effort'] == effort for level in entry['supported_reasoning_levels'])
        for entry in catalog['models']
    )
except (OSError, ValueError, KeyError, TypeError) as err:
    sys.exit(f'Cannot validate Codex selection {model}/{effort}: {err}')
if not supported:
    sys.exit(f'Unsupported Codex selection: {model}/{effort}')
PY
```

On a missing, unreadable or invalid catalog, missing model or unsupported
effort, ALWAYS stop before generation. Report the exact selection and ask
for a catalog refresh or an explicit alternative; NEVER choose by priority.

Completion criterion: the CLI supports the required flags and the catalog
check exits zero for the exact selected model and effort.

## 3. Check CLI auth

ALWAYS run the preflight without printing credentials:

```bash
if ! codex login status >/dev/null 2>&1 \
   && [ -z "${CODEX_API_KEY:-}${OPENAI_API_KEY:-}" ]; then
  echo 'codex unavailable — no auth configured' >&2
  exit 1
fi
```

The preferred credential source is the host's mounted `~/.codex`; supported
environment keys are the other path. NEVER read or print their contents.
`login status` reads stored credentials without exercising them. A revoked
refresh token can therefore pass this check.

If unavailable, ALWAYS report “codex isn't configured” and continue independent
work. On `token_revoked`, `refresh_token_invalidated` or `401 Unauthorized`
during a real call, ALWAYS stop and give the user `! codex login` to run.
NEVER drive the interactive login or retry a revoked token.

Completion criterion: a configured auth path is present; live validity remains
unproven until an authorized real call succeeds.

## 4. Invoke the CLI

ALWAYS use `--dangerously-bypass-approvals-and-sandbox` for an authorized CLI
worker. NEVER add `--sandbox` or `-s`; the bypass also avoids namespace setup
failures on restricted kernels. The outer task's permissions and boundaries
still apply.

ALWAYS select model and effort explicitly. Substitute the selected values and
the self-contained brief into this invocation:

```bash
codex exec --ephemeral --dangerously-bypass-approvals-and-sandbox \
  -C '<worker directory>' -m '<selected model ID>' \
  -c 'model_reasoning_effort="<selected effort>"' \
  '<brief per dispatch>' </dev/null
```

ALWAYS use an ephemeral context for delegated tasks, fresh plans/reviews,
Sol opinions, independent batch items, and every call from a Codex parent.
NEVER resume a thread from a Codex worker.

For a continued Astra opinion from Claude, ALWAYS use `resume --last` only
when the current directory's latest thread belongs to that same opinion and
selected model. Verify that context before resuming; otherwise use the fresh
invocation. `--last` filters by cwd; NEVER add `--all`, which removes the filter.
With no prior thread, resume starts a new one.

```bash
codex exec -C '<worker directory>' resume --last \
  --dangerously-bypass-approvals-and-sandbox -m '<selected model ID>' \
  -c 'model_reasoning_effort="<selected effort>"' \
  '<brief per dispatch>' </dev/null
```

NEVER combine `resume` and `--ephemeral`. ALWAYS redirect stdin as shown;
without EOF a CLI can wait for more input. ALWAYS use the shell tool's
supported background mechanism and retain its handle when launching
asynchronously. NEVER infer completion from a timeout.

Completion criterion: the recorded launch uses the selected model, effort,
context and cwd, and has a real worker/process handle or completed result.

## 5. Read the result

The final message goes to stdout; `--json` emits JSON Lines. ALWAYS inspect
exit status and output before accepting a result. A catalog check or auth
status is not evidence that the selected model actually ran.

ALWAYS give a peer agent the goal and entry points, not a reasoning chain.
`oracle` owns adversarial framing for a second opinion. ALWAYS verify claims
against the source before acting, and state the reason for rejecting a claim.

NEVER use `pkill -f codex`; it can match the calling shell. ALWAYS stop only a
process this run owns, by its recorded numeric PID or supported worker handle.

Completion criterion: findings and changes have inspected evidence, and any
launch failure remains a failure rather than a substituted model's result.

## Review Checklist

- ALWAYS preserve dispatch's model, effort, task and capacity accounting.
- ALWAYS check exposed native controls or the CLI catalog/auth path.
- ALWAYS keep delegated contexts fresh and pin the directory and effort.
- ALWAYS verify returned evidence and report limitations without substitution.
