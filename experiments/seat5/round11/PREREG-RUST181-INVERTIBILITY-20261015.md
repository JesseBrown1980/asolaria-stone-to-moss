# Seat 5 Round 11 — Prospective Rust 1.81.0 row-matrix challenge (2026-10-15)

**Prerecorded before Rust executables, workflows and measured outputs.** Branch base is exact already-reviewed, non-squash Seat4 PR #120 merge `b8a141ea7fcc1a193713e785382eabd66350372f`.

## Claim and independent implementation

Test original Seat3 PR11 81-bit cyclic XOR transitions with laws `[[0,1],[0,2],[0,1,3],[0,4,7],[0,1,5,9]]`; original Git source blob `2b0ed7e52776cd8a9b48086d83ba31c8486629fb`. Seat4 Round10 independently confirmed 195 cases and sealed 93,567B trace SHA256 `08a1ebbf1e7d24d7882258e9f341767b19093c1a4368b5e21f175592461f32ef`. A **third integer-only Rust 1.81.0 GF(2) output-ROW matrix implementation**, unlike Seat4's Python cyclic polynomial multiply or Node22 output-column matrix, must replay all 195 reference rows without importing Seat4's engines. Precommit the golden 15 SHA-derived initial seeds; exact artifact input roots must be pinned and hash-checked.

## Adversarial gates

1. Forward 81-bit state continuity for 5 fixed linear laws, 3 source seeds, 5 semigroup horizon pairs, 5 short steps and 3 bit perturbations = **195 independently recalculated rows**. Include `10^13`, `10^13+1`, `2*10^13+1`. Equality must be actual 81-bit integer states, not state hashes only.
2. Independent GF(2) Gaussian-elimination rank of each transition law, report ranks/nullities and explicit nonzero kernel witness. In particular `T0(x)=x xor rotate1(x)` sends all-ones to zero; forward skip **does not imply inverse or backward recovery**.
3. Independent 17-step T0 + 23-step T1 direct-step check; stale `T0^40` must disagree; correctly composed two-phase jump must match. Enforce state results `1284fb06a20fdbc73537c` stale and `1949302f90e20a0478bf2` correct.
4. Check that changing an archived final state, seed, step number, law, witness or simulated-physical flag is rejected. Test a single false 81-bit state hash as *insufficient* without a verified transition, and keep SHA256 per-step recurrence distinct from GF(2) evolution.
5. Pin **Rust 1.81.0** compiler, no floating-point state math, **Clippy `-- -D warnings`**, deterministic release/debug execution, offline zero-external-dependency crate, and independently SHA-check produced raw witness bytes across runs.
6. Do not rewrite Seat4's append-only evidence, original bank, other seats' PRs or historical August optical operator reports. Hosted compute is physically executed on real CPUs but not an optical detector nor 10^13 seconds elapsed.

## Acceptance

Two Linux Rust1.81 debug/release CI jobs with unit tests, Clippy and independently created row-matrix witness; third hosted referee checks exact receipt parity and original Seat4 trace/SHA. Report complete hosted run/commit IDs and **HOLD merge** pending separate review. No Rust success may be claimed until the actual workflow passes. This Round11 is a separate forward+inverse-capability falsification, not a replay of Seat4 authorship.
