#!/usr/bin/env python3
"""Codex hook adapter for the Kronael Claude hook scripts."""

from __future__ import annotations

import json
import os
import re
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
NUDGE_TARGETS = {'prompt_nudge', 'pretool_nudge', 'post_tool_nudge', 'stop'}
CODEX_SKILL_NAMES_TEXT = (
    'bugs ceo-eval cli codex commit create create-eval credit cto-eval '
    'data data-reports diagrams diary dispatch distill explore eye-13yo '
    'fable fin fix gh-comment go haiku hacker-eval humanize htmx improve '
    'learn mk merge oracle opus ops pr-draft py readme recall-memories '
    'refine release review rs scavenge service sh ship sonnet software '
    'sql specs testing trader ts tsx tweet visual wisdom writing'
)
CODEX_SKILL_NAMES = frozenset(CODEX_SKILL_NAMES_TEXT.split())
SKILL_REF_RE = re.compile(r'(?<![\w@])/(?P<name>[a-z][a-z0-9-]*)')


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
        event = str(payload.get('hook_event') or '')
        print(translate_output(result.stdout, event, target), end='')
    if result.stderr and os.environ.get('KRONAEL_CODEX_HOOK_DEBUG'):
        print(result.stderr, end='', file=sys.stderr)
    return result.returncode


def rewrite_skill_refs(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group('name')
        if name in CODEX_SKILL_NAMES:
            return f'@{name}'
        return match.group(0)

    return SKILL_REF_RE.sub(replace, text)


def rewrite_nudge_output(output: dict[str, Any], target: str) -> None:
    if target not in NUDGE_TARGETS:
        return
    for key in 'systemMessage', 'reason':
        value = output.get(key)
        if isinstance(value, str):
            output[key] = rewrite_skill_refs(value)
    hook_output = output.get('hookSpecificOutput')
    if not isinstance(hook_output, dict):
        return
    context = hook_output.get('additionalContext')
    if isinstance(context, str):
        hook_output['additionalContext'] = rewrite_skill_refs(context)


def translate_output(stdout: str, event: str, target: str = '') -> str:
    try:
        output = json.loads(stdout)
    except (json.JSONDecodeError, TypeError, ValueError):
        return stdout
    if not isinstance(output, dict):
        return stdout
    output.pop('ok', None)
    rewrite_nudge_output(output, target)

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


if __name__ == '__main__':
    main()
