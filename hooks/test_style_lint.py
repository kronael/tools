import io
import json
import subprocess
import sys
from pathlib import Path

import pytest
import style_lint
from style_lint import CAP_BULLETS
from style_lint import CAP_LINES
from style_lint import CAP_SENTENCES
from style_lint import check
from style_lint import measure
from style_lint import visible

HOOK = Path(__file__).with_name('style_lint.py')
CAVEMAN = Path(__file__).resolve().parent.parent / 'output-styles' / 'caveman.md'

LONG = 'This sentence fills more than one rendered line of the terminal because it runs on and on. '
OVER_LINES = '\n'.join(f'Line {n}.' for n in range(CAP_LINES + 1))
OVER_BULLETS = '\n'.join(f'- item {n}' for n in range(CAP_BULLETS + 1))
SHORT = 'Done. Run `make test`.'


@pytest.fixture
def home(tmp_path):
    settings = tmp_path / '.claude' / 'settings.json'
    settings.parent.mkdir()
    settings.write_text(json.dumps({'outputStyle': 'caveman'}))
    return tmp_path


def run_hook(home, **payload):
    payload = {'hook_event_name': 'Stop', 'session_id': 's1', **payload}
    r = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={'HOME': str(home), 'PATH': '/usr/bin:/bin'},
        check=False,
    )
    assert r.returncode == 0, r.stderr
    assert r.stderr == ''
    return json.loads(r.stdout) if r.stdout else None


def test_caps_match_the_style_file() -> None:
    text = CAVEMAN.read_text()

    assert f'→ ≤{CAP_LINES}, hard ceiling' in text
    assert f'Lists: ≤{CAP_BULLETS} bullets' in text
    assert CAP_SENTENCES == 2
    assert 'one sentence, two at most' in text


def test_fences_sit_outside_the_budget() -> None:
    assert visible('Run it.\n```sh\n' + OVER_LINES + '\n```\nDone.') == 'Run it.\n\nDone.'
    assert visible('~~~\n' + OVER_LINES + '\n~~~') == ''


def test_measure_counts_rendered_lines_lists_and_bullet_sentences() -> None:
    assert measure(LONG * 2)['lines'] == 3
    assert measure('a\n\nb')['lines'] == 3
    assert measure('- a\n- b\n\ntext\n1. c\n2. d\n3. e')['bullets'] == 3
    assert measure('- One. Two. Three.')['sentences'] == 3
    assert measure('- Run `a.b` then `c.d`.')['sentences'] == 1
    assert measure('plain')['bullets'] == 0


def test_compliant_reply_passes(home) -> None:
    assert check({'last_assistant_message': SHORT}, home) is None
    assert check({'last_assistant_message': OVER_LINES[: CAP_LINES * 8]}, home) is None


def test_twenty_one_lines_block_and_twenty_pass(home) -> None:
    twenty = '\n'.join(f'Line {n}.' for n in range(20))

    out = check({'last_assistant_message': twenty + '\nLine 20.'}, home)

    assert out['decision'] == 'block'
    assert '21 rendered lines, cap 20' in out['reason']
    assert check({'last_assistant_message': twenty}, home) is None
    assert 'a list of' not in out['reason']


def test_every_broken_rule_is_named(home) -> None:
    message = OVER_BULLETS + '\n- One. Two. Three.\n' + OVER_LINES

    out = check({'last_assistant_message': message}, home)

    assert 'a list of 7 bullets, cap 5' in out['reason']
    assert 'a bullet of 3 sentences, cap 2' in out['reason']


def test_code_over_the_cap_does_not_block(home) -> None:
    assert check({'last_assistant_message': '```\n' + OVER_LINES + '\n```'}, home) is None


def test_rewrite_turn_is_not_measured_again(home) -> None:
    payload = {'last_assistant_message': OVER_LINES, 'stop_hook_active': True}

    assert check(payload, home) is None


def test_other_style_or_no_settings_is_silent(tmp_path, home) -> None:
    (home / '.claude' / 'settings.json').write_text(json.dumps({'outputStyle': 'default'}))
    assert check({'last_assistant_message': OVER_LINES}, home) is None
    assert check({'last_assistant_message': OVER_LINES}, tmp_path / 'nowhere') is None


def test_missing_message_is_silent(home) -> None:
    assert check({}, home) is None
    assert check({'last_assistant_message': None}, home) is None


def test_hook_blocks_over_budget_reply_once(home) -> None:
    out = run_hook(home, last_assistant_message=OVER_LINES)
    assert out['decision'] == 'block'
    assert 'Send the final answer again within the budget' in out['reason']

    assert run_hook(home, last_assistant_message=OVER_LINES, stop_hook_active=True) is None
    assert run_hook(home, last_assistant_message=SHORT) is None


def test_bad_input_is_silent(home) -> None:
    for stdin in ('', '{bad', '[]'):
        r = subprocess.run(
            [sys.executable, str(HOOK)],
            input=stdin,
            capture_output=True,
            text=True,
            env={'HOME': str(home), 'PATH': '/usr/bin:/bin'},
            check=False,
        )
        assert r.returncode == 0
        assert r.stdout == ''


def test_main_reads_stdin(home, monkeypatch, capsys) -> None:
    monkeypatch.setenv('HOME', str(home))
    monkeypatch.setattr(
        'sys.stdin', io.StringIO(json.dumps({'last_assistant_message': OVER_LINES}))
    )

    style_lint.main()

    assert json.loads(capsys.readouterr().out)['decision'] == 'block'
