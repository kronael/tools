import io
import json

import prompt_nudge
import pytest
from prompt_nudge import explicit_route


def run(monkeypatch, capsys, prompt, cwd, session_id='sess'):
    data = {'prompt': prompt, 'session_id': session_id, 'cwd': str(cwd)}
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(data)))
    with pytest.raises(SystemExit):
        prompt_nudge.main()
    out = capsys.readouterr().out.strip()
    return json.loads(out) if out else None


def test_code_does_not_route_to_codex(monkeypatch) -> None:
    monkeypatch.delenv('KRONAEL_IN_CODEX', raising=False)
    assert explicit_route('write code for this') is None


def test_codex_route_requires_explicit_second_opinion(monkeypatch) -> None:
    monkeypatch.delenv('KRONAEL_IN_CODEX', raising=False)
    assert explicit_route('ask codex for a second opinion') == '/codex'
    assert explicit_route('oracle this') == '/codex'


def test_codex_route_suppressed_inside_codex(monkeypatch) -> None:
    monkeypatch.setenv('KRONAEL_IN_CODEX', '1')
    assert explicit_route('ask codex for a second opinion') is None


def test_fable_requires_explicit_escalation(monkeypatch) -> None:
    monkeypatch.delenv('KRONAEL_IN_CODEX', raising=False)
    assert explicit_route('fable nudge is bad') is None
    assert explicit_route('use fable for this') == '/fable'
    assert explicit_route('/fable handle this') == '/fable'


def test_continue_routes_to_continue_skill(monkeypatch) -> None:
    monkeypatch.delenv('KRONAEL_IN_CODEX', raising=False)
    assert explicit_route('continue') == '/continue'
    assert explicit_route('cont') == '/continue'
    assert explicit_route('pick up where we left off') is None


def test_first_prompt_nudges_resolve(tmp_path, monkeypatch, capsys) -> None:
    out = run(monkeypatch, capsys, 'add a health endpoint', tmp_path)
    assert prompt_nudge.RESOLVE_NUDGE in out['systemMessage']


def test_continuation_does_not_nudge_resolve(tmp_path, monkeypatch, capsys) -> None:
    run(monkeypatch, capsys, 'add a health endpoint', tmp_path)
    out = run(monkeypatch, capsys, 'now wire it into main', tmp_path)
    assert out is None


def test_resolve_nudge_precedes_route_on_first_prompt(tmp_path, monkeypatch, capsys) -> None:
    out = run(monkeypatch, capsys, 'ship this feature', tmp_path)
    message = out['systemMessage']
    assert message.startswith(prompt_nudge.RESOLVE_NUDGE)
    assert '/ship' in message


def test_explicit_resolve_prompt_is_not_nudged(tmp_path, monkeypatch, capsys) -> None:
    # User already invoked /resolve: no nudge, and first-prompt status is still
    # consumed so the next prompt is a silent continuation.
    assert run(monkeypatch, capsys, '/resolve this request', tmp_path) is None
    assert run(monkeypatch, capsys, 'now do the work', tmp_path) is None


def test_empty_prompt_is_silent_and_not_consumed(tmp_path, monkeypatch, capsys) -> None:
    # An empty/whitespace payload is not a task: no nudge, and it does not burn
    # the session's first-prompt status.
    assert run(monkeypatch, capsys, '   ', tmp_path) is None
    out = run(monkeypatch, capsys, 'add a feature', tmp_path)
    assert prompt_nudge.RESOLVE_NUDGE in out['systemMessage']


def test_meta_first_prompt_is_transparent(tmp_path, monkeypatch, capsys) -> None:
    # A hook-debugging prompt is skipped without consuming first-prompt status;
    # the next real prompt still gets the resolve nudge.
    assert run(monkeypatch, capsys, 'debug the hook', tmp_path) is None
    out = run(monkeypatch, capsys, 'add a feature', tmp_path)
    assert prompt_nudge.RESOLVE_NUDGE in out['systemMessage']
