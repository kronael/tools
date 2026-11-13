import json
import subprocess
import sys

import pytest
from reply_gate import CAP_LINES
from reply_gate import MAX_DENIALS
from reply_gate import check
from reply_gate import rendered_lines

WIDE = 'This sentence fills more than one rendered line of the terminal because it runs on and on. '
OVER = '\n'.join(f'Line {n}.' for n in range(CAP_LINES + 1))
AT_CAP = '\n'.join(f'Line {n}.' for n in range(CAP_LINES))
SHORT = 'Done. Run `make test`.'


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


def test_cap_matches_the_style_file(pytestconfig) -> None:
    style = pytestconfig.rootpath / '..' / 'output-styles' / 'caveman.md'

    assert f'→ ≤{CAP_LINES}, hard ceiling' in style.read_text()


def test_rendered_lines_wrap_at_80_columns_and_skip_fences() -> None:
    assert rendered_lines(WIDE * 2) == 3
    assert rendered_lines('a\n\nb') == 3
    assert rendered_lines('Run it.\n```sh\n' + OVER + '\n```\nDone.') == 3
    assert rendered_lines('[the report](https://example.com/' + 'x' * 200 + ')') == 1


def test_a_message_within_the_ceiling_passes(home) -> None:
    assert check(payload(SHORT), home) is None
    assert check(payload(AT_CAP), home) is None


def test_a_message_over_the_ceiling_is_denied_with_the_measured_count(home) -> None:
    out = check(payload(OVER), home)

    assert decision(out) == 'deny'
    assert out['hookSpecificOutput']['hookEventName'] == 'PreToolUse'
    text = out['hookSpecificOutput']['permissionDecisionReason']
    assert f'{CAP_LINES + 1} rendered lines' in text
    assert f'ceiling is {CAP_LINES}' in text


def test_the_gate_lets_a_message_through_after_the_denial_limit(home) -> None:
    for _ in range(MAX_DENIALS):
        assert decision(check(payload(OVER), home)) == 'deny'

    assert check(payload(OVER), home) is None
    assert decision(check(payload(OVER), home)) == 'deny'


def test_a_delivered_message_resets_the_denial_count(home) -> None:
    assert decision(check(payload(OVER), home)) == 'deny'
    assert check(payload(SHORT), home) is None

    for _ in range(MAX_DENIALS):
        assert decision(check(payload(OVER), home)) == 'deny'


def test_sessions_count_denials_apart(home) -> None:
    for _ in range(MAX_DENIALS):
        check(payload(OVER), home)

    assert decision(check(payload(OVER, session_id='s2'), home)) == 'deny'


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
    (home / '.claude' / 'settings.json').write_text(json.dumps({'outputStyle': 'default'}))
    assert check(payload(OVER), home) is None

    (home / '.claude' / 'settings.json').unlink()
    assert check(payload(OVER), home) is None


def test_no_state_directory_means_no_denial(home, monkeypatch) -> None:
    blocker = home / 'file'
    blocker.write_text('')
    monkeypatch.setenv('KRONAEL_HOOK_STATE', str(blocker / 'state'))

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

    assert decision(json.loads(run_hook(hook, home, json.dumps(payload(OVER))))) == 'deny'
    assert run_hook(hook, home, json.dumps(payload(SHORT))) == ''
    assert run_hook(hook, home, 'not json') == ''
    assert run_hook(hook, home, '[]') == ''
    assert run_hook(hook, home, '') == ''
