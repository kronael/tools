# pyright: basic
import io
import json
from pathlib import Path

import prompt_nudge
import pytest
from lib import kvs
from prompt_nudge import explicit_route
from prompt_nudge import main

SOLVE = '<reminder skill="solve">first prompt: route the task before acting</reminder>'


@pytest.fixture(autouse=True)
def memory(fake_kvs, monkeypatch, tmp_path):
    monkeypatch.setenv('HOME', str(tmp_path))
    return fake_kvs


def run(monkeypatch, capsys, prompt, session_id='sess', cwd='.'):
    data = {'prompt': prompt, 'session_id': session_id, 'cwd': cwd}
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(data)))
    main()
    out = capsys.readouterr().out.strip()
    return json.loads(out)['hookSpecificOutput']['additionalContext'] if out else ''


def test_code_does_not_route_to_codex() -> None:
    assert explicit_route('write code for this') is None


def test_codex_route_requires_explicit_second_opinion() -> None:
    assert explicit_route('ask codex for a second opinion') == 'astra'
    assert explicit_route('oracle this') == 'astra'


def test_slash_astra_routes_to_astra_and_is_suppressed_in_codex() -> None:
    assert explicit_route('/astra handle this') == 'astra'
    assert explicit_route('/astra handle this', harness='codex') is None


def test_every_route_names_a_bundled_skill() -> None:
    skills = Path(prompt_nudge.__file__).resolve().parent.parent / 'skills'
    targets = {*prompt_nudge.SKILL_KEYWORDS.values(), *prompt_nudge.TIERS, 'astra'}
    missing = [t for t in targets if not (skills / t / 'SKILL.md').is_file()]
    assert not missing


@pytest.mark.parametrize(
    'prompt',
    [
        'use SOL as collateral on the perp',
        'run sol through the swap simulator',
        'use astra db for vectors',
        'ls /sol/data',
        'cd /astra',
        'sol configuration',
    ],
)
def test_bare_astra_and_sol_words_do_not_route(prompt) -> None:
    assert explicit_route(prompt) is None


def test_ask_astra_routes_like_ask_codex() -> None:
    assert explicit_route('ask astra about this design') == 'astra'


def test_codex_route_suppressed_inside_codex() -> None:
    assert explicit_route('ask codex for a second opinion', harness='codex') is None


def test_route_is_a_bare_skill_name() -> None:
    assert explicit_route('use fable for this', harness='codex') == 'fable'


@pytest.mark.parametrize('tier', prompt_nudge.TIERS)
def test_tiers_require_explicit_escalation(tier) -> None:
    assert explicit_route(f'{tier} nudge is bad') is None
    assert explicit_route(f'use {tier} for this') == tier
    assert explicit_route(f'/{tier} handle this') == tier


@pytest.mark.parametrize(
    'prompt',
    [
        'the LUNA feed froze at $0.10',
        'terra classic depegged in may',
        'a haiku about the borrow checker',
    ],
)
def test_bare_tier_words_do_not_route(prompt) -> None:
    assert explicit_route(prompt) is None


def test_continue_routes_to_continue_skill() -> None:
    assert explicit_route('continue') == 'continue'
    assert explicit_route('cont') == 'continue'
    assert explicit_route('pick up where we left off') is None


@pytest.mark.parametrize(
    'word',
    [
        'ceo',
        'cto',
        'eval',
        'novice',
        'pentest',
        'roi',
        'security',
        'ux',
        'usability',
        'walkthrough',
    ],
)
def test_eval_lens_words_route_to_eval(word) -> None:
    assert explicit_route(f'run a {word} pass on the dashboard') == 'eval'


def test_ship_phrasings_route_to_ship() -> None:
    for prompt in ('ship this', 'ship it', "let's ship", 'and ship it'):
        assert explicit_route(prompt) == 'ship', prompt


def test_output_is_context_made_of_pointers(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        'sys.stdin', io.StringIO(json.dumps({'prompt': 'ship it', 'session_id': 's'}))
    )
    main()
    out = json.loads(capsys.readouterr().out)
    assert 'systemMessage' not in out
    assert out['hookSpecificOutput']['hookEventName'] == 'UserPromptSubmit'
    assert out['hookSpecificOutput']['additionalContext'] == f'{SOLVE}\n<skill name="ship"/>'


def test_commit_points_at_the_commit_skill_over_a_route(monkeypatch, capsys) -> None:
    run(monkeypatch, capsys, 'warm up')
    assert run(monkeypatch, capsys, 'commit this fix') == '<skill name="commit"/>'


def test_document_mention_points_at_readme(monkeypatch, capsys) -> None:
    run(monkeypatch, capsys, 'warm up')
    assert run(monkeypatch, capsys, 'update the README') == '<skill name="readme"/>'


def test_first_prompt_points_at_solve_and_local_files(monkeypatch, capsys, tmp_path) -> None:
    (tmp_path / 'LOCAL.md').write_text('# local\n')
    monkeypatch.setattr(prompt_nudge, 'LOCAL_FILES', ('LOCAL.md',))
    text = run(monkeypatch, capsys, 'add a health endpoint', cwd=str(tmp_path))
    assert text == f'{SOLVE}\n<file path="{tmp_path / "LOCAL.md"}"/>'


def test_continuation_is_silent(monkeypatch, capsys) -> None:
    run(monkeypatch, capsys, 'add a health endpoint')
    assert run(monkeypatch, capsys, 'now wire it into main') == ''


def test_explicit_solve_prompt_is_not_nudged(monkeypatch, capsys) -> None:
    assert SOLVE not in run(monkeypatch, capsys, '/solve this request')
    assert SOLVE not in run(monkeypatch, capsys, 'now do the work')


def test_empty_prompt_is_not_consumed(monkeypatch, capsys) -> None:
    assert run(monkeypatch, capsys, '   ') == ''
    assert SOLVE in run(monkeypatch, capsys, 'add a feature')


def test_meta_prompt_keeps_only_the_caveman_pointer(monkeypatch, capsys, fake_kvs) -> None:
    assert run(monkeypatch, capsys, 'debug the hook') == ''
    fake_kvs.data[(('sess', '.'), 'caveman')] = json.dumps({'level': 1, 'lines': 27, 'cap': 20})
    assert run(monkeypatch, capsys, 'fix the hook') == (
        '<reminder skill="caveman" rule="budget" lines="27" cap="20"/>'
    )
    assert SOLVE in run(monkeypatch, capsys, 'add a feature')


def test_caveman_pointer_follows_the_solve_pointer(monkeypatch, capsys, fake_kvs) -> None:
    fake_kvs.data[(('sess', '.'), 'caveman')] = json.dumps({'level': 2, 'bullets': 7, 'cap': 5})
    text = run(monkeypatch, capsys, 'ship it')
    assert text.split('\n') == [
        SOLVE,
        '<reminder skill="caveman" rule="budget" bullets="7" cap="5"/>',
        '<skill name="ship"/>',
    ]


def test_nudge_is_keyed_by_session(monkeypatch, capsys) -> None:
    run(monkeypatch, capsys, 'add a feature', session_id='a')
    assert SOLVE in run(monkeypatch, capsys, 'add a feature', session_id='b')


@pytest.mark.usefixtures('no_kvs')
def test_without_kvs_only_routes_remain(monkeypatch, capsys) -> None:
    monkeypatch.setattr(kvs, 'BINARY', None)
    monkeypatch.setattr(kvs, 'run', lambda *_, **__: None)
    assert run(monkeypatch, capsys, 'ship it') == '<skill name="ship"/>'
