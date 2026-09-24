# Faster debug builds with cranelift

Read from `SKILL.md` § Development Workflow when debug builds or tests are
the bottleneck. `cargo check` does no codegen and gains nothing here.

- Faster debug **builds/tests** (not `check` — it does no codegen): cranelift
  backend, nightly-only. Two ways:
  - **Opt-in (project stays stable):** per-invocation
    `cargo +nightly build -Zcodegen-backend --config
    'profile.dev.codegen-backend="cranelift"'`. NEVER put that block in
    `.cargo/config.toml` — stable cargo then hard-errors on EVERY build.
  - **Default (project commits to nightly):** pin nightly in
    `rust-toolchain.toml` (`components = ["rustc-codegen-cranelift-preview",
    ...]` auto-installs it), then put `[unstable] codegen-backend = true` +
    `[profile.dev] codegen-backend = "cranelift"` in `.cargo/config.toml`.
    `cargo build` = cranelift, `cargo build --release` = LLVM (release profile
    untouched). Pin a DATED nightly so a `rustup update` can't drift clippy/
    cranelift and break CI.
- **C+asm crates don't link under cranelift** (`aws-lc-rs`/`aws-lc-sys` +
  their `rustls` dependents = undefined native symbols, any linker). Pin just
  those to LLVM, cranelift does the rest:
  `--config 'profile.dev.package.aws-lc-rs.codegen-backend="llvm"'` (repeat for
  `aws-lc-sys`, `rustls`). ~7× faster rebuilds on codegen-heavy crates.
