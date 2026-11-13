import json
import re
import subprocess
import sys

import pytest
from reply_gate import CAP_LINES
from reply_gate import COLUMNS
from reply_gate import check
from reply_gate import rendered_lines

OVER = '\n'.join(f'Line {n}.' for n in range(CAP_LINES + 1))
AT_CAP = '\n'.join(f'Line {n}.' for n in range(CAP_LINES))
SHORT = 'Done. Run `make test`.'
KEY = re.compile(r'That line is: override ([0-9a-f]{8})$')


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv('KRONAEL_HOOK_STATE', str(tmp_path / 'state'))
    settings = tmp_path / '.claude' / 'settings.json'
    settings.parent.mkdir()
    settings.write_text(json.dumps({'outputStyle': 'caveman'}))
    return tmp_path


def payload(message, **extra):
    return {
        'hook_event_name': 'PreToolUse',
        'session_id': 's1',
        'tool_name': 'SendUserMessage',
        'tool_input': {'message': message, 'status': 'normal'},
        **extra,
    }


def decision(out):
    return out['hookSpecificOutput']['permissionDecision']


def denied_key(out):
    return KEY.search(out['hookSpecificOutput']['permissionDecisionReason']).group(1)


def test_cap_and_unit_match_the_style_file(pytestconfig) -> None:
    style = (pytestconfig.rootpath / '..' / 'output-styles' / 'caveman.md').read_text()

    assert f'→ ≤{CAP_LINES}, hard ceiling' in style
    assert f'Unit: the rendered {COLUMNS}-column terminal line' in style


def test_rendered_lines_wrap_at_80_columns() -> None:
    assert rendered_lines('x' * 80) == 1
    assert rendered_lines('x' * 81) == 2
    assert rendered_lines('x' * 161) == 3
    assert rendered_lines('a\n\nb') == 3


def test_rendered_lines_skip_code_fences() -> None:
    assert rendered_lines('Run it.\n```sh\n' + OVER + '\n```\nDone.') == 3
    assert rendered_lines('Run it.\n```sh\n' + OVER + '\n```') == 1
    assert rendered_lines('Run it.\n~~~\n' + OVER + '\n~~~') == 1
    assert rendered_lines('Run it.\n  ```\n' + OVER + '\n  ```') == 1
    assert rendered_lines('Run it.\n```\n' + OVER + '\n```  \nDone.') == 3
    assert rendered_lines('a\n```\nx\n```\nb\n```\ny\n```\nc') == 5


def test_rendered_lines_count_a_link_by_its_text() -> None:
    assert rendered_lines('[' + 'x' * 80 + '](https://example.com/' + 'x' * 200 + ')') == 1
    assert rendered_lines('[' + 'x' * 81 + '](https://example.com)') == 2
    assert rendered_lines('[' + 'x' * 80 + ']()') == 1


def test_a_message_within_the_ceiling_passes(home) -> None:
    assert check(payload(SHORT), home) is None
    assert check(payload(AT_CAP), home) is None


def test_a_message_over_the_ceiling_is_denied_with_the_measured_count(home) -> None:
    out = check(payload(OVER), home)

    assert decision(out) == 'deny'
    assert out['hookSpecificOutput']['hookEventName'] == 'PreToolUse'
    text = out['hookSpecificOutput']['permissionDecisionReason']
    assert f'{CAP_LINES + 1} rendered 80-column lines' in text
    assert f'ceiling is {CAP_LINES}' in text


def test_the_denial_names_a_key_that_passes_the_next_message_once(home) -> None:
    key = denied_key(check(payload(OVER), home))

    out = check(payload(f'override {key}\n\n{OVER}'), home)

    assert out == {
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'updatedInput': {'message': OVER, 'status': 'normal'},
        }
    }
    assert decision(check(payload(f'override {key}\n\n{OVER}'), home)) == 'deny'


def test_a_wrong_key_is_denied_and_spends_the_issued_key(home) -> None:
    key = denied_key(check(payload(OVER), home))

    assert decision(check(payload(f'override not-the-key\n{OVER}'), home)) == 'deny'
    assert decision(check(payload(f'override {key}\n{OVER}'), home)) == 'deny'


@pytest.mark.parametrize('body', [SHORT, '  Indented.', 'X marks it.'])
def test_a_valid_key_line_is_removed_and_the_message_kept_as_written(home, body) -> None:
    key = denied_key(check(payload(OVER), home))

    out = check(payload(f'override {key}\n\n{body}'), home)

    assert out['hookSpecificOutput']['updatedInput']['message'] == body


def test_each_denial_issues_another_key(home) -> None:
    first = denied_key(check(payload(OVER), home))
    second = denied_key(check(payload(OVER), home))

    assert first != second
    assert decision(check(payload(f'override {first}\n{OVER}'), home)) == 'deny'


def test_a_delivered_message_spends_the_issued_key(home) -> None:
    key = denied_key(check(payload(OVER), home))
    assert check(payload(SHORT), home) is None

    assert decision(check(payload(f'override {key}\n{OVER}'), home)) == 'deny'


def test_an_override_line_with_no_key_issued_is_denied(home) -> None:
    assert decision(check(payload(f'override None\n{OVER}'), home)) == 'deny'
    assert check(payload(f'override None\n{SHORT}'), home) is None


def test_the_key_must_be_the_whole_first_line(home) -> None:
    key = denied_key(check(payload(OVER), home))
    assert decision(check(payload(f'{OVER}\noverride {key}'), home)) == 'deny'

    key = denied_key(check(payload(OVER), home))
    assert decision(check(payload(f'override {key} now\n{OVER}'), home)) == 'deny'


def test_sessions_hold_their_keys_apart(home) -> None:
    key = denied_key(check(payload(OVER), home))

    assert decision(check(payload(f'override {key}\n{OVER}', session_id='s2'), home)) == 'deny'
    out = check(payload(f'override {key}\n{OVER}'), home)
    assert out['hookSpecificOutput']['updatedInput']['message'] == OVER


@pytest.mark.parametrize(
    'data',
    [
        payload(OVER, tool_name='SendMessage'),
        payload(OVER, tool_name='Bash'),
        payload(OVER, tool_input={'message': None}),
        payload(OVER, tool_input='text'),
        {'hook_event_name': 'PreToolUse', 'tool_name': 'SendUserMessage'},
    ],
)
def test_other_tools_and_malformed_input_pass(home, data) -> None:
    assert check(data, home) is None


def test_the_gate_is_silent_under_another_output_style(home) -> None:
    settings = home / '.claude' / 'settings.json'
    for text in json.dumps({'outputStyle': 'default'}), 'not json', '[]':
        settings.write_text(text)
        assert check(payload(OVER), home) is None

    settings.unlink()
    assert check(payload(OVER), home) is None


def test_no_state_directory_means_no_denial(home, monkeypatch) -> None:
    blocker = home / 'file'
    blocker.write_text('')
    monkeypatch.setenv('KRONAEL_HOOK_STATE', str(blocker / 'state'))

    assert check(payload(OVER), home) is None


def test_a_key_that_cannot_be_stored_means_no_denial(home) -> None:
    (home / 'state' / 'reply-gate-s1').mkdir(parents=True)

    assert check(payload(OVER), home) is None


def run_hook(hook, home, stdin):
    r = subprocess.run(
        [sys.executable, str(hook)],
        input=stdin,
        capture_output=True,
        text=True,
        env={
            'HOME': str(home),
            'PATH': '/usr/bin:/bin',
            'KRONAEL_HOOK_STATE': str(home / 'state'),
        },
        check=False,
    )
    assert r.returncode == 0, r.stderr
    assert r.stderr == ''
    return r.stdout


def test_the_script_denies_on_stdin_and_stays_silent_on_bad_input(home, pytestconfig) -> None:
    hook = pytestconfig.rootpath / 'reply_gate.py'

    denied = json.loads(run_hook(hook, home, json.dumps(payload(OVER))))
    assert decision(denied) == 'deny'
    resent = json.dumps(payload(f'override {denied_key(denied)}\n{OVER}'))
    passed = json.loads(run_hook(hook, home, resent))
    assert passed['hookSpecificOutput']['updatedInput']['message'] == OVER
    assert run_hook(hook, home, json.dumps(payload(SHORT))) == ''
    assert run_hook(hook, home, 'not json') == ''
    assert run_hook(hook, home, '[]') == ''
    assert run_hook(hook, home, '') == ''
