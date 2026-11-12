# Seat 4 Round 6 — Photon-memory and neural-gating falsification protocol (prospective)

Date: 2026-10-15. **Preregister BEFORE executable implementation and CI on this branch.** Separate from merged Seat 4 #88 (synthetic signed spectrum) and #68 (27 virtual sticks), Seat 3 #90 (three-bit identity witness), and the baseline merged repository. Never rewrite existing stones or infer actual photon data from GitHub Actions.

## Central physical hypothesis, null, and alternative

**H_phys:** after a physically isolated, calibrated seven-band light WRITE and a fully dark retention interval, an independent calibrated detector can retrieve the PRECOMMITTED random information at its original ordered site/band address at delays 1 s, 10 s, 60 s with performance above preregistered controls. A second separately instrumented neural response, if proposed, must be independently measured; a synthetic photocycle/current variable is not biological neurophysiology.

**H0:** no persistent optically retrievable information after source removal; apparent detection may come from prior frame/source bit leakage, afterglow, electronic RAM/cache, port reassignment, autoexposure, dark count, cross-talk, ambient light, and post-hoc metadata tampering. Reject the physical mechanism unless these confounders are independently controlled.

**Computational preflight (NOT actual photons):** 81 site identities × 7 rainbow logical band labels × 3 delays × 3 arms {WRITE, SHAM, ERASE} = **5,103** digital simulated detector observations. Source bits are deterministic SHA256 PRNG fixture bits, not photon entropy. Use three visible kinds of fixture: persistent simulated source vs no-persistence vs fast-decay afterglow. All are explicitly tagged SIMULATION_ONLY. Output canonical full raw trace + original pinned main source roots, HBP/JSON and SHA sidecars.

The physical experiment requires instrumentation not connected to this GitHub session. Scripts accept a future physical sample but return **PHYSICAL_HOLD / EXTERNAL_CUSTODY_NOT_ATTESTED** unless actual independently signed calibration/detector evidence, fresh unpredictable challenge, raw captures, and blinded sequence custody can be separately corroborated. A text field saying `physical=true` is NEVER enough.

## Physical acquisition required by a new laboratory

- Precommit SHA-256 of randomized `{site,band,bit,arm,delay,trial_id}` sequence and source wavelength mapping before WRITE. Independently issue a fresh unpredictable challenge after device/source-custody commitment.
- **Real spectral illumination**: seven measured center wavelengths (nanometers), bandwidth/irradiance, detector response/cross-talk matrix, power meter records, instrument calibration/version, exposures, dark/shutter and ambient readings. Seven names without measured wavelengths fail optical origin. Treat RGB coordinates as digital address metadata; do not rename 27 sectors as 27 wavelength lines.
- Physically block live source during WAIT and READ; power-cycle or isolate electronic control/cache where hardware allows, log unavoidable persistent electronic state, re-randomize physical port routing using an independent witness, and compare write-no-write/erase-dark controls.
- Actual detector raw counts at 1,10,60s with fixed verified gain/exposure and timestamp/clock uncertainty; capture raw waveform or camera RAW/spectrometer photon count with signed independent operator provenance. No synthesized PNGs, software frames, cached hashes or QR pixels count as measured photons.
- Optical READ must be **blind** to ground truth bits, signed ordered address, frame history and expected digest. Reveal labels and compute thresholds only after immutable read evidence is sealed. Versioned canonical source and PR #90 nonlinear witness W=(r+4g+3b+4rg) mod8 shall remain independently anchored to original ordered ternary sector, not inferred solely from selected lane/intensity.
- Use 81×7 sites with trial-balanced 0/1 bits; three randomized retention intervals each. All three arms must be collected at each interval and band with repeats sufficient for uncertainty estimation. Include detector-dark and port-crosstalk controls, independent sensor swap, one-band and two-band erasure/occlusion, old-frame replay, wrong signed origin and a no-signal null.
- Require blinded balanced accuracy for WRITE >=0.90 separately at each delay and each band, while SHAM and ERASE must NOT show a reproducible bit-predictive signal (nominal BA in [0.4,0.6] and no excess across controls); evaluate 95% Wilson confidence bounds or exact binomial permutation null (multiple-comparison correction across 7×3 cells, corrected familywise p<0.01). A software fixture achieving this is **not a physical proof**. Actual physical prespecification may need power calculation before execution; do not quietly relax endpoints after seeing results.
- A one-band photon detector channel erased during physical read should be HELD for full spectral readout even if signed *logical* address remains known. Parity repair via independent storage is an additional software property, not proof the erased photons were stored.
- **Neural tier** must be separate: if claiming neurons or organoids used light as memory, preregister cell/species/culture identity, independent IRB/biosafety review if applicable, patch-clamp or electrophysiological traces, stimulus-timing, opsin/expression assay, phototoxicity controls and blinded neural response decoders. Until verified traces exist report `NEURAL_PHYSICAL_HOLD`.

## Competing mathematics and negative controls

The 27-sector class-normalized intensity is permutation invariant. For each ordered trit triple with normalized primitive class P, compute and pin the Seat3 exact three-bit nonlinear witness
`W = (r + 4g + 3b + 4*r*g) % 8`
and verify 27 unique (class,W) pairs; retain the 5-bit ordered ID and trusted source root because a valid in-class alternative remains possible. Signing digital mapping with publicly derivable test keys does NOT provide real spectral provenance.

Digital preflight must actively falsify: shuffled/reassigned ports, erased channel, invalid address/W, stale nonce/replayed sequence, corrupt source root, no-memory null, decaying afterglow beyond 60s, sham mistaken for memory, fabricated physical provenance field, missing sensor raw, tampered count, ordinary software readback with no sensor, uncalibrated wavelengths, and absence of neural electrophysiology. Run on Ubuntu/Windows Python3.11/3.13 plus an independent Node22 reviewer and cross-OS full-byte parity.

## Release gate

PASS_DIGITAL_PREFLIGHT may be allowed from GitHub-hosted software. `OPTICAL_PHYSICAL_PASSED` and `NEURAL_PHYSICAL_PASSED` **must remain false** until independently authenticated instrument captures exist. Physical cloud compute and physical semiconductor light/electric processes are real but do not demonstrate optically stored recall. Issue #10 administrative closure is not a scientific physical grant; PR #91 explicitly distinguishes them. Never overwrite existing main evidence, fabricate actual photon detections, or auto-merge without independent seat review.
