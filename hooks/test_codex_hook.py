import json
from pathlib import Path

import pytest
from codex_hook import TARGETS
from codex_hook import normalize
from codex_hook import translate_output


def install_skills(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, *names: str) -> None:
    for name in names:
        (tmp_path / name).mkdir()
        (tmp_path / name / 'SKILL.md').touch()
    monkeypatch.setattr('codex_hook.SKILLS_DIR', tmp_path)


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
    # The adapter is the only process that knows this is Codex, so it is the
    # only one that says so — in band, per message, never inherited.
    assert payload['harness'] == 'codex'
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


def test_translate_output_rewrites_prompt_nudge_refs_for_codex(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_skills(monkeypatch, tmp_path, 'refine')
    output = translate_output(
        json.dumps({'ok': True, 'systemMessage': 'Invoke /refine, not /nope.'}),
        'UserPromptSubmit',
        'prompt_nudge',
    )
    parsed = json.loads(output)
    assert parsed['systemMessage'] == 'Invoke @refine, not /nope.'
    assert parsed['hookSpecificOutput']['additionalContext'] == 'Invoke @refine, not /nope.'


@pytest.mark.parametrize('skill', ['astra', 'sol'])
def test_translate_output_never_rewrites_codex_ref_recursively(skill) -> None:
    output = translate_output(
        json.dumps({'ok': True, 'systemMessage': f'Invoke /{skill}.'}),
        'UserPromptSubmit',
        'prompt_nudge',
    )
    parsed = json.loads(output)
    assert parsed['systemMessage'] == 'Invoke the current Codex session.'
    assert f'@{skill}' not in parsed['hookSpecificOutput']['additionalContext']


def test_translate_output_rewrites_pretool_refs_for_codex(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_skills(monkeypatch, tmp_path, 'py')
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


def test_md_format_is_a_target_and_its_post_tool_context_passes_through() -> None:
    assert TARGETS['md_format'] == [
        'python3',
        str(Path.home() / '.claude' / 'hooks' / 'md_format.py'),
    ]
    original = json.dumps(
        {
            'hookSpecificOutput': {
                'hookEventName': 'PostToolUse',
                'additionalContext': 'rumdl reformatted a.md; Read it again before the next Edit.',
            },
        }
    )
    assert json.loads(translate_output(original, 'PostToolUse', 'md_format')) == json.loads(
        original
    )


def test_translate_output_leaves_stop_block_unchanged() -> None:
    original = json.dumps({'decision': 'block', 'reason': 'commit first'})
    assert translate_output(original, 'Stop') == original


def test_translate_output_rewrites_stop_refs_for_codex(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_skills(monkeypatch, tmp_path, 'commit', 'diary')
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
