#!/usr/bin/env python3
import json
import math
import os
import re
import secrets
import sys

from lib.state import session_state

TOOL = 'SendUserMessage'
CAP_LINES = 20
LIFT = 3
COLUMNS = 80
OVERRIDE = 'override'
FENCE = re.compile(r'^[ \t]*((`|~)\2{2,})(?!\2)[\s\S]*?^[ \t]*\1\2*[ \t]*$', re.MULTILINE)
LINK = re.compile(r'\[([^\]]*)\]\([^)]*\)')


def caveman_selected(home):
    try:
        with open(os.path.join(home, '.claude', 'settings.json')) as f:
            return json.load(f).get('outputStyle') == 'caveman'
    except (OSError, ValueError, AttributeError):
        return False


def rendered_lines(message):
    text = LINK.sub(r'\1', FENCE.sub('', message)).strip()
    return sum(
        1 if not line.strip() else math.ceil(len(line) / COLUMNS) for line in text.split('\n')
    )


def take_key(stamp):
    """The pending key and the ceiling it lifts to; a ceiling of 0 is none."""
    try:
        with open(stamp) as f:
            ceiling, _, key = f.read().partition(' ')
        os.remove(stamp)
        return key, int(ceiling)
    except (OSError, ValueError):
        return None, CAP_LINES


def issue_key(stamp, ceiling):
    key = secrets.token_hex(4)
    try:
        with open(stamp, 'w') as f:
            f.write(f'{ceiling} {key}')
    except OSError:
        return None
    return key


def reason(lines, ceiling, lifted, key):
    ask, reach = (
        ('asked for a longer reply', f'up to {lifted} lines')
        if lifted
        else ('asked for it a second time', 'at any length')
    )
    return (
        f'Not delivered: the message is {lines} rendered {COLUMNS}-column lines '
        f'and the caveman ceiling is {ceiling}. The user has not seen it. '
        'Cut it per the caveman skill. Code fences do not count. '
        f'If the user {ask}, resend the message with one more line at its top. '
        'The hook removes that line, and its key works once, on the next message only, '
        f'{reach}. That line is: {OVERRIDE} {key}'
    )


def check(data, home):
    if data.get('tool_name') != TOOL or not caveman_selected(home):
        return None
    tool_input = data.get('tool_input')
    message = tool_input.get('message') if isinstance(tool_input, dict) else None
    if not isinstance(message, str):
        return None
    stamp = session_state('caveman-key', data.get('session_id'))
    if stamp is None:
        return None
    pending, ceiling = take_key(stamp)
    head, _, body = message.partition('\n')
    passed = None
    if pending and head == f'{OVERRIDE} {pending}':
        message = body.lstrip('\n')
        passed = {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'updatedInput': {**tool_input, 'message': message},
            }
        }
    else:
        ceiling = CAP_LINES
    lines = rendered_lines(message)
    if not ceiling or lines <= ceiling:
        return passed
    lifted = 0 if passed else LIFT * CAP_LINES
    key = issue_key(stamp, lifted)
    if not key:
        return passed
    return {
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': 'deny',
            'permissionDecisionReason': reason(lines, ceiling, lifted, key),
        }
    }


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
