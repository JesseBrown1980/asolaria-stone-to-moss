# Seat 3 optical cross-talk correction — second-fixture frozen challenge

**October 15, 2026. Post-hoc exploratory discovery explicitly disclosed.** The first independently verified physical-host-executed photon-arrival SOFTWARE simulator used deterministic test nonce `ASOLARIA-SEAT3-PHOTON-FIXTURE-NONCE-20261015` and revealed 803/160/25 errors over 15,309 symbols for 1/3/7 exposures respectively. The failure profile had all 25 remaining seven-exposure errors as false positives and zero missed ON symbols. I inspected the complete original corpus while evaluating correction thresholds. Thus the original-corpus corrected values are **exploratory, not blind holdout validation**.

**New fixed test before writing validation code**: a *different pseudo-random photon-event nonce*, `ASOLARIA-SEAT3-PHOTON-UNSEEN-COUNTS-VALIDATION-B-20261015`. Keep original source-bank roots and emission/cross-talk/dark model exactly unchanged. Do not retune after seeing new counts.

### Frozen deconvolution and thresholds

The original symbolic optical band/port assignment is `[2,5,0,6,1,4,3]`. Map detector physical-port counts back to ordered symbolic bands `C_j`, and calculate integer-only three-point correction:

`D_j = 7*C_j - (C_{j-1} if j>0 else 0) - (C_{j+1} if j<6 else 0)`.

Why: neighboring leak probability 24/256 compared with own-port 168/256 implies leak/direct ratio exactly `1/7`; `7*C_j - C_{j-1}-C_{j+1}` is a first-order physical cross-talk inverse surrogate. It is **not** the true full inverse of the seven-band sensor transfer matrix, nor sensor-calibrated optical spectroscopy. Edge terms use only existing neighbor; do not wrap.

From exploratory ORIGINAL data choose fixed correction thresholds:

- 1 exposure: corrected `D_j >= 28` versus original raw `C_j >= 5`.
- 3 exposures: corrected `D_j >= 26*3` versus original raw `C_j >= 5*3`.
- 7 exposures: corrected `D_j >= 26*7` versus original raw `C_j >= 5*7`.

**No further threshold optimization** for new fixture. Entire original 15,309 symbols are regenerated from the SAME frozen original 81×7 source bank SHA; new nonce changes only pseudo photon emission, routing and background noise. Run exactly seven new exposures, 16 emission trials per source per exposure with thresholds ON=192/256 and OFF=16/256; source detection own=168/256, left leak=24/256, right leak=24/256, lost=40/256; background event probability 8/256; event counts conserved and no photon routed to more than one detector.

### Outcomes and falsifiers
- Record independent corrected vs raw bit errors, false-positive/false-negative counts, for 1/3/7 on **entire new nonce dataset**, not a reweighted subset. Report if correction worsens new error rate; do not hide failure.
- Verify all 15,309 rows with exact original bank leaf SHA and ordered sector/site/band. Test dark/no-light symbol count; a corrected detector must not allow missing channel output or unchecked source/port swaps, even if it makes a plausible bit.
- Include a deliberately WRONG port assignment and missing violet band, return explicit HOLD on source-map mismatch and 2,187 erasures; a mathematically successful correction cannot substitute for trusted channel ownership.
- Independent Python and Node22 standard-library code compare exact results, with third full HBP/JSON checker, original source-root hashes, four Ubuntu/Windows runs and one full byte-parity aggregator. If no hardware sensor evidence exists, experimental labels remain `SIMULATED_PHOTONS`, `NOT_RUN` for optical physical measurements and retention.
- This prospectively frozen **second PRG fixture** checks repeatability across pseudo-random streams; it does NOT prove generalization to actual photon shot-noise distributions, nonlinear biological opsins, real photonic memory, an arbitrary wavelength mixer, physical host identity, or externally signed source custody.

Stage1 original source hashes, 5/5 run and the initial exploratory failure logs stay unmodified. The selected correction was **not a blinded discovery**; disclose both original-corpus exploration and independently fixed second-nonce test.
