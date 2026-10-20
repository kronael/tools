# Copyright 2026 kronael
"""An inspected outer container must isolate nested privileged payloads."""

import json
import sys

box = json.load(sys.stdin)[0]
config = box['HostConfig']
if config['Runtime'] != 'runsc-dockbox':
    sys.exit('wrong runtime')
if config['Privileged']:
    sys.exit('outer container is privileged')
if config['Devices']:
    sys.exit('outer container has host devices')
if config['PidMode'] == 'host':
    sys.exit('outer container shares host PIDs')
if config['NetworkMode'] == 'host':
    sys.exit('outer container shares host network')
for mount in box['Mounts']:
    if mount['Source'] in (
        '/var/run/docker.sock',
        '/run/docker.sock',
    ):
        sys.exit('outer container mounts the host Docker socket')
    if mount['Source'] == '/':
        sys.exit('outer container mounts the host root')
