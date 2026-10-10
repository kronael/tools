# Hooks Testing Guide

Manual smoke tests. Pipe a JSON payload into each hook and verify the
output / exit code.

Run the automated suite first — it covers routing, the unsafe-command
blocks, the nudge stamps and the stop checks. Malformed JSON, `local.py` and
`reclaude.py` are reached only by the smoke tests below:

```bash
make -C hooks test
```

## 1. JSON Error Handling (should NOT crash)

```bash
echo ""              | python3 ~/.claude/hooks/prompt_nudge.py
echo "{bad json}"    | python3 ~/.claude/hooks/prompt_nudge.py
echo "[]"            | python3 ~/.claude/hooks/local.py
echo "{incomplete"   | python3 ~/.claude/hooks/reclaude.py
```

Expected: exit 0, no stderr.

## 2. Null & Type Errors (should NOT crash)

```bash
echo '{"prompt": null}'                         | python3 ~/.claude/hooks/prompt_nudge.py
echo '{"prompt": {"nested": "dict"}}'           | python3 ~/.claude/hooks/prompt_nudge.py
echo '{"prompt": null}'                         | python3 ~/.claude/hooks/local.py
```

Expected: exit 0, no stderr.

## 3. Word Boundary (no false positives)

```bash
# "thecontinueword" / "recap_session" should NOT inject RULES
echo '{"prompt": "thecontinueword"}' | python3 ~/.claude/hooks/local.py
echo '{"prompt": "recap_session"}'   | python3 ~/.claude/hooks/local.py
```

Expected: exit 0, no `systemMessage` in output.

## 4. Prompt Routing (exact match)

```bash
echo '{"prompt": "improve code"}' | python3 ~/.claude/hooks/prompt_nudge.py | grep -q "/improve" && echo "✓ PASS"
echo '{"prompt": "visual"}'       | python3 ~/.claude/hooks/prompt_nudge.py | grep -q "/visual"  && echo "✓ PASS"
echo '{"prompt": "ship"}'         | python3 ~/.claude/hooks/prompt_nudge.py | grep -q "/ship"    && echo "✓ PASS"
echo '{"prompt": "diary"}'        | python3 ~/.claude/hooks/prompt_nudge.py | grep -q "/diary"   && echo "✓ PASS"
echo '{"prompt": "write code"}'   | python3 ~/.claude/hooks/prompt_nudge.py | grep -q "codex" && echo "✗ FAIL" || echo "✓ PASS"
```

Expected: all five print `✓ PASS`.

## 5. Negation Detection

```bash
# Should NOT inject rules
echo '{"prompt": "dont continue"}'  | python3 ~/.claude/hooks/local.py | grep -q "systemMessage" && echo "✗ FAIL" || echo "✓ PASS"
echo "{\"prompt\": \"don't continue\"}" | python3 ~/.claude/hooks/local.py | grep -q "systemMessage" && echo "✗ FAIL" || echo "✓ PASS"
echo '{"prompt": "never recap"}'    | python3 ~/.claude/hooks/local.py | grep -q "systemMessage" && echo "✗ FAIL" || echo "✓ PASS"
```

## 6. Normal Injection

```bash
echo '{"prompt": "continue with implementation"}' | python3 ~/.claude/hooks/local.py | grep -q "systemMessage" && echo "✓ PASS"
echo '{"prompt": "where were we"}'                | python3 ~/.claude/hooks/local.py | grep -q "systemMessage" && echo "✓ PASS"
```

## Hook-by-Hook Smoke

### codex_hook.py

```bash
echo '{"prompt": "refine this"}' \
  | python3 ~/.claude/hooks/codex_hook.py UserPromptSubmit prompt_nudge \
  | grep -q "@refine" && echo "✓ PASS"
```

### stop.py

```bash
# Not a git repo → silent
echo '{"cwd": "/tmp"}' | python3 ~/.claude/hooks/stop.py

# Git repo and no entry for today under ~/.claude/projects/<slug>/diary/ → warning, no file write
d=$(mktemp -d)
git -C "$d" init -q
echo "{\"cwd\": \"$d\"}" | python3 ~/.claude/hooks/stop.py
```

### post_tool_nudge.sh — reflows a Markdown write only in an opted-in repo

```bash
cd "$(mktemp -d)" && git init -q . && printf '[MD013]\nline-length = 100\nreflow = true\n' > .rumdl.toml
python3 -c 'print("# T\n\n" + "word " * 40)' > a.md
printf '{"hook_event_name":"PostToolUse","tool_name":"Write","tool_input":{"file_path":"%s/a.md"}}' "$PWD" | bash ~/.claude/hooks/post_tool_nudge.sh
wc -L a.md
```

Expected (with `rumdl` on PATH or in `node_modules/.bin`): no output, exit 0,
and the longest line of `a.md` is now under 100 columns. Without rumdl the one
output line says `rumdl is not installed; a.md was not reflowed.` Without the
`.rumdl.toml`, or for `a.py`, the file is untouched and nothing is printed.

## Debugging a Failed Test

```bash
# Full JSON output
echo '{"prompt": "continue"}' | python3 ~/.claude/hooks/local.py | jq .

# Exit code
echo '{"prompt": "continue"}' | python3 ~/.claude/hooks/local.py
echo "exit=$?"
```
