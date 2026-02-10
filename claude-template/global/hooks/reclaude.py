#!/usr/bin/env python3
import json
import sys
import os
import re

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError, ValueError):
    sys.exit(0)

if not isinstance(data, dict):
    sys.exit(0)

# Read RECLAUDE.md
reclaude = os.path.expanduser("~/.claude/RECLAUDE.md")
if not os.path.exists(reclaude):
    sys.exit(0)
try:
    with open(reclaude) as f:
        rules = f.read()
except OSError:
    sys.exit(0)

hook_event = data.get("hook_event", "")
prompt = data.get("prompt") or ""
if not isinstance(prompt, str):
    prompt = ""

# Check for negation (user explicitly saying "don't continue", etc)
prompt_lower = prompt.lower()
if re.search(r"\b(don\'?t|not|never)\s+\w*\s*(continue|recap)", prompt_lower):
    sys.exit(0)

# Inject on PreCompact OR manual triggers
should_inject = hook_event == "PreCompact" or re.search(
    r'\b(continue|recap|where\s+were\s+we|what\'?s\s+next)\b', prompt_lower
)

if should_inject:
    # Add compaction preservation instruction for PreCompact
    if hook_event == "PreCompact":
        rules = (
            rules.rstrip()
            + "\n\nThese instructions and the full wisdom context from CLAUDE.md should survive compaction.\n"
        )
    print(json.dumps({"ok": True, "systemMessage": rules}))

sys.exit(0)
