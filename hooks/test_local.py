import io
import json

import pytest
from local import main


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv('KRONAEL_HOOK_STATE', str(tmp_path / 'state'))
    monkeypatch.setenv('HOME', str(tmp_path / 'home'))
    (tmp_path / 'home' / '.claude').mkdir(parents=True)
    (tmp_path / 'home' / '.claude' / 'LOCAL.md').write_text('# LOCAL.md\n\nsync paths\n')


def run(monkeypatch, capsys, stdin):
    monkeypatch.setattr('sys.stdin', io.StringIO(stdin))
    with pytest.raises(SystemExit) as exit_info:
        main()
    return exit_info.value.code, capsys.readouterr().out.strip()


def payload(event, prompt, tmp_path):
    return json.dumps(
        {
            'hook_event_name': event,
            'prompt': prompt,
            'session_id': 'sess',
            'cwd': str(tmp_path),
        }
    )


def test_user_prompt_submit_gives_the_model_additional_context(
    monkeypatch, capsys, tmp_path
) -> None:
    code, out = run(monkeypatch, capsys, payload('UserPromptSubmit', 'continue', tmp_path))
    assert code == 0
    emitted = json.loads(out)
    assert set(emitted) == {'hookSpecificOutput'}
    assert emitted['hookSpecificOutput']['hookEventName'] == 'UserPromptSubmit'
    context = emitted['hookSpecificOutput']['additionalContext']
    assert 'LOCAL.md' in context
    assert 'Development reminders' in context


def test_pre_compact_emits_system_message_only(monkeypatch, capsys, tmp_path) -> None:
    code, out = run(monkeypatch, capsys, payload('PreCompact', '', tmp_path))
    assert code == 0
    emitted = json.loads(out)
    assert 'hookSpecificOutput' not in emitted
    assert 'LOCAL.md' in emitted['systemMessage']
    assert 'Development reminders' in emitted['systemMessage']


@pytest.mark.parametrize('stdin', ['[]', '"continue"', '42', 'null', '{bad', ''])
def test_payload_that_is_not_a_dict_exits_quietly(monkeypatch, capsys, stdin) -> None:
    assert run(monkeypatch, capsys, stdin) == (0, '')
