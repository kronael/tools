#!/usr/bin/env python3
import json
import math
import os
import re
import sys

from lib.state import session_state

TOOL = 'SendUserMessage'
STYLE = 'caveman'
CAP_LINES = 20
MAX_DENIALS = 2
FENCE = re.compile(r'^[ \t]*(```|~~~)[\s\S]*?^[ \t]*\1[ \t]*$', re.MULTILINE)
LINK = re.compile(r'\[([^\]]*)\]\([^)]*\)')


def rendered_lines(message):
    text = LINK.sub(r'\1', FENCE.sub('', message)).strip()
    return sum(1 if not line.strip() else math.ceil(len(line) / 80) for line in text.split('\n'))


def selected_style(home):
    try:
        with open(os.path.join(home, '.claude', 'settings.json')) as f:
            return json.load(f).get('outputStyle')
    except (OSError, ValueError, AttributeError):
        return None


def denials(stamp):
    try:
        with open(stamp) as f:
            return int(f.read())
    except (OSError, ValueError):
        return 0


def record(stamp, count):
    try:
        if count:
            with open(stamp, 'w') as f:
                f.write(str(count))
        else:
            os.remove(stamp)
    except OSError:
        return False
    return True


def reason(lines):
    return (
        f'Not delivered: the message is {lines} rendered lines and the caveman '
        f'ceiling is {CAP_LINES}. The user has not seen it. Send only the answer '
        f'to what the user asked, in {CAP_LINES} lines or fewer. Leave the status '
        'of other work, the evidence and the next steps in plain text, and name '
        'what you left out in one closing line. Code fences do not count.'
    )


def check(data, home):
    if data.get('tool_name') != TOOL or selected_style(home) != STYLE:
        return None
    tool_input = data.get('tool_input')
    message = tool_input.get('message') if isinstance(tool_input, dict) else None
    if not isinstance(message, str):
        return None
    stamp = session_state('reply-gate', data.get('session_id'))
    if stamp is None:
        return None
    lines = rendered_lines(message)
    refused = denials(stamp)
    if lines <= CAP_LINES or refused >= MAX_DENIALS:
        if refused:
            record(stamp, 0)
        return None
    if not record(stamp, refused + 1):
        return None
    return {
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': 'deny',
            'permissionDecisionReason': reason(lines),
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
