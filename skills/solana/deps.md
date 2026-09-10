# Versions, toolchain, harness

## The unification rule

Take the newest version of everything — framework, Rust toolchain, Solana CLI,
every crate — but *newest* means the newest that unifies with the framework's own
dependency graph, not the newest published. Cargo links two majors of the same
crate without complaint, and then a `Pubkey` from one is not a `Pubkey` from the
other, so the errors land in generated Anchor code far from the bump that caused
them.

`anchor-lang` 1.1.2 (the newest release) caret-depends on:

```text
solana-pubkey            ^3.0.0     solana-stake-interface   ^2.0.2
solana-account-info      ^3.1.0     solana-system-interface  ^2.0.0
solana-cpi               ^3.0.0     borsh                    ^1.5.7
solana-instruction       ^3.0.0     bincode                  ^1
solana-sysvar            ^3.1.1
```

The newest published are `solana-pubkey` 4.3.0, `solana-program` 4.1.0, and
`bincode` 3.0.0. Taking any of those links two majors of one crate. So the rule
in practice: pin exact with `=`, and inside each major the framework unifies on,
take the newest patch.

```toml
[dependencies]
bincode = "=1.3.3"
anchor-lang = "=1.1.2"
solana-program = "=3.0.0"
solana-stake-interface = { version = "=2.0.2", features = ["bincode", "serde"] }
solana-system-interface = { version = "=2.0.0", features = ["bincode"] }
```

Exact pins also mean Dependabot cannot move the Cargo stack — that is deliberate,
because a bump has to be checked against the graph by hand. Cover GitHub Actions
with Dependabot and move Cargo yourself.

## Reading the framework's deps

Before bumping anything the framework also depends on, read its declared ranges
from the Cargo sparse index. crates.io's JSON API answers `403` to tooling; the
sparse index answers `200`:

```bash
curl -sS https://index.crates.io/an/ch/anchor-lang   # 200, JSON lines
curl -sS https://crates.io/api/v1/crates/anchor-lang # 403
```

Path layout is `{first two chars}/{next two chars}/{name}` for names of four or
more characters, and `1/{name}`, `2/{name}`, `3/{first char}/{name}` for shorter
ones. Each line is one version: `{"name":…,"vers":…,"deps":[{"name":…,"req":…,
"kind":…,"optional":…}],…}`.

The lines are **not** sorted by semver — the last line of `anchor-lang` is 1.0.3
while 1.1.2 exists. Sort them yourself before calling anything "newest".

## Toolchain

The Anchor CLI pins a Solana release, so `avm use 1.1.2` also switches the active
Agave release (3.1.10 for Anchor 1.1.2). Record both in `Anchor.toml`:

```toml
[toolchain]
anchor_version = "1.1.2"
solana_version = "3.1.12"
```

Install `avm` from the Anchor repository — the `avm` crate on crates.io is an
unrelated project:

```bash
cargo install --git https://github.com/solana-foundation/anchor avm --locked
```

`anchor build` refuses to run without `[profile.release] overflow-checks = true`.
A deployed program is compiled once and then runs forever, so also take
`lto = "fat"` and `codegen-units = 1`: build time is the cheapest thing to trade.

Anchor generates a throwaway keypair on first build, so `anchor build` stops on
the mismatch when the repo has no keypair for its `declare_id!`. The artifact
itself is fine — its program id comes from `declare_id!` — so build with
`--ignore-keys` and treat the missing keypair as a deployment blocker, not a
build one. The program id is compiled into the bytecode: changing it (an
`anchor keys sync`, a vanity grind) forces a rebuild.

## The JS side

"Newest" there means newest the plugin stack accepts, and the binding constraint
is usually the TypeScript peer range rather than ESLint itself. `typescript-eslint`
8.65.0 declares `typescript: '>=4.8.4 <6.1.0'`, so it refuses TypeScript 7.0 —
pin TypeScript to 6.x until the plugin widens. Check the peer ranges in the
lockfile, not the changelogs.

pnpm 11 replaced `onlyBuiltDependencies` with `allowBuilds`, a map of package name
to `true`/`false` rather than a list. The old key is not honoured and a list under
the new one is not either, so any dependency with a build script and no explicit
`true`/`false` fails the install with `ERR_PNPM_IGNORED_BUILDS` and exit 1. That
blocks every `pnpm run <script>`, not just `pnpm install`, because `pnpm run`
re-runs a dependency-status check first:

```yaml
allowBuilds:
  bufferutil: true
  unrs-resolver: true
```

## Test harness choice

- `solana-program-test` for program correctness: the bank gives real epoch
  warping, partitioned epoch rewards, transaction rollback, and lets a fixture
  fabricate arbitrary account states (an active `Lockup`, a wrong deactivation
  epoch) that RPC cannot produce.
- `BPF_OUT_DIR` pointed at `target/deploy` makes that same harness load the
  compiled `.so` through the SBF loader instead of the natively linked processor
  — SBF-level fidelity for zero new dependencies. Prove it is really active by
  pointing `BPF_OUT_DIR` at an empty directory and watching the suite fail.
- LiteSVM and Mollusk are faster, but they want the Agave 4.x interface crates
  while `anchor-lang` 1.1.2 pins 3.x; adopting one means moving the whole stack
  or adding a second package. Wait for Anchor.
- Surfpool replaces `solana-test-validator`, not the bank scenarios. It fits the
  `make smoke` layer — a client driving realistic mainnet state — and requires a
  deployed artifact.

## Advisory triage

Most of what `cargo audit` flags on a program reaches the graph only through the
test harness and never links into the deployed artifact, so gating CI on those
blocks work without reducing on-chain exposure. Keep `make audit` out of
`make test-all`.

A flagged crate that *does* link on-chain needs an argument about its input, not
about its maintenance status. `bincode` 1.3.3 (RUSTSEC-2025-0141, unmaintained)
is acceptable here only because the decoder reads accounts the runtime has
already proven Stake-Program-owned, so an attacker cannot choose the bytes it
parses.

Baseline the accepted advisories with `--ignore RUSTSEC-…` so the target passes
on the known state and fails only on something new. A scheduled check that is
permanently red is worse than no check, because a real finding produces no
distinguishable signal.
