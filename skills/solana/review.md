# Review checklist

The questions that actually caught something. Ask each one against the diff, and
answer it from the code — a plausible answer from the design docs is how several
of these survived earlier passes.

## Authority

- Does the program take **every** authority that can change what a counterparty
  quoted, or only the one that transfers custody?
- Does each step of a multi-authority restore still hold the authority the next
  step needs? Walk the order, not the set.
- Is the handoff in the same instruction as the bookkeeping, so no asset can sit
  under program authority without an entry?
- Which instructions require a signer, and is any "no outsider can do X" claim
  actually enforced by a signer rather than assumed?

## Accounts

- For every account in every `Accounts` struct: what pins it — seeds, `address`,
  `has_one`, `owner`? An unpinned account is one the caller substitutes.
- Can two accounts in one struct be the same account? What breaks if they are?
- Does anyone choose *which* config, authority, or parent account their own
  instruction honours? If so, everything that config controls is opt-in.
- Does every account that is written or credited carry `mut`, including a
  `close =` recipient?
- Is any wrapper-level check being argued away as conditional ("harmless when the
  fee is zero")? Wrappers validate before the handler runs.

## State and bookkeeping

- Is any index into a container stored or accepted from a caller, when removal
  uses `swap_remove`? Entries move; only key lookups survive.
- Enumerate every path that adds or removes an entry, and check the open count
  moves on each — including the partial-vs-full branch and the not-found branch.
- Can a not-found branch be reached with the *wrong* container rather than a
  genuinely absent entry? That branch usually grants something.
- After a removal, is anything still holding the old length or the old slot?

## Lamports and rent

- Any logic keyed on an exact amount (`balance == 0`, `amount == balance`)?
  Anyone can transfer lamports into any account, so a donation must not deny an
  operation. Here one donated lamport denies every full fill for the epoch: the
  quoted split strands a lamport below the rent reserve, and re-quoting the
  larger balance exceeds the delegated stake.
- Does any transfer leave an account below its rent-exempt minimum? The runtime
  rejects the whole transaction, so this brick lands on whoever pays, not on
  whoever misconfigured it.
- Is every configured recipient viable — right owner program, already
  rent-exempt — and is that checked where it is set?
- Is every account the program creates closable, and can the party who paid its
  rent reach the close path? If closing B needs A to authorize it, they must
  close together.

## Arithmetic

- Which way does each division round, and who gains the remainder? Can a caller
  fragment one action into `N` to collect it?
- Does a saturating clamp produce a value that every downstream computation can
  still represent?
- Is a fee carved out of a quote that a counterparty set a minimum on?
- Can the caller bound its total cost, or is a component read from state that
  someone else can raise under a pending transaction?

## Liveness and blast radius

- For each mutable setting: whose operations stop when it changes, and is there a
  path out that reads none of it?
- Who can brick whom? Separate "harms only themselves" from "harms a
  counterparty" from "halts everyone" — and check that deposits into a
  now-untradeable venue still fail rather than accumulating.
- Which instructions carry a time guard? Does every recovery path avoid it?
- Can the program record an order or position that can never execute in any
  epoch?
- Is any recovery path one-shot where the underlying program can refuse
  temporarily (epoch rewards distribution)?

## Compute

- Does the change add a CPI or grow a batch? Then the native suite proves
  nothing — re-run against the `.so`.
- Recount the trace: `top_level + cpis_per_item * n <= 64`.
- Does the transaction still earn the budget it needs from its own length?
