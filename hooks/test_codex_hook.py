import json

from codex_hook import normalize
from codex_hook import translate_output


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


def test_translate_output_rewrites_prompt_nudge_refs_for_codex() -> None:
    output = translate_output(
        json.dumps({'ok': True, 'systemMessage': 'Invoke /refine.'}),
        'UserPromptSubmit',
        'prompt_nudge',
    )
    parsed = json.loads(output)
    assert parsed['systemMessage'] == 'Invoke @refine.'
    assert parsed['hookSpecificOutput']['additionalContext'] == 'Invoke @refine.'


def test_translate_output_never_rewrites_codex_ref_recursively() -> None:
    output = translate_output(
        json.dumps({'ok': True, 'systemMessage': 'Invoke /codex.'}),
        'UserPromptSubmit',
        'prompt_nudge',
    )
    parsed = json.loads(output)
    assert parsed['systemMessage'] == 'Invoke the current Codex session.'
    assert '@codex' not in parsed['hookSpecificOutput']['additionalContext']


def test_translate_output_rewrites_pretool_refs_for_codex() -> None:
    output = translate_output(
        json.dumps(
            {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'additionalContext': 'follow /py conventions.',
                },
            }
        ),
        'PreToolUse',
        'pretool_nudge',
    )
    parsed = json.loads(output)
    context = parsed['hookSpecificOutput']['additionalContext']
    assert context == 'follow @py conventions.'


def test_translate_output_leaves_stop_block_unchanged() -> None:
    original = json.dumps({'decision': 'block', 'reason': 'commit first'})
    assert translate_output(original, 'Stop') == original


def test_translate_output_rewrites_stop_refs_for_codex() -> None:
    output = translate_output(
        json.dumps({'decision': 'block', 'reason': 'Run /commit. Run /diary.'}),
        'Stop',
        'stop',
    )
    assert json.loads(output)['reason'] == 'Run @commit. Run @diary.'


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
