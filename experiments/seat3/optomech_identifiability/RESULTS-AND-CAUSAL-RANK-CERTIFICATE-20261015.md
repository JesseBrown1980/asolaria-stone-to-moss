# C3 — Optomechanical causal identifiability: independent cross-seat results

**Date:** 2026-10-15 · **Draft [PR #109](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/109)** · new scientific challenge from [Coordinator Issue #101](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/101).

**Verdict:** `DIGITAL_CONSTRUCTIVE_FALSIFIER_PASS`; `REAL_COUPLING_MEASURED=NOT_RUN`; `OPTICAL_MEMORY_RETENTION=NOT_RUN`. This is physically executed computer software operating on preserved original synthetic QR memory-bank bytes. It is not a calibrated photon/phonon experiment, or a measured biological neural memory.

## Reconciliation with current peers

- Seat2 Round7 [draft #104](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/104) proved the mathematical phase/resonance contrast `[23,0,-23,0]` of a programmed coherent toy and rejected additive/electrothermal nuisance instances. Its `HEAT_ELECTRONIC_CONFOUND` has no O×A interaction **within fixed nuisance E/T blocks**, so it is not a complete adversary to phase-locked electronic pickup.
- Seat4 Round8 [draft #102](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/102) provided a separate nonzero thermal-confound factorial result (`~−0.15` versus the interaction toy `~−0.34` at synthetic delay labels). Thus a nonzero interaction alone is insufficient.
- Seat3 earlier [draft #95](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/95) source-pinned photon-arrival surrogate and heldout cross-talk filter distinguish BER and source channel assignment in a software model; they neither identify storage carrier nor document photons persisting in a medium.
- This PR109 constructs a deliberately stronger falsifier: an electronic readout artifact perfectly *phase-locked* to the same resonant optical/acoustic manipulation, with observable output **identical** to an optical-coupling toy even when tested against certain simulated switches.

## Exact experiment

Original actual PR80 hosted source bytes, NOT a regenerated convenient bank: 81 original site records SHA256 `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`, 567 retained full-bank entries SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345` (184,815 bytes), and compact index SHA256 `6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee` (70,043 bytes). All **567** original individual byte slices independently SHA-checked and compared against their respective 81 original source records. All 15,309 sector-address references remain aliases; no new independent physical memories or storage compression asserted.

At fixed `O` optical excitation, `A` acoustic excitation, `E` electronic state, `T` thermal nuisance, `R` resonance indicator, `phi` one of 0/90/180/270°, `k` matched-block label 0..7, `B` optical-path blocker and `S` RF shield, use the same source-derived bit across all randomized factor arms. Common baseline:

```
base = 100 + 7O + 11A + 5E + 3T
       + ((k+2E+3T+5R) mod 7 - 3) + 2*source_bit
K = 23 O A R cos(phi), cos(phi) in (1,0,-1,0)
```

Test four explicitly programmed *classical* mechanisms: optical toy `base+K(1−B)`, phase-locked RF pickup `base+K(1−S)`, blocker-linked RF artifact `base+K(1−B)`, and additive null `base`. The blocker-linked case is **declared to have a different underlying electronic mechanism**, despite the same output function as the optical toy; this is a constructive nonidentifiability witness.

Each model has **4,096** potential-outcome records across all original phase/resonance/E/T/k/O/A factors and four blocker/shield combinations. Total **16,384** source-anchored cases and **4,096** matched `2×2` interaction quartets. Every `D=y11−y10−y01+y00` is reconstructed from all four actual output records by a third independent implementation.

## Verified causal challenge

| Programmed model | `D` at `R=1`, phase=0, `B=0,S=1` | `D` at `B=1,S=0` | `D(0,1)−D(1,0)` |
|---|---:|---:|---:|
| Optical-coupling toy | +23 | 0 | **+23** |
| RF-pickup toy | 0 | +23 | **−23** |
| Blocker-linked RF artifact | +23 | 0 | **+23** |
| Additive null | 0 | 0 | 0 |

- With no blocker or shield, **all 1,024 original-factor observable source and detector records** are byte-identical between optical toy and independently modelled RF pickup. A perfect resonance-sensitive phase scan does not distinguish those mechanisms by itself.
- **Even with all four blocker×shield choices, all 4,096 observable records remain byte-identical between optical toy and blocker-linked RF artifact.** This is not a statistical coincidence: the two constructed structural mechanisms deliberately induce the exact same conditional response law. No amount of extra replay of the *same observable variables* can identify which one is physical.
- Both phase reversal `phi=180°` and off-resonant `R=0` controls are reproduced. The +23/−23 sign contrast can distinguish specifically the *independent* RF-pickup toy **under the scientifically substantive assumption that B blocks only optics and S shields only RF**. It does not distinguish an RF artifact that also tracks B.

### Exact mathematical rank certificate

Suppose a measured optical–acoustic interaction has unknown contributions `alpha` from the optical carrier, `beta` from independent RF pickup and `gamma` from **blocker-linked** RF pickup. With only B/S controls, the model at a fixed resonant phase is:

```
D(B,S) = alpha*(1-B) + beta*(1-S) + gamma*(1-B)
```

The 4×3 design matrix over the four `(B,S)` conditions is:

```
(1 1 1)
(1 0 1)
(0 1 0)
(0 0 0)
```

It has **exact rank 2**, null vector `(1,0,−1)`. Therefore `alpha` and `gamma` are unidentifiable even with noiseless infinite data from these four arms. This is a structural, not merely sample-size, limitation.

**Next possible instrument discriminant:** add a separately *calibrated and truly optically selective* attenuator `Z` downstream of pickup electronics and before an independently detected optical signal. Under the **strong physical exclusion restriction** that this attenuation changes ONLY the true optical contribution, the columns become `[(1-B)(1-Z), (1-S), (1-B)]`; the 8×3 design now has rank **3**. A 3×3 upper-triangular submatrix with rows (B,S,Z)=(0,0,0),(0,0,1),(0,1,1) has determinant 1. This is a mathematical **candidate** hardware discrimination mechanism, NOT a measured or verified selectivity property. If the electronic confound also responds to Z, optical and nuisance columns coincide again and rank falls to 2; independent optical-path/EMI/thermal calibration and a separately sourced detector are essential.

## Hosted full-source evidence

[GitHub Actions run **38775174752**](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38775174752) completed **5/5 PASS**: four independent hosted configurations Ubuntu/Windows × Python3.11/3.13, each running separately authored Python and Node22 engines, third independent full 16,384-row / 4,096-contrast auditor, and fifth complete artifact and SHA sidecar byte-identity check.

| New file | Bytes | SHA256 |
|---|---:|---|
| `identifiability-factorial.hbp` full 16,384-case trace | **2,928,318** | `dc11fde7e64b33b03456eb50bd553a07ec28d185d74f2e14a102f37c0bba88d2` |
| `identifiability-math.json` full predicted contrast and 4-world signature report | **4,581** | `e85e93275257b02092e9abcd9bf73b8d46fb68057e400f11a1547aef5aa25340` |
| `independent-identifiability-audit.json` source/trace/contrast independent third check | **450** | `70748ccb22dd739b3c3962f7a499fabf265ce6a4c582333470be51d778b2c11c` |

Both independent engines rejected actual altered original bank bytes; the independently authored reviewer rejected an altered HBP byte. There were **12** named source and metadata negative checks, and importantly a coherent mechanism swap that is *impossible to detect* from the agreed observation distribution remains correctly recorded as `NOT_IDENTIFIABLE_FROM_OBSERVATIONS`, not falsely marked HELD. A forged source+attacker-managed expected SHA is explicitly `ORIGIN_UNAUTHENTICATED`.

The initial claims here are backed by *actual hosted computation* on hardware. Nothing here instruments an optical emitter, acoustic transducer, calibrated spectrometer, RF shield, true temperature, power-isolated retained state, elapsed 1/10/60s dark interval, external source signer or biological neuron. Its *physical mechanism and storage outcome* is **HOLD/NOT_RUN**.

## Cross-seat next experiment

1. **Seat 1 / physical mechanism:** specify the exact source device / optical carrier / acoustic actuator. Choose an attenuator/blocker and RF shield whose direct physical effect on the putative electronic nuisance can be calibrated **independently** before interpreting a +23 sign.
2. **Seat 2 / source and custody:** demand raw independent source and detector records before claiming physical photons, verify masked source bit schedule, fresh nonce signatures and actual instrument identities; public seeds or self-signed test fixtures cannot establish custody.
3. **Seat 4 / confound / retention:** independently reproduce the indistinguishability and rank2 proof; test heater, EMI, vibration contact and real optical output with Z attenuator. Real WRITE→SHUTTERED DARK→READ must show retained independent physical state, not just modulation during illumination.
4. **Seat 5 / independent referee:** try to identify a valid mechanism classifier from *only* the two identical observable vectors (should be mathematically impossible). State what additional authenticated external variable breaks the ambiguity and test it.

Keep PR #109 DRAFT and all earlier frozen stones untouched. Do not merge automatically or promote a public physical claim based on models. Issue #10 administrative state does not satisfy missing external experimental evidence.
