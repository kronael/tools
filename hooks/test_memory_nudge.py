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


def base(tmp_path, event, **extra):
    return {
        'hook_event': event,
        'cwd': str(tmp_path),
        'session_id': 'sess',
        **extra,
    }


def test_precompact_emits_and_marks_done(tmp_path, monkeypatch, capsys):
    out = run(monkeypatch, capsys, base(tmp_path, 'PreCompact'))

    assert out == {'ok': True, 'systemMessage': memory_nudge.NUDGE_TEXT}
    done = tmp_path / '.claude' / 'tmp' / 'memory-nudge-done-sess'
    assert done.exists()


def test_precompact_suppresses_later_stop(tmp_path, monkeypatch, capsys):
    run(monkeypatch, capsys, base(tmp_path, 'PreCompact'))
    out = run(monkeypatch, capsys, base(tmp_path, 'Stop'))

    assert out is None


def test_first_stop_is_silent_and_records(tmp_path, monkeypatch, capsys):
    out = run(monkeypatch, capsys, base(tmp_path, 'Stop'))

    assert out is None
    start = tmp_path / '.claude' / 'tmp' / 'memory-nudge-start-sess'
    started, count = memory_nudge.read_start(str(start))
    assert started is not None
    assert count == 1


def test_short_session_fires_on_count_threshold(tmp_path, monkeypatch, capsys):
    # Three rapid Stops (never near 30 min) still yield exactly one nudge.
    assert run(monkeypatch, capsys, base(tmp_path, 'Stop')) is None
    assert run(monkeypatch, capsys, base(tmp_path, 'Stop')) is None
    out = run(monkeypatch, capsys, base(tmp_path, 'Stop'))

    assert out['hookSpecificOutput']['hookEventName'] == 'Stop'
    assert out['hookSpecificOutput']['additionalContext'] == memory_nudge.NUDGE_TEXT


def test_fires_once_then_silent(tmp_path, monkeypatch, capsys):
    for _ in range(memory_nudge.STOP_COUNT_THRESHOLD):
        run(monkeypatch, capsys, base(tmp_path, 'Stop'))
    # Next Stop after the done marker stays silent.
    out = run(monkeypatch, capsys, base(tmp_path, 'Stop'))

    assert out is None


def test_wall_clock_path_fires_before_count(tmp_path, monkeypatch, capsys):
    # Seed a start well past the wall-clock threshold with a low count; the
    # next Stop should fire via elapsed time, not the count gate.
    start = tmp_path / '.claude' / 'tmp' / 'memory-nudge-start-sess'
    start.parent.mkdir(parents=True)
    memory_nudge.write_start(
        str(start), 100.0, 1
    )  # started long ago; time.time() >> 100 + threshold
    out = run(monkeypatch, capsys, base(tmp_path, 'Stop'))

    assert out['hookSpecificOutput']['additionalContext'] == memory_nudge.NUDGE_TEXT


def test_stop_hook_active_bails(tmp_path, monkeypatch, capsys):
    out = run(monkeypatch, capsys, base(tmp_path, 'Stop', stop_hook_active=True))

    assert out is None
