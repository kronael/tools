# tw-fetch

Twitter/X archiver. Drives a real logged-in browser and streams tweets
into JSONL files, skipping ids already on disk on the next run.

## Auth

```sh
uv run main.py login <username>   # opens a visible browser; log in by hand
```

Cookies land in `./cookies/<username>.json` and are replayed into later
headless runs. There is no API token — X's public API no longer reaches
timelines, so this reads the rendered page through Selenium.

Re-run `login` whenever a run stops returning tweets; `auth_token`
expires and the failure looks like an empty timeline, not an error.

## Commands

Single-file PEP 723 script. Both forms below auto-resolve `selenium` + `click`.

```sh
uv run main.py timeline <username>              # home timeline, continuously
uv run main.py user <username> <target>...      # one or more profiles
uv run main.py login <username>                 # save cookies
```

Common flags:

| flag | default | meaning |
|---|---|---|
| `--headless/--no-headless` | headless | watch the browser work |
| `-d, --delay` | `30` | seconds between profiles in `user` mode |
| `--debug` | off | DEBUG logging (before the subcommand) |

## Output

```
./export/timeline_<username>.jl
./export/user_<target>.jl
```

One tweet object per line — `id`, `url`, `author`, `text`, `ctime`. Existing
ids are read back before each run, so a re-run appends only what is new.

## Requirements

Chrome or Chromium on PATH; Selenium drives it through webdriver. A
headless run still needs the browser installed.
