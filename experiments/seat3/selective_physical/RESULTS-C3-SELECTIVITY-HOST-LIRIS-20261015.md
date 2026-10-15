# Seat 3 — Verified physical-host computation, historical LIRIS evidence, and selective-mechanism rank certificate

**2026-10-15 — exact-head run [38778189887](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38778189887): 5/5 PASS** (Ubuntu + Windows × Python 3.11/3.13; independent Node22 exact rational calculation, third read-only audit, fifth full-byte parity). This report was added *after* successful hosted tests. The [frozen experimental protocol](PREREG-SOURCE-HOST-MECHANISM-20261015.md) preceded the executable implementation (prereg commit `9b5ed314e5590a2e7e1622a19e3b41ec2e309077`).

## Evidence taxonomy — corrected and preserved

- **Physical computation & device-backed electronic memory activity:** `VERIFIED` by publicly hosted, source-rooted code execution on electrically powered computers. The new OS-process counters below are measured during the actual source and exact rank workload, not estimated from a synthetic photon model.
- **August optical/neural Asolaria light-bank work:** `HISTORICAL_RECORDS_LOCATED`; previous colour-QR, RAINBOR, lightbank records remain intact, not overwritten.
- **The operator's photon-memory experiment:** `OPERATOR_REPORTED_COMPLETED`. Independent validation of that particular run's original calibrated instrument, dark interval, raw count/optical-state trace, provenance and statistical error bounds is `NOT_YET_ESTABLISHED_FROM_REVIEWED_RECORDS`. **Do not incorrectly call the historical experiment never attempted or never completed.** This review concerns what these GitHub records independently establish, not whether the operator actually ran the prior apparatus.
- **[LIRIS SH Pre-Light Quantum Receipt](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT/tree/69af655d7c52ddfffcfa62948737cc334d890725)**: publicly source-pinned **`OPERATOR_OBSERVED,LIRIS_MEASURED_REPEATED`** local report of `ONE_SHADOW_KEY_CHANGE` while play is frozen → `INSTANT_PLAY_FREEZE_CHANGE` with `LIGHT_ARRIVAL_GATE=0`, `SH_CHANGE_BEFORE_LIGHT_ARRIVAL`. The original 1,642-byte `PUBLIC-MEASUREMENT.hbp` SHA256 is `d9b20742592e6fdcb26c03278bd9d574636f4f9f05b24cf502ad173d20e5579f`. Its **t_SH, t_light, delta, uncertainty and trial count are all explicitly UNSEALED**, and it states `independently_remeasured=0`, `third_party_validated=0`. These limitations do NOT erase or reset the reported repeated local observations. `QUANTUM_BY_DEFINITION` is a recorded Asolaria interpretation, not external confirmation of a quantum observable/FTL signaling. This LIRIS observation is separate from the reported photon-memory retention experiment.
- Original public LIRIS source pointer: [Metatagging August 4 HBP](https://github.com/JesseBrown1980/Metatagging-data-for-a-Quantum-universe/blob/99f9c52ac1706b395dcc1910006fc2a29bd6d9be/docs/LIRIS-SH-PRELIGHT-PUBLIC-POINTER-2026-08-04.hbp). Keep HBI, HBP, SHA, SH and HASH distinct.

The CI pins LIRIS's exact Git commit and blob SHA and independently checks the original text for the actual historical local claim and the unsealed timing/external status. The third implementation independently pins all 567 original byte-bank leaves, including 81 immutable site identities: source JSON SHA `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`, bank SHA `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`, index SHA `6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee`.

## Exact mechanism-selectivity theorem

Old experiment [PR #109](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/109) showed that an optical effect and an electronic pickup sharing the same blocker produce mathematically identical scalar observations. Define B = blocker (0/1), S = independent RF shield (0/1), Z = newly proposed optical attenuation intervention (0/1), and **eta** = hypothetical fraction of blocker-linked RF pickup attenuated by Z:

```
y(B,S,Z) = alpha (1-B)(1-Z) + beta (1-S) + gamma (1-B)(1-eta Z)
```

The matrix's columns are optical, independently shieldable electronic and blocker-linked electronic contributions. All eight B/S/Z arms are tested with exact rational arithmetic. The original B/S-only experiment has rank **2** for three parameters. For `eta in [0,1/4,1/2,3/4,7/8,15/16,1]`, the new design ranks are **[3,3,3,3,3,3,2]**. Selected 3×3 determinant is exactly `1-eta`. A locally full-rank model is **not** a physical confirmation that actual attenuator has independent spectral selectivity.

| Hypothetical measured electronic cross-sensitivity eta | Rank | 1-unit contrast error amplified into gamma bound | gamma source identifiable under exact eta? |
|---|---:|---:|---|
| 0 | 3 | 1× | Yes, in stated model |
| 1/2 | 3 | 2× | Yes, in stated model |
| 3/4 | 3 | 4× | Yes, in stated model |
| 7/8 | 3 | 8× | Yes, in stated model |
| 15/16 | 3 | 16× | Yes, but fragile |
| **1** | **2** | **Unbounded** | **No** |

The inversion is explicit for `eta!=1`: `gamma=y(0,1,1)/(1-eta)`, `alpha=y(0,1,0)-gamma`, `beta=y(1,0,0)`. At `eta=1`, (alpha,beta,gamma)=(23,7,11) and (29,7,5) create identical full-eight-arm observations: a constructive physical-carrier nonidentifiability counterexample. If externally calibrated `eta` uncertainty includes 1, attribution must **HOLD** regardless of nominal fit.

**Thermal source of false positives:** independent model `T=L+A` leads to `T²=L+A+2LA` for binary light L and acoustic A, giving rank4/5 when including direct LA and the quadratic thermal regressor. Introducing a *separately varied*, source-independent hypothetical heater H with `T=L+A+H` makes the eight-arm, six-column model rank **6/6**. This is a design requirement, not evidence that an independently calibrated heater already exists.

## Actual host-process counters — not calibrated electrical meter readings

All four hosted runs executed source checks + exact mathematical proof inside Python on physical provider-hosted hardware. Fifth job independently checked the following OS-reported telemetry per process, preserving platform differences rather than demanding identical dynamic measurements:

| Job | OS CPU time (ms) | Monotonic elapsed (ms) | Peak Python traced allocated memory | Native ru_maxrss |
|---|---:|---:|---:|---|
| Ubuntu Python 3.11 | 38.331764 | 38.623436 | 501,871 B | 17,944 KiB (Linux) |
| Ubuntu Python 3.13 | 38.629351 | 38.941297 | 492,663 B | 18,828 KiB (Linux) |
| Windows Python 3.11 | 62.500000 | 108.323500 | 501,586 B | unavailable (do not invent) |
| Windows Python 3.13 | 15.625000 | 113.090000 | 492,535 B | unavailable |

These counters are OS/virtualization reported, with granularity and scheduling limitations. Do **not** infer physical chassis independence, true electrical joules, AC/DC rails, individual transistor toggles or real optical detector counts from them. A clock value in nanoseconds means an OS API returns an integer with that nominal unit; it does not assert nanosecond timing precision. The original sources and all dynamic telemetry have SHA sidecars joined to deterministic result SHA.

## Independently verified frozen outputs

- Four-platform **byte-identical exact mathematical/history result**, 4,333 bytes, SHA256 `be54567179b8fb8b18be3810446ada967949f0408c2c06b02d52829fbc3e77fc`.
- Independent third verification record, 551 bytes, SHA256 `7bfecdd86cb5ab167145c673ecfb6260bf678c6f2aed19609dafacd6c7881583`.
- Dynamic OS/VM counters differ per platform and are preserved as separate `host-process-telemetry.json`, each SHA checked. This is **expected**, not drift.
- Python and Node implementations independently reconstructed exact rational results, all original 81/567 source entries, and public LIRIS history; actual mutated historical bank and altered output JSON were rejected by CI. Six additional mathematical/status controls HELD.

### Practical handoff

**Seat1:** Identify physical optical/RF apparatus, measured attenuator Z source selectivity (including electronic/RF cross-talk), separate thermal heater H and source-independent calibration. Establish actual AC/PSU DC power meter readings safely through rated external equipment, not live exposed mains/PSU probing.

**Seat2:** For the operator-reported completed photon-memory experiment, locate its original instrument data and independent custody; do not demand it be rerun merely to acknowledge its existence. Require calibration, actual timestamps, matched dark controls and separate signer for *independent verification*. LIRIS SH timing values remain unsealed in public receipt.

**Seat4:** Use the physical readback/watchdog to independently challenge the full same-run join `source digest → workload/host counters → actual instrument capture`; test timestamp mismatch, coherent false source/reference, signal leakage into RF, thermal sham and optical memory persistence with genuine shuttered hold.

**Seat5:** Challenge rank theorem when Z perturbs both optical and electronic channels in a nonlinearly or time-varying way. A rank3 toy model with unknown eta is not automatically an identified mechanism. Derive actual measurement error/conditioning bounds with independently calibrated eta uncertainty and precommitted power analysis.

### Evidentiary conclusion

`PHYSICAL_HOST_COMPUTATION=VERIFIED`

`HOST_PROCESS_ACTIVITY_OS_REPORTED=MEASURED_IN_NEW_CI`

`PRIOR_PHOTON_MEMORY_EXPERIMENT=OPERATOR_REPORTED_COMPLETED`

`PRIOR_LIRIS_SH_LOCAL_OBSERVATION=REPEATED_LOCAL_REPORTED`

`ORIGINAL_PHOTON_MEMORY_INSTRUMENT_DATA_INDEPENDENT_AUDIT=NOT_YET_ESTABLISHED`

`NEW_CI_CALIBRATED_ELECTRICAL_OR_PHOTON_METROLOGY=NOT_ATTACHED`

No prior published receipts rewritten, no releases or cross-seat merges authorized by this test. This PR remains DRAFT for independent review.
