# Seat 3 / Seat 1 cross-examination — photon–phonon–electronic memory coupling

**2026-10-15. Frozen executable simulation protocol (not a physical experiment).** Independent Seat 1 proposed separately testing optical-photon illumination, mechanical/phonon excitation and electronic controls. This extension belongs to Seat 3 draft PR #95 and supplements Stage A/B noise + crosstalk simulations and Seat 4 draft PR #94's write–dark-retain–read toy. No inference that the existing electronic light bank is physically optical or phononic memory is justified from software alone.

## Distinguish hypotheses and intervention factors

The desired **future physical** intervention design is three binary randomized, individually independently logged factors:

- **O: real optical illumination ON/OFF**. Calibrated spectral irradiance, wavelength/linewidth, illuminated medium and source shutter, separate optical probe/detector; sham lamp controls for heat/electrical pickup.
- **A: real mechanical/acoustic excitation ON/OFF**. Calibrated mechanical displacement/vibration spectrum, transducer, mechanically matched sham, verified isolation between acoustic driver and optical/electronic readout.
- **E: electronic memory stimulus/state ON/OFF**. Identical supply, bias, CPU/SSD/memory controller timing where appropriate; electronic-only and power-cycle tests. Keep E **fixed within each O×A contrast**, then replicate in the other E condition to detect dependence.

Factorial treatments: all 8 combinations of `(O,A,E)∈{0,1}³`, randomized and blinded. For every condition use **WRITE / SHAM / ERASE** with actual shuttered dark retention delays **1, 10, 60 s** (measured elapsed, not labels), 81 independently targeted original memory site IDs × seven **calibrated measured wavelength bands** (not labels only). For physical experiments record independent calibrated detector raw traces, simultaneously measured voltage/current/electromagnetic pickup, temperature and acoustic amplitude. Randomize order and apply trial-level blinding; source-custodian and detector-custodian should independently sign the precommitted labels and raw observations. Control temperature with matched heater/sham illumination and/or active thermal clamping; compare grounded Faraday-shielded/microphonic electronics and independent electrically decoupled optical sensor; explicitly test no-opson/no-cell if biological neural effects are claimed. Distinguish optical write from electronic storage of a light-triggered bit, and prevent afterglow sensor persistence being miscalled stored light.

**Causal estimand** at fixed E and site/band/delay:
`Delta_OA(E) = mean[Y|O=1,A=1,E] - mean[Y|1,0,E] - mean[Y|0,1,E] + mean[Y|0,0,E]`.
This is a *statistical interaction*, not proof photons were stored: heating, mechanical electrical pickup, biased detector electronics and sample handling can create interaction-like artifacts. Repeat with thermal clamp and separate optical readout, and report confidence intervals and all 21 band×delay results (plus correction/multiplicity protocol) rather than only the best cell. Repeated measures are clustered by site/device and pseudoreplication must not be presented as independent physical subjects.

## Frozen *toy* falsifier, executable now

Two independently authored, standard-library **Python and Node22** implementations will enumerate **81×7×3×8 = 13,608** simulated numerical outcomes for EACH of five distinct disclosure-labeled models:

1. `NULL`: sensor count baseline only, no factor causal effect, `Delta_OA(E)=0`.
2. `OPTICAL_MAIN_ONLY`: optical `+20O`, no actual O×A coupling.
3. `ACOUSTIC_MAIN_ONLY`: mechanical `+20A`, no O×A coupling.
4. `DIRECT_COUPLING_TOY`: `+10O + 6A + 30OA` at 1s and 10s; persistent `+30OA` at nominal 60s, with E included as additional fixed `+4E`. This model's coupled signal is **programmed**, not measured.
5. `THERMAL_ELECTRONIC_MIMIC`: apparent `+10O + 6A + 30OA` on a synthetic raw **electronic** sensor, but **zero** OA interaction on a separately modeled optical sensor under thermal clamp; demonstrates that an interaction on one electronic channel does not establish optical memory or photon–phonon coupling.

Every model shares an arm-independent deterministic common per-site/band/delay noise `SHA256("ASOLARIA-OAE-NOISE-V1|" + ASCII(model,site,band,delay)) first_octet % 7 -3` across the 8 interventions. This deliberate common-mode simulation design causes the paired exact factorial `Delta` to cancel noise algebraically; it is a *unit-test oracle*, not a realistic physical noise model or statistical power/false-discovery estimate. All model parameters listed above are synthetic and have no calibration. At nominal 60s, `FAST_AFTERGLOW` alternative is optionally modeled as an extra sixth model where `+30OA` is programmed only at delays 1 and 10 and zero at 60; it must not be falsely called long-term memory.

The producer must output **both** `electronic_readout` and `independent_optical_readout`, and explicit `temperature_surrogate`. In the DIRECT_COUPLING toy only, both sensors track programmed O×A interaction; in THERMAL_ELECTRONIC_MIMIC, electronic readout tracks apparent effect while independently controlled optical readout has zero interaction. For NULL/MAIN_ONLY, both have no OA interaction. Pin numeric expected factorial contrasts exactly and classify physical evidence **NOT_RUN**.

Source-bank constraints: read actual archived PR80 81-source and 567-band/site source roots, do not invent new persistent memories, verify all original leaf checksums and full 13,608 rows per model; original address representation stays independent of model count. Compare full byte-exact Python/Node receipts, third read-only auditor, active mutation rejection, Ubuntu/Windows Python3.11/3.13 and Node22, fifth byte-parity. Separate new HBP/JSON and a new append-only receipt, preserve earlier PR95 A/B SHA and upstream Seat4 PR94 unchanged. No network hardware drivers or instruments are attached to hosted GitHub Actions, so `REAL_PHOTON_PHONON_ELECTRONIC_COUPLING=NOT_RUN`.

**Promotion to physical coupling requires actual randomized interventions, raw detector + acoustic + electrical + thermal traces, shutter dark retention, independent calibration/witness signatures and identification of a persistent physical carrier.** Positive interaction in programmed simulation is proof the *test* detects a programmed interaction and nothing more. Physical source-authenticated spectrogram, real mechanical vibrational signal and physical memory readout are distinct from their labels.
