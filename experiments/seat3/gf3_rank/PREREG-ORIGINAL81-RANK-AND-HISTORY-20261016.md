# Seat 3 C3 / October 16 — Prospective GF(3) 81-trit matrix rank and recoverable-memory challenge

**Preregistered before this branch contains executable tests or measured results.** Independent target: [Seat1 Proxima PR #124](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/124), exact source `5303c9b2ed0c0ce33da684706d57caef516ffd2b`; file `experiments/seat1/proxima-rust181/src/lib.rs`, routine `gf3_step`, dimension 81, two tap laws `[0,1,3]` and `[0,4,7]`. Start from independently pinned base `main` `490a0b42dcfd07404fc983051da7b33fc75a810b`.

## Mathematical questions fixed now

The native Rust maps an 81-site column state over GF(3) via `(T x)_i=x_i+x_{i-a}+x_{i-b} mod 3`, indices modulo 81. This is **balanced ternary arithmetic through the standard residue encoding 0/1/2 (2 represents −1)**. The linear map is a useful exact logical-time evolution for this declared law, not a general black-box polynomial time skip and not real optical/neural state measurement.

**Preregistered theorem to falsify:**

1. `T(x)=1+x^a+x^b` in GF(3)[x] modulo `x^81-1=(x-1)^81`. Its value at x=1 vanishes mod3 and derivative at x=1 is `a+b mod3` (a=1,b=3 -> 1; a=4,b=7 -> 2). Both are nonzero, so each polynomial has *exactly one factor* of `x-1`; therefore `rank(T^h)=81-min(h,81)` for h in `0,1,3,9,27,81,82`.
2. Exact ranks must be `[81,80,78,72,54,0,0]` and nullities `[0,1,3,9,27,81,81]` for **both** taps, computed independently via **direct 81×81 GF3 Gaussian elimination** and an unrelated polynomial-gcd/multiplicity method. A mismatch is `FAIL`, not an occasion to fit the model after output.
3. The Frobenius 81st power must be **all-zero transition**: `(1+x^a+x^b)^81=1+x^(81a)+x^(81b)=0` in the quotient. Directly test 81 independent single-trit basis vectors (not merely one synthetic input).
4. At h=1, all-one state and all-zero state collide; neither state nor a matching final SHA is sufficient to reconstruct the original. At h=27 at least `3^27` distinct initial states map to zero in the mathematical space; at h=81 all `3^81` do. These are algebraic preimage cardinalities, **not physically instantiated memory rows**.
5. A *separate* exact append-only event/individual-identity sideband is required if original state recovery is intended, as demonstrated in Seat1's distinct `memory.rs` witness. Our test does not assert that the original asolaria system lacks such a sideband.
6. Confirm matrix skip for fixed transition law via both direct n-step state iteration and independent exponentiated matrix/composed polynomial at h=1,3,9,27,81,82, with fixed source seeds: single-basis at positions 0,13,80, dense state `x_i=(i*7+2)%3`, alternating state `x_i=i%3`. For h=81 and 82 all output states zero. A *changed hash alone* must not be counted as a legitimate state evolution.
7. Show valid law switching uses product `T2^m T1^n` rather than stale `T1^(n+m)`, with frozen `n=17,m=23`; test direct 40-step reference, and report whether stale calculation is identical for every seed or a falsifier. Law-switch nuance is scientifically essential for autonomy.
8. Source SHA commit should be pinned separately from output SHA. Deliberately tampered HBP and mutated tap law `[0,1,4]` must be rejected against frozen expected assertions.
9. Output **HBP plain-text + sha256 sidecar only**, no JSON, JSONL or NDJSON. Two independently written standard-library Python 3 and Node22 methods. Four GitHub Actions jobs Ubuntu/Windows × Python3.11/3.13; fifth compares byte-exact HBP and digests, denies false physical optical source claims, and preserves all run logs. Rust1.81 native tests remain the already verified PR124 production baseline rather than rewritten by this PR.

## Interpretation and review

Classifications: `GF3_FIXED_LAW_MATRIX_JUMP=MATHEMATICAL_PASS` if exact, `ALL_HISTORY_RECONSTRUCTIBLE_FROM_SURFACE_STATE=FALSE` without a separate sideband. Exact logical time is not OS CPU or electrical-rail measurement. HRM, Fischer, trained GNN/MTP models, genuine photons, astrophysical gravitational motion, and operator-reported completed prior photon-memory physical observations remain separate evidence layers.

Do not overwrite old stones, auto-merge #124 or #132, alter Rust scientific sources, pretend multiple hosted jobs represent independently attested physical chassis, or infer quantum/FTL/planet discovery. Publish pass and failure details to Seat1 PR124 and Coordinator Issue117 after actual CI; retain draft until independent review.

## Source publication status before tests

Hugging Face connected identity `Jessedbrown`: existing Asolaria model repository `Jessedbrown/asolaria-wasm81-rainbow-audit` updated October14 and six August historical public datasets plus static 3I-ATLAS Space. No October Hub dataset file SHA roundtrip yet verified for `Jessedbrown/tests`; do not substitute GitHub Actions success for Hugging Face remote readback.
