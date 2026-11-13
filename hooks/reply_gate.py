#!/usr/bin/env python3
import json
import math
import os
import re
import secrets
import sys

from lib.caveman import caveman_selected
from lib.state import session_state

TOOL = 'SendUserMessage'
CAP_LINES = 20
COLUMNS = 80
OVERRIDE = 'override'
FENCE = re.compile(r'^[ \t]*((`|~)\2{2,}+)[\s\S]*?^[ \t]*\1\2*[ \t]*$', re.MULTILINE)
LINK = re.compile(r'\[([^\]]*)\]\([^)]*\)')


def rendered_lines(message):
    text = LINK.sub(r'\1', FENCE.sub('', message)).strip()
    return sum(
        1 if not line.strip() else math.ceil(len(line) / COLUMNS) for line in text.split('\n')
    )


def take_key(stamp):
    try:
        with open(stamp) as f:
            key = f.read()
        os.remove(stamp)
    except OSError:
        return None
    return key


def issue_key(stamp):
    key = secrets.token_hex(4)
    try:
        with open(stamp, 'w') as f:
            f.write(key)
    except OSError:
        return None
    return key


def reason(lines, key):
    return (
        f'Not delivered: the message is {lines} rendered {COLUMNS}-column lines '
        f'and the caveman ceiling is {CAP_LINES}. The user has not seen it. Send '
        f'only the answer to what the user asked, in {CAP_LINES} lines or fewer. '
        'Leave the status of other work, the evidence and the next steps in '
        'plain text, and name what you left out in one closing line. Code fences '
        'do not count. If the answer needs the length, resend the message with '
        'one more line at its top. The gate removes that line, and its key works '
        f'once, on the next message only. That line is: {OVERRIDE} {key}'
    )


def check(data, home):
    if data.get('tool_name') != TOOL or not caveman_selected(home):
        return None
    tool_input = data.get('tool_input')
    message = tool_input.get('message') if isinstance(tool_input, dict) else None
    if not isinstance(message, str):
        return None
    stamp = session_state('reply-gate', data.get('session_id'))
    if stamp is None:
        return None
    pending = take_key(stamp)
    head, _, body = message.partition('\n')
    if pending and head == f'{OVERRIDE} {pending}':
        return {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'updatedInput': {**tool_input, 'message': body.lstrip('\n')},
            }
        }
    lines = rendered_lines(message)
    if lines <= CAP_LINES:
        return None
    key = issue_key(stamp)
    if not key:
        return None
    return {
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': 'deny',
            'permissionDecisionReason': reason(lines, key),
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
