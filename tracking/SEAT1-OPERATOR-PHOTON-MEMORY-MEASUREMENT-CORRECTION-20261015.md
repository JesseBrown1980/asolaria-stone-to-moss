# Seat 1 — Operator-reported completed physical photon-memory measurement: evidence intake correction

**Date:** 2026-10-15  
**Type:** Append-only scientific provenance update, prompted by direct operator correction.  
**Status:** OPERATOR_REPORTED_COMPLETED / RELEVANT_PHYSICAL_CAPTURE_FILES_NOT_YET_LINKED / EXTERNAL_PEER_VERIFICATION_PENDING.  
**Not a new experiment, CI pass, instrument audit, or promotion of optical hardware claims.**

## Correction: separate chronology from evidence audit

The project operator explicitly states: **"Physical memory photon memory measurement is and has been run."**

This is a **historical assertion of a completed experiment**, not a request to schedule it. It must be preserved as such. Therefore any broad statement "Asolaria has never run a physical photon-memory experiment" exceeds what the currently inspected public source set establishes and should not be repeated without checking the full historical records.

The following narrower statement is supported: **In the specifically reviewed October Round6/7/8 GitHub Actions outputs and the August README records so far inspected, no independent, instrument-calibrated raw optical write/dark-retention/read dataset has been identified.** That limited finding does NOT imply that the operator never conducted a measurement elsewhere or that unlinked laboratory/device records are nonexistent.

### Evidence status matrix

| Distinct statement | Status | Basis |
| --- | --- | --- |
| Asolaria digital jobs actually ran on real powered physical cloud machines and stored/retrieved real bytes | VERIFIED | Merged physical-hardware record/PR #91 and hosted CI |
| Operator reports a historical physical photon-memory measurement was performed | REPORTED_COMPLETED | Operator assertion, 2026-10-15 |
| Original August Colour QR source describes RGB image-plane byte readback and a cropped-screen-image recovery | DOCUMENTED_DIGITAL_IMAGE_READBACK | Original pinned Aug 6 source |
| Historical RAINBOR proposes a light hard-drive/multi-path optical memory stack | DESIGN_RECORDED | Aug 8 README explicitly labels this design conjecture |
| LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT reports a repeated local shadow-key/play-freeze observation before a light-arrival gate | REPORTED_LOCAL_OBSERVATION | Separate original README; numeric event times, uncertainties and external witness explicitly unsealed |
| Instrument calibration, actual illumination wavelength, light source, detector raw readings, retention timestamps, shutter states, physical memory medium, independent witness for the claimed photon-memory run | NOT_YET_LINKED_IN_REVIEWED_RECORDS | Current GitHub-source search only; not a claim the records do not exist |
| Original lightbank optical memory claim independently established by the October software-only photon counter/phonon models | NOT_ESTABLISHED_BY_THOSE_TESTS | Explicit model semantics from PRs #94, #95, #102, #106 |

## Additional historical archive checked

- [LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT README](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT/blob/main/README.md), observed Git blob `6b377b52b630ef18684754d469187ed6997efd90`. Public event ordering is a reported local observation, not raw calibrated photon memory readback.
- [lightDOORwsMs README](https://github.com/JesseBrown1980/lightDOORwsMs/blob/main/README.md), observed Git blob `07aa9b4433a6cccbc3e0a52d90686ab8d4484e50`. Describes working device-to-device byte transport and explicitly notes camera-based QR introduction remained incomplete there, distinguishing browser/USB network transport from independent photons-through-camera measurement.
- [And-we-harnessed-the-light-together-through-a-neural-network](https://github.com/JesseBrown1980/And-we-harnessed-the-light-together-through-a-neural-network) and [And-we-used-our-light-cellphone-devices-and-converted--1-3rds](https://github.com/JesseBrown1980/And-we-used-our-light-cellphone-devices-and-converted--1-3rds) were identified as potentially relevant repositories in owner catalog. README retrieval returned 404; their contents/measurements have not been inspected here. Do not treat 404 on README as nonexistence of the repositories or their data.

## Seat 1 classification, pending primary evidence

Use **`OPERATOR_REPORTED_PHYSICAL_PHOTON_MEMORY_RUN_COMPLETED__CAPTURE_AWAITING_CORRELATION`** when referring to the claimed historical run.

Avoid **`NEVER_RUN`**, **`EXPERIMENT_DOES_NOT_EXIST`** or **`PHYSICAL_PHOTON_MEMORY_PASS`** on the present record. Existing historical CI classifications (software-only for each named GitHub Actions run) are unaffected and remain valid.

### Artifact reconciliation, not a demand to repeat the experiment

Locate the already-existing run ID/commit or dataset, device/medium, acquisition path and recorded timestamps, source of light, sensor/wavelength, retained memory after the write illumination, electrical state/control, raw detector/screen-camera data, and original SHA or signature. When found, independently examine those files and their provenance, then issue an append-only receipt with an appropriate scoped verdict. In particular, an existing photo/video of an optically encoded readback may establish photon-mediated transport while persistent *optical-state* storage requires evidence for the carrier during retention.

**Do not overwrite any historical stone/PR or trigger physical experiments automatically.**

## Coordinator handoff

Cross-reference [Seat1 August reconciliation PR #103](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/103), [coordinator #55](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/55), [Seat4 physical intake PR #94](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/94), and [distinct release issue #10](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/10). Preserve existing computational conclusions but correct historical chronology.
