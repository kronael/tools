# diskclean

Free disk space on a development host. diskclean lists build output and caches
that a tool can build again, stalest first. It asks y/N before it removes
anything. It has two levels. A tool that is not installed is skipped.

```
diskclean [-1] [-2] [-k kind,...] [-o AGE] [-l] [dir...]
```

| Option | Meaning |
|--------|---------|
| `-1` | Level 1, the default. |
| `-2` | Level 2. It runs level 1 first. The last of `-1` and `-2` wins. |
| `-k kinds` | Only these kinds, as a comma list. `-k list` prints the kinds table. |
| `-o AGE` | Only candidates not used for `AGE`: `30d`, `8w`, `6m`, `1y`. A bare number is days. |
| `-l` | List only. diskclean never asks and never removes. |
| `-h`, `--help` | Print the usage text. |

`dir...` are the roots for level 1. With no `dir`, diskclean scans `~`. It
resolves each root with `realpath` and does not cross into other filesystems.
The global dirs of level 2 do not depend on `dir...`. Level 2 uses the roots
only to run level 1 and to find `rust-toolchain` pins. A level 2 kind in `-k`
does nothing without `-2`.

## Level 1 removes build output inside projects

Level 1 walks the roots. It lists a dir only when its kind has a proof that the
dir is rebuildable. See [the kinds table](#every-kind-has-a-proof). It prints one
row per dir with the age of its last use, its size and its path. It prints a
summary per kind, then the reasons it kept other dirs. One y/N removes all
listed rows.

A `target` dir loses everything except `target/deploy`, because that dir holds
program keypairs.

## Level 2 removes global toolchains, caches, boxes and images

Level 2 runs level 1, then lists the global dirs of kinds `rustup`,
`platform-tools`, `pipenv` and `browsers` in the same table, with one y/N.

Then it shows the tool prunes with one y/N for all of them:

- `pnpm store prune`, `bun pm cache rm`, `uv cache prune`, `pip cache purge`,
  `pre-commit gc` and `yay -Sc`.
- `go clean -cache` and `go clean -modcache`.
- `docker image prune -a -f`, which removes every image that no container
  uses, and `docker builder prune -f`.
- `qemubox prune` removes base sets no VM uses and stops running VMs that sit
  idle for over four hours. It removes no VM; `qemubox rm --stopped <hours>`
  does. `dockbox prune 0` removes idle and exited boxes.
- Anonymous docker volumes that no container uses. Only volumes with a
  64-character hex name count. Named volumes stay.

The prunes run only at level 2. diskclean lists the size of each cache before
it asks. The dockbox and qemubox images need a rebuild after this.

## Every kind has a proof

`diskclean -k list` prints the kinds. A dir becomes a candidate only when its
proof holds.

| Level | Kind | Dir | Proof |
|-------|------|-----|-------|
| 1 | `node_modules` | `node_modules` | `package.json` beside it |
| 1 | `target` | `target` | `Cargo.toml` beside it and `CACHEDIR.TAG` inside; `deploy` stays |
| 1 | `pnpm-store` | `.pnpm-store` | a `v<number>/files` dir inside |
| 1 | `next` | `.next` | `package.json` beside it and inside it |
| 1 | `venv` | `.venv`, `venv` | `pyvenv.cfg` inside |
| 1 | `pycache` | `__pycache__` | a `.pyc` file inside |
| 1 | `toolcache` | `.pytest_cache`, `.ruff_cache`, `.mypy_cache` | `CACHEDIR.TAG` with the standard signature on its first line |
| 1 | `gomod` | `pkg/mod` | `cache/download` inside and a `go.mod` in the project |
| 2 | `rustup` | numbered toolchains, such as `1.82.0-x86_64-unknown-linux-gnu`, in the rustup home | `bin/rustc` inside |
| 2 | `platform-tools` | Solana `v<number>.<number>` dirs in the cache home | `platform-tools` inside |
| 2 | `pipenv` | each dir in `~/.local/share/virtualenvs` | `pyvenv.cfg` and `.project` inside |
| 2 | `browsers` | `ms-playwright`, `puppeteer` in the cache home | a Playwright install marker, or a Chrome dir for puppeteer |
| 2 | `prunes` | the commands above | the vendor command decides |

A `pipenv` virtualenv whose project dir is gone shows "never" as its last use.

## What diskclean never touches

diskclean never searches these dirs, at any depth: `.git`, `.claude`, `.codex`,
`.agents`, `.diary`, `specs`, `plans` and `docs`. It never searches hidden dirs
directly under `~`, because tool installs such as `~/.bun` keep their own
`node_modules` there. A root inside any of them is an error.

A dir with a proof is still kept, with a reason in the `kept:` line, when it is:

- a symlink, a mount point, or a dir that holds `.git`,
- inside a project that is `~` itself,
- a `target` with no `CACHEDIR.TAG`,
- a rustup toolchain that is the default or active, that a `rust-toolchain` or
  `rust-toolchain.toml` file under the roots pins, or when `rustup` is not
  installed. Stable, nightly and linked toolchains do not match the numbered
  name, so they never appear,
- the newest Solana platform-tools, or one that a rustup toolchain links to,
- a dir that du or find cannot read,
- used within the age limit.

Before it removes a dir, diskclean checks the proof and these rules again. A dir
that changed since the listing is skipped with a message. At level 1 it also
refuses a dir outside the roots.

## Age stages the removal

The last use of a candidate is the newest of these times, never later than now:

- the project's git activity (`.git/index`, `HEAD`, `logs/HEAD`, `FETCH_HEAD`),
- the newest file change in the project outside `.git` and candidate dirs,
- the modification time of the dir and of what is inside it,
- the read time of those files, when the mount records read times. Level 1
  prints `atime recorded: no` when a root's mount uses `noatime`.

Level 1 looks two levels deep into the dir. Level 2 looks at the whole dir.

The default age limit is 30 days at level 1 and 0 at level 2, so `-2` lists
level 1 dirs of any age. Use `-o` to change it. The table lists the stalest rows
first.

## Examples

```sh
diskclean -l ~/projects              # list level 1 dirs, remove nothing
diskclean ~/projects ~/sandbox       # level 1 on two roots, 30 day limit
diskclean -o 8w -k node_modules,target ~/projects
diskclean -2 -l                      # list level 1 and level 2, remove nothing
diskclean -2 -k prunes               # only the tool prunes
diskclean -k list                    # the kinds table
```

Exit status: 0 on success, 1 when a removal fails or a run is interrupted, and
2 on bad usage. An interrupted run prints how many dirs it removed.

## Commands

```
make install   # → ~/.local/bin/diskclean
make test      # bash -n, then test.sh on temp dirs with every tool stubbed
```
