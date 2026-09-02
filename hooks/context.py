#!/usr/bin/env python3
import json
import re
import sys

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError, ValueError):
    sys.exit(0)

if not isinstance(data, dict):
    sys.exit(0)

# Key rules to re-inject (subset of CLAUDE.md)
RULES = """Development reminders:
- ALWAYS use make for build/lint/test/clean
- ALWAYS build/test/lint every ~50 lines - errors cascade
- NEVER improve beyond what's asked
- NEVER use git add -A
- NEVER use git commit --amend - make new commits
- NEVER add Co-Authored-By to commits"""

# Get prompt with type guard
prompt = data.get("prompt") or ""
if not isinstance(prompt, str):
    sys.exit(0)

prompt_lower = prompt.lower()

# Check for negation first (user explicitly saying "don't continue", etc)
if re.search(r"\b(don\'?t|not|never)\s+\w*\s*(continue|recap)", prompt_lower):
    sys.exit(0)

# Use word boundaries to match triggers exactly
if re.search(r'\b(continue|recap|where\s+were\s+we|what\'?s\s+next)\b', prompt_lower):
    print(json.dumps({"ok": True, "systemMessage": RULES}))

sys.exit(0)
