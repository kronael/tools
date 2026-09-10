import io
import json
import os
import subprocess
from datetime import UTC
from datetime import datetime

import stop
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


def test_missing_diary_warns_without_writing_a_file(tmp_path, monkeypatch, capsys) -> None:
    # Regression: stop.py must only warn about a missing diary entry, never
    # create one — ARCHITECTURE.md and README.md both document "does not
    # write diary headers" as the contract.
    subprocess.run(['git', 'init', '-q'], cwd=tmp_path, check=True)
    (tmp_path / '.diary').mkdir()

    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps({'cwd': str(tmp_path)})))
    stop.main()

    output = json.loads(capsys.readouterr().out)
    assert 'Run /diary' in output['reason']
    assert list((tmp_path / '.diary').iterdir()) == []


def test_stale_diary_warns_without_touching_the_file(tmp_path, monkeypatch, capsys) -> None:
    subprocess.run(['git', 'init', '-q'], cwd=tmp_path, check=True)
    diary_dir = tmp_path / '.diary'
    diary_dir.mkdir()
    today = datetime.now(tz=UTC).strftime('%Y%m%d')
    diary_file = diary_dir / f'{today}.md'
    diary_file.write_text('## old entry\n')
    old = datetime.now(tz=UTC).timestamp() - 7200
    os.utime(diary_file, (old, old))
    before = diary_file.read_text()

    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps({'cwd': str(tmp_path)})))
    stop.main()

    output = json.loads(capsys.readouterr().out)
    assert 'Diary not updated in over an hour' in output['reason']
    assert diary_file.read_text() == before
