#!/usr/bin/env python3
import json
import os
import re
import sys

DOCS_RULES = """Documentation naming rules:
- UPPERCASE files in root: CLAUDE.md, README.md, ARCHITECTURE.md, TODO.md, CHANGELOG.md, SPEC.md
- Organized in directories: use lowercase (specs/multi-tenancy.md, todos/general.md, plans/migration.md)
- Root standalone files use UPPERCASE (SPECv1.md, TODO_1.md)
- NEVER use lowercase for root documentation files (todo.md, readme.md)"""

COMMIT_RULES = """Commit rules:
- Format: "type(scope): Message" (scope optional), subject <= 72 chars (overflow -> second -m body)
- NEVER git add -A, NEVER git commit -a, NEVER amend, NEVER push, NEVER squash
- NEVER add Co-Authored-By, NEVER skip pre-commit hooks
- Pre-commit reformats on first run - ALWAYS retry commit once
Invoke /commit skill."""

AGENT_KEYWORDS = {
    'architecture': '/specs',
    'background': '/dispatch',
    'bugs': '/bugs',
    'ceo': '/ceo-eval',
    'cont': '/continue',
    'continue': '/continue',
    'create': '/create',
    'cto': '/cto-eval',
    'design': '/specs',
    'diagram': '/diagrams',
    'diary': '/diary',
    'dispatch': '/dispatch',
    'draft': '/pr-draft',
    'eval': '/create-eval',
    'explore': '/explore',
    'fin': '/fin',
    'fix': '/fix',
    'flowchart': '/diagrams',
    'haiku': '/haiku',
    'humanize': '/humanize',
    'inline': '/gh-comment',
    'merge': '/merge',
    'microcopy': '/writing',
    'novice': '/eye-13yo',
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
    'improve': '@improve',
    'visual': '@visual',
    'distill': '@distill',
    'review': '/review',
    'browse': '/browse',
}

CODEX_PATTERNS = [
    r'\bask\s+codex\b',
    r'\boracle\b',
    r'\bsecond\s+opinion\b',
]

ESCALATION_PATTERNS = [
    (r'(?<!\S)/(fable|opus)\b', {'fable': '/fable', 'opus': '/opus'}),
    (
        r'\b(?:use|spawn|run|invoke|switch to)\s+(fable|opus)\b',
        {'fable': '/fable', 'opus': '/opus'},
    ),
]


def exact_match(word, keywords):
    word = word.lower()
    if word in keywords:
        return keywords[word]
    # match singular/plural across a trailing 's' (bug<->bugs, spec<->specs).
    if word.endswith('s') and word[:-1] in keywords:
        return keywords[word[:-1]]
    if word + 's' in keywords:
        return keywords[word + 's']
    return None


META_PATTERNS = [
    r'\bhook\b',
    r'\bagent\b.*\b(check|fix|issue)',
    r'\b(check|fix|debug)\b.*(hook|agent|nudge|settings)',
    r'invoke.*agent',
]


def in_codex():
    return os.environ.get('KRONAEL_IN_CODEX') == '1'


def explicit_route(prompt):
    lower = prompt.lower()
    if not in_codex():
        for pattern in CODEX_PATTERNS:
            if re.search(pattern, lower):
                return '/codex'
    for pattern, routes in ESCALATION_PATTERNS:
        match = re.search(pattern, lower)
        if match:
            return routes.get(match.group(1))
    words = re.findall(r'\b[a-zA-Z]{2,}\b', prompt)
    for word in words:
        matched = exact_match(word, AGENT_KEYWORDS)
        if matched:
            return matched
    return None


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

    matched = explicit_route(prompt)

    if re.search(r'\bcommit\b', prompt, re.IGNORECASE):
        parts.append(COMMIT_RULES)
    elif matched:
        parts.append(f'info: Invoke {matched}.')

    if parts:
        print(json.dumps({'ok': True, 'systemMessage': '\n\n'.join(parts)}))

    sys.exit(0)


if __name__ == '__main__':
    main()
