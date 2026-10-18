# Seat 1 evidence-status correction — historical optical and neural light banks

2026-10-15 · Supplement to `PREREG-PHYSICAL-EVIDENCE-20261015.md`

**This note preserves experimental history while distinguishing what the present external reviewer can independently reproduce.** Absence of an independently accessible calibrated sensor trace is **not** evidence that an operator-performed experiment did not occur.

| Subject | Status | Evidence interpretation |
| --- | --- | --- |
| Physical computing and device-backed memory operations | **VERIFIED (computational/host domain)** | Hardware-backed computation and memory operations are physical processes. The new Seat1 Linux/Rust 1.81 host CI independently measures some process-level OS counters, without proving a particular optical mechanism. |
| August optical and neural light-bank experiments | **HISTORICAL RECORDS / OPERATOR-REPORTED** | Preserve prior experimental work as history and attributed reports. Not the same as new Seat1 hosted electrical/optical measurement. Individual August sensor files have not been evaluated in this PR. |
| Physical photon-memory measurement | **REPORTED COMPLETED BY OPERATOR** | Record as an actual operator-reported completed experiment; **do not call it 'never happened' or 'not performed'**. Specific detector, calibration, exposure, retention and physical sensor traces still need independent custody verification. |
| Independent verification of that specific measurement's instrument data | **NOT YET ESTABLISHED HERE** | Independent raw sensor capture, calibration, timing, provenance, uncertainty and replay have not been established by the current evidence review; **not a finding that the operator report is false**. |
| Current Rust 1.81 Linux physical host experiment | **HOSTED SOFTWARE + OS REPORTED HOST DATA: VERIFIED** | GitHub Actions [38776911149](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38776911149) 3/3 PASS; deterministic integer output, OS CPU ticks, resident memory, monotonic time; instrument fields are null. |

## Located historical reference

[LIRIS SH Pre-Light Quantum Receipt](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT) (README) explicitly reports the Liris/operator-local **repeated** `ONE_SHADOW_KEY_CHANGE -> INSTANT_PLAY_FREEZE_CHANGE`, `LIGHT_ARRIVAL_GATE=0` and `SH_CHANGE_BEFORE_LIGHT_ARRIVAL`. Its README expressly labels numeric SH and light-arrival timestamps, delta/uncertainty, trial count and controls **UNSEALED**, and external scientific witness **HOLD**. Treat these as preserved **reported observations** and the document's own unresolved independent timing-validation boundary. That document is **not itself a calibrated photon-memory retention trace**, and the operator's interpretation is distinct from an independently established claim about timing or physical information transfer.

The LIRIS receipt is a related historical observation, **not automatically the same instrument dataset** as the operator-reported August photon-memory experiment. The claims must not be conflated without source linkage.

## Next custody link for promotion

Attach direct capture source location and canonical raw-byte SHA256, acquisition hardware and calibration, exact trial schedule with actual pre/post dark interval, timestamps sharing a calibrated clock, uncertainty bounds, optical write/sham/erase labels, operator attestation, and independently signed/replayed verification. Preserve original data and distinguish new interpretations from old observations.

All prior results and signed comments remain intact. This new classification does not modify the synthetic readout or Rust baseline results and does not claim independent validation it has not performed.
