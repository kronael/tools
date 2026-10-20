# diskclean

Free disk space on a development host in three levels. Each level lists what
it removes and asks y/N before it removes anything. A higher level runs the
lower levels first. A tool that is not installed is skipped.

```
diskclean [-1|-2|-3] [dir...]
```

- `-1` (default): empty `node_modules` and Rust `target` dirs under `dir...`.
  A dir counts only when its parent has `package.json` or `Cargo.toml`.
  `target/deploy` stays, because it holds program keypairs. Then prune the
  pnpm, bun, pre-commit and yay caches and dangling docker images.
- `-2`: uninstall numbered rustup toolchains such as `1.82.0-...`. Stable,
  nightly, linked toolchains and the default stay.
- `-3`: `qemubox prune 0` and `dockbox prune 0` (stopped VMs, exited boxes,
  and ones that have run for over four hours and sit idle), docker images that
  no container uses and anonymous docker volumes that no container uses. Named
  volumes stay. The dockbox and qemubox images need a rebuild after this.

With no `dir`, it scans `~`. It skips hidden dirs, because tool installs such
as `~/.bun` keep their own `node_modules` there, and does not cross into other
filesystems.

## Commands

```
make install   # → ~/.local/bin/diskclean
make test      # bash -n, then test.sh on temp dirs with every tool stubbed
```
