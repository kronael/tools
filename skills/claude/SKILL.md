---
name: claude
description: Run a selected Claude model through native agents or the Claude CLI. NOT for task selection (use dispatch) or second-opinion framing (use oracle).
when_to_use: "Claude provider, ask Claude, use Claude from Codex, Claude CLI auth, Claude worker launch, native Claude agent effort"
user-invocable: true
---

# Claude

This runbook executes a selected Claude route. ALWAYS obtain the task, model
and effort from `dispatch` before launching. NEVER inherit the parent session's
effort or treat a provider name as a model choice.

## 1. Select the launch method

In Claude Code, ALWAYS prefer a native Agent launch with an available matching
agent definition. `skills/CLAUDE.md` § Agent definitions owns those bindings.
ALWAYS inspect the definition's actual model and effort before using it;
`model:` alone on a launch does not load an agent's effort pin.

For the selected standard model, ALWAYS use its lowercase agent type. For
Opus/xhigh, ALWAYS use the `spec` agent binding when the native tool cannot
explicitly override effort. NEVER select the high-effort `opus` binding and
claim prompt text raises it to xhigh.

For an owner override, ALWAYS use a supported launch effort control or a
binding that matches the exact selection. If native controls cannot express
it, ALWAYS use the CLI route when available. NEVER silently keep a binding's
default effort or create a provider alias for a different model.

From Codex, ALWAYS use the CLI route unless an exposed native tool explicitly
supports the selected Claude model and effort. A Codex `spawn_agent` model
parameter does not establish Claude support. ALWAYS preserve a fresh context
for delegated work; NEVER fork the author's conversation into a reviewer.

ALWAYS resolve and report the actual model argument, including whether it is
a provider alias. An alias is not proof of the resolved model version. ALWAYS
use dispatch's brief, capacity and launch report and `worktree` for required
editing isolation. A worker performs its own bounded assignment.

Completion criterion: one available launch method can express the selected
model, effort, directory and fresh context without an inherited default.

## 2. Check the CLI and auth

ALWAYS inspect `claude --version` and `claude --help` for the required flags.
The CLI accepts documented model aliases or full model IDs. NEVER infer model
entitlement from help, an installed agent file or a running parent session.

ALWAYS run `claude auth status --json` in the launching environment and inspect
only the login verdict. NEVER print account details, read credential files or
scrape a parent process's environment for tokens. CLI auth is separate from
the parent harness; a logged-in parent does not prove the subprocess is ready.

```bash
set -o pipefail
claude auth status --json | python3 -c '
import json
import sys

logged_in = json.load(sys.stdin).get("loggedIn") is True
print("claude auth configured" if logged_in else "claude unavailable — no auth configured")
sys.exit(0 if logged_in else 1)
'
```

If auth is unavailable, ALWAYS report “claude isn't configured” and give the
user `claude auth login` to run. NEVER drive interactive login from a tool.
If the installed CLI lacks a required flag, ALWAYS report the version and
unsupported selection. Installation or upgrade needs applicable authorization.

Completion criterion: the required flags exist and the CLI reports a configured
login; actual model access remains unproven until an authorized call succeeds.

## 3. Invoke the CLI

ALWAYS start in the worker's designated directory. Keep model, effort and brief
as separately quoted arguments. For an authorized full-access worker, use:

```bash
cd '<worker directory>' && claude --print --no-session-persistence \
  --dangerously-skip-permissions --model '<selected model ID or alias>' \
  --effort '<selected effort>' '<brief per dispatch>' </dev/null
```

ALWAYS respect the outer task's permission policy and boundaries. When it
requires a different supported permission mode, use that mode explicitly.
A read-only brief limits the work; a bypass flag does not authorize edits or
external actions outside the brief.

NEVER add `--continue`, `--resume`, `--fork-session`, a fallback model or
`--worktree` for a fresh worker. `--worktree` creates managed branches;
`worktree` owns detached isolation. NEVER disable the skills or project
instructions with `--bare`, `--safe-mode` or `--disable-slash-commands`.

ALWAYS use the shell tool's supported background mechanism and retain its
handle for asynchronous work. The command above completes in the foreground
unless that mechanism runs it asynchronously. NEVER confuse `--print` with
background execution or a polling timeout with completion.

Completion criterion: the actual launch pins the selected model and effort,
uses the assigned cwd and has a recorded handle or completed result.

## 4. Read the result

ALWAYS inspect exit status and output. On an auth, model, effort or usage-limit
failure, report the exact limitation and continue independent work. NEVER
retry with a fallback model or lower effort without an owner-approved choice.

ALWAYS verify returned claims and changes against the source before accepting
them. `oracle` owns second-opinion framing and verification; dispatch owns the
required evidence report. NEVER claim a model ran from a CLI help or auth check.

ALWAYS stop only this run's process by its recorded PID or native worker
handle. NEVER use a broad process-name kill or modify another session.

Completion criterion: the returned evidence supports the result, or the failed
selection is reported without a silent substitution.

## Review Checklist

- ALWAYS preserve dispatch's task, model, effort and capacity accounting.
- ALWAYS inspect native pins or verify the subprocess CLI and auth separately.
- ALWAYS use fresh contexts, explicit effort and the assigned detached cwd.
- ALWAYS verify the result and retain limitations in the final report.
