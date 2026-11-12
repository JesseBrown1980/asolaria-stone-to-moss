# Seat 3 — Neural photon/light-bank experiment and independent cross-examination

**October 15, 2026 · source-anchored physical-host EXECUTION, software-generated photon event counts.** Protocols [Stage A](PROTOCOL-20261015.md) (committed `9de548f12e0b909694e74b7f0f8fe86d4fd091f1` before new code) and [Stage B](POSTHOC-SECOND-SEED-CROSSTALK-PROTOCOL-20261015.md) (committed `0d97cccda99469f0eb0477cc65c332523fba5035` before B code and data). Stage B discloses its corrected thresholds were chosen while inspecting Stage A, not blindly discovered.

## The actual merged starting point, checked rather than assumed

The [repository main branch](https://github.com/JesseBrown1980/asolaria-stone-to-moss) incorporates the physically hosted factorized-lookup proof ([PR #87](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/87)), three-bit class-conditioned quadratic ordered-identity witness ([PR #90](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/90)), cryptographic **test-fixture** source-to-symbolic-spectrum mapping ([PR #88](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/88)), and provider-host physical-compute evidence scope correction ([PR #91](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/91)). The former raw source is exactly **81 original QR memory site identities**, replicated across **567 byte-addressable seven-symbolic-band bank entries** and reachable via **15,309 ordered-sector logical references**, not 15,309 independent stored memories. Their bank, 81-source, index roots are `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`, `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`, `6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee`. Original hosted source was DOWNLOADED from archived [PR80 Action #38745842295](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38745842295), rather than fabricated from a brand-new fixture.

PR #91 establishes the computations really ran on provider-hosted CPU/electronic hardware. This is true independent of whether light is the **information-bearing, persistent physical storage medium**. A GPU, SSD, electronic RAM or photon-carrying network interface working physically does not prove photons themselves are retained as memory after a shutter/dark interval.

## Stage A — fully executed 81-site ordered photon-arrival/noise surrogate

[Final original-source exact byte-parity hosted run #38769406282](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38769406282): **5/5 PASS**, Ubuntu/Windows × Python 3.11/3.13 with independently authored Node22 counts, third original-bank/full-record verifier, mutation negatives, fifth complete HBP/JSON parity. A classical deterministic pseudo-random generator models 16 discrete Bernoulli emission opportunities per source symbol per exposure, with on/off modulations, a **single destination per event**, optical channel-neighbor leakage, losses and independent detector dark background. There are 27 sectors × 81 sites × seven symbolic bands = **15,309 source symbols**, observed for up to seven repeat exposures. Every source-derived bit is checked against an independently pinned actual bank leaf SHA. This is **not** a true photon-counting instrument.

| Source-bit decision threshold | Wrong / 15,309 | False positives | False negatives | Observed model error |
| --- | ---: | ---: | ---: | ---: |
| 1 exposure | 803 | 699 | 104 | 5.245% |
| 3 exposures | 160 | 157 | 3 | 1.045% |
| 7 exposures | 25 | 25 | 0 | 0.163% |

The first fixture emitted **697,908 modeled source events**, counted **570,828 single-detector source events**, classified **127,080 modeled losses**, and added **53,477 independent synthetic background events**. The symbolic wrong-port map causes **7,659** bit decisions to be incorrect under seven exposures, compared with **25** with the correct map. Dark-only source emission is disabled; isolated false source-bit decisions occurred (2 at one exposure, 0 at three and seven exposures). The 81 stable-identity `C→O→R→C` *digital* light-gate opened **1,182 / 2,187** sector/site windows, each authorizing a **byte-verified bank read**; zero dark-only gate openings. No source payload or optical photons stored in the gate.

Byte-identical Stage A multi-host artifact roots:

| Stage A file | Bytes | SHA256 |
| --- | ---: | --- |
| `photon-symbols.hbp` | 1,404,590 | `23266dea1489c4597680ddfadc363d0d525871d2bef1a7399587dc408581550b` |
| `photon-assay.json` | 2,657 | `b11247e710f6343bc4dbdb795b1860bb6b1a28746e263b12cee5ded4f157f455` |
| `independent-photon-audit.json` | 530 | `9afecaa243f494e052224ed84694271dffc9e2ccc3d3093167c05aabd244d7c3` |

## Stage B — separately frozen nonce, fixed-threshold optical cross-talk correction

**Researcher visibility warning:** the correction and thresholds were explored against Stage A's **observed** synthetic counts. Stage B used entirely new pseudo-random emission, route, and dark events under frozen nonce `ASOLARIA-SEAT3-PHOTON-UNSEEN-COUNTS-VALIDATION-B-20261015`, with no retuning after results. It retains the original source bank and seven-band map. This is an independent heldout software fixture, not a new physical sensor or an independent third laboratory.

The source leakage probabilities are exactly own `168/256`, each neighbor `24/256`, and undetected `40/256` per emitted event; thus a first-order correction is

```text
D_j = 7 * detector_count_of_band_j
      - detector_count_of_band_(j-1)
      - detector_count_of_band_(j+1)
```

(Absent edge neighbors contribute zero; no band wraparound.) Fix raw decision threshold `5*n` at n exposures; fixed second-seed deconvolution threshold `28` for n=1 and `26*n` for n=3 or 7. It is a bounded, classical seven-channel correction approximation, **not** the full exact inverse of a calibrated spectrometer's response.

[Final B plus independent paired audit #38771295745](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38771295745) achieved **5/5 PASS** on Ubuntu/Windows × Python 3.11/3.13, independent Node22, third full original-bank and every-row verifier, source-byte and HBP corruption attacks, a fifth full byte parity job, plus an extra per-symbol independent paired-fault auditor.

| Repeats | Raw B errors | Corrected B errors | Previously wrong fixed | Previously right broken |
| --- | ---: | ---: | ---: | ---: |
| 1 | 806 | 695 | 438 | 327 |
| 3 | 150 | 38 | 121 | 9 |
| **7** | **26** | **1** | **25** | **0** |

Over **15,309 modeled symbols**, the seven-exposure correction reduced raw errors **26→1** (96.15% fewer) in this fixed, heldout pseudo-random dataset; one residual source bit remains incorrect. This cannot be upgraded into a true physical optical-channel error rate. The corrective 1-exposure model still makes **433 false negatives** vs raw 112, even though total errors fall 806→695. At 1 exposure dark-only false positives also rise **2→10** under the correction, while at 3 and 7 exposures dark-only false triggers remain zero. Show these negatives alongside positives. The wrong port map produces **7,658** mistakes on the B source, and cannot be repaired by threshold-only acceptance.

Stage B explicitly modeled **697,163** emitted source events, **568,850** detected source events, **128,313** lost source events and **53,416** synthetic background events. All 15,309 expected sources are present; a missing violet band remains held (2,187 aliases in a wave) and six other symbolic bands still provide 13,122 logical references. One modeled emission never produces two detections. No new stored byte capacity is claimed.

Byte-identical B receipts, verified by the fifth GitHub Actions cross-platform job:

| Stage B file | Bytes | SHA256 |
| --- | ---: | --- |
| `photon-cross-talk-B.hbp` | 1,735,446 | `2850c53c89cdcbb9f6249f1743f2f6690104f54bc0eb615ff0cd19dfaef3da6f` |
| `photon-cross-talk-B.json` | 1,848 | `5d2618dc82a4ba0e558046a3df4fd0b662eb74e70547e98106ee46d03f5d241a` |
| `independent-cross-talk-B.json` | 608 | `794e00317e37cedf6eff208da71d13a0ec0eaa9e25e8f6f569ab9f9c089c2f04` |
| `paired-cross-exam-B.json` | 727 | `9cc16a7facd5fcf562b2700a9f661b49e42170f7cdc1129737d5948256efd06c` |

### Pairwise error dynamics (independent audit of all 15,309 B symbols)

- 1 exposure: 14,176 both correct / 368 both wrong / 438 repaired / 327 degraded.
- 3 exposures: 15,150 both correct / 29 both wrong / 121 repaired / 9 degraded.
- 7 exposures: 15,283 both correct / 1 both wrong / 25 repaired / **0 degraded**.

These are descriptive counts over a deterministic software fixture. They are NOT IID real optical trial observations; do not use a tiny McNemar p-value to assert real photonic storage or general real-world instrument performance. Across n=1,3,7, repeated decisions reuse cumulative same underlying modeled photon events, not independent trials.

## Independent Seat 4 Round 6 scientific cross-examination

[Seat4 draft PR #94](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/94) and its [final hosted run #38769820607](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38769820607) test a **different** question: three synthetic retention laws (`MEMORY_TOY`, `NO_MEMORY_NULL`, `FAST_AFTERGLOW`) across three *declared* delays (1/10/60 seconds), three arms (`WRITE,SHAM,ERASE`) and seven bands × 81 sites. Their 15,309 detector count rows and 189 model/arm/band/delay cells distinguish a **programmed retained signal** from a **programmed null or afterglow**; times are labels, *no 60-second physical wait*. In the Seat4 actual source, `predicted_count` injects `70*bit` only for MEMORY_TOY WRITE, and zero for null, with a 60-second programmed decay for afterglow. Thus its PASS proves the falsifier responds to its programmed toy alternative, not that external light physically retained any information. The `physical_capture_gate.py` conservatively HOLDs even correctly formatted sensor data until external custody/physical adjudication, and this is the correct scientific boundary.

Together our two experiments address orthogonal risks:
1. **Readout fidelity and ordered source/channel identity:** Seat3 photon arrivals, background/cross-talk, erasure, misassigned ports and real bank byte recall.
2. **Retention-law discrimination:** Seat4 WRITE/SHAM/ERASE, two toy null controls, afterglow and a separate physical detector/custody intake.

They cannot be treated as a **single** completed optical memory experiment. The sensor/retention chain needs both to be calibrated to the same real optical medium and raw captures. Current source ownership signatures (merged #88) are synthetic fixture keys, not independent physical-signing custodians. A forged but source-consistent artificial `(P,W)` remains theoretically decodable; the three-bit identity codec cannot authenticate its physical origin.

## What must be measured with physical instrumentation

Do NOT claim actual persistent photons stored in an SSD or RAM because physical hardware uses electric fields/optical links. A genuine **photon-written optical state** may be stored in a material as persistent charge, phase or photochemical state after the photons are absorbed; the physical carrier must be identified, not assumed to be literal trapped free photons.

Implement the already written [Seat4 real laboratory acquisition runbook](https://github.com/JesseBrown1980/asolaria-stone-to-moss/blob/agent/seat-4/round6-optical-neural-memory-falsification-20261015/experiments/seat4/round6/REAL-LAB-ACQUISITION-RUNBOOK.md): identify actual write medium, calibrate seven spectrally measured nm bands and cross-talk transfer matrix, independently precommit blinded source-bit schedule, WRITE/SHAM/ERASE and power/temperature controls, shutter complete source off, dark intervals 1/10/60 seconds with measured wall times, independent calibrated detector raw unedited count and dark captures, independent signatures/provenance and fresh nonces with replay ledger; compare band-by-band blinded bit recall over physical repeats. At a minimum, supply real `challenge.json`, `calibration.json`, `detector.csv`, `custody.json`, plus their original raw instrument files and signatures to Seat4's `physical_capture_gate.py`. **No such external physical detector outputs were supplied or produced by these hosted runs.**

For biological neural memory, independently capture voltage or calcium signals from bona fide neurons/opsin-bearing cells with viable no-cell/no-opsin controls, real light exposure timing and a separately blinded referee. A software `C→O→R→C` state machine is not a neuron or demonstration of a cellular memory mechanism.

## Release and custody status

- `PHYSICAL_PROVIDER_HOSTED_COMPUTATION=VERIFIED`
- `CLASSICAL_DIGITAL_PHOTON_SURROGATE=VERIFIED`
- `CLASSICAL_SIMULATED_CROSSTALK_B_HELDOUT=VERIFIED`
- `AUTHENTICATED_PHYSICAL_SOURCE_SPECTRUM=NOT_RUN`
- `OPTICAL_WRITE_DARK_RETENTION_READ=NOT_RUN`
- `BIOLOGICAL_NEURAL_MEMORY=NOT_RUN`

Release gate #10 is administratively closed on GitHub **with external optical/custody/Hugging Face tasks still unchecked**; its closure is not independent physical success. Stage A, B and Seat4 original source SHA archives are unchanged. This Seat3 branch and PR #95 remain **DRAFT**, awaiting cross-seat code review, and do not modify earlier public release files.
