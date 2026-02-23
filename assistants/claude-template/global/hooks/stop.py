#!/usr/bin/env python3
"""Stop hook: nudge commit if uncommitted changes exist."""
import json
import subprocess
import sys

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError, ValueError):
    sys.exit(0)

if not isinstance(data, dict):
    sys.exit(0)

if data.get("stop_hook_active"):
    sys.exit(0)

r = subprocess.run(
    ["git", "status", "--porcelain", "-uno"],
    capture_output=True, text=True, timeout=5,
    cwd=data.get("cwd", "."),
)
if r.returncode != 0 or not r.stdout.strip():
    sys.exit(0)

diff = subprocess.run(
    ["git", "diff", "--stat"],
    capture_output=True, text=True, timeout=5,
    cwd=data.get("cwd", "."),
)
stats = diff.stdout.strip()
msg = "Uncommitted changes detected."
if stats:
    msg += "\n" + stats
msg += "\nConsider running /commit."

print(json.dumps({"decision": "block", "reason": msg}))
