#!/usr/bin/env python3
import json
import os
import re
import sys
import time

from lib.state import hook_event
from lib.state import session_state

SOLVE_NUDGE = (
    'New task (first prompt this session): run /solve before acting — it '
    'loads diary + memory context and routes to the right skill. Skip only '
    'if this prompt is a direct continuation of work already in context.'
)

IDLE_MINUTES = 30

IDLE_NUDGE = (
    'New task? This prompt follows an idle gap: run /solve before acting '
    'unless it continues the work already in context.'
)

SUBAGENT_NUDGE = (
    'New task (subagent brief): run /solve before acting — it routes the '
    'brief to the skill that owns it.'
)

HARNESS_AGENTS = frozenset({'Explore', 'Plan', 'claude-code-guide', 'statusline-setup'})

RESUMED_SESSION = re.compile(r'\s*This session is being continued from a previous conversation')

SKILL_KEYWORDS = {
    'browse': '/browse',
    'bugs': '/bugs',
    'ceo': '/eval',
    'commit': '/commit',
    'cont': '/continue',
    'continue': '/continue',
    'cto': '/eval',
    'diagram': '/diagrams',
    'diary': '/diary',
    'dispatch': '/dispatch',
    'distill': '/distill',
    'eval': '/eval',
    'fin': '/fin',
    'flowchart': '/diagrams',
    'humanize': '/humanize',
    'improve': '/improve',
    'merge': '/merge',
    'microcopy': '/writing',
    'novice': '/eval',
    'pentest': '/eval',
    'readme': '/readme',
    'recall': '/recall-memories',
    'refine': '/refine',
    'release': '/release',
    'review': '/review',
    'roi': '/eval',
    'scavenge': '/scavenge',
    'ship': '/ship',
    'spec': '/specs',
    'specs': '/specs',
    'tooltip': '/writing',
    'tweet': '/tweet',
    'usability': '/eval',
    'ux': '/eval',
    'visual': '/visual',
    'walkthrough': '/eval',
    'wisdom': '/wisdom',
    'writing': '/writing',
}

MODEL_COMMAND_PATTERN = r'^\s*[/@](?:astra|sol|luna|terra|haiku|sonnet|opus|fable)(?![\w/.-])'

MODEL_PATTERNS = [
    (MODEL_COMMAND_PATTERN, '/dispatch'),
    (r'\bask\s+(?:astra|sol|luna|terra|haiku|sonnet|opus|fable)\b', '/dispatch'),
    (
        r'\b(?:use|spawn|run|invoke|switch to)\s+(?:luna|terra|haiku|sonnet|opus|fable)\b',
        '/dispatch',
    ),
    (
        r'\b(?:use|spawn|run|invoke|switch to)\s+(?:astra|sol)\s+(?:for|to|at|on|with)\b',
        '/dispatch',
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


def explicit_route(prompt):
    lower = prompt.lower()
    command = re.match(r'\s*[/@]([a-z][a-z-]*)(?![\w/.-])', lower)
    if command:
        name = command.group(1)
        if name in {'codex', 'claude', 'oracle'}:
            return f'/{name}'
        if name in SKILL_KEYWORDS:
            return SKILL_KEYWORDS[name]
        if not re.match(MODEL_COMMAND_PATTERN, lower):
            return None
    if re.search(r'\bdispatch\b', lower):
        return '/dispatch'
    if re.search(r'\boracle\b|\bsecond\s+opinion\b', lower):
        return '/oracle'
    for pattern, route in MODEL_PATTERNS:
        if re.search(pattern, lower):
            return route
    provider = re.search(r'\b(?:ask|use|run|invoke)\s+(codex|claude)\b', lower)
    if provider:
        return f'/{provider.group(1)}'
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


def minutes_since_prompt(session_id):
    """Minutes since this session's previous prompt, stamping this one so the
    next call measures from it. None before the first prompt or when the
    state dir is unusable, so an unwritable dir never nudges every prompt."""
    marker = session_state('solve-nudge', session_id)
    if marker is None:
        return None
    try:
        previous = os.stat(marker).st_mtime
        os.utime(marker, None)
    except OSError:
        return None
    return (time.time() - previous) / 60


def is_routed(prompt, matched):
    return bool(matched or prompt.lstrip().startswith('/') or RESUMED_SESSION.match(prompt))


def emit(event, text):
    print(
        json.dumps(
            {
                'hookSpecificOutput': {
                    'hookEventName': event,
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

    if hook_event(data) == 'SubagentStart':
        if data.get('agent_type') not in HARNESS_AGENTS:
            emit('SubagentStart', SUBAGENT_NUDGE)
        sys.exit(0)

    prompt = data.get('prompt') or ''
    if not isinstance(prompt, str):
        sys.exit(0)

    if any(re.search(p, prompt, re.IGNORECASE) for p in META_PATTERNS):
        sys.exit(0)

    parts = []
    matched = explicit_route(prompt)
    session_id = data.get('session_id')

    if prompt.strip():
        if first_prompt_of_session(session_id):
            if not re.search(r'/solve\b', prompt):
                parts.append(SOLVE_NUDGE)
        else:
            idle = minutes_since_prompt(session_id)
            if idle is not None and idle >= IDLE_MINUTES and not is_routed(prompt, matched):
                parts.append(IDLE_NUDGE)

    if matched:
        parts.append(f'info: Invoke {matched}.')

    if parts:
        emit('UserPromptSubmit', '\n\n'.join(parts))

    sys.exit(0)


if __name__ == '__main__':
    main()
