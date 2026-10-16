# pyright: basic
import io
import json

import memory_nudge
import pytest
from memory_nudge import due

SESSION = {'session_id': 'sess', 'cwd': '/repo'}


def test_first_stop_is_silent_and_records_the_start(fake_kvs) -> None:
    assert due(SESSION, 1000.0) is False
    assert fake_kvs.value('memory:started', 'sess', '/repo') == '1000'
    assert fake_kvs.value('memory:stops', 'sess', '/repo') == '1'


@pytest.mark.usefixtures('fake_kvs')
def test_short_session_fires_on_the_third_stop() -> None:
    assert due(SESSION, 1000.0) is False
    assert due(SESSION, 1010.0) is False
    assert due(SESSION, 1020.0) is True


@pytest.mark.usefixtures('fake_kvs')
def test_fires_once_then_stays_silent() -> None:
    for now in (1000.0, 1010.0, 1020.0):
        due(SESSION, now)
    assert due(SESSION, 1030.0) is False
    assert due(SESSION, 9000.0) is False


@pytest.mark.usefixtures('fake_kvs')
def test_wall_clock_fires_before_the_count() -> None:
    assert due(SESSION, 1000.0) is False
    assert due(SESSION, 1000.0 + memory_nudge.SESSION_THRESHOLD) is True


@pytest.mark.usefixtures('fake_kvs')
def test_sessions_do_not_share_state() -> None:
    other = {'session_id': 'other', 'cwd': '/repo'}
    for now in (1000.0, 1010.0):
        due(SESSION, now)
    assert due(other, 1020.0) is False


@pytest.mark.usefixtures('no_kvs')
def test_without_kvs_nothing_is_due() -> None:
    assert due(SESSION, 1000.0) is False


def run_main(monkeypatch, capsys, payload):
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(payload)))
    memory_nudge.main()
    out = capsys.readouterr().out.strip()
    return json.loads(out) if out else None


@pytest.mark.usefixtures('fake_kvs')
def test_main_emits_the_learn_pointer_on_stop(monkeypatch, capsys) -> None:
    payload = {**SESSION, 'hook_event_name': 'Stop'}
    assert run_main(monkeypatch, capsys, payload) is None
    assert run_main(monkeypatch, capsys, payload) is None
    out = run_main(monkeypatch, capsys, payload)
    assert out['hookSpecificOutput']['hookEventName'] == 'Stop'
    assert out['hookSpecificOutput']['additionalContext'].startswith('<reminder skill="learn">')


def test_main_bails_on_a_revision_stop_and_other_events(fake_kvs, monkeypatch, capsys) -> None:
    assert (
        run_main(
            monkeypatch, capsys, {**SESSION, 'hook_event_name': 'Stop', 'stop_hook_active': True}
        )
        is None
    )
    assert run_main(monkeypatch, capsys, {**SESSION, 'hook_event_name': 'PreCompact'}) is None
    assert fake_kvs.calls == []
