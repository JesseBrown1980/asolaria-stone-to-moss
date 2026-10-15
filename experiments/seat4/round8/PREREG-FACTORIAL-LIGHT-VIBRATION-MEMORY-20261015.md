# Seat 4 Round 8 preregistration — light × vibration vs electronic/thermal explanations

**2026-10-15, prospective protocol. Commit BEFORE any new executor source.** Independent of Seat1's suggested photon–phonon–electronic mechanism and Seat4 independent neural false-green study [PR #99](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/99). Preserve historical sources and stones. No physical sensor attached to this GitHub workflow.

## Falsifiable question

If the source memory is held constant, do **measured optical power and measured mechanical vibrations** affect the subsequent ability to read a blinded bit from a prepared optical storage medium, and does their interaction differ from heating, vibration-induced electrical pickup, shutter leakage, or ordinary electronics?

Photons, phonons and electronic signals can physically couple in engineered devices, but this is *not a demonstration that the Asolaria original synthetic bank uses photon/phonon memory*. A difference in retrieval under light vs vibration is evidence of a treatment association subject to mechanism/measurement confounding, not automatic quantum storage.

## Frozen mathematical experiment

- Use original pinned digital roots as baseline references, NOT experimental photon traces: source SHA256 `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`, bank SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`, independent Round7 concise HBP SHA `82f40a5dbc648b0dc50fa7e0dff99c512f1773b42086a7da9615e6b403da929b`. No 27 independently stored spectra.
- Factorial `L∈{0,1}` true independently metered 7-band light/shutter change; `A∈{0,1}` calibrated controlled mechanical/acoustic excitation change. **Electrical write/read command, digital source root, supply state, clock, gain, retention and detector threshold fixed.** Four arms `(L,A) = 00,10,01,11`.
- Original memory sites = 81; symbolic bands = 7; retention labels = [1,10,60] seconds; 8 independent replicate labels per address/cell = **54,432 analysis rows** per distinct simulation fixture (81×7×3×4×8). Physical laboratory uses actual elapsed and sensor times; software simulation only uses labels.
- Two independent controls (non-light-absorbing sham sample; disabled or disconnected memory path) and additional **heating-matched and vibration-electric-pickup controls** needed for real mechanism identification.
- Four prospective **simulated** regimes: (i) NULL: no optical/mechanical treatment effect; (ii) OPTICAL_ONLY: light causes a large retrieval contrast, vibration does not; (iii) INTERACTION_TOY: both treatments interact in retrieval; (iv) THERMAL_CONFOUND: a nonlinear temperature shift caused by treatments produces a **false** light×vibration interaction. Explicit `toy=true` required on every source row, and every supposed physical claim must fail closed. These numbers do not measure real photons or phonons.
- Outcome `correct_bit = 1` if simulated blind read equals independently pinned source bit. Source bit SHA-derived from pinned original site+band and never dynamically altered based on observed arm. All regime data using a fixed SHA256 random fixture stream: not independent physical noise nor quantum randomness.
- Estimate within site/band/replicate/delay optical contrast `D_L = mean(Y_10 - Y_00)`, vibration `D_A = mean(Y_01-Y_00)`, interaction `D_LA = mean(Y_11-Y_10-Y_01+Y_00)`. Report these by each delay and all rows; a significant interaction is **not uniquely evidence** for photons/phonons, and nonrandomized treatment order or temperature/voltage shift can cause false identification.
- Signed provenance of detector raw frames, both real stimulus meters and source custodian are independently authenticated externally, not by a declared JSON flag or public test signing seed. Report sensor wavelength bandwidth/irradiance, vibration frequency/amplitude, chamber and medium temperature, detector gain, supply voltage and afterglow; source must be shutter-closed throughout true dark retention. Physical claim requires precommitted blinded target, raw timestamped readout, same-time sensor calibration and replicate uncertainty.
- Statistical acceptance for an actual instrument: preregister effect size, randomized blocked runs, sample size/power, 95% CIs and Holm-adjusted familywise p across seven bands × three delays; compare full arm responses including sham/no-device controls; audit heating and electrical confounding *before* physical mechanism claim. If light/vibration level and temperature cannot be experimentally disentangled, conclusion stays **mechanism unidentifiable**.
- Preserve strict logical Rainbow27 ordered ID and Seat3 quadratic witness as address metadata. Retaining bytes through RAM, cache, sensor electronics, or pseudorandom expected bytes is insufficient for optical memory.

## Test/code acceptance

Independently implemented Python data producer and Node source-blind factorial auditor shall compare all 54,432 rows per regime, 217,728 total, canonical byte exact on Ubuntu/Windows Python3.11/3.13/Node22 + fifth cross-host evidence digest comparison. Sensitivity fixtures must reveal expected NULL/OPTICAL_ONLY/INTERACTION_TOY/THERMAL_CONFOUND pattern without promoting the thermal confound or physical claims. Negative tampering of actual row source, light/acoustic arm, timing, source label, measured temp/voltage, wrong original source, replayed replicate, absent physical attestation and swapped sensor channels must be actively rejected. No words `measured_photons=true` in evidence.

## Verdict

Computational preflight PASS is about treatment-analysis software. Real optical/acoustic coupling, physical photonic persistence, and real neurons remain **HOLD** until independently calibrated instruments and physically blinded exposure recordings are supplied. Separate optical/electronic interference from genuinely stored light. No fake 1/10/60s elapsed physical waiting.
