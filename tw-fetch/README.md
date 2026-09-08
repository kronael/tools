# tw-fetch

Two ways to read X (Twitter). They solve different problems; pick by whether
you already know which posts you want.

## mirror.py — read posts you can name, no account

`api.fxtwitter.com` serves a post as JSON without a key. A plain fetch of
`x.com` answers `402`, so the mirror is the only keyless read path.

```bash
uv run --script mirror.py 2089711566392578231
uv run --script mirror.py https://x.com/CryptoHayes/status/2089711566392578231
printf '%s\n' 2089711566392578231 | uv run --script mirror.py
```

One JSON object per post on stdout: id, author, created_at, text, likes,
retweets, replies, views, url. Failures go to stderr and do not stop the run.
Exit code is 1 only when every reference fails.

Limits worth knowing before you plan around it:

- The mirror has **no timeline and no search**. `/<user>/timeline` answers 404,
  and `/<user>/status/latest` answers 200 with "Sorry, that post doesn't
  exist". You must supply the ids.
- A protected account answers `401`. That is the account's setting, not an
  egress fault.
- The client sets `trust_env=True`, so `HTTPS_PROXY` is honoured. Behind a
  filtering proxy, allow `api.fxtwitter.com`.

## main.py — archive a timeline, needs an account

Selenium against the real site with cookie auth. This is the only path that
discovers posts rather than resolving named ones.

```bash
uv run main.py login USERNAME       # opens a browser, then stores cookies
uv run main.py timeline USERNAME [--no-headless]
uv run main.py user USERNAME target1 target2
```

It writes JSONL and needs `./cookies/<username>.json` from the login step. No
account, no timeline — there is no keyless substitute.
