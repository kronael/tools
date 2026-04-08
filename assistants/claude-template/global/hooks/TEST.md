# Hooks Testing Guide

## Quick Test

```bash
python3 ~/.claude/hooks/test_hooks.py
```

Covers:
- JSON parse errors on every hook (empty, malformed, wrong type)
- Null/dict prompt guards in `nudge.py` and `local.py`
- `local.py` word-boundary and negation behaviour
- `nudge.py` keyword priority (fuzzy match, commit rules override)

## Manual Testing by Category

### 1. JSON Error Handling (should NOT crash)

```bash
echo ""              | python3 ~/.claude/hooks/nudge.py
echo "{bad json}"    | python3 ~/.claude/hooks/nudge.py
echo "[]"            | python3 ~/.claude/hooks/local.py
echo "{incomplete"   | python3 ~/.claude/hooks/learn.py
```

Expected: exit 0, no stderr.

### 2. Null & Type Errors (should NOT crash)

```bash
echo '{"prompt": null}'                         | python3 ~/.claude/hooks/nudge.py
echo '{"prompt": {"nested": "dict"}}'           | python3 ~/.claude/hooks/nudge.py
echo '{"prompt": null}'                         | python3 ~/.claude/hooks/local.py
```

Expected: exit 0, no stderr.

### 3. Word Boundary (no false positives)

```bash
# "thecontinueword" / "recap_session" should NOT inject RULES
echo '{"prompt": "thecontinueword"}' | python3 ~/.claude/hooks/local.py
echo '{"prompt": "recap_session"}'   | python3 ~/.claude/hooks/local.py
```

Expected: exit 0, no `systemMessage` in output.

### 4. Keyword Routing (fuzzy match)

```bash
echo '{"prompt": "improve code"}' | python3 ~/.claude/hooks/nudge.py | grep -q "@improve" && echo "✓ PASS"
echo '{"prompt": "visual"}'       | python3 ~/.claude/hooks/nudge.py | grep -q "@visual"  && echo "✓ PASS"
echo '{"prompt": "ship"}'         | python3 ~/.claude/hooks/nudge.py | grep -q "/ship"    && echo "✓ PASS"
echo '{"prompt": "diary"}'        | python3 ~/.claude/hooks/nudge.py | grep -q "/diary"   && echo "✓ PASS"
```

Expected: all four print `✓ PASS`.

### 5. Negation Detection

```bash
# Should NOT inject rules
echo '{"prompt": "dont continue"}'  | python3 ~/.claude/hooks/local.py | grep -q "systemMessage" && echo "✗ FAIL" || echo "✓ PASS"
echo "{\"prompt\": \"don't continue\"}" | python3 ~/.claude/hooks/local.py | grep -q "systemMessage" && echo "✗ FAIL" || echo "✓ PASS"
echo '{"prompt": "never recap"}'    | python3 ~/.claude/hooks/local.py | grep -q "systemMessage" && echo "✗ FAIL" || echo "✓ PASS"
```

### 6. Normal Injection

```bash
echo '{"prompt": "continue with implementation"}' | python3 ~/.claude/hooks/local.py | grep -q "systemMessage" && echo "✓ PASS"
echo '{"prompt": "where were we"}'                | python3 ~/.claude/hooks/local.py | grep -q "systemMessage" && echo "✓ PASS"
```

## Hook-by-Hook Smoke

### nudge.py

```bash
echo '{"prompt": "improve styling"}' | python3 ~/.claude/hooks/nudge.py
echo '{"prompt": "save progress"}'   | python3 ~/.claude/hooks/nudge.py   # commit rules
```

### local.py

```bash
echo '{"prompt": "continue with implementation", "cwd": "/tmp"}' | python3 ~/.claude/hooks/local.py
echo "{\"prompt\": \"don't continue\", \"cwd\": \"/tmp\"}"       | python3 ~/.claude/hooks/local.py  # silent
```

### learn.py

```bash
echo '{"hook_event": "SessionEnd", "session_id": "test-123"}' | python3 ~/.claude/hooks/learn.py
# Writes ~/.claude/flow-reports/<ts>-SessionEnd.md
```

### stop.py

```bash
# Clean tree, no diary dir → silent
echo '{"cwd": "/tmp"}' | python3 ~/.claude/hooks/stop.py

# Diary dir with no entry for today → nudge
mkdir -p /tmp/stoptest/.diary
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
