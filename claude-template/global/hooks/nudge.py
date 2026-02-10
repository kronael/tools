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

prompt = data.get("prompt") or ""
if not isinstance(prompt, str):
    sys.exit(0)

COMMIT_RULES = """Commit rules:
- NEVER git add -A
- NEVER git commit --amend
- NEVER add Co-Authored-By
- Pre-commit reformats on first run - ALWAYS retry commit (2 attempts)
- Format: "[section] Message"
Invoke /commit agent."""

AGENTS = [
    (r"\b(readme|docs|documentation|document|arch)\b", "/readme"),
    (r"\b(learn|extract|pattern|skill)\b", "/learn"),
    (r"\b(refine|finalize|finish|complete|ship|wrap.?up)\b", "/refine"),
    (r"\b(improve|enhance|fix|cleanup|refactor|optimize|polish)\b", "/improve"),
]

# Skip if prompt is about hooks, agents, or meta-instructions
META_PATTERNS = [
    r"\bhook\b",
    r"\bagent\b.*\b(check|fix|issue)",
    r"\b(check|fix|debug)\b.*(hook|agent|nudge|settings)",
    r"invoke.*agent",
]
if any(re.search(p, prompt, re.IGNORECASE) for p in META_PATTERNS):
    sys.exit(0)

# Check commit first (special case with rules)
if re.search(r"\b(commit|save|checkpoint)\b", prompt, re.IGNORECASE):
    print(json.dumps({"ok": True, "systemMessage": COMMIT_RULES}))
    sys.exit(0)

for pattern, agent in AGENTS:
    if re.search(pattern, prompt, re.IGNORECASE):
        print(json.dumps({"ok": True, "systemMessage": f"Invoke {agent} agent."}))
        break

sys.exit(0)
