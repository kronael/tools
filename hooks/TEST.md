# Hooks Testing Guide

Manual smoke tests. Pipe a JSON payload into each hook and verify the
output / exit code.

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
echo '{"prompt": "improve code"}' | python3 ~/.claude/hooks/prompt_nudge.py | grep -q "@improve" && echo "✓ PASS"
echo '{"prompt": "visual"}'       | python3 ~/.claude/hooks/prompt_nudge.py | grep -q "@visual"  && echo "✓ PASS"
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

## codex_hook.py

```bash
echo '{"prompt": "refine this"}' \
  | python3 ~/.claude/hooks/codex_hook.py UserPromptSubmit prompt_nudge \
  | grep -q "@refine" && echo "✓ PASS"
```

## prompt_nudge.py

```bash
echo '{"prompt": "improve styling"}' | python3 ~/.claude/hooks/prompt_nudge.py
echo '{"prompt": "save progress"}'   | python3 ~/.claude/hooks/prompt_nudge.py   # commit rules
```

## local.py

```bash
echo '{"prompt": "continue with implementation", "cwd": "/tmp"}' | python3 ~/.claude/hooks/local.py
echo "{\"prompt\": \"don't continue\", \"cwd\": \"/tmp\"}"       | python3 ~/.claude/hooks/local.py  # silent
```

## stop.py

```bash
# Clean tree, no diary dir → silent
echo '{"cwd": "/tmp"}' | python3 ~/.claude/hooks/stop.py

# Git repo with diary dir and no entry for today → warning, no file write
mkdir -p /tmp/stoptest/.diary
git -C /tmp/stoptest init
echo '{"cwd": "/tmp/stoptest"}' | python3 ~/.claude/hooks/stop.py
rm -rf /tmp/stoptest
```

## Debugging a Failed Test

```bash
# Full JSON output
echo '{"prompt": "continue"}' | python3 ~/.claude/hooks/local.py | jq .

# Exit code
echo '{"prompt": "continue"}' | python3 ~/.claude/hooks/local.py
echo "exit=$?"
```
