# Repo layout and config

## Crate and file layout

```text
src/lib.rs                   declare_id! + the #[program] module, nothing else
src/instructions/<name>.rs   one instruction: its Accounts struct + handler
src/instructions/mod.rs
src/stake.rs                 native-program interaction
src/price.rs                 money math
state/src/<type>.rs          account types, impls, constants, #[error_code]
```

`lib.rs` is wiring. Every `#[program]` function is a one-line delegation:

```rust
pub fn fill(ctx: Context<Fill>, stake_lamports: u64, offered_price: u64) -> Result<()> {
    instructions::fill::handler(ctx, stake_lamports, offered_price)
}
```

One file per instruction, with that instruction's `#[derive(Accounts)]` struct
directly above its handler — the constraints are the first half of the
instruction, and splitting them into a shared `accounts.rs` makes a reader hold
two files to check one authorization. Doc comments explaining an instruction's
design live on the `#[program]` function, where a client reading the IDL sees
them.

Account types, their impls, the constants, and the `#[error_code]` enum go in a
separate crate (`state/`), so off-chain Rust clients depend on the layouts
without pulling in the program.

### Moving state to its own crate

Three mechanics, each verified in the anchor 1.1.2 macro sources:

- `#[account]` derives the discriminator as `sha256("account:<StructName>")[..8]`
  — the namespace plus the bare struct identifier, never a module or crate path
  (`anchor-attribute-account-1.1.2/src/lib.rs` → `gen_discriminator` →
  `anchor-syn`'s `sighash`). Moving a type between crates therefore changes no
  on-chain layout.
- `#[account]` also expands an `Owner` impl returning `crate::ID`. The state
  crate must name the program itself, and a test has to pin the two together — a
  divergence is a runtime owner-check failure on every account, not a compile
  error:

  ```rust
  pub const ID: Pubkey = pubkey!("J9Rve…6F25");   // in the state crate

  #[test]                                          // in the program crate
  fn state_crate_names_this_program() {
      assert_eq!(crate::ID, limit_program_state::ID);
  }
  ```

- The IDL-build impls are emitted under `#[cfg(feature = "idl-build")]` inside
  the derive macros, and Cargo features are per-crate, so the program's feature
  must forward into the state crate:

  ```toml
  idl-build = ["anchor-lang/idl-build", "limit-program-state/idl-build"]  # program
  idl-build = ["anchor-lang/idl-build"]                                   # state
  ```

  Without the forward the build still succeeds and the IDL silently loses those
  types.

### Where the test-module declarations go

`rs` puts unit tests in `src/<module>_test.rs`, declared with
`#[cfg(test)] mod <module>_test;`. In a multi-file program that declaration
cannot sit in the module it tests: `mod price_test;` inside `src/price.rs`
resolves to `src/price/price_test.rs` and fails with `E0583`. Declare them in
`lib.rs` (or in the directory's `mod.rs`, where `mod deposit_accounts_test;`
does resolve to a sibling file) and leave a one-line note saying why they are not
next to their subject.

### Module names

NEVER `support.rs`, `utils.rs`, `helpers.rs`, `common.rs`. Split by subject:
`stake.rs` for native-program interaction, `price.rs` for money math, its own
module for PDA lifecycle. A module named for its role rather than its subject is
a dumping ground — nothing can be wrong to add to it, so everything gets added,
and the file stops fitting in one mental context.

### Where invariants live

`rs`'s abstraction rules hold, with one on-chain corollary: a per-account
invariant belongs as a method on the account type in the state crate, not as a
free function taking that account as its first argument. Signer seeds, an
open-item counter, an entry lookup:

```rust
impl Book {
    pub fn signer_seeds(&self) -> BookSeeds { … }
    pub fn add_positions(&mut self, count: usize) -> Result<()> { … }
    pub fn remove_position(&mut self) -> Result<()> { … }
}
```

Signer seeds need a companion type that owns the little-endian byte arrays,
because the seed slices must outlive the `invoke_signed` that borrows them. A
method cannot return `[&[u8]; N]` pointing at bytes it built locally — return a
struct that owns the arrays and carries `as_seeds()`.

## Naming

Name the program crate for what it does, then keep five names in sync: the
package name, the `[lib] name`, the `#[program]` module, the `Anchor.toml`
`[programs.*]` key, and the built `.so`. Cargo derives the lib target from the
package name with dashes turned to underscores (`limit-program` →
`limit_program`), and the artifact filename is the lib name — so a rename that
misses one of the five still builds, and silently deploys under the old name.

## Cargo profiles: declare only what is not already the default

Verified at cargo 1.97.1 on a scratch crate. Check with a build rather than
trusting the scaffold you inherited: `cargo build --release -v` prints every
rustc invocation, so the flags cargo actually passes are readable, and a test
that overflows tells you whether the checks are on.

| Line | Verdict |
|---|---|
| `[profile.dev] overflow-checks = true` | default |
| `[profile.test]` repeating dev's settings | dead weight |
| `[profile.release] overflow-checks = true` | load-bearing |
| `[profile.release.build-override] incremental = false` | default |
| `[profile.release.build-override] opt-level = 3` | load-bearing |

Dev and test already abort on integer overflow, so declaring it there writes a
default, and `[profile.test]` inherits dev. Release does *not* check overflow, and
`anchor build` refuses to produce an SBF artifact without the explicit release
`overflow-checks = true` — that one line is the only reason the block exists.

`build-override` is the surprise. Its defaults are hardcoded and do NOT inherit
the base profile, so a release build passes proc macros and build scripts no
`-C opt-level` at all — 0 — while the local crate gets 3. Setting
`opt-level = 3` there is a genuine change, and worth it for an Anchor program:
`anchor-syn`'s expansion is the heavy part of the build. `incremental = false` is
redundant, because release already emits no `-C incremental`.

Two methods worth keeping. For the overflow defaults, a test asserting
`bump(255) == 0` panics under `cargo test` and passes under `cargo test
--release`; adding `[profile.dev] overflow-checks = false` also silences it under
`cargo test`, which is what proves `[profile.test]` inherits dev.

For "what flags does this profile really pass", read the exact
``Running `rustc --crate-name <the crate you mean>` `` line out of
`cargo build -v`. The flags differ per crate inside one build — that is the whole
point of `build-override` — so grepping the log for `opt-level` hands you a
neighbouring crate's line and the wrong answer.

## The cruft test

Does removing this line break a fresh clone, a fresh CI run, or a documented
workflow? If yes it stays. If no, it goes — and "it documents intent" is not a
yes, that is what a comment or the diary is for.

`rust-toolchain.toml`'s `components = ["clippy", "rustfmt"]` passes the test: it
is what makes `make lint` work on a fresh clone without a separate
`rustup component add`, so it is not dev-only noise. It also imposes nothing
downstream — a toolchain file applies only while this repo is the working
directory, and a crate depending on this one never reads it.
