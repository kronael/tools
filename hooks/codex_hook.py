#!/usr/bin/env python3
"""Codex hook adapter for the Kronael Claude hook scripts."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

HOOKS_DIR = Path.home() / '.claude' / 'hooks'
TARGETS = {
    'local': ['python3', str(HOOKS_DIR / 'local.py')],
    'prompt_nudge': ['python3', str(HOOKS_DIR / 'prompt_nudge.py')],
    'pretool_nudge': ['python3', str(HOOKS_DIR / 'pretool_nudge.py')],
    'post_tool_nudge': ['bash', str(HOOKS_DIR / 'post_tool_nudge.sh')],
    'reclaude': ['python3', str(HOOKS_DIR / 'reclaude.py')],
    'stop': ['python3', str(HOOKS_DIR / 'stop.py')],
}
CONTEXT_EVENTS = {'UserPromptSubmit', 'PreToolUse', 'PostToolUse'}


def _first_str(data: dict[str, Any], names: tuple[str, ...], default: str = '') -> str:
    for name in names:
        value = data.get(name)
        if isinstance(value, str) and value:
            return value
    return default


def _nested_dict(data: dict[str, Any], *names: str) -> dict[str, Any]:
    for name in names:
        value = data.get(name)
        if isinstance(value, dict):
            return value
    return {}


def normalize(data: object, event: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        data = {}
    normalized = dict(data)

    cwd = _first_str(normalized, ('cwd', 'current_working_directory'), os.getcwd())
    session_id = _first_str(
        normalized,
        ('session_id', 'sessionId', 'thread_id', 'threadId', 'conversation_id', 'conversationId'),
        'codex',
    )
    prompt = _first_str(normalized, ('prompt', 'user_prompt', 'userPrompt', 'message'))

    tool = _nested_dict(normalized, 'tool', 'tool_call', 'toolCall')
    tool_name = _first_str(normalized, ('tool_name', 'toolName'), _first_str(tool, ('name',)))
    tool_input = _nested_dict(normalized, 'tool_input', 'toolInput', 'arguments', 'input')
    if not tool_input:
        tool_input = _nested_dict(tool, 'tool_input', 'toolInput', 'arguments', 'input')

    normalized['cwd'] = cwd
    normalized['session_id'] = session_id
    normalized['hook_event'] = event
    if prompt:
        normalized['prompt'] = prompt
    if tool_name:
        normalized['tool_name'] = tool_name
    if tool_input:
        normalized['tool_input'] = tool_input
    return normalized


def run_target(target: str, payload: dict[str, Any]) -> int:
    command = TARGETS.get(target)
    if command is None:
        return 0

    cwd = payload.get('cwd')
    if not isinstance(cwd, str) or not cwd:
        cwd = os.getcwd()

    result = subprocess.run(
        command,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=cwd,
        timeout=30,
        check=False,
    )
    if result.stdout:
        print(translate_output(result.stdout, str(payload.get('hook_event') or '')), end='')
    if result.stderr and os.environ.get('KRONAEL_CODEX_HOOK_DEBUG'):
        print(result.stderr, end='', file=sys.stderr)
    return result.returncode


def translate_output(stdout: str, event: str) -> str:
    try:
        output = json.loads(stdout)
    except (json.JSONDecodeError, TypeError, ValueError):
        return stdout
    if not isinstance(output, dict):
        return stdout
    output.pop('ok', None)

    if event == 'PreCompact':
        if output.get('decision') == 'block':
            translated: dict[str, Any] = {'decision': 'block'}
            reason = output.get('reason')
            if isinstance(reason, str) and reason:
                translated['reason'] = reason
            return json.dumps(translated)
        return ''

    system_message = output.get('systemMessage')
    if not isinstance(system_message, str) or not system_message:
        return json.dumps(output)
    if event not in CONTEXT_EVENTS:
        return stdout

    hook_output = output.get('hookSpecificOutput')
    if not isinstance(hook_output, dict):
        hook_output = {'hookEventName': event}
        output['hookSpecificOutput'] = hook_output
    hook_output.setdefault('hookEventName', event)
    hook_output.setdefault('additionalContext', system_message)
    return json.dumps(output)


def main() -> None:
    if len(sys.argv) != 3:
        return
    event = sys.argv[1]
    target = sys.argv[2]
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        data = {}
    payload = normalize(data, event)
    run_target(target, payload)


def test_normalize_keeps_claude_shape() -> None:
    payload = normalize(
        {
            'cwd': '/repo',
            'session_id': 's1',
            'prompt': 'commit this',
            'tool_name': 'Read',
            'tool_input': {'file_path': 'x.py'},
        },
        'UserPromptSubmit',
    )
    assert payload['cwd'] == '/repo'
    assert payload['session_id'] == 's1'
    assert payload['prompt'] == 'commit this'
    assert payload['tool_name'] == 'Read'
    assert payload['tool_input'] == {'file_path': 'x.py'}
    assert payload['hook_event'] == 'UserPromptSubmit'


def test_normalize_accepts_codex_camel_case() -> None:
    payload = normalize(
        {
            'sessionId': 'abc',
            'userPrompt': 'continue',
            'tool': {'name': 'apply_patch', 'input': {'patch': '*** Begin Patch'}},
        },
        'PreToolUse',
    )
    assert payload['session_id'] == 'abc'
    assert payload['prompt'] == 'continue'
    assert payload['tool_name'] == 'apply_patch'
    assert payload['tool_input'] == {'patch': '*** Begin Patch'}
    assert payload['hook_event'] == 'PreToolUse'


def test_translate_output_promotes_system_message_for_codex_prompt() -> None:
    output = translate_output(
        json.dumps({'ok': True, 'systemMessage': 'Use the project rules.'}),
        'UserPromptSubmit',
    )
    parsed = json.loads(output)
    assert 'ok' not in parsed
    assert parsed['systemMessage'] == 'Use the project rules.'
    assert parsed['hookSpecificOutput'] == {
        'hookEventName': 'UserPromptSubmit',
        'additionalContext': 'Use the project rules.',
    }


def test_translate_output_leaves_stop_block_unchanged() -> None:
    original = json.dumps({'decision': 'block', 'reason': 'commit first'})
    assert translate_output(original, 'Stop') == original


def test_translate_output_suppresses_precompact_context_for_codex() -> None:
    output = translate_output(
        json.dumps({'ok': True, 'systemMessage': 'Reload context before compact.'}),
        'PreCompact',
    )
    assert output == ''


def test_translate_output_keeps_precompact_block_for_codex() -> None:
    output = translate_output(
        json.dumps({'ok': True, 'decision': 'block', 'reason': 'finish summary first'}),
        'PreCompact',
    )
    assert json.loads(output) == {'decision': 'block', 'reason': 'finish summary first'}


if __name__ == '__main__':
    main()
