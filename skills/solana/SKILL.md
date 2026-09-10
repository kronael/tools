---
name: solana
description: On-chain Solana programs — Anchor instructions, PDAs, CPIs, account layout, compute budget, contract audit. NOT for general Rust idiom (use rs), NOT for client or SDK TypeScript (use ts).
when_to_use: writing or reviewing a Solana program, Anchor instruction, #[program], #[derive(Accounts)], declare_id, Account/UncheckedAccount/SystemAccount/Sysvar wrapper, PDA seeds, find_program_address, invoke_signed, signer seeds, CPI, remaining_accounts, on-chain account layout, rent-exempt minimum, close account, compute budget, set_compute_unit_limit, MaxInstructionTraceLengthExceeded, exceeded CUs meter, instruction trace, address lookup table, solana-program-test, BPF_OUT_DIR, litesvm, anchor build, avm, anchor-lang version conflict, two majors of solana-pubkey, smart contract audit, lamport arithmetic, stake account, treasury and fee design
---

# Solana on-chain programs

Requires the `rs` skill (Rust idiom) and `software/code.md`. Only what is
specific to on-chain code is here. On-chain there is no `eyre` and no `tracing`:
errors are one `#[error_code]` enum returned through Anchor's `Result` and
checked with `require!` / `require_eq!` / `require_keys_eq!` / `err!`.

Read the sibling file that matches the work:

| If you need | Read |
|---|---|
| repo and crate layout, one-file-per-instruction, a state crate, naming, Cargo profiles, config cruft | `layout.md` |
| picking or bumping crate, framework, CLI, or JS versions; test-harness choice; advisory triage | `deps.md` |
| compute, batching, PDAs, account layout, money math, authority and custody design | `onchain.md` |
| auditing a program or reviewing an instruction diff | `review.md` |

## Layout

- ALWAYS `lib.rs` = `declare_id!` plus the `#[program]` module, every handler a
  one-line delegation to `instructions::<name>::handler`. ALWAYS one file per
  instruction, its `#[derive(Accounts)]` struct beside its handler.
- ALWAYS put account types, their impls, the constants, and the `#[error_code]`
  enum in a separate `state` crate, so off-chain clients depend on the layouts
  without pulling in the program. `#[account]` derives the discriminator from the
  bare struct name, so moving a type across crates changes nothing on-chain.
- NEVER `support.rs`, `utils.rs`, `helpers.rs` — ALWAYS split by subject
  (`stake.rs`, `price.rs`). A module named for its role accepts anything.
- ALWAYS keep the package name, `[lib] name`, `#[program]` module, `Anchor.toml`
  `[programs.*]` key, and the built `.so` in sync. The artifact filename comes
  from the lib name, so a partial rename still builds and deploys under the old
  name.
- ALWAYS declare only config that is not already the default, and apply the cruft
  test — does removing this line break a fresh clone, a fresh CI run, or a
  documented workflow? `layout.md` carries the verified profile table.

## Versions

- ALWAYS the newest — framework, toolchain, CLI, every crate — that **unifies
  with the framework's own dependency graph**, NEVER the newest published. Two
  majors of one crate link happily, and then `Pubkey` is two incompatible types.
- ALWAYS pin exact (`=1.1.2`) in a program's `Cargo.toml`, NEVER caret.
- ALWAYS read the framework's own `deps` out of the sparse index before bumping
  anything it depends on — `deps.md` has the recipe and the current numbers.

## Accounts

- ALWAYS assume an `Accounts` wrapper validates BEFORE the handler's first line:
  a constraint is a precondition on every path, never only on the paths that
  read that field. `SystemAccount::try_from` (anchor-lang 1.1.2) rejects a
  non-System owner during deserialization, so "we never touch it when the fee is
  zero" is not a mitigation.
- ALWAYS pin every account by seeds, `address`, `has_one`, or `owner`. An
  unconstrained account is an account the caller chose.
- ALWAYS ask which party picked each state account. Whoever picks the config
  controls the fee that config charges.
- ALWAYS `mut` on anything written or credited, including a `close =` recipient.

## PDAs

- PDA signing authority comes from seeds plus program id, NEVER from an
  initialized account — a program can sign as a PDA that does not exist yet or
  was closed. Build recovery instructions on that, instead of making the caller
  re-create state just to sign with it.
- ALWAYS put the caller's key in the seeds when a PDA's authority is
  caller-scoped; it makes misaiming structurally impossible rather than checked.

## Arithmetic

- ALWAYS one named unit (`PRICE_UNIT`), a `u128` intermediate, one narrowing
  `try_from`, and `div_ceil` so rounding favours the protocol. Flooring lets a
  caller fragment one action into `N` and underpay by up to `N-1`.
- Saturating arithmetic turns a bad input into a dead position instead of an
  error — ALWAYS verify the clamped value is still representable downstream, and
  reject the input at the instruction that sets it rather than at use.

## Compute and testing

- Native `solana-program-test` runs an unmetered processor and is structurally
  blind to compute-budget failures. ALWAYS re-run with `BPF_OUT_DIR` pointed at
  the built `.so` after any change that adds a CPI or grows a batch.
- The default budget is `min(instructions * 200_000, 1_400_000)`: a long
  transaction earns budget from its own length while a short one starves. Batch
  size and budget are coupled — NEVER size a batch without metering it.

## Custody

- ALWAYS give a custody design one recovery path that reads none of the mutable
  config, so no operator switch can trap another party's assets.
- ALWAYS guard the epoch (or any clock) on the counterparty path only. The same
  guard on the owner's own path traps their recovery.
- ALWAYS let a caller bound what it pays. A cost read from mutable state at
  execution time can be raised under a pending transaction.
- NEVER add a permissionless crank over assets that have a strict owner — it is
  new attack surface for liveness the owner already has.
