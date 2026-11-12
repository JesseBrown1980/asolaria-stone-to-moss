# Seat 2 Round 7 — photon / phonon / electronic coupling: independent factorial falsifiers

Date: 2026-10-15. **This file is committed before any Round 7 implementation or results.** Work originated in the Seat 1 scientific handoff identifying published optomechanical coupling as a possible Asolaria mechanism. Do not rewrite historical stones or imply physical hardware measurements.

## Grounded background
NIST Balram et al. (2016), *Coherent coupling between radio frequency, optical, and acoustic waves in piezo-optomechanical circuits*, Nature Photonics 10:346–352, DOI 10.1038/nphoton.2016.46: **a specialized GaAs piezo-optomechanical cavity** with ~1550 nm optical photons and ~2.4 GHz phonons, not ordinary GPU RAM. NIST primary source: https://www.nist.gov/publications/coherent-coupling-between-radio-frequency-optical-and-acoustic-waves-piezo. Published existence of coupling in that apparatus does not certify Asolaria photon storage, neural memory, or physical coupling on its uninstrumented hardware.

## Frozen repository anchors
- Main `5d3e3a1147ad7af84c1b5b1ba482dfddd9832c86`; Seat4 R6 PR #94 tested head `a427ee599d7bd64ebb503d632e0c047588038c4f`, digital trace `46a7b6c55ed32b6b1bf5d5d3f5033d8b3ef0214a54e1eb7942dc952a1de1c8bc`.
- Seat2 Round6 PR #96 head `fec6c06c4d91dd93683a9ae523a82fe41720063c` demonstrated published fixture signing seeds and trust-root boundary.
- Frozen Round5 signed-spectrum 701-byte HBP SHA256 `077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400`; main source-bank SHA `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`.

## Level A — independently varying experimental inputs
Optical excitation `O`, acoustic excitation `A`, electronic nuisance `E`, and thermal nuisance `T` are each 0 or 1; optical-acoustic phase `phase_idx` is 0,1,2,3 (0°,90°,180°,270°); detuning/resonance `R` is 0/1; repeated matched blocks `block` 0..7. **Full factorial:** 2^4 × 4 × 2 × 8 = **1,024 digital mock observations per model**. Exactly four deliberately programmed mock models, **4,096 rows total**:
- `COHERENT_TOY`: detector units `y=100+7O+11A+5E+3T+23 O A R c_phase+n(block,E,T,R)`, where `c_phase=[1,0,-1,0]`.
- `ADDITIVE_NULL`: same with the `O A` term absent.
- `HEAT_ELECTRONIC_CONFOUND`: replace true `O A` coupling with `23 O T + 17 A E`.
- `PHASE_INSENSITIVE_ARTIFACT`: add `23 O A` at every phase and detuning. An interaction contrast alone is insufficient to identify coherent optomechanics.
- Matched-block noise is `n=((block + 2*E+3*T+5*R)%7)-3`, which cancels exactly in within-block differences. This is deterministic mathematical verification, not independent noise physics or statistical inference.

At every fixed phase, detuning, block, E and T form:
`D = y11 − y10 − y01 + y00`.
Predictions averaged over 8 blocks × four nuisance (E,T) states (32 paired contrasts per phase/detuning):
- COHERENT_TOY resonant `D=[23,0,-23,0]`; detuned `[0,0,0,0]`.
- ADDITIVE_NULL and HEAT_ELECTRONIC_CONFOUND both `[0,0,0,0]` at both detunings.
- PHASE_INSENSITIVE_ARTIFACT `[23,23,23,23]` at both detunings.
- Required independent algebraic phase-and-resonance classifier rejects additive, nuisance and phase-insensitive alternatives; only toy coherent model passes the predetermined pattern. Acceptance is **SIMULATOR_TEST_PASS**, never real coupling.

## Level B — source-blinded memory interpretation
Independently test that readout records containing true `precommitted_bit`, or its algorithmically recoverable public-seed equivalent, can spoof memory recall even for no-memory controls. The original Seat4 PR94 numerical model exposed a public deterministic bit schedule as metadata. Preserve this counterexample and require a **decoder-input-only detector envelope**, separately held truth source and sealed predictions before reveal for any prospective hardware experiment. A local software harness still lacks real independent secret custody; do not call it authenticated physical blinding.

## Active negative controls
Reject injected wrong phase, detuning, O/A channel swap, falsified sensor value, duplicated or missing factorial record, and `physical_photon_measured=true` metadata. Show phase-insensitive `O A` artifact produces a nonzero conventional interaction but **fails** phase/resonance discrimination. Demonstrate that joint changes in electric/thermal nuisance cannot explain the phase contrast **within this programmed model**. Keep all failures as named falsifiers.

## Independent review & publication policy
Run Python >=3.11 and separately authored Node >=22 over all 4,096 rows with byte-identical canonical JSON/HBP and SHA256 checks on Ubuntu/Windows. Compare full archived bytes from four CI environments (5th job), not only summary metrics. Preserve older artifacts; independent peer review before merge. Physical experiment needs actual measured optical/acoustic/RF stimuli, calibrated cavities/transducers, phase/frequency sweeps, temperature and electrical sensors, independently secured challenge/optical shutters, **real elapsed** dark-retention and fresh blinded readouts. Photons/phonons coupling is NOT equivalent to photons storing stable neural memory. Real biological neural memory requires separate electrophysiology.

Verdict fields: `digital_coherent_fixture_verified`, `physical_optomechanical_coupling_measured`, `independent_optical_memory_measured`, `biological_neural_memory_measured`; three latter always false in this synthetic run. Issue #10 administrative state does not override physical research scope.
