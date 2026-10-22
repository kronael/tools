# TODO

## Posting skill: send to Discord, Telegram and others from keys in standard home paths (2026-10-17)

**Owner request:** a skill and tool for posting messages, with the keys in files at standard
locations in the home directory, not pasted into sessions. Not started.

**Adopt candidate:** [Apprise](https://github.com/caronc/apprise) (v2.0.1, 2026-10-03). One CLI and
Python library for Discord, Telegram, Slack, email and about 100 more services. Each target is one
URL (`discord://webhook_id/webhook_token`, `tgram://bot_token/chat_id`). With no `--config`, the
CLI reads `~/.config/apprise/apprise.yaml` (and `~/.apprise*`, `~/.config/apprise.conf`). A tag
on each URL lets one command post to a named group (`apprise -g news -b "..."`).

**Open decisions:**

- Key storage: a `0600` Apprise file under `$XDG_CONFIG_HOME/apprise/`, or the Secret Service
  keyring (`secret-tool`). A plaintext file is readable by every process of the user and is
  picked up by dotfile sync and backups; the keyring is often missing on headless hosts.
- Approval gate: a post is outward-facing, so the skill shows the exact text and target and waits
  for approval, the same way `gh-comment` does.
- Discord keys exist today as `[discord] token` in the trading repo's `cfg/*/system_monitor.toml` and
  `server_*.toml` (bot tokens, not webhooks). Apprise's Discord plugin takes only a webhook
  (`discord://webhook_id/webhook_token`), so each target channel needs a webhook created once.

**Done when:** a `post` skill names the config path, the tag convention and the approval gate, and
`apprise --dry-run -g <tag>` resolves each configured target on this host.
