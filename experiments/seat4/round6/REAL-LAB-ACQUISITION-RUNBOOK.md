# Seat 4 Round 6 — Physical Light-Bank Acquisition Runbook (not yet performed)

## Objective and division of labor

Digital Round6 simulation is an *engineering preflight*. The real experiment requires access to an optically responsive **storage medium**, an instrument-controlled multi-band illuminator, optical isolation/shutter, external spectrometer/CCD/photon-counter instrument, and an independently operated randomization/custody referee. Existing GPU/SSD/QR records do not count as optical memory simply because electronics or photons are involved.

The detector must observe **an actual optical signal after a WRITE and a dark retention interval** and recover a blinded random input through independently authenticated site/band assignments. For a neural memory claim, also record actual neuron/organoid electrophysiology, not just a simulated photocycle or artificial-neural-network state.

### Freeze before seeing outcomes

1. Referee creates a fresh unpredictable nonce and randomized 81 sites × 7 calibrated measured bands × 3 delays (1,10,60s) × {WRITE,SHAM,ERASE}, balanced target bit assignment and trial order. Publish only SHA256 commitment and signer identity before exposing light; **do not publish bit patterns to readout operator**.
2. Instrument operator reports instrument model, firmware, integration/exposure, dark-frame baseline, measured wavelength centers in nanometers, passband widths, absolute optical irradiance (if calibrated), cross-talk response matrix, and calibration asset hash. A label `violet` without measured wavelength is metadata, not spectroscopy.
3. Prepare light-writing medium and WRITE, SHAM/no-write, ERASE/reset controls using comparable timing and temperature. Close light shutter during retention, prevent camera view of live source, and isolate electrical frame-cache/QR payload when possible.
4. Read with independently operated sensor after each delay. Seal raw unedited detector exports and timestamps **before** target labels are revealed; save separate independent witness signatures/public keys and audit who held source and detector. Exchange source/reader ports in a controlled blinded subset to test channel ownership. Do not use fabricated digital RAW or image files as real instruments.
5. Referee independently links raw detector channel IDs to calibrated seven-band map, verifies proper order `sector=9r+3g+b` and nonlinear identity witness `W=(r+4g+3b+4rg) mod8`, checks source nonce and sequence, and reports fail-closed if any signed optical channel is erased/missing or replayed.
6. Decode with threshold frozen during calibration. Compare each of 21 band×delay strata WRITE against SHAM and ERASE using label-blind predictions, balanced accuracy, confidence intervals, and preregistered corrected hypothesis tests; report per-band/interval actual sample sizes. Positive correlation with target alone does not establish **what physical carrier stored** the bit—specifically rule out afterglow, charge, thermal state, sensor persistence and conventional digital RAM.
7. For claimed neural persistence, require approved biological preparation, light-sensitive target characterization, actual electrophysiology readouts, no-cell/no-opsin and sham responses, blinding and temporal controls. Without this, neural tier remains HOLD regardless of optical result.

### Accepted file shapes for instrument intake

Put the following **real externally obtained** files in a new untracked local folder `capture/` (never replace archived synthetic receipts):

- `challenge.json`, with `schema="ASOLARIA-R6-PHYSICAL-CHALLENGE-V1"`, `fresh_external_nonce`, `source_precommit_sha256`, `raw_capture_sha256` and separately retained challenge/public-key provenance.
- `calibration.json`, with `schema="ASOLARIA-R6-PHYSICAL-SPECTROMETER-CALIBRATION-V1"`, `seven_wavelengths_nm` (7 distinct measured numbers), `spectrometer_model`, `detector_calibration_sha256`, plus actual calibration attachments.
- `custody.json` with non-empty `source_custodian`, `detector_custodian` and `external_witness`, linked externally signed witness statements. These strings alone do not establish authenticity.
- `detector.csv` has a header containing `arm,band,site,delay_s,detector_counts,dark_counts,integration_ms,raw_capture_id,source_sequence,spectrometer_channel`. Provide full 5,103 addressed samples if following this design. Actual raw instrument logs, shutter status and timestamp uncertainties must also be retained for peer review.

Then, on the independently controlled acquisition host:

```bash
python experiments/seat4/round6/physical_capture_gate.py --capture capture/ capture-verdict/
```

The intake validates field shape, count, source SHA check, channel completeness, non-negative counts and declared wavelength existence. It **deliberately returns PHYSICAL_HOLD** even for well-formed files, because self-reported text and checksums alone do not certify actual instruments, independently attested custody, precommitted blinding, or photons persisting in the medium. Independent peer review and authenticated raw instrument analysis are necessary to revise the verdict. Do not alter the tool to simply accept a `physical=true` field.

### Future falsification interpretation

- `DIGITAL_PREFLIGHT_PASS`: software logic, frozen source SHA, source/witness arithmetic, null and afterglow controls work on synthetic data only.
- `PHYSICAL_HOLD`: no externally authenticated complete calibrated READ evidence available, or actual real capture not yet independently adjudicated.
- `PHYSICAL_REJECT` (future referee): measured bits not retained at 60s, no improvement over sham/erase, missing a calibrated band, changed raw instrument SHA, or corroborated side-channel source leakage.
- `PHYSICAL_CANDIDATE` (future lab): blinded, authenticated measured recall meets preregistered acceptance with controls; requires further attribution experiments to establish photons versus conventional physical/electronic retention.
- `NEURAL_PHYSICAL_HOLD`: no real patch-clamp or independently calibrated neural measurements with blinded optogenetic controls.

No human biological study, physical spectrometer reading, neural recording, or real optical write–wait–read has been performed by this GitHub/ChatGPT run.
