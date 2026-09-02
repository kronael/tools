import json

from stop import emit


def test_emit_keeps_stop_block(capsys) -> None:
    emit(['commit first'], {'hook_event': 'Stop'})

    output = json.loads(capsys.readouterr().out)
    assert output == {'decision': 'block', 'reason': 'commit first'}


def test_emit_post_tool_nudge_is_context(capsys) -> None:
    emit(['commit soon'], {'hook_event_name': 'PostToolUse'})

    output = json.loads(capsys.readouterr().out)
    assert 'decision' not in output
    assert output == {
        'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': 'commit soon',
        },
    }


def test_emit_post_tool_env_is_context(capsys, monkeypatch) -> None:
    monkeypatch.setenv('KRONAEL_HOOK_EVENT', 'PostToolUse')
    emit(['commit soon'], {})

    output = json.loads(capsys.readouterr().out)
    assert 'decision' not in output
    assert output['hookSpecificOutput']['hookEventName'] == 'PostToolUse'


import io
import os
import subprocess

import pytest
import stop


@pytest.fixture(autouse=True)
def state_root(tmp_path, monkeypatch):
    root = tmp_path / 'state'
    monkeypatch.setenv('KRONAEL_HOOK_STATE', str(root))
    monkeypatch.delenv('KRONAEL_HOOK_EVENT', raising=False)
    return root


def test_append_header_creates_missing_file(tmp_path) -> None:
    diary = tmp_path / '.diary' / '20260829.md'

    assert stop.append_header(str(diary), '07:57 2026-08-29') is True
    assert diary.read_text() == '\n## 07:57 2026-08-29\n\n'


def test_append_header_refuses_second_empty_header(tmp_path) -> None:
    """An unfilled header is the pending nudge — never stack another on it."""
    diary = tmp_path / '.diary' / '20260829.md'
    stop.append_header(str(diary), '07:57 2026-08-29')

    assert stop.append_header(str(diary), '09:12 2026-08-29') is False
    assert diary.read_text().count('## ') == 1


def test_append_header_appends_once_entry_is_filled(tmp_path) -> None:
    diary = tmp_path / '.diary' / '20260829.md'
    stop.append_header(str(diary), '07:57 2026-08-29')
    with open(diary, 'a') as f:
        f.write('shipped the thing\n')

    assert stop.append_header(str(diary), '09:12 2026-08-29') is True
    assert diary.read_text().count('## ') == 2


def git_repo(tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    return repo


def run_stop(monkeypatch, capsys, repo, session_id):
    payload = {'hook_event': 'Stop', 'cwd': str(repo), 'session_id': session_id}
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(payload)))
    stop.main()
    return capsys.readouterr().out


def test_diary_nudge_fires_once_per_session(tmp_path, monkeypatch, capsys) -> None:
    repo = git_repo(tmp_path)

    first = run_stop(monkeypatch, capsys, repo, 'sess')
    second = run_stop(monkeypatch, capsys, repo, 'sess')

    assert 'No diary entry for today' in first
    assert second == ''


def test_diary_nudge_survives_cwd_change(tmp_path, monkeypatch, capsys) -> None:
    """One session visiting two repos still gets one diary nudge."""
    repo = git_repo(tmp_path)
    other = tmp_path / 'other'
    other.mkdir()
    subprocess.run(['git', 'init', '-q', str(other)], check=True)

    run_stop(monkeypatch, capsys, repo, 'sess')

    assert run_stop(monkeypatch, capsys, other, 'sess') == ''
    assert not (other / '.diary').exists()


def test_diary_nudge_is_honest_when_header_not_written(tmp_path, monkeypatch, capsys) -> None:
    repo = git_repo(tmp_path)
    diary = repo / '.diary'
    diary.mkdir()
    stamp = diary / (stop.datetime.now(tz=stop.UTC).strftime('%Y%m%d') + '.md')
    stamp.write_text('\n## 06:00 old\n\n')
    os.utime(stamp, (0, 0))

    out = run_stop(monkeypatch, capsys, repo, 'sess')

    assert 'Diary not updated in over an hour' in out
    assert 'Entry header appended' not in out
    assert stamp.read_text().count('## ') == 1
