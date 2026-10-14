# ASOLARIA — Rainbow81 Stone Index | 2026-10-14

This is the stable public navigation point for the three-agent verification effort. Separate **observed checks**, **published sources**, **derived interpretations**, and **unverified hypotheses**.

## Verified program and receipts

| Deposit | Tested structure | Published evidence | CI verification |
| --- | --- | --- | --- |
| Stone 1 — hash-cascade baseline | 9 isolated mutations; 81 derived cells and 171 ring commitments each wave; five SHA-based register labels | [Baseline HBP](stone-hash-81-2026-10-14-baseline.hbp) · [HBI](stone-hash-81-2026-10-14-baseline.hbi) · [runnable Python](../../experiments/hash-cascade-81-2026-10-14.py) | [Successful CI 38578220972](https://github.com/JesseBrown1980/one-click/actions/runs/38578220972), Python 3.11 / 3.13 |
| Stone 2 — coordinate versus hash | 27 independent waves: nine source bodies × three coordinate scales; 81 identity hashes invariant under position-only scaling | [Spatial HBP](stone-81-spatial-hash-27-waves-2026-10-14.hbp) · [HBI](stone-81-spatial-hash-27-waves-2026-10-14.hbi) · [runnable Python](../../experiments/test_spatial_hash_27_waves_ci.py) | [Successful CI 38581376561](https://github.com/JesseBrown1980/one-click/actions/runs/38581376561), Python 3.11 / 3.13 |
| Stone 3 — independent verification | Separate CI receipt for Stone 2 | [CI HBP](stone-81-spatial-hash-27-waves-CI-2026-10-14.hbp) · [HBI](stone-81-spatial-hash-27-waves-CI-2026-10-14.hbi) | [Run 38581376561](https://github.com/JesseBrown1980/one-click/actions/runs/38581376561) |

The original stone files have SHA-256 sidecars in this directory. Do not overwrite old receipts; append a new stone for corrections and new measurements.

## What the measurements show

- **9 waves**: changing the shared source checksum and explicitly rebuilding derived commitments changed all 81 constructed cell hashes, all five labels per cell and 171 chained ring commitments. Changing a stored record without dependency recomputation did **not** make remote peer records change.
- **27 waves**: stable metadata identity across coordinate scalings 1×, 10⁶× and 10⁹×; a shared-root rebuild changed 81 derived records, while a no-shared-root control changed one.
- In a local nearest-neighbor ring, changed records numbered 1, 3, 5, 21, 79, 81 at logical rounds 0, 1, 2, 10, 39, 40. Full-fanout metadata changes all 81 **after** its synchronous update.
- The **same identity hash** was compatible with different assigned distances; the hash alone cannot recover physical distance in this fixture.
- All measurements are synthetic software tests; no real-GPU, light detector, brain coupling, gravity, faster-than-light transport or independently separated endpoints were measured.

See [evaluation](EVALUATION-2026-10-14.md) for precise limitations.

## Track the three agents

- [Three-seat collaboration protocol](../../tracking/THREE-SEAT-LEDGER.md)
- [Live activity snapshots](../../tracking/) (GitHub commit/branch/PR/workflow metadata; a shared GitHub author is **not** proof of a particular agent).
- Every agent should tag new measurements with a **unique seat ID**, input SHA, source commit, test command, output SHA-256, run classification, clock model, and independent CI run where available.

## Status of Hugging Face

The standalone repository `Jessedbrown/tests` was not found in the last verified Hub lookup; publishing this GitHub stone is **not** evidence that artifacts have been uploaded to Hugging Face. The existing `Jessedbrown/asolaria-wasm81-rainbow-audit` repo exists, but publication of the current stone receipts there is not established.

**Do not put access tokens or other credentials in public stones, code, logs, or issue comments.**
