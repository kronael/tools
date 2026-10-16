# pyright: basic
import subprocess

import pytest
from lib import kvs


class Done:
    def __init__(self, stdout, returncode):
        self.stdout = stdout
        self.returncode = returncode


@pytest.mark.usefixtures('no_kvs')
def test_missing_binary_is_silent() -> None:
    assert kvs.run(['get', 'k']) is None
    assert kvs.get('k') is None
    assert kvs.set('k', 1) is False
    assert kvs.incr('k') is None


def test_arguments_carry_scope_and_options(monkeypatch) -> None:
    seen = []

    def fake_run(command, **_):
        seen.append(command)
        return Done('7\n', 0)

    monkeypatch.setattr(kvs, 'BINARY', '/bin/kvs')
    monkeypatch.setattr(subprocess, 'run', fake_run)
    assert kvs.incr('n', 'sess', '/repo', ttl=600) == 7
    assert seen[-1] == ['/bin/kvs', '-s', 'sess', '-p', '/repo', 'incr', 'n', '-t', '600']
    assert kvs.set('flag', 1, 'sess', if_old='') is True
    assert seen[-1] == ['/bin/kvs', '-s', 'sess', 'set', 'flag', '1', '-i', '']
    assert kvs.get('n', cwd='/repo') == '7'
    assert seen[-1] == ['/bin/kvs', '-p', '/repo', 'get', 'n']


def test_nonzero_exit_reads_as_absent_or_unset(monkeypatch) -> None:
    monkeypatch.setattr(kvs, 'BINARY', '/bin/kvs')
    monkeypatch.setattr(subprocess, 'run', lambda *_, **__: Done('', 1))
    assert kvs.get('k') is None
    assert kvs.set('k', 1, if_old='') is False
    assert kvs.incr('k') is None


def test_a_failing_process_is_silent(monkeypatch) -> None:
    def boom(*_, **__):
        raise subprocess.TimeoutExpired('kvs', 3)

    monkeypatch.setattr(kvs, 'BINARY', '/bin/kvs')
    monkeypatch.setattr(subprocess, 'run', boom)
    assert kvs.run(['get', 'k']) is None
