# pyright: basic
"""An in-memory kvs for the hook tests: the CLI's get/set/incr contract over a
dict, so a test never touches the real database or needs the binary."""

import time

import pytest
from lib import kvs


class FakeKvs:
    def __init__(self):
        self.data = {}
        self.expiry = {}
        self.calls = []

    def run(self, args, session=None, cwd=None):
        args = list(args)
        self.calls.append((tuple(args), session, cwd))
        scope = (session or '', cwd or '')
        command = args[0]
        key = (scope, args[1])
        if self.expiry.get(key, float('inf')) <= time.time():
            self.data.pop(key, None)
            self.expiry.pop(key, None)
        if command == 'get':
            return (self.data[key], 0) if key in self.data else ('', 1)
        options = dict(zip(args[2:], args[3:]))
        if command == 'set':
            if '-i' in args:
                old = args[args.index('-i') + 1]
                present = key in self.data
                if present != bool(old) or (present and self.data[key] != old):
                    return ('', 1)
            self.data[key] = args[2]
            self.arm(key, args)
            return ('', 0)
        if command == 'incr':
            step = int(args[2]) if len(args) > 2 and not args[2].startswith('-') else 1
            if key not in self.data:
                self.arm(key, args)
            value = int(self.data.get(key, '0')) + step
            self.data[key] = str(value)
            return (str(value), 0)
        raise AssertionError(f'unexpected kvs call {args} {options}')

    def arm(self, key, args):
        if '-t' in args:
            self.expiry[key] = time.time() + int(args[args.index('-t') + 1])

    def value(self, key, session=None, cwd=None):
        return self.data.get(((session or '', cwd or ''), key))


@pytest.fixture
def fake_kvs(monkeypatch):
    fake = FakeKvs()
    monkeypatch.setattr(kvs, 'BINARY', '/fake/kvs')
    monkeypatch.setattr(kvs, 'run', fake.run)
    return fake


@pytest.fixture
def no_kvs(monkeypatch):
    monkeypatch.setattr(kvs, 'BINARY', None)
