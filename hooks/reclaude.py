#!/usr/bin/env python3
import importlib.util
import json
import os
import re
import sys

spec = importlib.util.spec_from_file_location(
    'hook_state', os.path.expanduser('~/.claude/hooks/lib/state.py')
)
hook_state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook_state)
hook_event = hook_state.hook_event


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        sys.exit(0)

    if not isinstance(data, dict):
        sys.exit(0)

    reclaude = os.path.expanduser('~/.claude/RECLAUDE.md')
    if not os.path.exists(reclaude):
        sys.exit(0)
    try:
        with open(reclaude) as f:
            rules = f.read()
    except OSError:
        sys.exit(0)

    event = hook_event(data)
    prompt = data.get('prompt') or ''
    if not isinstance(prompt, str):
        prompt = ''

    prompt_lower = prompt.lower()
    if re.search(r'\b(don\'?t|not|never)\s+\w*\s*(continue|recap)', prompt_lower):
        sys.exit(0)

    should_inject = event == 'PreCompact' or re.search(
        r'\b(continue|recap|where\s+were\s+we|what\'?s\s+next)\b', prompt_lower
    )

    if should_inject:
        if event == 'PreCompact':
            rules = (
                rules.rstrip()
                + '\n\nThese instructions and the full wisdom context from CLAUDE.md should survive compaction.\n'
            )
        print(json.dumps({'ok': True, 'systemMessage': rules}))

    sys.exit(0)


if __name__ == '__main__':
    main()
