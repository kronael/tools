---
name: finalize-crate
description: Finalize a Rust crate for external audience: competition research, honest benchmarks, rtrb-style README.
when_to_use: "finalize the X crate", "prepare X for release", "document X for external audience"
user-invocable: true
---

# Finalize Crate

Distilled from the rsx-cast / rsx-dxs open-source finalization sprint
(Feb–May 2026). That sprint: systematic competitor survey (70+ projects,
9 categories), oracle critique, benchmark harness, rtrb-style README.

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
- Minimum 20 entries. Store in `compare/niche.md`.

### 2b — Serious competitors (deep)
Identify the 3–6 most comparable projects (by use case, not just name).
For each, write a dedicated `compare/<name>.md` covering:
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
```
cargo bench  →  facts/<topic>.md  →  README "How fast" table
```
Numbers in README are only changed by updating `facts/` first.
Stale numbers are worse than no numbers.

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
4. **Honest performance section.** Numbers from `facts/`, labelled,
   caveated. Link the bench command.
5. **Cite alternatives generously.** 5-link subset in README body;
   full survey in `compare/niche.md`.
6. **Acknowledge lineage.** 2–4 sentence origin story.
7. **MSRV explicit.** "Minimum supported rustc: X.Y.Z. Bumps = minor
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
If the crate is intended as an extractable open-source library:
- **No `../` paths** in README, ARCHITECTURE, or CLAUDE.md.
- **No references to sibling crates by source path.**
- Specs: either copy locally into `crate/specs/` or inline the substance.
- Project-level docs: inline key numbers; link as full GitHub URLs.

## 5 — Verification pass

Before shipping:
- [ ] Every number in README traceable to `facts/` or a named bench
- [ ] No features in README that were removed from code
- [ ] Quick-start examples compile (`cargo test --doc`)
- [ ] "Guarantees" section matches current behavior (not aspirational)
- [ ] "When NOT to use" includes current known failure modes
- [ ] MSRV matches `rust-version` in Cargo.toml
- [ ] `cargo clippy -- -D warnings` passes
- [ ] All `../` links removed (grep -r "\.\.\/" docs/ README.md)

## Execution template

When executing this skill against a specific crate, run these steps:

```
1. Read: crate README, ARCHITECTURE, CLAUDE.md punch list, compare/*, facts/*
2. Step 1: write differentiator sentence, update README line 2
3. Step 2a+b: survey competitors; update compare/niche.md; write missing compare/*.md
4. Step 3: check facts/ freshness; run missing benches; update table
5. Step 4: apply rtrb principles; fix punch list items one by one
6. Step 5: verification pass
7. commit [crate] finalize: README, competition, benchmarks
```
