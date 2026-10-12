#!/usr/bin/env python3
"""Run one Serena tool on the git project around the working directory, then
stop Serena.

Usage: call.py <tool> '<json object of arguments>'
Prints the tool's text reply. Exits 1 when the tool reports an error and 2
when Serena cannot start or answer; Serena's own log tail goes to stderr.
"""

import json
import os
import subprocess
import sys
import tempfile
from typing import IO
from typing import Any

PROTOCOL = '2025-06-18'
STOP_GRACE_S = 30


def project_root() -> str:
    top = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True
    )
    return top.stdout.strip()


def send(server: subprocess.Popen[str], message: dict[str, Any]) -> None:
    assert server.stdin is not None
    server.stdin.write(json.dumps(message) + '\n')
    server.stdin.flush()


def request(
    server: subprocess.Popen[str], n: int, method: str, params: dict[str, Any]
) -> dict[str, Any]:
    assert server.stdout is not None
    send(server, {'jsonrpc': '2.0', 'id': n, 'method': method, 'params': params})
    for line in server.stdout:
        message = json.loads(line)
        if message.get('id') != n:
            continue
        if 'error' in message:
            raise RuntimeError(f'{method}: {message["error"]}')
        return message['result']
    raise RuntimeError(f'{method}: serena exited before it answered')


def stop(server: subprocess.Popen[str]) -> None:
    assert server.stdin is not None
    server.stdin.close()
    try:
        server.wait(timeout=STOP_GRACE_S)
    except subprocess.TimeoutExpired:
        server.terminate()
        server.wait(timeout=STOP_GRACE_S)


def log_tail(log: IO[str]) -> str:
    log.seek(0)
    return ''.join(log.readlines()[-20:])


def run_serena(tool: str, arguments: dict[str, Any], log: IO[str]) -> dict[str, Any]:
    server = subprocess.Popen(
        ['serena', 'start-mcp-server', '--context', 'ide', '--project', project_root()],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=log,
        text=True,
        env=dict(os.environ, SERENA_USAGE_REPORTING='false'),
    )
    try:
        client = {'name': 'kronael-serena-call', 'version': '1'}
        request(
            server,
            1,
            'initialize',
            {'protocolVersion': PROTOCOL, 'capabilities': {}, 'clientInfo': client},
        )
        send(server, {'jsonrpc': '2.0', 'method': 'notifications/initialized'})
        return request(server, 2, 'tools/call', {'name': tool, 'arguments': arguments})
    finally:
        stop(server)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    tool = sys.argv[1]
    arguments = json.loads(sys.argv[2])
    with tempfile.TemporaryFile('w+') as log:
        try:
            result = run_serena(tool, arguments, log)
        except RuntimeError as err:
            print(f'serena-call: {err}\n{log_tail(log)}', file=sys.stderr)
            return 2
    print(''.join(part.get('text', '') for part in result['content']))
    return 1 if result.get('isError') else 0


if __name__ == '__main__':
    raise SystemExit(main())
