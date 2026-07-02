import json

from stop import emit
from stop import fin_recent


def write_transcript(path, *items) -> None:
    lines = []
    for item in items:
        if isinstance(item, str):
            lines.append(item)
        else:
            lines.append(json.dumps(item))
    path.write_text('\n'.join(lines), encoding='utf-8')


def make_user_message(content):
    return {'type': 'user', 'message': {'role': 'user', 'content': content}}


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


def test_fin_recent_detects_explicit_slash_command(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('TMPDIR', str(tmp_path / 'tmp'))
    transcript = tmp_path / 'transcript.jsonl'
    write_transcript(transcript, make_user_message('/fin'))

    data = {'transcript_path': str(transcript), 'session_id': 'slash'}
    assert fin_recent(data) is True


def test_fin_recent_detects_command_marker(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('TMPDIR', str(tmp_path / 'tmp'))
    transcript = tmp_path / 'transcript.jsonl'
    write_transcript(
        transcript,
        make_user_message('<command-name>fin</command-name><command-args></command-args>'),
    )

    data = {'transcript_path': str(transcript), 'session_id': 'marker'}
    assert fin_recent(data) is True


def test_fin_recent_ignores_hook_wording(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('TMPDIR', str(tmp_path / 'tmp'))
    transcript = tmp_path / 'transcript.jsonl'
    write_transcript(
        transcript,
        make_user_message(
            '/fin (finish mode) was invoked. Before stopping, re-run the open-items pass.'
        ),
    )

    data = {'transcript_path': str(transcript), 'session_id': 'hook'}
    assert fin_recent(data) is False


def test_fin_recent_is_one_shot_per_session(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('TMPDIR', str(tmp_path / 'tmp'))
    transcript = tmp_path / 'transcript.jsonl'
    data = {'transcript_path': str(transcript), 'session_id': 'once'}
    write_transcript(transcript, make_user_message('/fin'))

    assert fin_recent(data) is True
    assert fin_recent(data) is False
