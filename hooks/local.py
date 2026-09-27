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
session_state = hook_state.session_state
hook_event = hook_state.hook_event

RULES = """Development reminders:
- ALWAYS use make for build/lint/test/clean
- ALWAYS build/test/lint every ~50 lines - errors cascade
- NEVER improve beyond what's asked
- NEVER use git add -A
- NEVER use git commit --amend - make new commits"""


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

    event = hook_event(data)
    session_id = data.get('session_id') or 'default'
    cwd = data.get('cwd') or '.'

    # Session-keyed, not cwd-keyed: cd'ing to another repo mid-session used to
    # reset this and re-inject LOCAL.md as if the session had just started.
    state_file = session_state('local', session_id)

    parts = []
    first_prompt = state_file is None or not os.path.isfile(state_file)
    is_compaction = event == 'PreCompact'

    if first_prompt or is_compaction:
        for path in [
            os.path.expanduser('~/.claude/LOCAL.md'),
            os.path.join(cwd, 'LOCAL.md'),
        ]:
            if os.path.isfile(path):
                try:
                    with open(path) as f:
                        content = f.read().strip()
                    if content:
                        parts.append(content)
                except OSError:
                    pass

        if first_prompt and state_file is not None:
            try:
                open(state_file, 'w').close()
            except OSError:
                pass

    prompt_lower = prompt.lower()
    if not re.search(r'\b(don\'?t|not|never)\s+\w*\s*(continue|recap)', prompt_lower) and re.search(
        r'\b(continue|recap|where\s+were\s+we|what\'?s\s+next)\b',
        prompt_lower,
    ):
        parts.append(RULES)

    if is_compaction:
        parts.append(RULES)

    if parts:
        print(json.dumps({'ok': True, 'systemMessage': '\n\n'.join(parts)}))

    sys.exit(0)


if __name__ == '__main__':
    main()
