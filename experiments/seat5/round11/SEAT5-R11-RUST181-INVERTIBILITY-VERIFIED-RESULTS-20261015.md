# Seat5 Round11 — Independently verified Rust 1.81 output-row GF(2) and 81-bit kernel analysis

**2026-10-15 · computational verification PASS · physical optical instrumentation NOT RUN**

## Source and chronology
- Original five 81-bit Seat3 laws from merged PR#11 `experiments/seat3/two_horizon_matrix.py`, verified original blob `2b0ed7e52776cd8a9b48086d83ba31c8486629fb`.
- Full Seat4 Round10 work [PR#120](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/120) was first independently reviewed at head `dfbdcacf885123135f5fc088d7955d10d860f11c` and merged to main without squash, merge commit `b8a141ea7fcc1a193713e785382eabd66350372f`. Original historic evidence retained.
- Seat5 prospective registration committed FIRST `c1d346a72b1328d2efa38f94f1ec381c722c9c77`.
- Seat5 Rust source `experiments/seat5/round11/rust/src/main.rs` implements output-row GF(2) basis, independent of Seat4 Python cyclic polynomial and Node output-column matrices. No external crates, no floating point state, Rust **1.81.0** pinned. Clippy warnings forbidden.

## Actual GitHub CI result
[GitHub Actions run #38798453654](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38798453654), exact producing branch head `48cf421db833f6e54bf702630fcb9942a1b1fc96` (pre-results-doc), **3/3 SUCCESS**:
- Linux Rust1.81 **debug**: Clippy `-- -D warnings`, **5/5** unit tests, independent 195-case replay PASSED.
- Linux Rust1.81 **release**: same checks **5/5** and 195-case replay PASSED.
- Separate downloaded-artifact peer referee: exact two-job output bytes and fixed rank/trace assertions PASSED.

All 195 original case states equal the full original Seat4 93,567-byte `r10-81bit-cases.jsonl` fixture, SHA256 `08a1ebbf1e7d24d7882258e9f341767b19093c1a4368b5e21f175592461f32ef`. The 195 rows cover 5 laws × 3 pinned seeds × 5 semigroup horizons / 5 short direct transitions / 3 bit-perturbation checks.

## Independently downloaded raw artifact receipt
Downloaded both original CI ZIPs again via GitHub API and verified their raw bytes and contents:
- Debug artifact ID `12002747951`, release ID `12002094642`. Both original ZIP archives have exactly SHA256 `9ebba0da8c294530398fbf108b2ec6892655b877e2d5b6e37c1e2c2a076644c6`.
- `r11-cases.tsv` 13,395 bytes SHA256 `b955a8774adb0ad72cf25fbc17a76c3adf05683283e18955d05d4ae6f60d5a59`.
- `r11-receipt.json` 376 bytes SHA256 `90b804c6aaaa3114c350111ef72b7fc16ee0c6e72eec35e5e99c2e180b0298bd`.
- All raw output bytes identical between Rust debug and Rust release. These are digital receipts for **genuine powered hosted computation**, not calibrated electrical/optical measurements.

## NEW independent matrix rank and information-loss result

| Original 81-bit law taps | GF2 rank | Nullity | Invertibility |
| --- | ---: | ---: | --- |
| `[0,1]` | 80 | 1 | NONINVERTIBLE |
| `[0,2]` | 80 | 1 | NONINVERTIBLE |
| `[0,1,3]` | 81 | 0 | INVERTIBLE |
| `[0,4,7]` | 81 | 0 | INVERTIBLE |
| `[0,1,5,9]` | 80 | 1 | NONINVERTIBLE |

For each even-tap-count law, the **nonzero 81-bit all-ones vector is in the kernel** and maps to exactly zero. Thus original states 0 and all-ones produce identical next state: no unique inverse exists. This **does not** negate forward `T^n(s)` state evolution or skip efficiency.

## Independent hostile checks

- A frozen one-law `T0^40` incorrectly applied across a 17×T0 then 23×T1 schedule returns stale `1284fb06a20fdbc73537c`; correct direct reference and explicit scheduled composition return `1949302f90e20a0478bf2` EXACT.
- Nonlinear AND feedback and arithmetic carry both break GF(2) superposition and must not be silently replaced with an unchanged linear fast-forward map.
- Five Rust unit tests cover rank/kernel, identity/direct stepping, `10^13` continuation/composition, changing-law challenge and metadata/physical-sensor forgery rejection.
- State hash alone is not a recurrence proof. Iterating SHA256 must not be described as a proven GF(2) fast-forward; the original Seat4 128 sequential hash-chain test remains in merged main and is not modified here.
- **No physically measured photon, optical retention or 10^13 elapsed real-world time.** Operator-reported August optical-history experiments preserved separately.

**Verdict:** PASS mathematical and reproducible software evidence; new Seat5 PR #121 remains **DRAFT, NOT MERGED** pending independent cross-seat review. No old source, historical stones, merges or other seats modified.

**Important architecture note:** original laws use GF(2) XOR over 81 bits. That binary state algebra is not interchangeable with balanced-ternary `−1,0,+1` addressing without an explicit proven mapping. The Rust workload is fully integer-only; no unsupported ternary reinterpretation is claimed.
