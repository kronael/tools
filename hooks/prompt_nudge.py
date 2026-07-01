#!/usr/bin/env python3
import json
import re
import sys

DOCS_RULES = """Documentation naming rules:
- UPPERCASE files in root: CLAUDE.md, README.md, ARCHITECTURE.md, TODO.md, CHANGELOG.md, SPEC.md
- Organized in directories: use lowercase (specs/multi-tenancy.md, todos/general.md, plans/migration.md)
- Root standalone files use UPPERCASE (SPECv1.md, TODO_1.md)
- NEVER use lowercase for root documentation files (todo.md, readme.md)"""

COMMIT_RULES = """Commit rules:
- Format: "[section] Message", subject <= 72 chars (overflow -> second -m body)
- NEVER git add -A, NEVER git commit -a, NEVER amend, NEVER push, NEVER squash
- NEVER add Co-Authored-By, NEVER skip pre-commit hooks
- Pre-commit reformats on first run - ALWAYS retry commit once
Invoke /commit skill."""

AGENT_KEYWORDS = {
    'architecture': '/specs',
    'background': '/dispatch',
    'bugs': '/bugs',
    'ceo': '/ceo-eval',
    'codex': '/codex',
    'create': '/create',
    'cto': '/cto-eval',
    'design': '/specs',
    'diagram': '/diagrams',
    'diary': '/diary',
    'dispatch': '/dispatch',
    'draft': '/pr-draft',
    'eval': '/create-eval',
    'explore': '/explore',
    'fable': '/fable',
    'fin': '/fin',
    'fix': '/fix',
    'flowchart': '/diagrams',
    'haiku': '/haiku',
    'humanize': '/humanize',
    'inline': '/gh-comment',
    'merge': '/merge',
    'microcopy': '/writing',
    'novice': '/eye-13yo',
    'opus': '/opus',
    'oracle': '/oracle',
    'pentest': '/hacker-eval',
    'recall': '/recall-memories',
    'refine': '/refine',
    'release': '/release',
    'roi': '/ceo-eval',
    'scavenge': '/scavenge',
    'security': '/hacker-eval',
    'ship': '/ship',
    'sonnet': '/sonnet',
    'spec': '/specs',
    'specs': '/specs',
    'test': '/testing',
    'testing': '/testing',
    'thread': '/tweet',
    'tooltip': '/writing',
    'tweet': '/tweet',
    'ux': '/eye-13yo',
    'usability': '/eye-13yo',
    'walkthrough': '/eye-13yo',
    'wisdom': '/wisdom',
    'writing': '/writing',
    'readme': '@readme',
    'learn': '@learn',
    'improve': '@improve',
    'visual': '@visual',
    'distill': '@distill',
    'review': '/review',
    'browse': '/browse',
}


def edit_distance(a, b):
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


def fuzzy_match(word, keywords):
    word = word.lower()
    if word in keywords:
        return keywords[word]
    # match singular/plural across a trailing 's' (bug<->bugs, spec<->specs)
    if word.endswith('s') and word[:-1] in keywords:
        return keywords[word[:-1]]
    if word + 's' in keywords:
        return keywords[word + 's']
    if len(word) < 4:
        return None
    for kw, agent in keywords.items():
        if len(kw) < 4:
            continue
        dist = edit_distance(word, kw)
        if dist <= max(1, len(kw) // 4):
            return agent
    return None


META_PATTERNS = [
    r'\bhook\b',
    r'\bagent\b.*\b(check|fix|issue)',
    r'\b(check|fix|debug)\b.*(hook|agent|nudge|settings)',
    r'invoke.*agent',
]


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        sys.exit(0)

    if not isinstance(data, dict):
        sys.exit(0)

    prompt = data.get('prompt') or ''
    if not isinstance(prompt, str):
        sys.exit(0)

    if any(re.search(p, prompt, re.IGNORECASE) for p in META_PATTERNS):
        sys.exit(0)

    parts = []

    if re.search(r'\b(todo|readme|changelog|spec|architecture)\b|\.md\b', prompt, re.IGNORECASE):
        parts.append(DOCS_RULES)

    words = re.findall(r'\b[a-zA-Z]{2,}\b', prompt)
    matched = None
    for word in words:
        matched = fuzzy_match(word, AGENT_KEYWORDS)
        if matched:
            break

    if re.search(r'\bcommit\b', prompt, re.IGNORECASE):
        parts.append(COMMIT_RULES)
    elif matched:
        parts.append(f'Invoke {matched}.')

    if parts:
        print(json.dumps({'ok': True, 'systemMessage': '\n\n'.join(parts)}))

    sys.exit(0)


if __name__ == '__main__':
    main()
