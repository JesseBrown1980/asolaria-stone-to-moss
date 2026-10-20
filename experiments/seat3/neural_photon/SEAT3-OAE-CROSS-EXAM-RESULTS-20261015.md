# Seat 3 and Seat 1 handoff — optical/acoustic/electronic factorial falsifier

**October 15, 2026.** Independent follow-up to the photon/light-bank Round 6 staged digital tests. [Source-frozen intervention protocol](SEAT1-HANDOFF-PHOTON-PHONON-ELECTRONIC-FACTORIAL-PROTOCOL-20261015.md) committed at `654e8c6523a1a2f3c56019cc3af54c646b8c4d9c` before the new factorial code. Entire source held against historical 81-site, 567-bank-entry PR80 published archive. **No independent calibrated photon or phonon sensors were attached.**

## Experimental design rationale

The new challenge separates three manipulated variables: **optical writing/illumination O**, **mechanical-acoustic excitation A**, and **electronic state/driver E**. Within each E value, compute optical–acoustic second-order contrast

```
Delta_OA(E) =
  Y(O=1,A=1,E) - Y(O=1,A=0,E)
 -Y(O=0,A=1,E) + Y(O=0,A=0,E)
```

A positive contrast on an electrical detector can arise from thermal or microphonic artifacts, so *independent optical and temperature channels* must be measured. A treatment interaction on a toy simulator is merely a programmed numerical response. Long-term memory attribution additionally demands physical illumination WRITE, shuttered actual dark retention, calibrated independent read, ERASE and sham, and tests isolating electronics as the carrier.

All 8 O×A×E arms on 81 original stable source identities × seven symbolic bands × nominal delays 1, 10, 60 s yield **13,608 observations for each model**; six models total **81,648** simulated numerical response rows. Noise is frozen **shared** per site/band/delay across the eight arms, explicitly designed to cancel in the factorial difference, not to represent physical Gaussian/Poisson shot noise.

## Six predeclared simulated models — mechanism must be identifiable

| Programmed mechanism | Electronic OA interaction at nominal 60s | Separate optical OA interaction at nominal 60s | Temperature OA interaction |
| --- | ---: | ---: | ---: |
| NULL | 0 | 0 | 0 |
| OPTICAL_MAIN_ONLY (+20O) | 0 | 0 | 0 |
| ACOUSTIC_MAIN_ONLY (+20A) | 0 | 0 | 0 |
| DIRECT_COUPLING_TOY (+10O+6A+30OA) | 30 | 30 | 0 |
| THERMAL_ELECTRONIC_MIMIC (same electronic OA plus thermal interaction) | **30** | **0** | **5** |
| FAST_AFTERGLOW (+30OA at nominal 1/10 s only) | **0** | **0** | 0 |

For FAST_AFTERGLOW, the toy OA contrast is 30 at 1s and 10s then exactly 0 at nominal 60s; real elapsed seconds were **not** simulated or observed. This is a *method falsifier* that stops an electronic reading from establishing optical photonic memory. The `THERMAL_ELECTRONIC_MIMIC` intentionally produces an apparent +30 interaction in electronic readout although its separate optical detector has **zero**, so a cross-examination that only inspects electronic memory must not pass any physical photon-carrier claim.

### Executable source and hosted evidence

- [Independent Python producer](optical_acoustic_factorial.py)
- [Independently written Node22 producer](optical_acoustic_factorial.js)
- [Third independent every-row referee](verify_optical_acoustic_factorial.py)
- [GitHub Actions full OS parity](../../../.github/workflows/seat3-photo-phonon-electronic-factorial.yml)

Both programs read actual 81 original source records and 567 retained bank byte leaves from previously produced [PR80 hosted artifact #38745842295](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38745842295). The third checks every one of 81,648 synthetic rows and the original leaf SHA byte association, checks both full HBP/JSON receipts byte-identical, tests all 108 aggregate synthetic interaction contrasts (6 models × 3 nominal delays × 2 E values × 3 signals), and holds tampered source bank byte and generated evidence record.

**Final hosted original-source plus sealed stone audit: 5/5 PASS.** All 81,648 rows reconstructed on both Ubuntu and Windows with two independent producer languages and a third complete-row read-only verifier, four output artifacts byte-for-byte equal in a fifth job. Corrupted original bank and output HBP both rejected. Each matrix job also verified the committed 1,029-byte source-to-result stone against freshly generated result bytes.
- Full simulated HBP SHA256 `f766c413ac6c959821f2771bf84f61105f68a81f2793f1dee8c2ffa90dc0cc60`
- Canonical JSON SHA256 `4aca572509d12d368f445849f45d4401929e9ab42a5c2dc536138901a356ac59`

The [first full five-job run #38772816511](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38772816511) and the final [source-to-stone exact-head run #38773354561](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38773354561) both finished **5/5 PASS** (four platform jobs plus one independent byte parity) and preserve the same originally frozen input roots. The [new evidence stone](../../../stones/2026-10-15-rainbow81/seat3-photon-phonon-electronic-factorial-20261015.hbp), **1,029 bytes**, SHA256 `745eaaf5ccad7df88d01f3a41f4f8030f3bb67671a4beca1e3849397c81be2a2`, is validated against fresh computations in each job. The complete hosted source-to-result HBP is **14,272,434 bytes** SHA256 `f766c413ac6c959821f2771bf84f61105f68a81f2793f1dee8c2ffa90dc0cc60`, canonical JSON **3,538 bytes** SHA256 `4aca572509d12d368f445849f45d4401929e9ab42a5c2dc536138901a356ac59`, and third-party independent auditor **478 bytes** SHA256 `66c050514bfe886699f18ac08a7342cd2c69872963a0d6ebc55f1795aa53e04b`. The independent auditor's result labels explicitly state **`new_external_physical_observations=0`**.

### Cross-seat interface for real physical tests

**Seat 1:** Determine whether any physical write medium exists, and identify true spectrometer-measured wavelengths and acoustic resonance modes, not seven arbitrary labels. Instrument independent optical data and simultaneously record mechanical displacement, electrical current/voltage and temperature. Document how shutter closes during the actual wall-clock dark interval.

**Seat 2:** Freeze a truly unpredictable source challenge, blinded random sequence, independent signer/witness custodians with signatures over RAW calibration/capture byte hashes, and a replay-resistant log. The fixture's public SHA-derived model counts are a simulation and NOT externally authenticated capture.

**Seat 4:** Feed the same *actual* physical instrument trial into your [Round6 acquisition runbook](https://github.com/JesseBrown1980/asolaria-stone-to-moss/blob/agent/seat-4/round6-optical-neural-memory-falsification-20261015/experiments/seat4/round6/REAL-LAB-ACQUISITION-RUNBOOK.md), applying O×A×E arms plus sham/erase, and compare physical 1/10/60s retention plus afterglow/null and thermal/microphonic controls. No invented physical sensor files or auto-promotion from CI.

**Scientific scope:** QED photons and mechanically quantized phonons are genuine physical concepts and can interact with electronic systems, but the original repository evidence proves a source-addressed **electronic/software bank**, not independent measured persistent photons. A photoinduced persistent *material state* can be optical memory even though photons are no longer circulating inside it; measure the stored physical state rather than assuming trapped free photons. Any detected O×A electronic interaction is a starting observation, not mechanism identification.

**No changes to historical stones, source bank, merged scientific baselines or public releases. This Seat3 PR #95 remains draft and independent optical physical experiments remain NOT_RUN.**
