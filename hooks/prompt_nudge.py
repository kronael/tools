#!/usr/bin/env python3
"""UserPromptSubmit: point at the skills a prompt calls for.

Every line is a pointer (lib/reminder.py): the first prompt of a session gets
`solve` and the host-local LOCAL.md files, a prompt that names a skill's
keyword gets that skill, "commit" gets `commit`, a document mention gets
`readme`, and the caveman pointer comes from style_nudge when the last reply
missed its budget.
"""

import json
import os
import re
import sys

import style_nudge
from lib import kvs
from lib.reminder import context
from lib.reminder import emit
from lib.reminder import file
from lib.reminder import reminder
from lib.reminder import skill

SKILL_KEYWORDS = {
    'architecture': 'specs',
    'background': 'dispatch',
    'bugs': 'bugs',
    'ceo': 'eval',
    'cont': 'continue',
    'continue': 'continue',
    'create': 'create',
    'cto': 'eval',
    'design': 'specs',
    'diagram': 'diagrams',
    'diary': 'diary',
    'dispatch': 'dispatch',
    'draft': 'pr-draft',
    'eval': 'eval',
    'fin': 'fin',
    'fix': 'fix',
    'flowchart': 'diagrams',
    'humanize': 'humanize',
    'inline': 'gh-comment',
    'merge': 'merge',
    'microcopy': 'writing',
    'novice': 'eval',
    'pentest': 'eval',
    'recall': 'recall-memories',
    'refine': 'refine',
    'release': 'release',
    'roi': 'eval',
    'scavenge': 'scavenge',
    'security': 'eval',
    'ship': 'ship',
    'sonnet': 'sonnet',
    'spec': 'specs',
    'specs': 'specs',
    'test': 'software',
    'testing': 'software',
    'thread': 'tweet',
    'tooltip': 'writing',
    'tweet': 'tweet',
    'ux': 'eval',
    'usability': 'eval',
    'walkthrough': 'eval',
    'wisdom': 'wisdom',
    'writing': 'writing',
    'readme': 'readme',
    'improve': 'improve',
    'visual': 'visual',
    'distill': 'distill',
    'review': 'review',
    'browse': 'browse',
}

CODEX_PATTERNS = [
    r'\bask\s+(?:codex|astra)\b',
    r'\boracle\b',
    r'\bsecond\s+opinion\b',
]

TIERS = ('fable', 'haiku', 'luna', 'opus', 'terra')
TIER_PATTERN = '|'.join(TIERS)
ESCALATION_PATTERNS = [
    rf'(?<!\S)/({TIER_PATTERN})\b',
    rf'\b(?:use|spawn|run|invoke|switch to)\s+({TIER_PATTERN})\b',
]

META_PATTERNS = [
    r'\bhook\b',
    r'\bagent\b.*\b(check|fix|issue)',
    r'\b(check|fix|debug)\b.*(hook|agent|nudge|settings)',
    r'invoke.*agent',
]

LOCAL_FILES = ('~/.claude/LOCAL.md', 'LOCAL.md')


def exact_match(word, keywords):
    word = word.lower()
    if word in keywords:
        return keywords[word]
    if word.endswith('s') and word[:-1] in keywords:
        return keywords[word[:-1]]
    if word + 's' in keywords:
        return keywords[word + 's']
    return None


def explicit_route(prompt, harness=None):
    """The skill a prompt names, or None. Codex never gets routed to itself."""
    lower = prompt.lower()
    if harness != 'codex':
        if re.match(r'\s*/astra(?![\w/.-])', lower):
            return 'astra'
        for pattern in CODEX_PATTERNS:
            if re.search(pattern, lower):
                return 'astra'
    for pattern in ESCALATION_PATTERNS:
        match = re.search(pattern, lower)
        if match:
            return match.group(1)
    for word in re.findall(r'\b[a-zA-Z]{2,}\b', prompt):
        matched = exact_match(word, SKILL_KEYWORDS)
        if matched:
            return matched
    return None


def is_first_prompt(data):
    return kvs.set('prompted', 1, data.get('session_id'), data.get('cwd'), if_old='')


def local_pointers(cwd):
    lines = []
    for name in LOCAL_FILES:
        path = os.path.expanduser(name) if name.startswith('~') else os.path.join(cwd or '.', name)
        if os.path.isfile(path):
            lines.append(file(name if name.startswith('~') else path))
    return lines


def lines_for(prompt, data):
    if any(re.search(pattern, prompt, re.IGNORECASE) for pattern in META_PATTERNS):
        pointer = style_nudge.on_prompt(data)
        return [pointer] if pointer else []
    lines = []
    if prompt.strip() and is_first_prompt(data):
        if not re.search(r'/solve\b', prompt):
            lines.append(reminder('solve', text='first prompt: route the task before acting'))
        lines.extend(local_pointers(data.get('cwd')))
    pointer = style_nudge.on_prompt(data)
    if pointer:
        lines.append(pointer)
    if re.search(r'\b(todo|readme|changelog|spec|architecture)\b|\.md\b', prompt, re.IGNORECASE):
        lines.append(skill('readme'))
    matched = explicit_route(prompt, data.get('harness'))
    if re.search(r'\bcommit\b', prompt, re.IGNORECASE):
        lines.append(skill('commit'))
    elif matched and skill(matched) not in lines:
        lines.append(skill(matched))
    return lines


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        return
    if not isinstance(data, dict):
        return
    prompt = data.get('prompt') or ''
    if not isinstance(prompt, str):
        return
    lines = lines_for(prompt, data)
    if lines:
        emit(context('UserPromptSubmit', *lines))


if __name__ == '__main__':
    main()
