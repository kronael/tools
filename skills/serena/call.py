#!/usr/bin/env python3
"""Run one Serena tool on the git project around the working directory, then
stop Serena.

Usage: call.py <tool> '<json object of arguments>'
Prints the tool's text reply and exits 0; exits 1 when the tool reports an
error and 2 when the call cannot run (no git tree, no serena, bad JSON, no
reply within 300 s), with the reason and Serena's log tail on stderr.
"""

import contextlib
import json
import os
import signal
import subprocess
import sys
import tempfile
from typing import IO
from typing import Any

PROTOCOL = '2025-06-18'
REPLY_DEADLINE_S = 300
STOP_GRACE_S = 30


def run_git_toplevel() -> str:
    top = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE, text=True, check=True
    )
    return top.stdout.strip()


def send(server: subprocess.Popen[str], message: dict[str, Any]) -> None:
    assert server.stdin is not None
    server.stdin.write(json.dumps(message) + '\n')
    server.stdin.flush()


def request(
    server: subprocess.Popen[str], request_id: int, method: str, params: dict[str, Any]
) -> dict[str, Any]:
    assert server.stdout is not None
    send(server, {'jsonrpc': '2.0', 'id': request_id, 'method': method, 'params': params})
    for line in server.stdout:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            raise RuntimeError(f'{method}: serena wrote a non-JSON line: {line.strip()}') from None
        if 'method' in message or message.get('id') != request_id:
            continue
        if 'error' in message:
            raise RuntimeError(f'{method}: {message["error"]}')
        return message['result']
    raise RuntimeError(f'{method}: serena exited before it answered')


def stop(server: subprocess.Popen[str]) -> None:
    assert server.stdin is not None
    with contextlib.suppress(BrokenPipeError):
        server.stdin.close()
    try:
        server.wait(timeout=STOP_GRACE_S)
    except subprocess.TimeoutExpired:
        os.killpg(server.pid, signal.SIGTERM)
        try:
            server.wait(timeout=STOP_GRACE_S)
        except subprocess.TimeoutExpired:
            os.killpg(server.pid, signal.SIGKILL)
            server.wait()


def on_alarm(*_: object) -> None:
    raise TimeoutError(f'serena did not answer within {REPLY_DEADLINE_S} s')


def log_tail(log: IO[str]) -> str:
    log.seek(0)
    return ''.join(log.readlines()[-20:])


def run_serena(tool: str, arguments: dict[str, Any], log: IO[str]) -> dict[str, Any]:
    server = subprocess.Popen(
        ['serena', 'start-mcp-server', '--context', 'ide', '--project', run_git_toplevel()],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=log,
        text=True,
        env=dict(os.environ, SERENA_USAGE_REPORTING='false'),
        start_new_session=True,
    )
    signal.signal(signal.SIGALRM, on_alarm)
    signal.alarm(REPLY_DEADLINE_S)
    try:
        request(
            server,
            1,
            'initialize',
            {
                'protocolVersion': PROTOCOL,
                'capabilities': {},
                'clientInfo': {'name': 'kronael-serena-call', 'version': '1'},
            },
        )
        send(server, {'jsonrpc': '2.0', 'method': 'notifications/initialized'})
        return request(server, 2, 'tools/call', {'name': tool, 'arguments': arguments})
    finally:
        signal.alarm(0)
        stop(server)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    tool = sys.argv[1]
    try:
        arguments = json.loads(sys.argv[2])
    except json.JSONDecodeError as err:
        print(f'serena-call: arguments are not JSON: {err}', file=sys.stderr)
        return 2
    with tempfile.TemporaryFile('w+') as log:
        try:
            result = run_serena(tool, arguments, log)
        except (RuntimeError, OSError, subprocess.CalledProcessError) as err:
            print(f'serena-call: {err}\n{log_tail(log)}', file=sys.stderr)
            return 2
    print(''.join(part.get('text', '') for part in result['content']))
    return 1 if result.get('isError') else 0


if __name__ == '__main__':
    raise SystemExit(main())
