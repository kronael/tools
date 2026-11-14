# Handoff recall on a PR

When a PR passes to another person, ALWAYS share the session recall behind it as a secret gist
linked from one comment; the REST API attaches no file to a comment.

- ALWAYS `gh gist create <file> -d '<PR>: recall'`. NEVER commit it to the PR branch, where the
  squash merge lands it.
- ALWAYS strip passwords, logins, tokens, keys, emails, IPs and private hostnames, and show the
  user the exact gist and comment first: a secret gist is readable by anyone with its address.
- ALWAYS end the comment with who deletes the gist and when ("whoever merges #499 deletes this
  gist"): a gist never expires, so ALWAYS delete it explicitly with `gh gist delete <id>`.
