#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path

from lib.state import session_state
from style_nudge import read_reminder

DOCS_RULES = """Documentation naming rules (layout: the readme skill's topology.md):
- Organized in directories: use lowercase (specs/multi-tenancy.md, docs/setup.md); NO todos/ or plans/ dir: plans and ship records live under ~/.claude/ (ship skill § Work record), never in the repo
- NEVER use lowercase for root documentation files (todo.md, readme.md)"""

COMMIT_RULES = """Commit rules:
- Format: "type(scope): Message" (scope optional), subject <= 72 chars (overflow -> second -m body)
- ALWAYS commit in detached HEAD - NEVER on or creating a branch
- NEVER git add -A, NEVER git commit -a, NEVER amend, NEVER push, NEVER squash a pushed commit (unpushed ones only via /squash)
- NEVER skip pre-commit hooks
- Pre-commit reformats on first run - ALWAYS retry commit once
Invoke /commit skill."""

SOLVE_NUDGE = (
    'New task (first prompt this session): run /solve before acting — it '
    'loads diary + memory context and routes to the right skill. Skip only '
    'if this prompt is a direct continuation of work already in context.'
)

SKILL_KEYWORDS = {
    'architecture': '/specs',
    'background': '/dispatch',
    'bugs': '/bugs',
    'ceo': '/eval',
    'cont': '/continue',
    'continue': '/continue',
    'create': '/create',
    'cto': '/eval',
    'design': '/specs',
    'diagram': '/diagrams',
    'diary': '/diary',
    'dispatch': '/dispatch',
    'draft': '/pr-draft',
    'eval': '/eval',
    'fin': '/fin',
    'fix': '/fix',
    'flowchart': '/diagrams',
    'humanize': '/humanize',
    'inline': '/gh-comment',
    'merge': '/merge',
    'microcopy': '/writing',
    'novice': '/eval',
    'pentest': '/eval',
    'recall': '/recall-memories',
    'refine': '/refine',
    'release': '/release',
    'roi': '/eval',
    'scavenge': '/scavenge',
    'security': '/eval',
    'ship': '/ship',
    'sonnet': '/sonnet',
    'spec': '/specs',
    'specs': '/specs',
    'test': '/software',
    'testing': '/software',
    'thread': '/tweet',
    'tooltip': '/writing',
    'tweet': '/tweet',
    'ux': '/eval',
    'usability': '/eval',
    'walkthrough': '/eval',
    'wisdom': '/wisdom',
    'writing': '/writing',
    'readme': '/readme',
    'improve': '/improve',
    'visual': '/visual',
    'distill': '/distill',
    'review': '/review',
    'browse': '/browse',
}

CODEX_PATTERNS = [
    r'\bask\s+(?:codex|astra)\b',
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


# Claude Code spellings only. codex_hook.py rewrites `/name` to Codex's
# `@name`, and a spelling written here instead never reaches that rewriter.
def explicit_route(prompt, harness=None):
    lower = prompt.lower()
    if harness != 'codex':
        # A leading slash command only: "use astra" is as likely the vector DB
        # as the skill, and "/astra/data" a path.
        if re.match(r'\s*/astra(?![\w/.-])', lower):
            return '/astra'
        for pattern in CODEX_PATTERNS:
            if re.search(pattern, lower):
                return '/astra'
    for pattern, routes in ESCALATION_PATTERNS:
        match = re.search(pattern, lower)
        if match:
            return routes.get(match.group(1))
    words = re.findall(r'\b[a-zA-Z]{2,}\b', prompt)
    for word in words:
        matched = exact_match(word, SKILL_KEYWORDS)
        if matched:
            return matched
    return None


def first_prompt_of_session(session_id):
    """True the first time a session submits a prompt, recording a marker so
    later prompts stay silent. False when the marker exists or cannot be
    written, so an unwritable state dir never turns the nudge into per-prompt
    spam."""
    marker = session_state('solve-nudge', session_id)
    if marker is None or os.path.exists(marker):
        return False
    try:
        open(marker, 'w').close()
    except OSError:
        return False
    return True


def emit(text):
    # additionalContext is the only UserPromptSubmit field the model reads;
    # systemMessage renders in the transcript for the user and never reaches
    # the model.
    print(
        json.dumps(
            {
                'hookSpecificOutput': {
                    'hookEventName': 'UserPromptSubmit',
                    'additionalContext': text,
                },
            }
        )
    )


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

    try:
        reminder = read_reminder(Path.home())
    except (OSError, TypeError, ValueError):
        reminder = None

    if any(re.search(p, prompt, re.IGNORECASE) for p in META_PATTERNS):
        if reminder:
            emit(reminder)
        sys.exit(0)

    parts = []

    if (
        prompt.strip()
        and first_prompt_of_session(data.get('session_id'))
        and not re.search(r'/solve\b', prompt)
    ):
        parts.append(SOLVE_NUDGE)

    if reminder:
        parts.append(reminder)

    if re.search(r'\b(todo|readme|changelog|spec|architecture)\b|\.md\b', prompt, re.IGNORECASE):
        parts.append(DOCS_RULES)

    matched = explicit_route(prompt, data.get('harness'))

    if re.search(r'\bcommit\b', prompt, re.IGNORECASE):
        parts.append(COMMIT_RULES)
    elif matched:
        parts.append(f'info: Invoke {matched}.')

    if parts:
        emit('\n\n'.join(parts))

    sys.exit(0)


if __name__ == '__main__':
    main()
