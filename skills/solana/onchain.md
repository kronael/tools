# On-chain engineering

Each rule below is one class of bug that a real program shipped, or nearly
shipped. Examples are cited only where the number or the mechanism is the point.

## Compute, trace, and size

Three separate bounds cut a batched instruction, and they bind in this order.

**Instruction trace** — a transaction's trace is capped at 64 entries and every
CPI counts:

```text
top_level_instructions + cpis_per_item * n <= 64
```

Overrunning it reports `MaxInstructionTraceLengthExceeded`. A compute shortfall
reports "exceeded CUs meter" instead. Read which one you got before optimizing;
they have opposite fixes.

**Compute budget** — the default is `min(instructions * 200_000, 1_400_000)`, not
a flat 200,000. A long transaction earns budget from its own length; a short one
starves. Both directions bite:

- A lone instruction gets 200,000 units. Five active stake listings, three CPIs
  each, exhaust that once the CPIs are metered — about 34,000 CU per listing.
- A transaction with 22 top-level instructions already has the full 1.4M, so
  `set_compute_unit_limit` is unnecessary — and dropping it frees the trace slot
  it would have occupied.

That is why moving work to the client can *increase* what fits: a top-level
`Deactivate` costs ~40 transaction bytes, removes one CPI from the handler, and
grants 200,000 CU. 21 deactivations + 1 deposit + 42 CPIs is exactly 64 frames;
letting the handler deactivate makes it 3 CPIs per item and caps out at 20.

**Transaction size** — 1232 bytes for a legacy message. It binds after the trace:
once the trace fits, size is what forces a v0 message with an address lookup
table. An ALT shrinks account keys only, never the trace.

## What the native runtime hides

The natively linked `solana-program-test` processor is not compute-metered, so a
transaction that would exhaust its on-chain budget passes there. Any change that
adds a CPI or grows a batch must be re-run against the real `.so` (`BPF_OUT_DIR`)
before you believe it. Compute is not the only property the harness cannot see:
a "no outsider can close this" property enforced by a missing signer fails at
`Transaction::sign` with `NotEnoughSigners`, before the program runs, so no bank
test can cover it — that one is structural, argue it instead of asserting it.

## PDAs and signer seeds

A PDA's signing authority is its seeds plus the program id. Nothing about it
requires an initialized account, so a program can `invoke_signed` as a PDA that
does not exist yet — that is exactly how a PDA pays for and creates itself — or
as one that has been closed.

Use that for recovery. A `reclaim`-shaped instruction takes the seed components
as arguments (`owner: Signer`, `epoch: u64`, `id: u32`), takes the PDA as an
empty `UncheckedAccount`, derives seeds and bump in the handler, and signs. It
works whether the PDA is live, closed, or never created, and it cannot be aimed
at another party's assets as long as the caller's key is one of the seeds. The
alternative — making the owner re-create the account and pay rent just to sign
with it — costs two extra transactions for the same effect.

## Anchor account wrappers

Wrapper validation happens in `try_accounts`, before the handler's first line.
Treat every constraint as a precondition of the whole instruction:

- `SystemAccount::try_from` (anchor-lang 1.1.2) returns
  `AccountNotSystemOwned` for a non-System owner during deserialization. A
  mitigation of the form "the handler never touches that account when the fee is
  zero" is therefore false — the instruction already failed.
- `UncheckedAccount` plus `#[account(address = …)]` is the way to pin a CPI
  target. `#[account(owner = …)]` is the way to accept foreign-program state the
  callee will validate itself.
- An account with none of seeds / `address` / `has_one` / `owner` is an account
  the caller substitutes freely.

## Account layout: one page beats one PDA per item

When the binding constraint is transaction bytes, inline entries in one account
beat one PDA per item: a per-item PDA costs 32 bytes of account key per item in
every batch, while a page pays one key for the whole batch. In this program that
was the difference between 4 listings per transaction and 21.

Flattening loses the seed-derived join, so the checks the seeds used to make
free must be written by hand — equal list lengths for positionally paired
arguments, owner-program check on each item, duplicate rejection, and a state
validity check.

**Exactly one page per parent is then a correctness requirement, not a
simplification.** A page is not derivable from the item it holds, so with an
indexed page family nothing stops a caller naming the wrong page: the lookup
misses, the handler takes its not-found branch (in this program, the
unlisted-recovery branch that hands authorities back), and both the entry and the
open count strand — leaving the parent permanently unclosable and the same item
listable twice. Proving "present on no page" would require loading every page, so
a multi-page variant has no safe not-found branch at all. If one page's capacity
is too small, the answer is not more pages.

Locate entries by scanning for their key and remove with `swap_remove`. NEVER
accept a caller-supplied index: removal moves the last entry into the hole, so an
index is not merely unsafe, it is wrong as soon as anything else leaves.

## Money math

Fix one unit and name it. Here `PRICE_UNIT = 1_000_000_000` — lamports paid per
SOL of stake, so par is exactly the unit and there are nine decimals on a market
trading near par.

Compute in `u128`, narrow once with `try_from`, and round in the protocol's
favour with `div_ceil`:

```rust
let quote = (stake_lamports as u128)
    .checked_mul(price as u128)
    .map(|value| value.div_ceil(PRICE_UNIT as u128))
    .and_then(|value| u64::try_from(value).ok());
```

The `u128` intermediate cannot overflow for any `u64` pair, so only the narrowing
can fail — one error path, and it is real. Flooring is the bug: it lets a caller
split one purchase into `N` fills and pay up to `N-1` lamports less than buying
the same amount at once. Round every derived amount the same way, including fees.

Charge a fee **on top of** the quote rather than carving it out, whenever the
counterparty set a minimum: carving pays them less than the limit they set and
quietly breaks the promise the limit was.

Saturating arithmetic is a deliberate choice with a condition attached. It turns a
bad price into an unfillable position instead of a failed instruction — fine, but
only if the clamped value is still representable everywhere downstream. Both
clamps failed that test here:

- Saturating to 0 produced a zero limit, which accepted a zero offer and handed
  the assets over for free. Giving stake away is a transfer, not a trade — reject
  a zero limit explicitly.
- Saturating to `u64::MAX` produced a limit that no quote can express: the
  `u128` product overflows `u64` for any amount over one SOL, so the position is
  unfillable above that size. The clamp itself created the dead state.

Reject an unrepresentable value at the instruction that sets it, where the party
responsible sees the error, rather than at the instruction that reads it.

## Authority handoff

Take **every** authority that can change what a counterparty just quoted. Taking
withdraw authority over a stake account but leaving the depositor as staker lets
them re-delegate, split, or merge it and change the balance a taker priced.
Holding both also removes an intermediate CPI later: the native `Split` requires
the staker specifically, because only `Authorize` lets a withdrawer stand in for
one.

Do the handoff and the bookkeeping in one instruction. Then an asset cannot end
up under program authority without an entry, and a failure rolls both back.

An unsigned CPI inherits the transaction's signers. So
`Authorize(Withdrawer -> pda)` issued unsigned under the owner's signature both
performs the transfer and *is* the authorization check, since only the current
withdrawer may hand withdraw authority over. Let the native program be the
authority on authority instead of re-deriving its rules.

Restore in the order that keeps you authorized at every step. Returning staker
first and withdrawer second is load-bearing: giving up withdrawer first, on an
asset the program holds only withdraw authority over, leaves it neither authority
and the second call fails.

## CPI mechanics worth knowing

The runtime resolves a CPI's callee from the transaction's account list, not from
the `AccountInfo` slice passed to `invoke`. Handing a System Program instruction
the Stake Program's account info therefore *works*. Fix it anyway — it reads as a
bug to every reviewer, and the next refactor will assume it was one.

`solana_stake_interface::instruction::split` returns three instructions —
allocate, assign, then `Split` — the first two owned by the System Program and
the third by the Stake Program. A helper that returns a vector of instructions
across two programs needs each `invoke` to carry the right program account.

## Time guards and recovery

Guard the epoch on the counterparty path only. An owner acting outside the
current epoch harms nobody, and a stale book is unfillable regardless — while an
unconditional guard traps their recovery, since cancel and close must work in any
epoch. The accepted cost is that the program will happily record an order that
can never execute; bound that by comparing against the *recorded* epoch instead
of the clock inside the owner's instruction, never by adding a clock guard to it.

Recovery paths must be retryable rather than one-shot: native stake authority
changes are unavailable while partitioned epoch rewards distribute, so a
cancellation simply fails during that window and must be re-sent.

Close paired accounts together. If closing account B requires account A to
authorize it, closing A alone strands B's rent until an identical A is recreated
— so `close_book` closes the page in the same instruction.

## Config, fees, and who controls whom

Whoever picks the config controls the fee. A book that takes a bare
`Account<'info, Config>` with no address or authority constraint, against config
seeds of `["config", operator]` for any signer, makes the fee opt-in: a depositor
creates their own config naming themselves operator at `fee_bps = 0`,
whitelists their counterparty, and pays nobody. A repointing instruction extends
that to the pause switch — the depositor walks a live book out of a paused config
and keeps trading, so `paused` halts only the books whose owners leave them
pointed there.

Decide which one the design wants and write it down either way. An enforceable
fee needs one canonical config PDA with a fixed seed and no per-operator
component, with the book pinned to it — which gives up the multi-operator
whitelist. A voluntary fee is a legitimate choice; calling it "the protocol fee"
or the pause "the finalize switch" without the caveat is not.

A caller must be able to bound what it pays. A fee read from mutable config at
execution time can be raised between a quote and its landing, and the fill still
succeeds because the fee is mandatory and unbounded from the caller's side. Take
a caller-supplied `max_total_lamports` and reject above it. The same argument
shape defends against donation-inflated payments, so build them together.

Validate a recipient at the instruction that *sets* it, not at the one that pays
it. A treasury below the rent-exempt minimum for an empty account cannot receive
a fee at all, because the runtime rejects any transaction that leaves an account
rent-paying; a treasury not owned by the System Program fails
`SystemAccount` deserialization. Either silently bricks every fill for every book
on that config while deposits keep succeeding. Require the account itself,
constrained and asserted rent-exempt, so the failure lands in the operator's own
transaction where it belongs.

## Ownership model

Give assets a strict owner and no permissionless crank over them. A
permissionless post-epoch cleanup instruction is redundant with the owner's own
cancel — which has no time gate, restores every authority, and already handles
the unlisted case — and it is new attack surface for a liveness problem the owner
already solves. The accepted cost is that an owner who loses their key strands
their own assets under program authority forever. No third party is harmed, and
that is the trade to state out loud, not to engineer around.
