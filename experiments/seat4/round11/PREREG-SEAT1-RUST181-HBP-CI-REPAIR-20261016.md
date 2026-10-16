# Seat 4 — Prospective PR124 exact-source Rust 1.81 / Clippy / ternary / no-JSON repair

Freeze 2026-10-16. Original Seat1 PR #124 source HEAD: `66906dcf55894f1642f1b11c30559c3855de5e8d`. Do not modify source or main retrospectively, do not merge without authorization.

## Diagnosis from actual hosted output

Original GitHub Actions run `38898745078` has 4 failed Rust jobs, all at "Execute all levels and exact 200-year horizons", after pinned Rust1.81, Clippy -D warnings and unit/integration tests passed. All four jobs report Cargo's multiple-binary ambiguity (`cargo run` without `--bin`): crate contains `src/main.rs` and `src/bin/observational_rv.rs`. This specific failure is NOT a proven GF3 arithmetic failure or rustc version mismatch. Tests of both binaries and other referee steps still require end-to-end confirmation.

## Change constraints

1. Original `rust-toolchain.toml` retains `1.81.0` and clippy; `Cargo.toml` retains `rust-version=1.81` and standard-library-only.
2. Fix CLI to `cargo run --bin asolaria-proxima-ternary` for both debug/release. Preserve `cargo clippy --offline --locked --all-targets -- -D warnings` and `cargo test --offline --locked`.
3. Explicitly require balanced ternary `-1,0,+1`, `field=GF3`, 7 levels, 200 epochs, and output-only HBP, CSV, TSV, FITS, text ledger, SHA; **no runtime JSON or JSONL files**. No JSON formatter or serializer added. Existing source-language input metadata not rewritten.
4. Four original hosted Ubuntu/Windows × debug/release executions plus fifth full artifact byte parity. Separately evaluate `observational_rv` via all-target Clippy and tests without silently running the wrong binary.
5. Be honest about unmeasured photons, electrical instruments, real astronomical vs synthetic observations, and historical operator-reported physical experiments. Do not claim after-the-fact five-job PASS until provider completion.

Publish Seat4 correction as a small stacked DRAFT PR targeting Seat1 PR124 branch `agent/seat1/proxima-rust181-20261015`. Do not force-push or overwrite the ongoing seat's work.
