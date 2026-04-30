# Cookbook

Daily recipes for `rig + dockbox + kronael`. Detached HEAD by
default — drop the clutter, make git do what you want.

## Why detached HEAD

Local branches are the wrong default. They drift, accumulate, need
tracking config, and pile up as stale refs. Detached HEAD is the
honest state: you have a commit, the remote has a branch, push when
ready. Reflog keeps everything for 90 days — no work is ever lost.

Mental model: **you commit to a SHA, not a branch**. The branch is
just a label that lives upstream.

## Start work on a feature

```bash
rco feature           # fetch + checkout origin/feature, detached
# … edit, commit …
rip feature           # push HEAD to origin/feature
```

`rco` (rig checkout) takes a fuzzy pattern; `?` forces fzf.

```bash
rco apm               # best match for "apm"
rco ?                 # interactive
rco -z apm            # offline (no fetch)
```

## Push without thinking about which branch

In detached HEAD, `rip` walks first-parent ancestry to find the
branch this commit belongs to. Stops at merge commits.

```bash
rip                   # auto-detect branch from ancestry
rip my-branch         # explicit target
rip -n                # dry-run
rip my-branch -f      # force-push (flags forwarded)
```

When detection is ambiguous (merge commit), `rip` falls back to fzf.

## Rebase before push (clean history)

```bash
rco feature           # checkout feature
# … work, commit …
rir main              # interactive rebase on origin/main
rip feature           # push the rebased history
```

`rir` always fetches main first unless `-z`. The rebase is `-i` so
you can squash, reorder, drop fixups.

## Merge upstream into your feature

```bash
rco feature           # on the feature
rim main              # fetch + merge origin/main
rip feature           # push merged result
```

No local main needed. You never created `main` as a local branch in
the first place.

## Recover work after "I lost my commit"

You didn't lose it. Detached HEAD commits stay in the reflog for 90
days.

```bash
git reflog            # find the SHA
git checkout <sha>    # back on it
rip my-branch         # push it
```

Reflog beats branch hygiene every time.

## Multi-commit feature

```bash
rco feature                # start
# … commit A …
# … commit B …
# … commit C …
rir main                   # squash A+B in interactive editor
rip feature -f             # force-push the cleaner history
```

Force-push to your own feature branch is fine. Force-push to main is
a wisdom violation — `rip` doesn't stop you, but don't.

## Switch contexts mid-flight

You're on `feature-a` with uncommitted work. Boss asks for a fix on
`hotfix`.

```bash
git stash                  # park current changes
rco hotfix                 # detached on hotfix
# … fix, commit …
rip hotfix                 # ship the fix
rco feature-a              # back to your feature
git stash pop              # resume
```

No branch creation, no tracking, no merge mess.

## Ship from spec end-to-end

Combine `rig + dockbox + /ship`:

```bash
rco feature                # checkout starting point
dockbox .                  # enter sandbox (current dir mounted)
# inside dockbox:
/ship                      # plan → build → judge from specs/
exit
rip feature                # push from host
```

`dockbox` mounts `~/.claude` rw, so the boxed agent can update
skills/memory just like a host session. Use it when you want
isolation from `node_modules`, system Python, or random caches —
not security isolation.

## Polish before PR

```bash
/refine                    # @improve + @readme + commit [refined]
/pr-draft                  # draft PR description
rip feature                # push
```

`/refine` validates build/test, delegates code improvement to
`@improve` and docs to `@readme`, then commits. Never does
improvement work itself — pure orchestration.

## End of session

The Stop hook nudges you when there are uncommitted changes or no
diary entry for today.

```bash
/commit                    # cohesive [section] commit
/diary                     # append `## HH:MM` to .diary/YYYYMMDD.md
```

Commit and diary are local-only — no automatic push. `rip` is
explicit, always.

## Bash shortcuts

`rig install` creates the symlinks: `rco`, `rip`, `rir`, `rim`. Add
the install dir to PATH. That's the whole setup.

```bash
rco -h                     # per-command help
```

## See also

- [rig/README.md](rig/README.md) — full flag reference
- [dockbox/README.md](dockbox/README.md) — sandbox config and mounts
- [skills/README.md](skills/README.md) — skill rationale
