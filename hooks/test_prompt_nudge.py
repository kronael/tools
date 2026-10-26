import io
import json
import os
import time
from pathlib import Path

import prompt_nudge
import pytest
from prompt_nudge import explicit_route
from prompt_nudge import main


@pytest.fixture(autouse=True)
def state_root(tmp_path, monkeypatch):
    monkeypatch.setenv('KRONAEL_HOOK_STATE', str(tmp_path / 'state'))


def run(monkeypatch, capsys, prompt, session_id='sess'):
    data = {'prompt': prompt, 'session_id': session_id, 'cwd': '.'}
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(data)))
    with pytest.raises(SystemExit):
        main()
    out = capsys.readouterr().out.strip()
    return json.loads(out)['hookSpecificOutput']['additionalContext'] if out else ''


def test_code_does_not_route_to_codex() -> None:
    assert explicit_route('write code for this') is None


@pytest.mark.parametrize(
    ('prompt', 'route'),
    [
        ('dispatch implement this change', '/dispatch'),
        ('review this with dispatch', '/dispatch'),
        ('dispatch this to Astra for a second opinion', '/dispatch'),
        ('oracle this', '/oracle'),
        ('ask codex for a second opinion', '/oracle'),
        ('use opus for a second opinion', '/oracle'),
        ('ask Sol for a second opinion', '/oracle'),
        ('ask codex about this design', '/codex'),
        ('use claude for this task', '/claude'),
        ('ask astra about this design', '/dispatch'),
        ('use sol for this implementation', '/dispatch'),
        ('use fable for this', '/dispatch'),
        ('/astra handle this', '/dispatch'),
        ('/fable handle this', '/dispatch'),
        ('@luna inventory these files', '/dispatch'),
        ('/refine this with Astra', '/refine'),
        ('@review this with Sol', '/review'),
        ('/oracle use opus', '/oracle'),
        ('/codex implement this', '/codex'),
    ],
)
def test_task_provider_and_opinion_routes(prompt, route) -> None:
    assert explicit_route(prompt) == route


@pytest.mark.parametrize(
    'prompt',
    [
        '/ans ask codex to explain this',
        '@ans ask claude to explain this',
        '/fix use Sol for this bug',
        '@fix use Astra for this bug',
        '/custom-workflow dispatch this review',
    ],
)
def test_other_leading_commands_suppress_conflicting_routes(prompt) -> None:
    assert explicit_route(prompt) is None


@pytest.mark.parametrize('harness', ['claude', 'codex'])
def test_leading_answer_mode_receives_no_provider_nudge(monkeypatch, capsys, harness):
    payload = {'prompt': '/ans ask codex to explain this', 'harness': harness}
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(payload)))
    with pytest.raises(SystemExit):
        main()
    output = json.loads(capsys.readouterr().out)
    context = output['hookSpecificOutput']['additionalContext']
    assert context == prompt_nudge.SOLVE_NUDGE


def test_every_route_names_a_bundled_skill() -> None:
    skills = Path(prompt_nudge.__file__).resolve().parent.parent / 'skills'
    targets = {
        *prompt_nudge.SKILL_KEYWORDS.values(),
        *(route for _, route in prompt_nudge.MODEL_PATTERNS),
        explicit_route('ask codex about this design'),
        explicit_route('ask claude about this design'),
        explicit_route('oracle this'),
    }
    missing = [
        target
        for target in targets
        if not (target and (skills / target.removeprefix('/') / 'SKILL.md').is_file())
    ]
    assert not missing


@pytest.mark.parametrize(
    'prompt',
    [
        'use SOL as collateral on the perp',
        'run sol through the swap simulator',
        'use astra db for vectors',
        'ls /sol/data',
        'cd /astra',
        '/astra/data contains vectors',
        '/codex/data contains files',
        'cd /claude',
        'sol configuration',
        'fable nudge is bad',
        'sonnet is a poem',
    ],
)
def test_model_like_names_and_paths_do_not_route(prompt) -> None:
    assert explicit_route(prompt) is None


@pytest.mark.parametrize('harness', ['claude', 'codex'])
@pytest.mark.parametrize(
    ('prompt', 'route'),
    [
        ('dispatch a fresh review using Sol high', '/dispatch'),
        ('ask codex for a second opinion', '/oracle'),
        ('/refine the entire change with Astra', '/refine'),
    ],
)
def test_both_harnesses_receive_the_requested_workflow(monkeypatch, capsys, harness, prompt, route):
    payload = {'prompt': prompt, 'harness': harness, 'session_id': 'route-fixture'}
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(payload)))
    with pytest.raises(SystemExit):
        main()
    output = json.loads(capsys.readouterr().out)
    context = output['hookSpecificOutput']['additionalContext']
    assert f'info: Invoke {route}.' in context
    assert 'the current Codex session' not in context


def test_continue_routes_to_continue_skill() -> None:
    assert explicit_route('continue') == '/continue'
    assert explicit_route('cont') == '/continue'
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
        'ux',
        'usability',
        'walkthrough',
    ],
)
def test_eval_lens_words_route_to_eval(word) -> None:
    assert explicit_route(f'run a {word} pass on the dashboard') == '/eval'


def test_ship_phrasings_route_to_ship() -> None:
    for prompt in ('ship this', 'ship it', "let's ship", 'and ship it'):
        assert explicit_route(prompt) == '/ship', prompt


def test_commit_routes_to_commit() -> None:
    assert explicit_route('commit this') == '/commit'


@pytest.mark.parametrize(
    'prompt',
    [
        'fix the failing test',
        'design the schema',
        'create a config file',
        'run it in the background',
        'add the security headers',
        'draft the email',
        'the inline comment is wrong',
    ],
)
def test_plain_verbs_do_not_route(prompt) -> None:
    assert explicit_route(prompt) is None


def test_continuation_without_a_route_is_silent(monkeypatch, capsys) -> None:
    run(monkeypatch, capsys, 'add a health endpoint')
    assert run(monkeypatch, capsys, 'now wire it into main') == ''


def test_output_reaches_the_model(monkeypatch, capsys) -> None:
    # Only hookSpecificOutput.additionalContext is added to the model's context;
    # systemMessage is rendered for the user alone.
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps({'prompt': 'ship it'})))
    with pytest.raises(SystemExit):
        main()
    out = json.loads(capsys.readouterr().out)
    assert 'systemMessage' not in out
    assert out['hookSpecificOutput']['hookEventName'] == 'UserPromptSubmit'
    assert 'info: Invoke /ship.' in out['hookSpecificOutput']['additionalContext']


def test_first_prompt_nudges_solve(monkeypatch, capsys) -> None:
    assert prompt_nudge.SOLVE_NUDGE in run(monkeypatch, capsys, 'add a health endpoint')


def test_continuation_does_not_nudge_solve(monkeypatch, capsys) -> None:
    run(monkeypatch, capsys, 'add a health endpoint')
    assert prompt_nudge.SOLVE_NUDGE not in run(monkeypatch, capsys, 'now wire it into main')


def test_solve_nudge_precedes_route_on_first_prompt(monkeypatch, capsys) -> None:
    text = run(monkeypatch, capsys, 'ship this feature')
    assert text.startswith(prompt_nudge.SOLVE_NUDGE)
    assert '/ship' in text


def test_explicit_solve_prompt_is_not_nudged(monkeypatch, capsys) -> None:
    # User already invoked /solve: no nudge, and first-prompt status is still
    # consumed so the next prompt is a silent continuation.
    assert prompt_nudge.SOLVE_NUDGE not in run(monkeypatch, capsys, '/solve this request')
    assert prompt_nudge.SOLVE_NUDGE not in run(monkeypatch, capsys, 'now do the work')


def test_empty_prompt_is_not_consumed(monkeypatch, capsys) -> None:
    # A whitespace payload is not a task: no nudge, and it does not burn the
    # session's first-prompt status.
    assert prompt_nudge.SOLVE_NUDGE not in run(monkeypatch, capsys, '   ')
    assert prompt_nudge.SOLVE_NUDGE in run(monkeypatch, capsys, 'add a feature')


def test_meta_first_prompt_is_transparent(monkeypatch, capsys) -> None:
    # A hook-debugging prompt is skipped without consuming first-prompt status;
    # the next real prompt still gets the solve nudge.
    assert prompt_nudge.SOLVE_NUDGE not in run(monkeypatch, capsys, 'debug the hook')
    assert prompt_nudge.SOLVE_NUDGE in run(monkeypatch, capsys, 'add a feature')


def test_nudge_is_keyed_by_session_not_cwd(monkeypatch, capsys) -> None:
    run(monkeypatch, capsys, 'add a feature', session_id='a')
    assert prompt_nudge.SOLVE_NUDGE in run(monkeypatch, capsys, 'add a feature', session_id='b')


def age_previous_prompt(session_id='sess', minutes=prompt_nudge.IDLE_MINUTES + 1) -> None:
    marker = prompt_nudge.session_state('solve-nudge', session_id)
    old = time.time() - minutes * 60
    os.utime(marker, (old, old))


def test_prompt_after_idle_gap_nudges_solve(monkeypatch, capsys) -> None:
    run(monkeypatch, capsys, 'add a health endpoint')
    age_previous_prompt()
    text = run(monkeypatch, capsys, 'study this library, could we use it?')
    assert prompt_nudge.IDLE_NUDGE in text
    assert prompt_nudge.SOLVE_NUDGE not in text


def test_prompt_within_the_gap_is_silent(monkeypatch, capsys) -> None:
    run(monkeypatch, capsys, 'add a health endpoint')
    age_previous_prompt(minutes=prompt_nudge.IDLE_MINUTES - 1)
    assert prompt_nudge.IDLE_NUDGE not in run(
        monkeypatch, capsys, 'study this library, could we use it?'
    )


@pytest.mark.parametrize(
    'prompt',
    [
        'cont and fin',
        'commit this',
        '/goal finish the migration',
        'This session is being continued from a previous conversation that ran out of context.',
    ],
)
def test_routed_prompt_after_idle_gap_is_silent(monkeypatch, capsys, prompt) -> None:
    run(monkeypatch, capsys, 'add a health endpoint')
    age_previous_prompt()
    assert prompt_nudge.IDLE_NUDGE not in run(monkeypatch, capsys, prompt)


def test_every_prompt_restamps_the_gap(monkeypatch, capsys) -> None:
    # A routed "cont" is silent but still the previous prompt: a task-shaped
    # prompt one minute after it is inside the gap.
    run(monkeypatch, capsys, 'add a health endpoint')
    age_previous_prompt()
    run(monkeypatch, capsys, 'cont')
    assert prompt_nudge.IDLE_NUDGE not in run(monkeypatch, capsys, 'now study this library')


def run_subagent_start(monkeypatch, capsys, agent_type, session_id='sess'):
    data = {
        'hook_event_name': 'SubagentStart',
        'session_id': session_id,
        'agent_id': 'agent-1',
        'agent_type': agent_type,
    }
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(data)))
    with pytest.raises(SystemExit):
        main()
    out = capsys.readouterr().out.strip()
    return json.loads(out) if out else None


def test_subagent_start_nudges_solve(monkeypatch, capsys) -> None:
    out = run_subagent_start(monkeypatch, capsys, 'sonnet')
    assert out['hookSpecificOutput']['hookEventName'] == 'SubagentStart'
    assert out['hookSpecificOutput']['additionalContext'] == prompt_nudge.SUBAGENT_NUDGE


def test_subagent_start_does_not_consume_the_parent_first_prompt(monkeypatch, capsys) -> None:
    # The payload carries the parent's session id.
    run_subagent_start(monkeypatch, capsys, 'sonnet')
    assert prompt_nudge.SOLVE_NUDGE in run(monkeypatch, capsys, 'add a feature')


def test_harness_agent_start_is_silent(monkeypatch, capsys) -> None:
    assert run_subagent_start(monkeypatch, capsys, 'Explore') is None
