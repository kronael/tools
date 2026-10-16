#!/usr/bin/env python3
"""Caveman adherence: measure the final reply at Stop, remember the result in
kvs, and point at the broken rule where the next reply is written.

The session's level (kvs key `caveman`) rises by one on a miss and falls by one
on a compliant reply. 0: silent. 1: one measured pointer on the next prompt.
2: the pointer also after every tool call. 3: the same, and a reply over twice
its cap gets one revision request at Stop. Stop never injects anything else.
Without kvs the hook has no memory and stays silent.
"""

import json
import math
import re
import sys

from lib import kvs
from lib.reminder import context
from lib.reminder import emit
from lib.reminder import reminder
from lib.state import hook_event

STYLE = 'caveman'
CAP_LINES = 20
CAP_LINES_REPORT = 25
REPORT_TOOLS = 4
CAP_BULLETS = 5
CAP_SENTENCES = 2
MAX_LEVEL = 3
GROSS = 2
STATE_KEY = 'caveman'
TOOLS_KEY = 'tools'
SILENT_BLOCK = re.compile(r'<(?:status|think)>[\s\S]*?</(?:status|think)>')
FENCE = re.compile(r'^[ \t]*```[\s\S]*?^[ \t]*```[ \t]*$', re.MULTILINE)
BULLET = re.compile(r'^\s*(?:[-*]|\d+\.)\s+')
SENTENCE_END = re.compile(r'[.!?](?=\s|$)')


def visible(message):
    return FENCE.sub('', SILENT_BLOCK.sub('', message)).strip()


def rendered_lines(text):
    return sum(1 if not line.strip() else math.ceil(len(line) / 80) for line in text.split('\n'))


def sentences(line):
    return max(1, len(SENTENCE_END.findall(re.sub(r'`[^`]*`', 'code', line))))


def measure(text):
    lists = []
    run = 0
    bullet_sentences = [0]
    for line in text.split('\n'):
        if BULLET.match(line):
            run += 1
            bullet_sentences.append(sentences(BULLET.sub('', line)))
            continue
        if run:
            lists.append(run)
        run = 0
    if run:
        lists.append(run)
    return {
        'lines': rendered_lines(text),
        'bullets': max(lists, default=0),
        'sentences': max(bullet_sentences),
    }


def cap_for(tools):
    return CAP_LINES_REPORT if tools >= REPORT_TOOLS else CAP_LINES


def find_miss(measured, cap_lines):
    """The first Budget rule the reply broke, with its measured value and cap."""
    for metric, cap in (
        ('lines', cap_lines),
        ('bullets', CAP_BULLETS),
        ('sentences', CAP_SENTENCES),
    ):
        if measured[metric] > cap:
            return {metric: measured[metric], 'cap': cap}
    return None


def load(session, cwd):
    raw = kvs.get(STATE_KEY, session, cwd)
    try:
        state = json.loads(raw) if raw else {}
    except ValueError:
        state = {}
    return state if isinstance(state, dict) else {}


def save(state, session, cwd):
    kvs.set(STATE_KEY, json.dumps(state, separators=(',', ':')), session, cwd)


def pointer(state):
    level = int(state.get('level') or 0)
    if level < 1:
        return None
    measured = {key: value for key, value in state.items() if key not in {'level', 'miss', 'ok'}}
    return reminder(STYLE, 'budget', **measured)


def on_prompt(data):
    """The pointer for a new turn; resets the turn's tool count."""
    session = data.get('session_id')
    cwd = data.get('cwd')
    kvs.set(TOOLS_KEY, 0, session, cwd)
    return pointer(load(session, cwd))


def on_tool(data):
    session = data.get('session_id')
    cwd = data.get('cwd')
    kvs.incr(TOOLS_KEY, session, cwd)
    state = load(session, cwd)
    if int(state.get('level') or 0) < 2:
        return None
    return pointer(state)


def on_stop(data):
    if data.get('stop_hook_active'):
        return None
    message = data.get('last_assistant_message')
    if not isinstance(message, str):
        return None
    text = visible(message)
    if not text:
        return None
    session = data.get('session_id')
    cwd = data.get('cwd')
    previous = load(session, cwd)
    level = int(previous.get('level') or 0)
    counts = {'miss': int(previous.get('miss') or 0), 'ok': int(previous.get('ok') or 0)}
    last = {key: value for key, value in previous.items() if key not in {'level', 'miss', 'ok'}}
    tools = int(kvs.get(TOOLS_KEY, session, cwd) or 0)
    miss = find_miss(measure(text), cap_for(tools))
    if miss:
        level = min(MAX_LEVEL, level + 1)
        counts['miss'] += 1
        last = miss
    else:
        level = max(0, level - 1)
        counts['ok'] += 1
    state = {'level': level, **counts, **last}
    save(state, session, cwd)
    gross = miss and 'lines' in miss and miss['lines'] > GROSS * miss['cap']
    if level == MAX_LEVEL and gross:
        return reminder(
            STYLE,
            'budget',
            'revise the final answer to the cap; keep the evidence and the uncertainty',
            **miss,
        )
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        return
    if not isinstance(data, dict) or not kvs.BINARY:
        return
    event = hook_event(data)
    if event == 'PostToolUse':
        line = on_tool(data)
    elif event == 'Stop':
        line = on_stop(data)
    else:
        return
    if line:
        emit(context(event, line))


if __name__ == '__main__':
    main()
