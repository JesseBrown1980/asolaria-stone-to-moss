# Seat 4 Round 8 — Real photon/phonon/electronic light-bank handoff (NOT RUN)

This is a physical apparatus experiment proposal grounded in the [prospective protocol](PREREG-FACTORIAL-LIGHT-VIBRATION-MEMORY-20261015.md). **None of the current GitHub computations contains measured optical photon or acoustic phonon observations.** The 217,728-row factorial trace is a deliberately synthetic software preflight.

## Separate three claims

1. **Optical/electromechanical coupling:** physical light, sound/vibration and charge may exchange energy in many materials. This is the mechanism-level question behind Seat1's proposed experiment.
2. **Light-dependent data retention:** independently detect previously blinded source data *after* a controlled WRITE→perturb→isolation/retention→READ sequence. Merely producing a sensor signal when light is on does not establish retention.
3. **Photonic (rather than electronic/thermal/mechanical) memory:** after (2), independent mechanism-specific controls must show *which physical degree of freedom* retains the bit. A successful light-triggered electronic flip-flop is optically controlled **electronic** memory, not necessarily photons persisting in the storage medium. A neural/biological claim requires separate live-cell electrophysiology.

## Apparatus and operator duties

**Independently calibrated hardware needed:** addressable optical storage specimen, controllable seven measured spectral lines or passbands (report center nm, bandwidth, power/area, uncertainty), shutter/optical isolation and stray-light meter, source write/read electronics with verified constant voltage/clock, coherent acoustic actuator with measured acceleration/frequency/strain (actual phonons are lattice quantized modes, not simply any electrical audio stream), stabilized temperature chamber with actual logged temperature probe near the medium, independent detector and spectrometer/camera RAW data, and an independent blinded custodian.

Source bit assignment uses the 81 original pinned memories and 567 logical band-site labels but must be **randomized for real experimental measurement** by an independent referee. Do not reuse the public fixed SHA fixture stream from the software preflight as a security challenge. Distinct 27 ternary addresses are metadata, not 27 measured spectral lines.

**Order on every blinded trial:**

1. Precommit independently chosen random source bit, ordered site/band ID, real sampled wavelength and arm permutation; public timestamp/SHA but concealed values to instrument reader.
2. Calibrate wavelength, optical irradiance, acoustic vibration and detector response, dark counts, read threshold and exposure. Record independent raw calibration files with SHA256 and signatures.
3. Write actual bit to optical medium under fixed conditions, seal source optics; *then* randomly deliver controlled perturbation L∈{off,on} and A∈{off,on}. Use sham actuators that produce comparable electrical power/heat without light/acoustic excitation.
4. Close both light and acoustic stimuli. Enforce genuine measured delay of 1, 10 or 60 seconds under shutter-closed or independently accounted optical isolation. Record measured temperatures, clocks, voltage and accelerometer/optical power during WAIT. The perturbing illumination is distinct from optical READ probing.
5. Perform a blind fixed-gain independent detector read, **without providing source bit to the reader**. Seal the unedited timestamped raw frames/waveform and digital detector-read bit before target and arm labels are disclosed. Use independent operator signatures and fresh nonce/sequence ledger.
6. Randomize instrument port permutation without changing source labelling, remove/disable one wavelength channel, inject stale read receipts, swap detector and control optical path. Require ordered identity and exact source auth, not just a valid intensity class or simulated neural spike fingerprint.
7. Repeat sham-medium/dummy-device, heating-matched light-off and vibration-off, electronic/RAM isolation controls, afterglow-only substrate and a blind blank run with precommitted ground truth.
8. Unlock treatment/ground-truth labels **only after all raw acquisitions have been externally sealed**; compute unaltered factorial estimates and predeclared familywise statistical significance with confidence intervals.

**Critical confounds to exclude:** laser/LED afterglow, camera sensor persistence, electro-optic charging, heating, piezoelectric voltage from vibration, electromagnetic pickup from speaker/piezo driver, detector threshold/gain drift, mechanical motion of the optical path, light leakage, imperfect shuttering, standby RAM and source identification from the readout message.

## Sensor file contract for a later *physical* referee

Create raw evidence outside the synthetic Round8 artifact prefix; never write real data into `r8-synthetic-factorial.jsonl`. The hardware intake should receive:

- `commitment.json`: blinded target sequence digest, immutable original source SHA, experiment design version, full preregistration SHA, external challenge nonce and arm allocation hash; challenge issuer custody.
- `calibration/`: seven measured wavelengths + bandwidths, optical power meter scans, acoustic shaker acceleration-frequency trace, temperature sensor, dark counts, detector gain, power rail readings and signed independent calibration witness.
- `raw/`: full unedited detector RAW/waveform count files, timestamps, shutter state, vibration power and measured temperature/voltage traces, and per-file SHA256.
- `readouts.csv`: `trial_id,site,band,ordered_id,delay_measured_ms,light_arm,acoustic_arm,rep,independent_readout_bit,raw_detector_id,raw_sha256,temperature_mK,supply_uV,measured_optical_power_nW,measured_acceleration_mg,source_challenge_id,signature_ref`; every row references a distinct real source acquisition. **Ground truth target bits must remain blinded until after raw-readout sealing**.
- `unblind.json`: signed source bits, source precommit reveal and external source/spectrometer/custody signatures, only after sealing all readouts.

Do not promote any physical verdict from field presence alone. Source signatures by the same self-controlled party and self-reported string `physical: true` are not trusted external custody. An independent referee must validate key ownership, actual device signals, correct elapsed delays, raw file identity, randomized assignment, conditional treatment exposure and source readback, with correction for per-band/delay multiplicity.

## Reporting labels

- `DIGITAL_FACTORIAL_PREFLIGHT_PASS`: expected statistical software algebra reproduces on GitHub hosts.
- `PHYSICAL_CAPTURE_NOT_AVAILABLE`: cannot estimate real effects from the internet or GitHub CI.
- `PHYSICAL_INTERACTION_CANDIDATE`: genuine blinded optical/acoustic interventions alter actual verified memory reads with controls and raw provenance.
- `PHYSICAL_MEMORY_MECHANISM_UNIDENTIFIED`: treatment association survives, but can't separate photon/phonon storage from heating, electronic state and optical afterglow.
- `PHOTONIC_STORAGE_CANDIDATE`: requires mechanism-specific real physical evidence beyond a simple factorial treatment contrast.
- `BIOLOGICAL_NEURAL_HOLD`: requires actual electrophysiological and neural biological characterization.

**Seat4 present custody status:** no independently signed real optical/phonon detector files, no raw instrument signals, no experimental medium controlled through this connector, and no biological recordings. The factorized synthetic bank is real computational memory; physics-specific mechanism remains unverified.
