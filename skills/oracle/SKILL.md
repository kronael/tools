---
name: oracle
description: Legacy alias — routes to coding-oracle (fable) for code critique or creative-oracle (codex) for creative critique. NOT for routine lookups or Agent delegation.
when_to_use: "oracle, second opinion, sanity check, ask oracle, disagreement after reasoning"
user-invocable: true
---

# Oracle

`oracle` split in two, by what's being critiqued:

- **Code** (review, bug-hunt, design/architecture critique) → load
  `coding-oracle` (routes to fable).
- **Creative** (naming, prose, narrative, novel ideation) → load
  `creative-oracle` (routes to codex).

Default to `coding-oracle` if the target is ambiguous but touches code at
all. Load the matched skill and follow it.
