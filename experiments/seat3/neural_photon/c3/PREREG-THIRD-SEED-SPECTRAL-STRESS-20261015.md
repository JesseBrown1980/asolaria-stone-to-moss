# C3 Seat 3 — Third-seed held-out rainbow-lightbank source-bound spectral stress test

**Freeze date: 2026-10-15. This protocol is committed BEFORE the C3 generator or any C3/D outputs.** Prior Stage A/B results ARE KNOWN (B: raw 806/150/26, corrected 695/38/1) and the decoder law was selected using the earlier Stage A data. Do **not** describe the C3 test as blinded discovery of the decoder; it is a locked, prospective independent synthetic-seed generalization test. Preserve previous PR #95 and its SHA receipts; do not merge automatically.

**Parent:** [Seat3 draft PR #95](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/95), this branch stacked on PR #95 exact starting HEAD `3c2d41a52d0b1c6a1d58ecf9b2d5327c81b493f3`. Response to [Seat5 S5-02 independent readout challenge](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/55) and [Seat3 factorial work order #101](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/101).

## Source anchors, model and two independent validation conditions

Reuse actual 81 original QR memories (SHA256 `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`), 567 seven-band actual bank entries (SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`), 567-row base HBI (SHA256 `6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee`). Download actual pinned PR80 GitHub Actions run `38745842295` artifact `ordered27-rainbow7-ubuntu-latest`; original producer commit `7b5faf1103a7b42b603b44b08a5a5bfa994d0f76`. Source bit `SHA256(ASCII("ASOLARIA-PHOTON-BIT-V1|") || 32-byte bank leaf digest || octet(sector))[0] & 1`; 27 sectors ×81 sites ×7 symbolic bands = 15,309 logical symbols, **not** 15,309 independent stored memories. Symbolic band-to-detector mapping is fixed `[2,5,0,6,1,4,3]`.

**Completely different pseudo-random photon-event seed for both tests:** `ASOLARIA-C3-HOLDOUT-THIRD-SEED-20261015-V1`. Reuse earlier SHA256 count-domain `ASOLARIA-PHOTON-COUNTS-V1|` and dark-domain `ASOLARIA-PHOTON-DARK-V1|` and positions `(sector,site,band,exposure)`; 16 emission events per original source/ exposure, independent 16 routing pseudobytes per source, seven cumulative exposures. The SHA seed is public and digital **NOT a truly independent physical capture nonce**.

A separate model-tagged SHA256 digest for each frame must include condition label `C` or `D` as a single ASCII byte before the coordinate bytes. This prevents coincidental identical pseudo-counts being presented as independent new exposures and keeps fixed coordinate geometry. Both conditions share source bits and fixed decoder with no retuning.

**Condition C — third held-out original apparatus model:** emission probability ON=192/256, OFF=16/256, own detector routing 168/256, neighbor-left 24/256, neighbor-right 24/256, loss 40/256, dark noise 8/256 per one of 16 background slots.

**Condition D — prospectively specified *shifted leakage and dark noise*:** ON and OFF emission probabilities SAME as C, own detector routing=120/256, left=40/256, right=40/256, loss=56/256; independent dark/background probability=16/256. This is a plausible synthetic worse detector model; **no claim these coefficients are measured physical device parameters**. Do NOT change this model after seeing results.

No negative photon detection, duplicated event arrival, or wraparound neighbor. If a leaky event selects a nonexistent neighbor at band 0 or band 6, it is **lost**.

## Fixed decoders and tests, no adaptive tuning

At 1/3/7 exposures, raw detector decision for band j is `C_j >= 5*n`. The frozen three-point deconvolution score is
`D_j = 7*C_j - C_(j-1) - C_(j+1)` with nonexistent neighbors as zero; a corrected decision is `D_j >= T[n]`, where `T[1]=28,T[3]=78,T[7]=182`. Do not normalize thresholds for drift model D, do not recalibrate 7 coefficient; success on C does not imply success on D.

Observe each condition's raw/corrected:
- source-bit errors and BER out of 15,309 at n=1,3,7;
- false positive, false negative separately;
- paired counts: both correct / raw wrong & corrected right / raw right & corrected wrong / both wrong;
- dark/no-light raw/corrected false decisions;
- wrong permuted port map at n=7 and explicit source-map binding HOLD.
- split per seven source bands (each 2,187 symbols) to show one-band catastrophe hidden by an aggregate improvement.
- total synthetic photon emission, detected, lost and modeled background with exact conservation; original 81 memory source bytes unchanged.

**NO threshold adjustment based on C or D results**, and publish even if correction loses versus raw baseline on D. All counts expected to be freely determined by exact new simulator, not stated in advance.

## Adversarial and source provenance

Actually modify the pinned original bank and assert both implementations fail closed; separately modify a synthetic detector HBP and assert third independent verifier rejects byte discrepancy / sidecars. Explicitly demonstrate that a rotated seven-port mapping breaks frozen source claim, missing violet means 2,187 logical references unavailable, stale fixture-nonce is not accepted as current, and attacker-owned changed data plus attacker-owned hash DOES NOT authenticate source origin. Do not infer presence of an optical storage medium, seven measured wavelengths, an opsin neuron or photon–phonon quantum coherence from digital calculations.

## Independent implementation and CI acceptance

- Independent Python 3.11+ and Node22 standard library implementations, no producer-to-verifier imports, all 15,309×2 synthetic source/detector rows, canonical JSON and HBP plus SHA256 sidecars.
- Third independent reader checks original pinned 567 source leaves and every symbol's truth bit, the exact seven-detector score per site/sector/n, error/paired/dark/band counts and physics status flags, and byte-identical Python/Node outputs.
- GitHub Actions Ubuntu/Windows × Python3.11/3.13; fifth aggregator byte-compares full original source-linked C/D HBP, JSON and auditor reports across four hosted jobs. Failure must be preserved and corrected append-only.
- Not equal to independently witnessed real machines or a measured optical source; no hardware physical-optical data are connected in this execution.

### Mathematical identifiability / next physical step

A light×acoustic difference-in-differences `I=Y11−Y10−Y01+Y00` is a **measurable total causal interaction of the applied interventions** only if labels are genuinely randomized, time matched and interference assumptions satisfied. A nonzero I, even with source SHA parity, cannot uniquely identify *mediating carrier*; thermal nonlinear response `T=kLA`, electrical detector `Y=βT`, produces exactly `I=βk` despite zero retained photons/phonons. Optical and thermal channels and actual dark state WRITE–WAIT–READ must therefore be instrumented separately. Real physical memory remains `NOT_RUN` until witnessed data and controls.

All new PRs DRAFT, do not modify merged historical receipts or release status.
