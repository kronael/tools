#!/usr/bin/env python3
import json
import os
import re
import sys

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError, ValueError):
    sys.exit(0)

if not isinstance(data, dict):
    sys.exit(0)

RULES = """Development reminders:
- ALWAYS use make for build/lint/test/clean
- ALWAYS build/test/lint every ~50 lines - errors cascade
- NEVER improve beyond what's asked
- NEVER use git add -A
- NEVER use git commit --amend - make new commits
- NEVER add Co-Authored-By to commits"""

prompt = data.get("prompt") or ""
if not isinstance(prompt, str):
    sys.exit(0)

event = data.get("hook_event") or ""
session_id = data.get("session_id") or "default"
cwd = data.get("cwd") or "."

# State file to track first prompt per session
state_dir = os.path.join(cwd, ".claude", "tmp")
state_file = os.path.join(state_dir, f"local-{session_id}")

parts = []

# Inject LOCAL.md on first prompt or PreCompact
first_prompt = not os.path.isfile(state_file)
is_compaction = event == "PreCompact"

if first_prompt or is_compaction:
    for path in [
        os.path.expanduser("~/.claude/LOCAL.md"),
        os.path.join(cwd, "LOCAL.md"),
    ]:
        if os.path.isfile(path):
            try:
                with open(path) as f:
                    content = f.read().strip()
                if content:
                    parts.append(content)
            except OSError:
                pass

    # Mark session as seen
    if first_prompt:
        try:
            os.makedirs(state_dir, exist_ok=True)
            open(state_file, "w").close()
        except OSError:
            pass

# Re-inject key rules on continue/recap
prompt_lower = prompt.lower()
if not re.search(
    r"\b(don\'?t|not|never)\s+\w*\s*(continue|recap)", prompt_lower
):
    if re.search(
        r"\b(continue|recap|where\s+were\s+we|what\'?s\s+next)\b",
        prompt_lower,
    ):
        parts.append(RULES)

# Always inject RULES on compaction
if is_compaction:
    parts.append(RULES)

if parts:
    print(json.dumps({"ok": True, "systemMessage": "\n\n".join(parts)}))

sys.exit(0)
