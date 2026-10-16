# Hooks Testing Guide

Manual smoke tests. Pipe a JSON payload into each hook and read the output and
exit code. Run the automated suite first; it covers routing, the measurements,
the escalation ladder, the unsafe-command blocks and the stop checks against an
in-memory kvs (`conftest.py`):

```bash
make -C hooks test
```

The smoke tests below run the installed scripts against the real `kvs`. Set
`KVS_DIR=$(mktemp -d)` first so they never touch the live database.

## 1. Malformed payloads never crash

```bash
for h in prompt_nudge pretool_nudge stop memory_nudge style_nudge; do
  echo ""           | python3 ~/.claude/hooks/$h.py
  echo "{bad json}" | python3 ~/.claude/hooks/$h.py
  echo "[]"         | python3 ~/.claude/hooks/$h.py
  echo '{"prompt": null}' | python3 ~/.claude/hooks/$h.py
done
```

Expected: exit 0 every time, no stderr, no output.

## 2. Pointers, never rule text

```bash
echo '{"prompt": "ship it", "session_id": "smoke", "cwd": "/tmp"}' | python3 ~/.claude/hooks/prompt_nudge.py
echo '{"prompt": "ship it", "session_id": "smoke", "cwd": "/tmp"}' | python3 ~/.claude/hooks/prompt_nudge.py
```

Expected: the first call's `additionalContext` is `<reminder skill="solve">…</reminder>`,
then `<file path="~/.claude/LOCAL.md"/>` when that file exists, then
`<skill name="ship"/>`; the second call prints `<skill name="ship"/>` alone.

```bash
echo '{"tool_name": "Edit", "session_id": "smoke", "cwd": "/tmp", "tool_input": {"file_path": "/tmp/x.py"}}' \
  | python3 ~/.claude/hooks/pretool_nudge.py
```

Expected: `<skill name="py"/>` once; a repeat of the same call prints nothing.

## 3. Caveman: measure at Stop, point on the next prompt

```bash
long=$(python3 -c 'print("\\n".join(f"Line {n} of a long reply." for n in range(30)))')
printf '{"hook_event_name": "Stop", "session_id": "smoke", "cwd": "/tmp", "last_assistant_message": %s}' "$(printf '%s' "$long" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')" \
  | python3 ~/.claude/hooks/style_nudge.py
kvs -s smoke -p /tmp get caveman
echo '{"prompt": "next", "session_id": "smoke", "cwd": "/tmp"}' | python3 ~/.claude/hooks/prompt_nudge.py
```

Expected: the Stop call prints nothing; `kvs` shows `{"level":1,"miss":1,"ok":0,"lines":30,"cap":20}`;
the prompt call carries `<reminder skill="caveman" rule="budget" lines="30" cap="20"/>`.

## 4. stop.py

```bash
echo '{"cwd": "/tmp", "hook_event_name": "Stop"}' | python3 ~/.claude/hooks/stop.py
d=$(mktemp -d) && git -C "$d" init -q
echo "{\"cwd\": \"$d\", \"hook_event_name\": \"Stop\"}" | python3 ~/.claude/hooks/stop.py
```

Expected: silent outside git; in the fresh repository a `decision: block` whose
reason is `<reminder skill="diary">no diary entry today</reminder>`, and no file
written under `~/.claude/projects/`.

## 5. pretool_nudge.py — a review submit asks in Claude Code and is denied under Codex

```bash
p='{"tool_name":"Bash","tool_input":{"command":"gh api repos/o/r/pulls/1/reviews/2/events -f event=COMMENT"}}'
printf '%s' "$p" | python3 ~/.claude/hooks/pretool_nudge.py
printf '%s' "$p" | python3 ~/.claude/hooks/codex_hook.py PreToolUse pretool_nudge
```

Expected: the first call prints `"permissionDecision": "ask"` with the reason
the permission dialog shows, the second `"permissionDecision": "deny"` with a
reason that hands the command to the user.

## 6. pretool_nudge.py — reflows a Markdown write only in an opted-in repo

```bash
cd "$(mktemp -d)" && git init -q . && printf '[MD013]\nline-length = 100\nreflow = true\n' > .rumdl.toml
python3 -c 'print("# T\n\n" + "word " * 40)' > a.md
printf '{"hook_event_name":"PostToolUse","tool_name":"Write","tool_input":{"file_path":"%s/a.md"}}' "$PWD" \
  | python3 ~/.claude/hooks/pretool_nudge.py
wc -L a.md
```

Expected (with `rumdl` on PATH or in `node_modules/.bin`): no output, exit 0,
and the longest line of `a.md` is now under 100 columns. Without rumdl the one
output line says `rumdl is not installed; a.md was not reflowed.` Without the
`.rumdl.toml`, or for `a.py`, the file is untouched and nothing is printed.

## 7. codex_hook.py

```bash
echo '{"prompt": "refine this", "session_id": "smoke"}' \
  | python3 ~/.claude/hooks/codex_hook.py UserPromptSubmit prompt_nudge
```

Expected: `<skill name="refine"/>` inside `hookSpecificOutput.additionalContext`.

## Debugging

```bash
echo '{"prompt": "ship it", "session_id": "smoke", "cwd": "/tmp"}' | python3 ~/.claude/hooks/prompt_nudge.py | jq .
kvs -s smoke -p /tmp ls
```
