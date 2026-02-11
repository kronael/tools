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

DOCS_RULES = """Documentation naming rules:
- UPPERCASE files in root: CLAUDE.md, README.md, ARCHITECTURE.md, TODO.md, CHANGELOG.md, SPEC.md
- Organized in directories: use lowercase (specs/multi-tenancy.md, todos/general.md, plans/migration.md)
- Root standalone files use UPPERCASE (SPECv1.md, TODO_1.md)
- NEVER use lowercase for root documentation files (todo.md, readme.md)"""

COMMIT_RULES = """Commit rules:
- NEVER git add -A
- NEVER git commit --amend
- NEVER add Co-Authored-By
- Pre-commit reformats on first run - ALWAYS retry commit (2 attempts)
- Format: "[section] Message"
Invoke /commit agent."""

# Exact keyword → agent mapping (1:1, specific)
AGENT_KEYWORDS = {
    "ship": "/ship",
    "build": "/build",
    "refine": "/refine",
    "readme": "/readme",
    "learn": "/learn",
    "improve": "/improve",
    "visual": "/visual",
    "commit": "/commit",
}


def edit_distance(a, b):
    """Levenshtein distance between two strings."""
    if len(a) < len(b):
        return edit_distance(b, a)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = curr
    return prev[-1]


def fuzzy_match(word, keywords, max_dist=2):
    """Match word against keywords with edit distance tolerance."""
    word = word.lower()
    # Exact match first
    if word in keywords:
        return keywords[word]
    # Fuzzy: only for words >= 4 chars (avoid false positives)
    if len(word) < 4:
        return None
    for kw, agent in keywords.items():
        if len(kw) < 4:
            continue
        dist = edit_distance(word, kw)
        # Allow dist=1 for short words (4-5), dist=2 for longer
        allowed = 1 if len(kw) <= 5 else max_dist
        if dist <= allowed:
            return agent
    return None


# Skip if prompt is about hooks, agents, or meta-instructions
META_PATTERNS = [
    r"\bhook\b",
    r"\bagent\b.*\b(check|fix|issue)",
    r"\b(check|fix|debug)\b.*(hook|agent|nudge|settings)",
    r"invoke.*agent",
]
if any(re.search(p, prompt, re.IGNORECASE) for p in META_PATTERNS):
    sys.exit(0)

parts = []

# Context: docs naming convention
if re.search(r"\b(todo|readme|changelog|spec|architecture)\b|\.md\b", prompt, re.IGNORECASE):
    parts.append(DOCS_RULES)

# Extract words and fuzzy-match against agent keywords
words = re.findall(r"\b[a-zA-Z]{3,}\b", prompt)
matched_agent = None
for word in words:
    matched_agent = fuzzy_match(word, AGENT_KEYWORDS)
    if matched_agent:
        break

if matched_agent == "/commit":
    parts.append(COMMIT_RULES)
elif matched_agent:
    parts.append(f"Invoke {matched_agent} agent.")

if parts:
    print(json.dumps({"ok": True, "systemMessage": "\n\n".join(parts)}))

sys.exit(0)
