# Claude Config Management

## Problem
`~/.claude.json` is a single file — no native split/include support.

## Solution: drop-in directory + wrapper script

Split config into `~/.claude.d/*.json` fragments, merge before launch.

### Pipeline
```bash
cat ~/.claude.d/*.json | envsubst | jq -s 'reduce .[] as $x ({}; . * $x)' > ~/.claude.json
exec claude "$@"
```

- `envsubst` — substitutes `${VAR}` placeholders in fragments
- `jq -s reduce * $x` — deep-merges all fragments (later files win on conflict)
- `exec` — replaces wrapper process, no extra PID

### Wrapper at ~/.local/bin/claude
```bash
#!/bin/bash
cat ~/.claude.d/*.json | envsubst | jq -s 'reduce .[] as $x ({}; . * $x)' > ~/.claude.json
exec /usr/bin/claude "$@"
```

### Fragment example: ~/.claude.d/elastic.json
```json
{
  "mcpServers": {
    "elasticsearch": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "ES_URL", "-e", "ES_API_KEY",
               "docker.elastic.co/mcp/elasticsearch", "stdio"],
      "env": {
        "ES_URL": "${ES_URL}",
        "ES_API_KEY": "${ES_API_KEY}"
      }
    }
  }
}
```

### Notes
- Fragments are merged alphabetically — name them `00-base.json`, `10-elastic.json` etc. to control order
- `jq *` does recursive merge; right side wins on conflict
- No extra dependencies beyond `jq` and `envsubst` (GNU gettext, standard on Linux)
- Secrets stay in env, never hardcoded in fragments
