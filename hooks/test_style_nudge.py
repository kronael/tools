from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from style_nudge import main
from style_nudge import output_for
from style_nudge import read_reminder


def install_style(home: Path, selected: str = 'caveman') -> None:
    claude = home / '.claude'
    (claude / 'output-styles').mkdir(parents=True)
    (claude / 'settings.json').write_text(json.dumps({'outputStyle': selected}))
    (claude / 'output-styles' / 'caveman.md').write_text(
        '# Caveman\n\n## Budget — chat only\n\nKeep replies short.\n\n'
        '## Shape — chat only\n\nLead with the answer.\n\n## Language\n\nPlain.\n'
    )


def run(monkeypatch, capsys, home: Path, event: str) -> dict | None:
    monkeypatch.setenv('HOME', str(home))
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps({'hook_event_name': event})))
    main()
    text = capsys.readouterr().out.strip()
    return json.loads(text) if text else None


def test_reader_uses_the_selected_caveman_file(tmp_path: Path) -> None:
    install_style(tmp_path)
    reminder = read_reminder(tmp_path)
    assert reminder == (
        '<caveman-reminder>\n## Budget — chat only\n\nKeep replies short.\n\n'
        '## Shape — chat only\n\nLead with the answer.\n</caveman-reminder>'
    )


def test_reader_is_silent_for_another_selected_style(tmp_path: Path) -> None:
    install_style(tmp_path, selected='concise')
    assert read_reminder(tmp_path) is None


@pytest.mark.parametrize('event', ['UserPromptSubmit', 'PostToolUse'])
def test_context_events_reach_the_model(event: str) -> None:
    assert output_for(event, 'style') == {
        'hookSpecificOutput': {'hookEventName': event, 'additionalContext': 'style'}
    }


def test_compaction_uses_session_start_context() -> None:
    assert output_for('SessionStart', 'style') == {
        'hookSpecificOutput': {
            'hookEventName': 'SessionStart',
            'additionalContext': 'style',
        }
    }


def test_precompact_emits_no_discarded_context() -> None:
    assert output_for('PreCompact', 'style') is None


@pytest.mark.parametrize('event', ['UserPromptSubmit', 'PostToolUse', 'SessionStart'])
def test_installed_hook_emits_on_each_lifecycle_path(
    monkeypatch, capsys, tmp_path: Path, event: str
) -> None:
    install_style(tmp_path)
    output = run(monkeypatch, capsys, tmp_path, event)
    assert output is not None
    assert 'caveman-reminder' in json.dumps(output)


def test_missing_canonical_budget_fails_silent(monkeypatch, capsys, tmp_path: Path) -> None:
    install_style(tmp_path)
    (tmp_path / '.claude' / 'output-styles' / 'caveman.md').write_text(
        '# Caveman\n\n## Shape — chat only\n\nLead with the answer.\n'
    )
    assert run(monkeypatch, capsys, tmp_path, 'UserPromptSubmit') is None


def test_arizuko_mode_adds_the_selected_surface_length(tmp_path: Path) -> None:
    install_style(tmp_path, selected='discord-channel')
    styles = tmp_path / '.claude' / 'output-styles'
    (styles / 'discord-channel.md').write_text(
        '# Discord\n\n## Length\n\nDefault ceiling: ~500 chars.\n\n## Tone\n\nBrief.\n'
    )
    reminder = read_reminder(tmp_path, portable=False)
    assert reminder is not None
    assert '## Budget — chat only' in reminder
    assert '## Shape — chat only' in reminder
    assert '## Length\n\nDefault ceiling: ~500 chars.' in reminder


def test_bundle_source_and_lifecycle_wiring_stay_connected() -> None:
    root = Path(__file__).resolve().parent.parent
    raw = (root / 'output-styles' / 'caveman.md').read_text()
    assert '## Budget — chat only' in raw
    assert '## Shape — chat only' in raw
    assert (root / 'skills' / 'caveman' / 'reminder.py').is_file()

    settings = json.loads((root / 'settings-recommended.json').read_text())
    hooks = settings['hooks']
    for event in 'UserPromptSubmit', 'PostToolUse':
        commands = [hook['command'] for group in hooks[event] for hook in group['hooks']]
        assert 'python3 ~/.claude/hooks/style_nudge.py' in commands
    compact = [group for group in hooks['SessionStart'] if group['matcher'] == 'compact']
    assert len(compact) == 1
    commands = [hook['command'] for hook in compact[0]['hooks']]
    assert 'python3 ~/.claude/hooks/style_nudge.py' in commands
    precompact = [hook['command'] for group in hooks['PreCompact'] for hook in group['hooks']]
    assert 'python3 ~/.claude/hooks/style_nudge.py' not in precompact
