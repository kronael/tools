import io
import json

import memory_nudge
import pytest


def run(monkeypatch, capsys, data):
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(data)))
    with pytest.raises(SystemExit):
        memory_nudge.main()
    out = capsys.readouterr().out.strip()
    return json.loads(out) if out else None


@pytest.fixture(autouse=True)
def state_root(tmp_path, monkeypatch):
    root = tmp_path / 'state'
    monkeypatch.setenv('KRONAEL_HOOK_STATE', str(root))
    return root


def base(tmp_path, event, **extra):
    return {
        'hook_event': event,
        'cwd': str(tmp_path),
        'session_id': 'sess',
        **extra,
    }


def test_compact_emits_and_marks_done(tmp_path, monkeypatch, capsys, state_root):
    out = run(monkeypatch, capsys, base(tmp_path, 'SessionStart', source='compact'))

    assert out == {
        'hookSpecificOutput': {
            'hookEventName': 'SessionStart',
            'additionalContext': memory_nudge.NUDGE_TEXT,
        }
    }
    assert (state_root / 'memory-nudge-done-sess').exists()


def test_compact_suppresses_later_prompts(tmp_path, monkeypatch, capsys):
    run(monkeypatch, capsys, base(tmp_path, 'SessionStart', source='compact'))
    for _ in range(memory_nudge.PROMPT_COUNT_THRESHOLD):
        assert run(monkeypatch, capsys, base(tmp_path, 'UserPromptSubmit')) is None


def prompts_until_nudge(tmp_path, monkeypatch, capsys):
    for _ in range(memory_nudge.PROMPT_COUNT_THRESHOLD - 1):
        assert run(monkeypatch, capsys, base(tmp_path, 'UserPromptSubmit')) is None
    return run(monkeypatch, capsys, base(tmp_path, 'UserPromptSubmit'))


@pytest.mark.parametrize('source', ['startup', 'resume', 'unknown', None])
def test_other_session_starts_leave_prompt_path(tmp_path, monkeypatch, capsys, source):
    assert run(monkeypatch, capsys, base(tmp_path, 'SessionStart', source=source)) is None
    out = prompts_until_nudge(tmp_path, monkeypatch, capsys)
    assert out['hookSpecificOutput']['additionalContext'] == memory_nudge.NUDGE_TEXT


def test_precompact_leaves_prompt_path(tmp_path, monkeypatch, capsys):
    assert run(monkeypatch, capsys, base(tmp_path, 'PreCompact')) is None
    out = prompts_until_nudge(tmp_path, monkeypatch, capsys)
    assert out['hookSpecificOutput']['additionalContext'] == memory_nudge.NUDGE_TEXT


def test_first_prompt_is_silent_and_records(tmp_path, monkeypatch, capsys, state_root):
    out = run(monkeypatch, capsys, base(tmp_path, 'UserPromptSubmit'))

    assert out is None
    started, count = memory_nudge.read_start(str(state_root / 'memory-nudge-start-sess'))
    assert started is not None
    assert count == 1


def test_short_session_fires_on_count_threshold(tmp_path, monkeypatch, capsys):
    # Four rapid prompts (never near 30 min) still yield exactly one nudge.
    out = prompts_until_nudge(tmp_path, monkeypatch, capsys)

    assert out['hookSpecificOutput']['hookEventName'] == 'UserPromptSubmit'
    assert out['hookSpecificOutput']['additionalContext'] == memory_nudge.NUDGE_TEXT


def test_fires_once_then_silent(tmp_path, monkeypatch, capsys):
    prompts_until_nudge(tmp_path, monkeypatch, capsys)
    # Next prompt after the done marker stays silent.
    out = run(monkeypatch, capsys, base(tmp_path, 'UserPromptSubmit'))

    assert out is None


def test_wall_clock_path_fires_before_count(tmp_path, monkeypatch, capsys, state_root):
    # Seed a start well past the wall-clock threshold with a low count; the
    # next prompt should fire via elapsed time, not the count gate.
    start = state_root / 'memory-nudge-start-sess'
    start.parent.mkdir(parents=True)
    memory_nudge.write_start(str(start), 100.0, 1)
    out = run(monkeypatch, capsys, base(tmp_path, 'UserPromptSubmit'))

    assert out['hookSpecificOutput']['additionalContext'] == memory_nudge.NUDGE_TEXT


def test_stop_payload_does_nothing(tmp_path, monkeypatch, capsys, state_root):
    start = state_root / 'memory-nudge-start-sess'
    start.parent.mkdir(parents=True)
    memory_nudge.write_start(str(start), 100.0, memory_nudge.PROMPT_COUNT_THRESHOLD)
    out = run(monkeypatch, capsys, base(tmp_path, 'Stop'))

    assert out is None
    assert not (state_root / 'memory-nudge-done-sess').exists()


def test_cwd_change_does_not_reset_once_per_session(tmp_path, monkeypatch, capsys):
    # The guard is session-keyed: cd'ing between repos must not re-nudge.
    prompts_until_nudge(tmp_path, monkeypatch, capsys)
    elsewhere = tmp_path / 'other-repo'
    elsewhere.mkdir()
    out = run(monkeypatch, capsys, base(elsewhere, 'UserPromptSubmit'))

    assert out is None


def wired(settings, event):
    return [hook['command'] for group in settings['hooks'][event] for hook in group['hooks']]


def test_wiring_runs_on_prompt_and_compact_not_stop(pytestconfig):
    path = pytestconfig.rootpath / '..' / 'settings-recommended.json'
    settings = json.loads(path.read_text())

    for event in ('UserPromptSubmit', 'SessionStart'):
        assert any(c.endswith('memory_nudge.py') for c in wired(settings, event))
    assert not any(c.endswith('memory_nudge.py') for c in wired(settings, 'Stop'))
    assert any(c.endswith('stop.py') for c in wired(settings, 'Stop'))
