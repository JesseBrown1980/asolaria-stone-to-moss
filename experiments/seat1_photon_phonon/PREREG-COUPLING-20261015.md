# Seat 1 — Photon–Phonon–Electron Memory Coupling: Frozen Track A Protocol

**Date:** 2026-10-15. **Issue:** [#100](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/100). **Mode:** computational phenomenological model physically executed on cloud computers. **Protocol frozen before writing the new coupled producer or independent verifier.** The source branch starts at the unmodified neural-lightbank PR #97 head `6d8a761c0292113a75e3417eec9ef57152738013`.

## Source of truth and independent outputs

Original 81 synthetic QR memories, retained 567 Rainbow7 full-byte bank rows totaling 184,815 bytes; exact bank SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`; 70,043-byte base index SHA256 `6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee`; full original QR source SHA256 `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`. A separate upstream photon/electron digital model, [PR #93](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/93), was verified cross-platform but does **not** supply physical photonic detector readings.

This round generates its own full payload readback, not just a synthetic row number or mock aggregate: **every byte** of each 567 retained row, for **12 frozen arms**, including 7 symbolic rainbow bands and 81 original sources. Multiple 27-sector aliases are references, not 15,309 distinct stored payloads. Independent Python and Node implementations and third-party full-byte referee on Ubuntu and Windows must agree on exact HBP, JSON, original source and sha256 sidecars.

## Phenomenological transfer law (assumptions, not a measured material law)

Source bit `b` sends `N × b` *modeled photons* into a hypothetical optical state. A single replica generates `E ~ Binomial(N*b, p)` *modeled photoelectrons*. A 0 source bit generates 0 signal electrons, but a modeled independent dark electron is possible at fixed probability `d`. The electronic threshold recovers 1 iff `E + dark > 0`; otherwise 0. No biological cells, photon counters or physical optomechanical transducers are connected.

Define **assumed** detector probabilities as exact fractions `p = p100 / 100` or `p = 32768 / 100000`, depending on case. The toy resonant mechanical coupling law at immediate read is `p100 = 32 + 12*cos(phase)` when a unit-strength resonant phonon drive is present; phase=0 -> p=0.44, phase=π -> p=0.20, off-resonant -> p=0.32. A thermal sham p=0.36 is deliberately a *confounder* rather than genuine mechanical coupling. At a modeled 3-tick held state, p=0.16 without drive and p=0.22 for phase=0. Those fixed toy probabilities are not calibrated detector efficiencies or physical resonator laws.

12 frozen test arms (respect exact order):

| arm | N photons per source-one | detector p | dark-electron probability | modeled state / intervention |
|---|---:|---:|---:|---|
| `reference_bright` | 24 | 0.64 | 0 | bright immediate software positive control |
| `baseline_t0` | 8 | 0.32 | 0 | optical input, no acoustic coupling |
| `resonant_phase0` | 8 | 0.44 | 0 | constructive resonant mechanical drive |
| `resonant_phase180` | 8 | 0.20 | 0 | destructive / phase-inverted drive |
| `off_resonance` | 8 | 0.32 | 0 | acoustic drive outside designated resonance |
| `thermal_sham` | 8 | 0.36 | 0 | nuisance heating can mimic improvement |
| `detector_dark_noise` | 8 | 0.32 | 0.001 | electronic detector false pulses |
| `optical_dark` | 0 | 0 | 0 | no light, no phonon drive |
| `acoustic_only` | 0 | 0 | 0 | mechanical drive but no injected photons |
| `held_t3` | 8 | 0.16 | 0 | 3-tick *modeled* retained optical state |
| `held_t3_resonant` | 8 | 0.22 | 0 | 3-tick state and constructive phonon drive |
| `held_t3_erased` | 0 | 0 | 0 | source write absent/erased: no retained signal |

Photon budget is `N × (#original one-bits)`; model photoelectron budget must be ≤ emitted photons, one modeled electronic decision per source bit. No actual optical time scale or optical-memory lifetime is inferred. Wavelength labels 650/610/580/530/470/440/405 nm are symbolic, not calibrated seven-band sources. For reference, per-photon theoretical free-space energy may be computed from `hc/lambda` but is **not observed**.

## Frozen randomness, testability and expected relationships

For each original source row and each bit position use two independently salted **SHA256-seeded xorshift32** streams: `ASOLARIA-COUPLING-A|banksha|ordinal|signal` and `ASOLARIA-COUPLING-A|banksha|ordinal|dark`. Each bit consumes one 32-bit signal draw and one dark draw, whether source bit is 1 or 0. For signal b=1 use exact integer binomial inverse-CDF comparison against the signal draw, with floor scaling to 2^32; for b=0 signal count=0. Dark event if dark U32 < floor(2^32*d). A common seed **across arms** holds exogenous randomness fixed, allowing per-bit monotonic and byte-identical negative comparisons. This is a deterministic pseudo-random software test, **not quantum randomness or a measurement**.

Predeclared accept/hold criteria:

1. All 12 arms decode **184,815 original source bytes / 567 rows**, forming **6,804 signed-by-source-root simulated digital frame records**. All source hashes, readback bytes, modeled electron totals, modeled phonon treatment, LIF fingerprint authorization and byte errors must be independently recomputed, not accepted from self-reported summary totals.
2. `reference_bright` should have dramatically lower error rate than `baseline_t0`; `resonant_phase0` must reduce bit errors relative to `baseline_t0`, and `resonant_phase180` must worsen them; `off_resonance` must be byte-identical to `baseline_t0` under common randomness.
3. `optical_dark`, `acoustic_only`, `held_t3_erased` yield all-zero signal and identical readback bytes. Acoustic-only changes no photoelectrons, **even though it may be assigned a positive virtual phonon drive**.
4. `held_t3` has more errors than `baseline_t0`. `held_t3_resonant` improves on `held_t3`. These are software-assumed *retention* properties, NOT experimental proof of physical write/hold/read storage.
5. The `thermal_sham` should **also** appear to improve recovery; its false causal implication is recorded explicitly: an observed improvement alone cannot distinguish phonon physics from heating. `detector_dark_noise` should add false positives.
6. Electron-MCP envelope `tools/call electron.capture` and neuron `tools/call neuron.gate` are **JSON-RPC/MCP-style modeled messages**, not live MCP tool transports or electron-controlled physical actuators. Strict source authorization `original row SHA match AND trained LIF fingerprint match`, never fingerprint alone.
7. Controls actually mutate source row bytes, band/wavelength, acoustic condition, nonce, sector, detector count, output hash, message tool, response authorization, partial violet-band deletion and coherent forged self-contained receipt. Fail closed against **independent original byte roots**. Merely attaching a matching untrusted hash must not count as external sensor custody.
8. Independently compute analytic expected errors `ones × (1-p)^N (1-d) + zeros × d` for each arm; compare observed fixed pseudo-outcomes with predeclared 6-sigma+2 finite-sample bound. This is model-consistency screening, not physical instrument calibration.
9. A positive *modeled* readback at t3 with prior source bytes available in software does NOT demonstrate retention of a physical optical state. Physical proof needs prepared medium, input removed, independently measured delayed readback and null controls.

## External measured Track B — not available to the GitHub-only seat

Require actual independently measured light source + acoustic transducer + known optical/optomechanical storage medium + detector, timestamped interventions, optical/dark/acoustic/EMI/thermal shams, calibration, input disconnected during hold, real digitized electrical readout, and blinded physical source custody. If no device is connected, report `MEASURED_PHOTON_PHONON_COUPLING=false`, `PHYSICAL_PHOTON_STORAGE=false`, `PHYSICAL_PHONON_SIGNAL_MEASURED=false`, `ACTUAL_PHOTOELECTRON_CURRENT_MEASURED=false`, `RUNS_ON_PHYSICAL_COMPUTE=true`.

**Do not merge automatically.** Preserve upstream PRs #93/#97, source stones and historical Windows failure. Share failures as appended receipts and explicitly request Seats 2/3/4 review.
