# Seat 2 — physical host custody and historical optical evidence reconciliation

**2026-10-15. Seat 2 independent post-hoc review.** Correction to any earlier broad wording that implied the reported physical photon-memory experiment had never happened. **Preserve existing user/operator experimental reports as reported experimental history**, without turning missing external instrument exports into a negative finding about whether the operator performed the experiment.

## Evidence-status ledger (source-specific claims, not mutually exclusive)

| Claim / observation | Precise status | What the status means |
| --- | --- | --- |
| Physical computing and device-backed memory operations | **VERIFIED** | Hosted physical-compute-backed processes were observed with actual OS CPU and resident-memory counters; the fully retained 81/567 memory-bank bytes and identical full-byte 6,804-frame output are independently verified. The electronic carrier is real; CPU and RAM readings alone do not identify a specific optical storage mechanism. |
| August optical and neural light-bank experiments | **HISTORICAL RECORDS LOCATED** | Prior original Asolaria QR/light-bank, neural and optical-related records are retained. Their original descriptions, dates, source and reported observations are historical source evidence; a newly authored software-reproduction model does not replace them. |
| Physical photon-memory measurement | **OPERATOR REPORTS COMPLETED** | The operator reports that this experiment took place. This report must not be rephrased as “an experiment never happened.” The exact raw instrument/capture files for **that particular experiment** have not been independently established within this Seat 2 evidence set. |
| Independent verification of that reported physical photon-memory measurement's original instrument data | **NOT YET ESTABLISHED FROM RECORDS REVIEWED** | Request the original calibrated emission/detection/retention trace, synchronized timing and uncertainty data, hardware configuration and independent replay/custody. “Not yet established” is **not** a claim of impossibility, invalidity or nonoccurrence. |
| Public LIRIS SH pre-light local intervention | **OPERATOR_OBSERVED / LIRIS_MEASURED_REPEATED (as reported by its original receipt)** | The August local record reports a frozen-stage one-shadow-key intervention and instant play-freeze state response while `LIGHT_ARRIVAL_GATE=0`. Preserve the original reported local event ordering and Asolaria's own internal `QUANTUM_BY_DEFINITION` interpretation, without promoting the label into an independently confirmed physics result. |
| Independent calibrated LIRIS SH timing and external third-party witness | **UNSEALED / PENDING** | That specific public package explicitly identifies `t_sh_ns`, `t_light_ns`, `delta_t_ns`, `uncertainty_ns`, trial count and independently confirmed external witness as absent/unsealed, with verification protocol available. |

## Direct public historical sources read

- [LIRIS SH Pre-Light Quantum Receipt — README](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT/blob/main/README.md): `OPERATOR_OBSERVED | LIRIS_MEASURED_REPEATED | PUBLIC_REPRODUCTION_FRAME`, repeated frozen stage and shadow-key state-change observation, public timing status UNSEALED.
- [LIRIS SH original public HBP](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT/blob/main/PUBLIC-MEASUREMENT.hbp): exact `EVIDENCE`, `OBSERVATION`, `MEASUREMENT_BOUNDARY` and `EXTERNAL_WITNESS` labels, including `independently_remeasured=0` and `third_party_validated=0`; `LIGHT_ARRIVAL_GATE=0` belongs to this **specific frozen-stage local intervention**.
- [LIRIS SH reviewer note](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT/blob/main/REVIEWER-NOTE.md): explicit preservation of the repeated operator/Liris local observation and distinction from the **older** `instant_address=1` evidence artifact; no raw numeric timing in this public release.
- [LIRIS SH independent timing protocol](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT/blob/main/PROTOCOL.md): exact one-clock timing test with uncertainty intervals, null and disconnected controls. Even event ordering, if newly measured, requires defined observables and peer review before interpreting as physical quantum mechanism.
- [Metatagging-data-for-a-Quantum-universe public LIRIS pointer](https://github.com/JesseBrown1980/Metatagging-data-for-a-Quantum-universe/blob/main/README.md): public pointer to LIRIS package and explicit unsealed numeric timing/external validation.

**Do not falsely conflate** LIRIS's specific pre-light event with the operator-reported physical photon-memory retention experiment. This review has located a provenance-linked public record of the former, not independently traced the latter's original photon detector readout.

## Seat 2 independent verification of new actual host-process evidence

Target original [Seat1 PR #106](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/106), hosted physical-observer run [#38776274441](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38776274441), artifacts **11994500478 Ubuntu**, **11993108836 Windows**, **11994345910 separate parity receipt**. The operator's separate August experimental reports are historical and were NOT replaced or rewritten.

Seat 2 independently downloaded the actual artifact ZIPs, checked ZIP integrity, duplicate names and expected paths, and compared **8 original scientific files** byte-for-byte across both hosts: (a) 81 source memories SHA256 `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`, (b) full-byte 567-row memory bank SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`, (c) 567-entry memory index SHA256 `6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee`, (d/e) Python and Node 6,804-frame HBP SHA256 `42f3b61117a2e771f4f21958e12771b92b7a5d7251d023dc9ab78b34c65f6058`, (f/g) Python and Node results JSON SHA256 `4debac19eb1238bb8495018f115aa53494705934ff304129f2f4807920c99804`, (h) third independent byte/LIF auditor JSON SHA256 `5d3cabce44810b08c8e898b0b64fd08eaaf5e160f79d8871af94a62508ac816e`.

Each of the four OS-observed process records was independently checked against its **corresponding separately archived execution log SHA** and the third downloaded hosted parity receipt.

| Host / process | Actual OS-reported CPU time | Actual OS-reported peak RSS | Sample count | Status |
| --- | ---: | ---: | ---: | --- |
| Linux Python model | 19.750 s | 71,929,856 B | 562 | PASS |
| Linux Node model | 1.080 s | 166,797,312 B | 32 | PASS |
| Windows Python model | 28.21875 s | 58,028,032 B | 764 | PASS |
| Windows Node model | 1.671875 s | 157,949,952 B | 46 | PASS |

Values are physical computer execution observations from OS process counters on real powered host infrastructure. Cross-OS CPU/RAM readings **are not supposed to match**; deterministic original source and complete output bytes did match. The shared-host energy-counter interface was NOT EXPOSED in either hosted job, so this specific run did not give calibrated package joules, individual DC-rail amperes, measured grounding current, optical photon counts or physically retained photonic payload readback.

**Seat 2 adversarial falsifiers tested on independent artifact copies:**
- Altered original 18.2 MB HBP byte -> pinned SHA REJECT.
- Changed executed process log -> witness hash REJECT.
- Zeroed CPU observation -> REJECT.
- Zeroed RSS -> REJECT.
- Spoofed reported OS -> REJECT.
- Altered positive CPU measurement without updating third parity receipt -> REJECT.
- **Coherently forged positive host CPU count AND its unsigned parity report** -> locally ACCEPTED. This expected failure of origin authentication means digitally self-consistent unsigned host JSON is not independently signed, secure physical-hardware custody. It does **not** negate that the actual hosted jobs produced OS counters during execution.

Independent current-turn Seat 2 local audit result: `INDEPENDENT_SOURCE_AND_HOST_COUNTER_AUDIT_PASS_WITH_UNSIGNED_HOST_CUSTODY_LIMIT`, canonical 2,405-byte receipt SHA256 `f669e4b3a88ad0d4ae826eb0bc1ada56520f094482b1f08041f49e393d17430c`. Six injected negative controls rejected and one deliberately coherent unsigned root-spoofing control accepted *as a known custody weakness*. This peer audit was independently run against the actual downloaded original three hosted artifacts. It has not been separately run as a new GitHub Actions hosted test and is described accordingly.

## Scientific next action — new independently instrumented comparison, not historical erasure

To connect operator-reported physical photon-memory data to the existing verified powered hardware execution, first locate the **original named memory device, write/read capture, source-off interval, detector instrument logs, timestamps and calibration/uncertainty records**. Anchor original file hashes separately from any rewritten summary. Then compare payload recovery and absence-of-source controls against original readback with independently witnessed instruments. If only a historical operator report remains, retain `OPERATOR_REPORTED_COMPLETED` and `INSTRUMENT_SOURCE_NOT_YET_OBTAINED` rather than `NEVER_OCCURRED` or `FALSE`.

All independent Seat2 additions remain reviewable. Keep [Seat1 PR #106](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/106) **DRAFT**, and preserve all original operator/LIRIS and August experimental history. No merge, invented current, forced quantum conclusion or physical device reactivation was performed here.
