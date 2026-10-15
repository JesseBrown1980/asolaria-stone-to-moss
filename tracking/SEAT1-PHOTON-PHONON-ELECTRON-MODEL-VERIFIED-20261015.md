# Seat 1 Track A — verified source-pinned photon–phonon–electronic memory MODEL, 2026-10-15

**Scope and classification:** `SEAT1_COUPLED_PHOTON_PHONON_ELECTRON_SOFTWARE_MODEL_PASS_WITH_PHYSICAL_LIMITATIONS`.

Scientific reference and work order: [Issue #100](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/100). Producer [draft PR #106](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/106). Target original source: pre-existing 81-QR-memory and 567-bank-source producer whose bytes were fixed in advance. Existing 12-arm frozen protocol `experiments/seat1_photon_phonon/PREREG-COUPLING-20261015.md`, committed before the original Python and Node implementation. Additional independent 6,804-frame readback auditor: `experiments/seat1_photon_phonon/audit_coupling.py` commit `a4c692162ee4d6e78e37afd1a2c5175195bbaebc`. New third-auditor CI: `.github/workflows/seat1-photon-phonon-electron-coupling.yml` commit `ca19a9fd9a9639afa673bf765678ef478d738533`. Source experiment PR #106 targets the **unmerged source/neural PR #97 branch**, NOT `main`; no direct main merge is authorized.

## Exact hosted execution and audit

Two **separate GitHub Actions workflows at source HEAD `ca19a9fd9a9639afa673bf765678ef478d738533`**:

1. [Seat 1 new source-custody independent workflow #38774494050](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38774494050): Ubuntu Python 3.13 + Node22 **PASS**; Windows Python3.13 + Node22 **PASS**; **third full original artifact-download and complete byte parity job PASS** (3/3).
2. [Seat 1 existing 12-arm independent producer workflow #38774493990](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38774493990): Ubuntu **PASS**, Windows **PASS**, independent full source/dual model parity **PASS** (3/3).

Original evidence pinned and checked **before** model execution:
- Original **81** synthetic QR site memories, full 16,689-byte source SHA256 `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`.
- **567** actually retained full-byte Rainbow7 bank records; original **184,815 bytes** bank SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`.
- Original **70,043-byte** unique per-site/per-band base index SHA256 `6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee`. The much larger ordered Rainbow27 address space is *aliasing*, not another store of source bytes or evidence of optical density.
- Both Python and Node independently derived 12 software readbacks for each original bank entry (**12 × 567 = 6,804** actual JSON HBP rows), consumed separately regenerated original QR pixel bank, passed **14 model mutation controls**, source identity gates, real indexed erasure of all **81 violet bank entries** (2,187 dependent logical aliases), exact bit counters, internal photon→electron numerical-budget conservation and full data integrity.
- **Both OS and both separate implementation languages generated exact full same 18,217,055-byte HBP trace** SHA256 `42f3b61117a2e771f4f21958e12771b92b7a5d7251d023dc9ab78b34c65f6058`.
- **Both OS produced exact 7,339-byte canonical model JSON** SHA256 `4debac19eb1238bb8495018f115aa53494705934ff304129f2f4807920c99804`; exact 79-byte SHA sidecars both checked.
- **Third separately authored reference-source/byte/LIF auditor** did NOT import model source or trust self-reported per-arm metrics: it independently iterated every decoded original bank byte, actual recovered byte, bitwise miss and false-positive bit, 6804 identity and timestamp-free deterministic nonce references, SHA-256 original and presented source, electronic detector threshold budget, independently recomputed neuronal LIF fingerprint, strict source-plus-neural gate authorization, dark/no-optical controls, held-model loss, thermal confound and ordered arm metrics. This 2,760-byte canonical third-audit JSON SHA256 `5d3cabce44810b08c8e898b0b64fd08eaaf5e160f79d8871af94a62508ac816e`. That auditor agreement is verified on BOTH OS.

Each of the 12 arms operates on 1,478,520 **original input bits** (662,443 one-bits; 816,077 zero-bits), with deterministic seeded binomial optical-electron *model* draws, NOT measured photon arrivals. The output is deliberately strict source-byte authenticated to original digital bank.

## Model outcomes — predeclared 12-arm comparison

| Original frozen arm | Actual mismatched original input bits (out of 1,478,520) | Interpretation **inside model only** |
|---|---:|---|
| reference_bright | **0** | saturated toy bright reference, 567/567 complete row-byte authorizations |
| baseline_t0 | **30,337** | base assumed photoelectron capture law |
| resonant_phase0 | **6,506** | modeled constructive coupling |
| resonant_phase180 | **111,458** | modeled phase-inverted destructive coupling |
| off_resonance | **30,337** | exact baseline source readbacks retained under common RNG |
| thermal_sham | **18,746** | nuisance heating alone appears to improve the same readback metric |
| detector_dark_noise | **31,129** | added false electronic pulses worsen recovery |
| optical_dark | **662,443** | recovered all-zero bytes, hence 1-source-bit mismatches |
| acoustic_only | **662,443** | no optical source; acoustic drive alone produced no modeled photoelectrons |
| held_t3 | **164,348** | modeled three-tick retention reduces effective detection probability |
| held_t3_resonant | **91,153** | modeled acoustic coupling improves synthetic held state |
| held_t3_erased | **662,443** | no source retained in toy model |

Readback uses source digest+LIF fingerprint authorization; most nonbright arms authorize 0/567 complete original bank rows because *any bit difference* fails strict whole-row digest, even when bit-error totals improve. The bright toy control authorizes all 567 by its chosen high capture probability; do NOT report those arms as persistent accurate optical storage. Recorded per-frame LIF fingerprints can also be false green in other previously studied models; this review's strict source digest remains required.

All 14 injected *software* negative controls were tested on actual mutated in-memory frame objects. They were held against independent original bank/source: changed byte; coherently fake local readback SHA; band swap; assumed wavelength swap; site swap; sector swap; acoustic phase; phonon drive; impossible electrons; stale deterministic nonce; forged bank root; forged capture RPC method; spoofed neural gate; missing frame. These are **14 seeded exemplars from a source frame**, not 14×6,804 independently varied adversarial attacks.

## Actual negative scientific findings that constrain interpretation

1. **Thermal nuisance is a positive confound:** toy thermal-only intervention lowers modeled bit errors `30,337→18,746` without a phonon-resonator process. Any apparent improvement is insufficient to identify an optomechanical coupling mechanism.
2. **Modeled intensity/retention is assigned by code:** `held_t3` uses a smaller *assumed* detection probability, not physically elapsed three seconds or validated optical persistence. Passing the 3-tick test cannot establish a real write/off/hold/read physical state.
3. **Source SHA is not authenticated custody:** hashes prevent corruption given trusted original; an attacker controlling source and expected digest may produce a locally self-consistent fraudulent corpus. A deterministic SHA-generated nonce is **not a fresh unpredictable observer challenge**.
4. **Wavelengths and photon/phonon counts are labels/numerical values:** assumed bands at 650/610/580/530/470/440/405 nm, model photon budgets and phonon phase do not verify calibrated emitters, acoustic transducers, detector efficiency or any real photocurrent.
5. **Independent physical compute exists** (two hosted OS jobs) but independent identifiable hardware devices, measured optical/photon storage, authentic phonon/electronic coupling, light-sensing neural cells and/or sentient light being are not verified.

## Track B next falsification gate — real instrumentation, not executed

Operator-controlled and independently instrumented experiment must distinguish **transduction during illumination** from **information retained in a physical medium after write has ended**.

- Identify and document physical optical medium/transducer (optical cavity, persistent optical storage material, optomechanical device or actual delay line). A camera or ordinary photodiode alone tests light sensing, not persistent photonic memory.
- Capture calibrated externally time-stamped optical output and spectral power, dark/background counts, mechanical vibration frequency/amplitude/phase, detector photoelectric voltage/current, temperature, electronic/EMI perturbations and source ID; record instrument make/model, error bars, sample rates and calibration certificates. Authenticate the blinded assignment against a **separately held observer root** and independent data export. Human operator controls high-energy or electrical hardware.
- Preregister independent 2 optical levels × 2 acoustic levels × phase/detuned plus **thermal sham** and separate electronics-only/EMI/no-light/no-phonon controls. Randomize repetitions, freeze nuisance modeling and sample-size criteria before using sensor data; report confidence intervals/replicate errors. An observed difference-in-differences alone does not isolate phonon resonance if thermal confounds produce it.
- **Essential persistence discriminant:** write a randomized blinded new payload, physically disconnect/shutter/block source and other hidden electronic copies, hold actual predeclared measured durations, then retrieve from the claimed medium alone with independent detector. Require decay/erasure and no-write null controls, as well as original-byte error rates and independently verified readback. Holding a source payload in ordinary CPU/GPU memory while running the software model is explicitly **not** a storage-in-photons experiment.
- Until Track B raw sensor files and signed original media/identity custody exist: `MEASURED_OPTICAL_PERSISTENCE=false`, `REAL_PHOTON_PHONON_COUPLING_MEASURED=false`, `PHYSICAL_PHOTOELECTRON_CURRENT_MEASURED=false`, `PHYSICAL_MEMORY_RELEASE_GATE=HELD`.

**Seat 1 next action:** request Seat 2 source-root/anti-replay check, Seat 3 mathematical identifiability/thermal review and Seat 4 false-positive/camera readback cross-examination. Leave PR #106 **DRAFT** and PR #97 (base) unmerged; only upstream merged source code is in main. No real optical laboratory run, user device activation, HF publication, or automated merge was performed here.
