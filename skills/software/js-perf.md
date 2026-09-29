# JS/TS performance — writing for V8

V8 never reads type annotations: TS is erased before the engine sees the code,
and TS is unsound anyway (`any`, `as`, structural typing), so declarations
cannot drive codegen. V8 specialises on runtime feedback only. What buys speed
is shape discipline — which TS encourages but cannot enforce.

## Rules

- ALWAYS create objects of one logical type with the same properties assigned
  in the same order, ideally via one constructor/factory. `{a, b}` and
  `{b, a}` get different hidden classes despite an identical TS type.
- NEVER add or delete properties after construction — deletes and pathological
  adds flip the object to dictionary mode, abandoning optimisation for it.
- ALWAYS keep hot call sites monomorphic (one shape). Each extra shape adds
  checks; past the polymorphic limit (4 — expert-secondary source, not on
  v8.dev) the site goes megamorphic: a hash-table probe on every access.
- NEVER make an array holey or mixed: no `delete a[i]`, no writing past the
  end, no mixing a string into a numeric array. Elements kinds move one way
  down a lattice — one hole or one non-number degrades the array permanently.
- ALWAYS use typed arrays (`Float64Array`) for bulk numbers — contiguous,
  unboxed, no per-element map check. On default (pointer-compressed) builds a
  double in a plain object FIELD is heap-boxed; only array elements and typed
  arrays store doubles unboxed.
- NEVER feed a hot function a rare divergent type (number 999x, string 1x) —
  each guard failure deopts to bytecode; repeated deopts make V8 give up on
  the function.
- ALWAYS warm up before measuring: V8 always starts in Ignition. Node's
  compile cache (`module.enableCompileCache()`, `NODE_COMPILE_CACHE`) stores
  bytecode, not optimised code — TurboFan warmup repeats every process start.
- ALWAYS batch across Wasm and N-API boundaries: Wasm passes only numbers, so
  share memory (`new Float64Array(memory.buffer, ptr, len)`) and cross once
  per batch, NEVER per element.
- ALWAYS measure JS→Wasm and Wasm→JS separately — costs are directional.
  JS→Wasm goes through a wrapper V8 can inline into optimised JS; Wasm→JS
  re-enters the JS ABI and costs much more, and Go's `syscall/js` shim adds
  more on top.

## Mechanism — how V8 gets fast

- Values: small integers (Smi) are tagged in the pointer; every other value
  is a heap object whose first word points at its map (hidden class).
- Maps form a transition tree keyed by property name and insertion order —
  order is part of shape identity.
- Feedback: per-function feedback vectors, one slot per feedback-consuming
  bytecode; inline caches per site move uninitialised → monomorphic →
  polymorphic → megamorphic (global stub-cache probe).
- Tiers: Ignition (bytecode + feedback) → Sparkplug (baseline, straight from
  bytecode, no IR, consumes existing feedback) → Maglev (SSA mid-tier built
  from feedback) → TurboFan (top tier, speculative with guards). Turboshaft
  is TurboFan's new CFG IR: as of Mar 2025 it carries the whole JS backend
  and the whole Wasm pipeline; sea-of-nodes survives only in builtins and the
  JS frontend (being replaced by Maglev). "Turbolev" (Maglev feeding
  Turboshaft) is community talk — unconfirmed on v8.dev.
- Deoptimisation rewinds an optimised frame to the equivalent bytecode
  offset, widens the feedback, and re-optimises later; repeated failure
  abandons optimisation for that function (exact counters unpublished).
- Elements kinds: PACKED_SMI → PACKED_DOUBLE → PACKED, each with a HOLEY
  twin; transitions are one-way, and holey access adds prototype-chain checks.

## Comparison — GraalVM/Truffle

The other design: speculation lives in the interpreter's own data structures,
not in a hand-written JS-specific pipeline.

- GraalJS is a Truffle AST interpreter that rewrites its own nodes into
  type-specialised versions — the feedback IS the tree. Assumption objects
  give zero-guard global speculation (invalidating one discards dependent
  code). Shapes mirror V8's maps, but transition edges encode the property's
  Java type, so doubles sit unboxed in a primitive storage area — the case
  V8 lost under pointer compression.
- Partial evaluation flattens interpreter + specialised AST into one Graal
  compilation unit. Payoff: a JS→Java call inlines into that unit — no
  wrapper, no marshaling; the cross-language boundary nearly disappears
  after warmup. V8 has no cross-language body inlining in either direction
  (as of mid-2025); the wrapper frame is its floor.
- Cost: much slower warmup — interpret to thresholds (default 400 first-tier
  / 10000 last-tier), then PE, then a peak-only compiler. The main mitigation
  (auxiliary engine caching) is Oracle-licensed, absent from Community
  Edition.
- GraalJS ≥ 25.0.3 ships native-image (AOT) standalones only; JVM standalones
  are discontinued (current release 25.2.4).

## Where type annotations DO drive codegen (none of these is V8)

- AssemblyScript: TS-like language compiled ahead-of-time to Wasm.
- Static Hermes: typed-JS AOT to native (Meta, research stage).
- Porffor: experimental AOT JS engine.

## References

- Maps, transition trees: https://v8.dev/docs/hidden-classes
- Property storage, dictionary mode: https://v8.dev/blog/fast-properties
- Elements kinds lattice: https://v8.dev/blog/elements-kinds
- Boxed double fields under compression: https://v8.dev/blog/pointer-compression
- Feedback vectors: https://v8.dev/blog/v8-lite
- IC states and the 4-shape limit (expert-secondary, ex-V8):
  https://mrale.ph/blog/2015/01/11/whats-up-with-monomorphism.html
- Tiers: https://v8.dev/blog/sparkplug, https://v8.dev/blog/maglev
- Turboshaft status: https://v8.dev/blog/leaving-the-sea-of-nodes
- Wasm call boundaries: https://v8.dev/blog/v8-release-90,
  https://v8.dev/blog/wasm-speculative-optimizations
- N-API call cost (~20 ns): https://github.com/nodejs/node/pull/21072
- Node compile cache: https://nodejs.org/api/module.html,
  https://v8.dev/blog/code-caching-for-devs
- Truffle: Würthinger et al., DLS 2012 (self-optimising AST); PLDI 2017
  https://dl.acm.org/doi/10.1145/3062341.3062381 (partial evaluation);
  Wöß et al., PPPJ 2014 (object storage model); Grimmer et al., DLS 2015
  https://dl.acm.org/doi/10.1145/2816707.2816714 (zero-marshaling interop)
- Truffle thresholds: https://www.graalvm.org/latest/graalvm-as-a-platform/language-implementation-framework/Options/
- Engine caching (Oracle-only): https://www.graalvm.org/latest/graalvm-as-a-platform/language-implementation-framework/AuxiliaryEngineCachingEnterprise/
- GraalJS standalones: https://github.com/oracle/graaljs/releases
- AOT alternatives: https://www.assemblyscript.org,
  https://github.com/facebook/hermes, https://porffor.dev
