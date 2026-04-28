# Redirect Hook Overhaul + Committer

Rewrite `redirect.py` as a generic declarative rule engine.
Rules in a flat text file, three response modes, prefix matching.
Add git safety rules. Update nudge.py and commit skill.

## Background

Multiple agents on same repo: staging collisions, lock races,
accidental `git add .`. Also: existing redirects are hard rewrites
— agent can't go around even with a good reason.

See project specs for multi-agent commit research.

## Rules File

`~/.claude/hooks/redirect.rules` — flat text, one rule per line:

```
# mode    match                   action/message
block     git add .               Stage specific files: git add -- f1 f2
block     git add -A              Stage specific files: git add -- f1 f2
block     git add --all           Stage specific files: git add -- f1 f2
block     git commit --amend      Make a new commit, never amend
block     git commit -a           Stage explicitly first
nudge     pytest                  make test
nudge     cargo test              make test
nudge     npm test                make test
nudge     tsc                     make build
nudge     cargo build             make build
nudge     ruff check              make lint
nudge     git stash               Multi-agent: don't stash
rewrite   git add                 git restore --staged :/ 2>/dev/null; {cmd}
```

### Format

```
mode  match  action
```

- **mode**: `block`, `nudge`, or `rewrite`
- **match**: prefix match against the Bash command. Plain string,
  compared with `cmd.startswith(match)`. Optionally `~regex` for
  rare cases that need regex (`~` prefix = regex mode)
- **action**: depends on mode:
  - `block`: reason message shown to agent
  - `nudge`: reason message (agent can `force` past it)
  - `rewrite`: replacement command (`{cmd}` = original command)
- Lines starting with `#` are comments
- First match wins (put specific rules before general ones)
- Whitespace-separated: mode, match (until double-space or tab),
  action (rest of line)

### Per-project override

```
~/.claude/hooks/redirect.rules        # global default
.claude/redirect.rules                # per-project (takes precedence)
```

If project file exists, it's loaded instead of (or merged with?)
global. Lean: project replaces global entirely — keeps it simple.
Agent can always `force` or `!` to escape.

## Three Response Modes

| Mode | Behavior | Override |
|---|---|---|
| **rewrite** | Silently replace command | No (transparent) |
| **nudge** | Block + explain | `force` prefix |
| **block** | Hard block | Only `!` escape |

### Prefixes

```
pytest               → nudged: "use make test"
force pytest         → passes through (overrides nudge)
git add .            → hard blocked
force git add .      → still blocked (force doesn't help)
!git add .           → passes through (escapes ALL hooks)
```

- (none): normal processing
- `force `: strip prefix, override nudges, blocks still block
- `!`: existing behavior, escape everything

## Hook Implementation

`redirect.py` becomes a generic engine (~40 lines):

```python
#!/usr/bin/env python3
import json, os, sys

data = json.load(sys.stdin)
if data.get("tool_name") != "Bash":
    sys.exit(0)

cmd = data.get("tool_input", {}).get("command", "")
if not isinstance(cmd, str) or cmd.startswith("!"):
    sys.exit(0)

forced = False
if cmd.startswith("force "):
    forced = True
    cmd = cmd[6:]

# Load rules: project-local first, then global
cwd = data.get("cwd", "")
rules_paths = [
    os.path.join(cwd, ".claude", "redirect.rules"),
    os.path.expanduser("~/.claude/hooks/redirect.rules"),
]

rules = []
for p in rules_paths:
    if os.path.isfile(p):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(None, 2)
                if len(parts) == 3:
                    rules.append(tuple(parts))
        break  # first found wins

def block(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "block",
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)

def rewrite(new_cmd, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": reason,
        "updatedInput": {"command": new_cmd},
    }}))
    sys.exit(0)

import re

for mode, match, action in rules:
    # regex match (~ prefix) or prefix match
    if match.startswith("~"):
        if not re.search(match[1:], cmd):
            continue
    elif not cmd.startswith(match):
        continue

    if mode == "block":
        block(action)
    elif mode == "nudge":
        if forced:
            rewrite(cmd, f"forced: {action}")
        else:
            block(action)
    elif mode == "rewrite":
        rewrite(action.replace("{cmd}", cmd), f"redirect: {match}")
    break

sys.exit(0)
```

No toolchain.py dependency. No lib/. Rules file is the config.
Hook is the generic engine.

## nudge.py — update COMMIT_RULES

```python
COMMIT_RULES = """Commit rules:
- git add -- file1 file2 (whole files, explicit paths)
- git commit -m "msg" -- file1 file2 (scoped commit)
- NEVER git add . / -A / --all
- NEVER git commit --amend / -a
- NEVER git stash
- Pre-commit reformats: retry once
- Format: "[section] Message"
Invoke /commit skill."""
```

## Commit skill — already updated

Workflow: git status/diff/log → decide → `git add -- files` →
`git commit -m "msg" -- files`. Hook handles restore-staged
automatically. Skill handles message format and cohesive check.

## What happens to toolchain.py

Current redirect.py uses `lib/toolchain.py` for cwd-aware command
lookup (detect Makefile, Cargo.toml, etc). The rules file replaces
this — nudge rules are static per-project or global.

If a project needs `pytest` → `make test` only when Makefile
exists, put the rule in `.claude/redirect.rules` in that project.
Global rules apply everywhere. Simpler than runtime detection.

toolchain.py and lib/ can be removed after migration.

## Sync to agent SDK

Port rules engine to agent-runner SDK PreToolUse hook. Rules
could be:
- Embedded in TypeScript (small static list)
- Read from a rules file mounted into the container
- Both: defaults embedded, overrides from file

## Testing

1. `git add .` → blocked
2. `git add -A` → blocked
3. `git add file1` → rewrite with restore-staged
4. `git commit --amend` → blocked
5. `git commit -a` → blocked
6. `git stash` → nudge blocked
7. `force git stash` → passes through
8. `!git add .` → escapes all hooks
9. `pytest` → nudge: "make test"
10. `force pytest` → passes through
11. Per-project `.claude/redirect.rules` overrides global
12. Two agents commit different files → no staging collision

## Open questions

### Rules file format separator
Mode and match need a clear separator. Options:
- Tab-separated (clean but invisible)
- Double-space (readable but fragile)
- Fixed columns
- TOML/YAML (heavier but unambiguous)
Lean: tab-separated. Simple, `split(None, 2)` handles it.

### Project rules: replace or merge with global?
Current spec: project replaces global entirely. Alternative:
project prepends to global (project rules match first, then
global). Lean: replace — simpler mental model, project is
self-contained.

### Chained commands
`git add f1 && git commit -m "msg"` — prefix match on `git add`
catches it. Rewrite prepends restore-staged to the whole chain.
Commit part passes through. Skill says use `-- files`. Good enough.

### Pre-commit typecheck scope
Separate concern — no hook-level fix for `pass_filenames: false`.
