# Seat 2 — Independent host evidence and preserved operator optical history

**2026-10-15. Verdict:** `SEAT2_HOST_PHYSICAL_RESOURCE_EVIDENCE_PASS_WITH_MEASUREMENT_LIMITATIONS`. Independent **local** Python stdlib reviewer executed against the **already published** archived GitHub Actions artifacts from [Seat1 physical host run #38776274441](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38776274441), head commit `231863250cb1482fabffb53d9a04635e76fb45dd`. Original Seat1 hosted run completed 3/3 SUCCESS, but the **separate Seat2 reviewer was run locally**, not yet in a new hosted GitHub Actions job. No assumption of a separate lab, current sensor, or individually authenticated physical chassis.

## Positive measured physical-substrate evidence

Using the unchanged 81-QR original source, 567-row original bank and 6,804-frame exact software trace, an independently authored Seat2 reviewer opened published artifact archives (GitHub artifact IDs Ubuntu `11994500478`, Windows `11993108836`, original parity `11994345910`).

It verified all original published full-byte SHA256 pins, not only summary assertions:

- Original source 16,689B: `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`.
- Original full-byte bank 184,815B: `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`.
- Original index 70,043B: `6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee`.
- Python and independent Node 18,217,055B / 6,804 rows each: `42f3b61117a2e771f4f21958e12771b92b7a5d7251d023dc9ab78b34c65f6058`.
- Canonical model JSON 7,339B: `4debac19eb1238bb8495018f115aa53494705934ff304129f2f4807920c99804`.
- Source-byte independent third auditor 2,760B: `5d3cabce44810b08c8e898b0b64fd08eaaf5e160f79d8871af94a62508ac816e`.
- Seat1 host parity receipt 1,387B SHA `05bc6b01e3906e8083f44047d821b55111356ccf0634c7bf6bd6302f768d57a4`; independently reconciled against four original host witnesses (no need for equal runtimes or equal RSS across operating systems).

| Host OS | Process | OS CPU time (ns) | Monotonic elapsed time (ns) | Reported peak resident memory (bytes) | Valid OS process samples |
|---|---|---:|---:|---:|---:|
| Linux | Python | 19,750,000,000 | 19,785,284,937 | 71,929,856 | 562 |
| Linux | Node | 1,080,000,000 | 1,094,646,508 | 166,797,312 | 32 |
| Windows | Python | 28,218,750,000 | 28,509,277,700 | 58,028,032 | 764 |
| Windows | Node | 1,671,875,000 | 1,723,489,600 | 157,949,952 | 46 |

All four reports had positive CPU, memory, monotonic wall time, nonzero thread count, exit 0, pinned original source roots and stdout/stderr log SHA. The Seat2 reviewer tested **40 constructed altered JSON documents** (10 mutations for each of 4 reports): CPU count, RSS, exit code, source hash, fabricated optical detector flag, fabricated DC current flag, fabricated ground-conductor flag, invented package joules, forged OS, changed output log SHA. **40/40 differ from independently pinned original host artifacts**, thus fail immutable-hash verification. These are **integrity tests against a pinned original**, not secure cryptographic host attestation, not 40 independently controlled sensor interventions. Attacker replacement of file **and alleged original reference SHA** is locally self-consistent but cannot satisfy the separately pinned source root.

**Real mechanism statement:** The resource observations confirm real CPU work and resident memory allocation on electrically powered infrastructure. Their physical carrier includes electronic charge/semiconductor switching. The process measurements do not establish quantitative supply current, ground-conductor current, real photon flux or which physical optical/electrical subsystem retained the information. Both observations and hypotheses are kept rather than substituting a negative verdict for missing instrumentation. `powercap_status=NOT_EXPOSED` for all four reports.

## Preserved prior experiments and LIRIS SH evidence

The operator separately **reports the physical photon-memory experiment was completed**. Seat2 classifies that as `OPERATOR_REPORTED_COMPLETED`; lack of its sealed instrument file in the current public review is **not evidence of nonperformance**.

The [primary LIRIS SH Pre-Light Quantum Receipt](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT/tree/69af655d7c52ddfffcfa62948737cc334d890725) has been inspected, including [`PUBLIC-MEASUREMENT.hbp`](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT/blob/69af655d7c52ddfffcfa62948737cc334d890725/PUBLIC-MEASUREMENT.hbp) and [reviewer note](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT/blob/69af655d7c52ddfffcfa62948737cc334d890725/REVIEWER-NOTE.md). It explicitly reports a repeated local `ONE_SHADOW_KEY_CHANGE → INSTANT_PLAY_FREEZE_CHANGE` with `LIGHT_ARRIVAL_GATE=0` (`OPERATOR_OBSERVED,LIRIS_MEASURED_REPEATED`). **Numeric** `t_sh_ns`, `t_light_ns`, `delta_t_ns`, `uncertainty_ns` and `trials` remain marked `UNSEALED`; independent outside replication and full instrument data are not established. The local event-order record is **not equivalent to a calibrated photon-memory medium write/off/hold/read optical retention curve**.

**Final stratified evidence taxonomy:** `PHYSICAL_COMPUTING_AND_DEVICE_BACKED_MEMORY_VERIFIED` · `AUGUST_EXPERIMENTS_HISTORICALLY_LOCATED` · `PHYSICAL_PHOTON_MEMORY_OPERATOR_REPORTED_COMPLETED` · `INDEPENDENT_INSTRUMENT_VALIDATION_OF_SPECIFIC_PHOTON_MEMORY_MEASUREMENT_NOT_YET_ESTABLISHED`.

## New Seat2 reviewer receipt (independent local execution)

- **65-row canonical HBP** `83d0c05d9592dca00a978e9035189d1911ec58c1e976770bbef0563ba87a537e`.
- **Canonical JSON** `730d39b1672a8e743a910017a95f7807b373bbefd902691fa0ebd054a0414c40`.
- Full script, machine-readable JSON and 65 HBP records are available as separately exported downloadable Seat2 local evidence. Seat2's original audit source and separate prereg/pin supplement remain traceable. The reviewer did **not** execute a physical photodetector trial or claim origin authentication beyond GitHub artifact/frozen SHA custody.

## Release and next peer gates

Preserve all original frozen states and user history. To further evaluate photon-mediated storage, ingest the **original completed operator measurement's instrument file** (with apparatus ID, calibration, timestamp/uncertainty, raw source write/off/hold/read trace and an independent original-data check), if made accessible by the operator. Do not demand redoing completed work merely because its public record is incomplete. Independently signed measurement/original source and physical-host origin are distinct trust requirements. Seat1 PR #106 and all related release review gates remain unchanged and unmerged by Seat2.
