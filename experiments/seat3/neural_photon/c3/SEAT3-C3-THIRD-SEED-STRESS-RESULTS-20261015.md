# C3 Seat 3 — Third-heldout spectral drift and photon–phonon mechanism cross-examination

**2026-10-15.** Third-seed digital photons / preserved historical Asolaria source. [Stacked draft PR #108](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/108) on draft [PR #95](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/95). This report documents **physically hosted software computation**, not photons caught by a calibrated sensor, optomechanical memory retention, quantum behavior, or biological neuron state.

## Frozen protocol and source

[Prospectively frozen protocol](PREREG-THIRD-SEED-SPECTRAL-STRESS-20261015.md), commit `373fbd258f64cfd6a41bf6a9dc4860905d3dc1ce` before generator implementation and before examining C3 counts. **Earlier A/B readout formula was selected after looking at A data**, already disclosed. This is a new independent *deterministic pseudorandom* seed/model holdout, not a truly blinded physical laboratory.

- Real prior PR80 original hosted digital source: 81 unique memory-site JSON, SHA `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`; 567 bank/site leaf payloads, 184,815 bytes SHA `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`; original 70,043-byte base index SHA `6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee`. Frozen source PR80 commit `7b5faf1103a7b42b603b44b08a5a5bfa994d0f76`, archived GitHub Actions run `38745842295`.
- Logical symbols per condition = 27 ordered sectors ×81 sites ×7 *symbolic* spectrum bands = 15,309; only 81 underlying distinct original site memories. Band-port identity pinned `[2,5,0,6,1,4,3]`.
- New fixed C3 seed `ASOLARIA-C3-HOLDOUT-THIRD-SEED-20261015-V1`, separately tagged per condition. 16 Bernoulli attempts per source/band/exposure, seven repeated exposures, deterministic SHA256 pseudo randomness. No actual photons/accelerometers/laser/shutter involved.
- **C = original prior noise model**: detected own channel 168/256, left/right 24/256, lost 40/256, source ON/OFF emission probability 192/256 and 16/256, dark background 8/256.
- **D = shifted leak/dark stress** (frozen pre-run): own 120/256, left/right 40/256, lost 56/256, same ON/OFF, dark background 16/256.
- Decoders **unchanged** across both: raw `C_j>=5n`, corrected `7C_j-C_(j-1)-C_(j+1)>=T_n`, `(T_1,T_3,T_7)=(28,78,182)`, no wrap for edge channels. No tuning on C3/D outcome.

## Complete first-run quantitative results

[First fully hosted run #38774885670](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38774885670) **5/5 PASS**, Ubuntu/Windows × Python3.11/3.13 + independent Node22 + third full-source/event-by-event Python auditor + fifth complete output byte-parity. Deliberately modified original bank bytes and altered detector HBP were rejected.

| Model | Exposures | Raw errors/15,309 | Frozen-correction errors/15,309 | Repaired | Degraded | Both still wrong |
|---|---:|---:|---:|---:|---:|---:|
| C original model, third seed | 1 | 833 | 702 | 443 | 312 | 390 |
| C | 3 | 150 | 38 | 127 | 15 | 23 |
| **C** | **7** | **25** | **0** | **25** | **0** | **0** |
| D higher leakage/noise | 1 | 2,430 | 2,326 | 748 | 644 | 1,682 |
| D | 3 | 1,388 | 971 | 548 | 131 | 840 |
| **D** | **7** | **947** | **419** | **567** | **39** | **380** |

**Interpretation:** a third seed reproduces a strong improvement *within the same declared detector model*, but under model shift, seven-exposure BER remains **419/15309 ≈ 2.737%** (vs original raw 947/15309 ≈ 6.186%). This model-shift result qualifies—not invalidates—the earlier 26→1 observation on the second fixed fixture. It does not generalize to unmeasured physical detectors.

Dark-only false positives under fixed raw vs corrected decoder: C at one exposure **4→15**, D **36→69**; at three and seven exposures, all zero. Do not hide the worse one-exposure dark false-alarm behavior. Misassigned receiver port map at seven exposures produces **7,659** errors for C, **6,795** for D, not an authenticated spectrum binding.

**C3's new failure localization: edge bands deteriorate under model shift.** At seven exposures in harsher D, original raw vs corrected errors by band (2,187 symbols/band):

| Ordered band ID | Raw errors | Corrected errors | Direction |
|---|---:|---:|---|
| 0 (red) | 9 | **16** | Worse |
| 1 (orange) | 167 | **75** | Better |
| 2 (yellow) | 191 | **71** | Better |
| 3 (green) | 186 | **73** | Better |
| 4 (blue) | 189 | **82** | Better |
| 5 (indigo) | 196 | **89** | Better |
| 6 (violet) | 9 | **13** | Worse |

The no-wrap three-point deconvolution does not behave uniformly at band boundaries. A future edge-aware model must be **precommitted and tested on fourth unseen detector/seed**, not tuned on these now-exposed C/D data and called held-out success. Deleting actual violet storage remains unavailable even when other aliases point toward 567 bank rows; optical counts cannot manufacture its missing byte payload.

**Modeled event conservation:** C emitted 697,991, detected 570,156, lost 127,835, background 53,537. D emitted 698,251, detected 514,225, lost 184,026, background 107,230. A single synthetic event never arrives at two detectors. The independent auditor recomputes all 30,618 source rows **and their underlying pseudo-emission/routing and dark-count events**, comparing original bank-leaf SHA and the raw class bit.

Complete platform-identical initial results:
- `c3-third-seed.hbp`, **3,822,639 bytes** SHA256 `6bfa715772871d1290cbb1977bb966bc60354ac53c30101f8d3dda469a282c54`.
- `c3-results.json`, **9,388 bytes** SHA256 `37a7c2124f87d6fe5dc704d31dc4071c9b897b67384906a2bc2967eec75cc0f1`.
- `independent-c3-check.json`, **1,184 bytes** SHA256 `8156f8c73f29375dd6134c752074fb4a71257988bb564ca5ca26aadf549ef642`.

The later hosted workflow run also checks independent exact causal counterexample, and must be separately verified before its new status is called PASS.

## Formal Seat3 photon–phonon factorial identifiability counterexamples

I independently inspected actual source for [Seat2 draft PR #104](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/104) `experiments/seat2/round7/seat2_coupling.py` and [Seat4 draft PR #102](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/102) `experiments/seat4/round8/factorial.py`. These are mathematically transparent software fixtures, not real optomechanical observations.

**Counterexample A — Seat2 phase pattern does not establish a photonic carrier.** The observed scalar `Y=baseline+23*O*A*resonance*phase`, phase vector `(1,0,-1,0)`, is *exactly identical over every one of the 1,024 crossed source factors* whether its causal interpretation is a genuine optomechanical modulation or a phase-locked electronic EMI/microphonic response to common optical/acoustic control clocks. Hence both models have DiD vector `[23,0,-23,0]` at resonance, zeros off resonance. All tests on **Y alone** have zero distinguishing power between these two models unless actual independent mediator instrumentation/control is added. This is a *mathematical nonidentifiability construction*, not a claim of real EMI in the user's device.

**Counterexample B — Seat4 quadratic thermal term exactly aliases an interaction column.** For binary light L, acoustic A, `(L+A)^2=L+A+2LA`. Therefore in a factorial response model with design columns `(intercept,L,A,LA,thermal_nonlinearity)`, the so-defined thermal nonlinear term is a linear combination of the main treatment effects and interaction; the 4×5 treatment matrix has **rank four**, not five. No amount of repeating those same four treatment combinations independently separates the direct `LA` mechanism coefficient from the quadratic temperature-mediated coefficient absent extra independent temperature/thermal sham perturbation or an external identifiability assumption. Actual Seat4 model reports a simulated linear temperature proxy that is fully determined by L+A, while readout nonlinearity uses its squared value. Both are programmed rather than measured.

**Statistical implication:** an intervention contrast alone can identify total interaction only under actual exchangeable randomized physical trials, but not which physical carrier mediates it. Physical mechanism identification needs separate calibrated optical readout, vibration spectrum, electrical supply/EMI, thermal matched shams, true source isolation, actual physical elapsed dark retention and independent signer/custody. Synthetic SHA noise shared across arms gives exact contrasts **by construction**, not a physical confidence interval.

### C3 executable mathematical audit

See `identifiability_counterexamples.py` and the new hosted CI artifacts. It independently reconstructs all 1,024 Seat2 model response combinations for the coherent/EMI alternatives, validates the same phase contrast and checks the exact 4×5 rank defect using rational arithmetic. These were derived POST HOC after reading other seats' code; not misrepresented as pre-registered.

## Next physical and peer gates

- Seat1 identify actual optically addressable physical medium, calibrated seven detector responses, genuine independent acoustic drive, RF and thermal instrumentation and time-synchronized write–dark–probe mechanism.
- Seat2 challenge false/missing external custody, original full raw signed instrument bytes, replay after process restart and phase-coherent EMI / temperature correlated nuisance.
- Seat4 verify independent raw detector acquisition and controlled 1/10/60 actual-second retention vs afterglow, optical transduction without retention, and electronic state contamination.
- Seat5 adversarial review of S5-02 exact C/D models and source roots; challenge false green, edge-band problem and lack of independent physical input.

C3 implementation PASS is a real hosted computation with **zero** real optical/phonon/biological readings. Keep stacked PR #108 DRAFT, no auto-merge, preserve original PR #95, original #104/#102 and the already published computational release. Issue #10's administrative status is not a substitute for a physical proof.
