#!/usr/bin/env python3
"""Stop hook: measure the final reply against the caveman budget and block once.

The caps are `output-styles/caveman.md` § Budget: 20 rendered 80-column lines
outside code fences, 5 bullets per list, 2 sentences per bullet.
`test_style_lint.py` pins the numbers to that file. The hook runs only while
`~/.claude/settings.json` selects the caveman style, blocks with the measured
miss once per turn (`stop_hook_active` is set on the rewrite), and never
reads the transcript.
"""

import json
import math
import os
import re
import sys

STYLE = 'caveman'
CAP_LINES = 20
CAP_BULLETS = 5
CAP_SENTENCES = 2
FENCE = re.compile(r'^[ \t]*(```|~~~)[\s\S]*?^[ \t]*\1[ \t]*$', re.MULTILINE)
BULLET = re.compile(r'^\s*(?:[-*+]|\d+[.)])\s+')
INLINE_CODE = re.compile(r'`[^`]*`')
SENTENCE_END = re.compile(r'[.!?](?=\s|$)')
LINK = re.compile(r'\[([^\]]*)\]\([^)]*\)')


def visible(message):
    return LINK.sub(r'\1', FENCE.sub('', message)).strip()


def rendered_lines(text):
    return sum(1 if not line.strip() else math.ceil(len(line) / 80) for line in text.split('\n'))


def sentences(line):
    return max(1, len(SENTENCE_END.findall(INLINE_CODE.sub('code', line))))


def measure(text):
    lists = []
    run = 0
    bullet_sentences = [0]
    for line in text.split('\n'):
        if BULLET.match(line):
            run += 1
            bullet_sentences.append(sentences(BULLET.sub('', line)))
            continue
        if run and not line.strip():
            continue
        if run and line[:1].isspace():
            bullet_sentences[-1] += sentences(line)
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


def misses(measured):
    found = []
    if measured['lines'] > CAP_LINES:
        found.append(f'{measured["lines"]} rendered lines, cap {CAP_LINES}')
    if measured['bullets'] > CAP_BULLETS:
        found.append(f'a list of {measured["bullets"]} bullets, cap {CAP_BULLETS}')
    if measured['sentences'] > CAP_SENTENCES:
        found.append(f'a bullet of {measured["sentences"]} sentences, cap {CAP_SENTENCES}')
    return found


def reason(found):
    return (
        'The reply breaks the caveman budget: '
        + '; '.join(found)
        + '. Send the final answer again within the budget: keep every fact, '
        'path, command and uncertainty, cut sentences and bullets. '
        'Code fences and a document the user asked for do not count.'
    )


def selected_style(home):
    try:
        with open(os.path.join(home, '.claude', 'settings.json')) as f:
            return json.load(f).get('outputStyle')
    except (OSError, ValueError, AttributeError):
        return None


def check(data, home):
    if data.get('stop_hook_active') or selected_style(home) != STYLE:
        return None
    message = data.get('last_assistant_message')
    if not isinstance(message, str):
        return None
    found = misses(measure(visible(message)))
    if not found:
        return None
    return {'decision': 'block', 'reason': reason(found)}


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        return
    if not isinstance(data, dict):
        return
    out = check(data, os.path.expanduser('~'))
    if out:
        print(json.dumps(out))


if __name__ == '__main__':
    main()
