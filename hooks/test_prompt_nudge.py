from prompt_nudge import explicit_route


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


def test_continue_routes_to_cont(monkeypatch) -> None:
    monkeypatch.delenv('KRONAEL_IN_CODEX', raising=False)
    assert explicit_route('continue') == '/cont'
    assert explicit_route('cont') == '/cont'
    assert explicit_route('pick up where we left off') is None
