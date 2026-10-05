---
name: finalize-crate
description: Finalize a library for an external audience in any language — extraction from a host repo, competitor survey, honest benchmarks, rtrb-style README, release verification. NOT for in-flight feature work (use ship) or doc-only sync (use readme).
when_to_use: "finalize the X crate, finalize the X package, finalize the X library, prepare X for release, extract X into a standalone library, publish to crates.io / npm / PyPI, document X for external audience"
user-invocable: true
---

# Finalize Library

Distilled from the rsx-cast / rsx-dxs open-source finalization sprint
(Feb–May 2026): systematic competitor survey (70+ projects, 9 categories),
oracle critique, benchmark harness, rtrb-style README.

The steps are language-agnostic. Where a command appears, read it through
this table.

| Step | Rust | TypeScript | Python | Go |
|---|---|---|---|---|
| registry survey | crates.io | `registry.npmjs.org/<pkg>` | PyPI | pkg.go.dev |
| lint gate | `cargo clippy -- -D warnings` | `eslint .` | `ruff check` | `go vet` |
| typecheck | (compiler) | `tsc --noEmit` | `pyright` | (compiler) |
| examples compile | `cargo test --doc` | typecheck `example/` with the source | `pytest --doctest-modules` | `go test ./...` |
| bench | Criterion | a script with a stated method | `pytest-benchmark` | `go test -bench` |
| min version | `rust-version` (MSRV) | `engines.node` | `requires-python` | `go` directive |

The minimum-version claim is the one people copy without checking. State it
only for versions you actually ran the suite on — download the runtime and
run it rather than asserting a floor from which APIs you happened to use.

## 0 — Extraction, when the library lives inside a bigger repo

Skip if it is already standalone. Otherwise, before anything else:

- **Cut the host's infrastructure out of the API.** Anything the parent
  injected — a metrics client, a logger implementation, a config service, a
  DI container — becomes either an interface the caller supplies or a plain
  return value the caller wires up. A library that drags the parent's stack
  in is not extractable; it is a copy.
- **Aim for zero runtime dependencies** and treat each one you keep as a
  claim you have to defend in the README.
- **Name it.** Check the registry for availability before writing docs
  (`curl -s -o /dev/null -w "%{http_code}" https://registry.npmjs.org/<name>`
  → 404 means free). Pick a name that says what it does or names the role it
  plays; a pun is fine if the pun is the role.
- **Port the host's tests, then add the ones the host did not need.** The
  host tested its own use; a library has to test its contract.
- **Settle ownership before the first commit.** Code extracted from an
  employer's private repo is theirs. Write the chain in `NOTICE`, and say
  plainly in your report that publishing needs their sign-off — do not
  quietly relicense it and do not push it anywhere.

## 1 — Define the differentiator first

Write one sentence that names the *non-obvious* thing that separates
this crate from every alternative. Not the category label — the
architectural bet that makes it different.

Example (rsx-cast): "The retransmit source IS the WAL, not a sidecar
archive — so the retransmit horizon equals retention for free."

Pin this sentence as the second line of README.md and the opening of
ARCHITECTURE.md. Everything else hangs off it.

## 2 — Competitor research

### 2a — Niche survey (broad)
- Search crates.io + GitHub for every crate in the same space.
- Categorize into ≤ 9 buckets (e.g. "reliable UDP", "log-structured
  transports", "multicast", "zero-copy queues").
- For each: one-line description, star count, last commit, license.
- Minimum 20 entries. Store in `test/research/niche.md` (`readme` → `topology.md`).

### 2b — Serious competitors (deep)
Identify the 3–6 most comparable projects (by use case, not just name).
For each, write a dedicated `test/research/<name>.md` covering:
- Architecture (how it solves the same problem)
- Protocol / wire format (if applicable)
- Performance claims (from their own docs or papers)
- Where it wins vs. our crate
- Where our crate wins (be specific)

### 2c — Lineage
Trace the design ancestry. Credit every project we learned from, even
if we didn't copy code. Goes in README.md "Acknowledgements / Lineage"
section. Example chain: LBM → Aeron → MoldUDP64 → rsx-cast.

## 3 — Benchmark honestly

### 3a — What to measure
Cover at minimum:
- **Micro-op**: the single hot operation (e.g. WAL append, send body)
- **End-to-end**: loopback RTT at realistic message rate
- **Contention**: N senders or N receiver threads

### 3b — Label everything
Every number needs three labels: operation, environment (CPU model,
OS, build profile), and measurement method (Criterion, manual timing,
loopback vs LAN). Example: "WAL append — 31 ns (Ryzen 9 5950X, Linux,
release, Criterion micro-bench)".

### 3c — Caveats that MUST appear
- "Loopback ≠ production" — write it explicitly.
- p50 ≠ p99 — if you only have p50, say so.
- If warm vs cold cache matters, report both.

### 3d — Source-of-truth chain
Every README number lives in the numbers ledger beside its bench command
(`readme` → `topology.md` § Numbers) and changes only by re-running it.

### 3e — Competitor comparison bench
Run at least one benchmark that directly compares our crate to a
serious competitor under identical conditions (same payload size, same
hardware, same operation). Even if the comparison is unfavorable,
publish it with the methodology so readers can reproduce.

## 4 — README (rtrb principles)

Source: https://github.com/mgeier/rtrb — the reference for Rust crate
documentation quality. Apply these principles:

1. **Line 2 = elevator pitch.** One sentence, technical, no marketing.
   Lead with the differentiator from step 1.
2. **No badges.** Clean header.
3. **No marketing language.** "Wait-free" (checkable) yes;
   "blazingly fast" (uncheckable) no.
4. **Honest performance section.** Numbers from the ledger, labelled,
   caveated. Link the bench command.
5. **Cite alternatives generously.** 5-link subset in README body;
   full survey in `test/research/niche.md`.
6. **Acknowledge lineage.** 2–4 sentence origin story.
7. **Minimum runtime version explicit**, and verified by running the suite
   on it. "Minimum supported rustc / node / python: X.Y.Z. Bumps = minor
   version bump."
8. **Breaking-changes link.** → CHANGELOG.md.
9. **Sections are short.** >3 paragraphs → move to ARCHITECTURE.md.
10. **No architecture diagram in README.** → ARCHITECTURE.md.
11. **Standard license block** (MIT/Apache dual recommended).

### Keeper sections (do NOT cut chasing rtrb minimalism)
If the crate implements a non-obvious protocol or contract:
- "Why this exists" — what gap it fills vs. alternatives
- "Wire format" — if bytes cross a process boundary, document the layout
- "Guarantees" — delivery promises, ordering, durability
- "When NOT to use" — failure modes that are non-obvious
- "Requirements and assumptions" — trust model, environment constraints

### Standalone rule
If the library is intended as an extractable open-source project:
- **No `../` paths** in README, ARCHITECTURE, or CLAUDE.md.
- **No references to sibling crates by source path.**
- Specs: either copy locally into `crate/specs/` or inline the substance.
- Project-level docs: inline key numbers; link as full GitHub URLs.

## 5 — Verification pass

Before shipping:
- [ ] Every number in README has its ledger section and command
- [ ] No features in README that were removed from code
- [ ] Quick-start examples compile — as code the build actually checks, not
      as prose in a fenced block nobody runs
- [ ] "Guarantees" section matches current behavior (not aspirational), and
      every guarantee names the test that fails without it
- [ ] "When NOT to use" includes current known failure modes, and every
      alternative it names is described accurately enough that its author
      would not object
- [ ] Minimum runtime version matches the manifest AND was run
- [ ] Lint and typecheck gates pass (see the table above)
- [ ] All `../` links removed (grep -r "\.\.\/" docs/ README.md)
- [ ] `NOTICE` states where the code came from, if it came from somewhere
- [ ] An adversarial audit ran against the code and a truth-vs-docs audit
      ran against the README, and each finding is fixed or recorded

## Execution template

When executing this skill against a specific crate, run these steps:

```
0. Step 0: if extracting, decouple from the host, name it, settle ownership
1. Read: README, ARCHITECTURE, CLAUDE.md punch list, test/research/*
2. Step 1: write differentiator sentence, update README line 2
3. Step 2a+b: survey competitors; update test/research/niche.md; write missing test/research/*.md
4. Step 3: re-run stale ledger commands; run missing benches; update table
5. Step 4: apply rtrb principles; fix punch list items one by one
6. Step 5: verification pass
7. commit finalize: README, competition, benchmarks
```
