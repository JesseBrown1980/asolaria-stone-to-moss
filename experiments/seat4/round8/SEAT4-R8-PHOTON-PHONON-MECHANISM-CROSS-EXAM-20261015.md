# Seat 4 Round 8 — Photon–phonon–electronic coupling falsifier: first verified hosted result

**2026-10-15 | Independent computational model comparison | NO PHYSICAL SPECTRA / MECHANICAL VIBRATION / NEURAL TISSUE WERE INSTRUMENTED**

Preregistered FIRST at commit `ee90d029403cbb064d844cce52a489947562d044`, before Python/Node implementations. Prior Seat4 PR99 independent neural-lane false-positive source audit is separate. This report is a prospective factorial *analysis-code* test, not the actual photon–phonon physical experiment.

## Experiment and frozen original source

Read the actual previously archived original Seat1 PR80 GitHub Actions [source run 38745842295](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38745842295) (original 81 synthetic source records, exactly 567 band/site payload records, source SHA256 `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`, full 184,815-byte bank SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`, compact index SHA256 `6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee`). The old SHA-pinned source archives were read-only; no original dataset, prior release or archived stone changed.

Mathematical treatment is `L∈{0,1}` simulated light arm and `A∈{0,1}` simulated vibration arm, giving four factorial conditions `00` (both absent), `10` (light), `01` (acoustic), `11` (both). **Measured outcomes are intentionally a deterministic mathematical function, not physical actual light or sound.** SHA-fixed original source bit is shared across four treatments. The same site/band/delay/replicate SHA-defined pseudorandom roll is used in all four arms, so this is a *paired toy potential-outcome design*, not four independently sampled experimental noise streams.

At 81 sites × seven symbolic band labels × three delay **labels** (1/10/60, not seconds elapsed) × four interventions × eight replicate labels = **54,432** synthetic rows per regime. Four regimes were fully evaluated = **217,728** digitally generated comparisons, all independently recomputed with separate Python 3 and Node22 mathematical implementations on Ubuntu/Windows.

**Predefined null/contrast equations:**
```
D_light = p(correct | L=1,A=0) - p(correct | 0,0)
D_acoustic = p(correct | L=0,A=1) - p(correct | 0,0)
D_interaction = p(correct |1,1) - p(correct |1,0) - p(correct |0,1) + p(correct |0,0)
```

Digital scenarios set toy retrieval probability thresholds out of 1000: `NULL=880`; `OPTICAL_ONLY=880-300L`; `INTERACTION_TOY=880-40(L+A)-340LA`; `THERMAL_CONFOUND=880-75(L+A)²`. **The confound model contains no explicitly stored photon or phonon state**, and its nonlinear temperature-mediated retrieval error still yields a strong apparent interaction.

## Independent sample results by delay

All entries are fractional differences in synthetically correct digital readouts, not optical loss rates. Each entry uses 4,536 source/site/replicate comparisons per arm/delay. D values are computed from the FULL original 217,728-row trace.

| Regime | Label delay | Δ light | Δ vibration | Δ light×vibration | Physical claim |
|---|---:|---:|---:|---:|---|
| No treatment effect | 1 | 0 | 0 | **0** | None |
| Simulated light effect only | 1 | -0.291667 | 0 | **0** | None |
| Simulated optical–acoustic interaction | 1 | -0.039903 | -0.039903 | **-0.333774** | None |
| Nonlinear heating confound (no optical memory) | 1 | -0.068122 | -0.068122 | **-0.155423** | None |
| No treatment effect | 10 | 0 | 0 | **0** | None |
| Simulated light effect only | 10 | -0.287037 | 0 | **0** | None |
| Simulated optical–acoustic interaction | 10 | -0.037919 | -0.037919 | **-0.339506** | None |
| Nonlinear heating confound | 10 | -0.072310 | -0.072310 | **-0.142416** | None |
| No treatment effect | 60 | 0 | 0 | **0** | None |
| Simulated light effect only | 60 | -0.306437 | 0 | **0** | None |
| Simulated optical–acoustic interaction | 60 | -0.041667 | -0.041667 | **-0.338624** | None |
| Nonlinear heating confound | 60 | -0.074735 | -0.074735 | **-0.156966** | None |

**Scientific conclusion:** a seemingly convincing positive or negative optical–acoustic factorial *interaction* is NOT sufficient evidence that photons or phonons store memory. Identical experiment-level interaction signatures can arise from temperature, piezoelectric pickup, electronic readout shifts and other unmeasured paths. Seat4's toy thermal confound is a constructive falsifier of the inference "interaction ⇒ physical photon/phonon storage."

## Source, tampering and independent cross-OS evidence

**First completed hosted [GitHub Actions #38772771026](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38772771026): 5/5 SUCCESS** (Ubuntu/Windows × Python3.11/3.13, independent Node22 verifier, fifth full-data output artifact downloader and exact byte-parity job). All four producer jobs regenerated the original source bit, every simulated readout and all 48 model/delay/factorial success cells (4 models × 3 delays × 4 arms) independently.

**13 actually mutated digital negative inputs were rejected**: original leaf SHA replacement, wrong light arm, wrong vibration arm, altered time label, repeated replicate, wrong original site, wrong band, tampered readout, fabricated actual-photon flag, changed modeled temperature, incorrect supply voltage, fraudulent optical meter and unrequested real biological/neural evidence field. This only verifies software input consistency; it does not infer trustworthy instrument authorship.

| Downloadable GitHub artifact | Exact bytes | SHA256 |
|---|---:|---|
| `r8-synthetic-factorial.jsonl` full raw toy trace | **104,495,520** | `1eca9fe230f986a31c8948563d4ab13191a72566c5ab79d9478d3ed2d6cafbfc` |
| `r8-results.json` factorial summary | **3,335** | `17238fd0f807d26153c2cdec5f7bf9d97c2ba543c991fc9ab050e68d3af53e4c` |
| `r8-results.hbp` source-anchored receipt | **502** | `826bfd820f5cb34f79a3ab7f3ef1cf201a15c63c29801f8ddc8feb9f6137cd7e` |
| `r8-independent-node.json` independent Node result | **385** | `2567e194ead80f7cca5784422e2a22873ed38fa4f70c3491558b5cc112e352c7` |

After the **first successful run**, this PR deposited the new exact immutable 502-byte [Seat4 Round8 HBP stone](../../../stones/2026-10-15-rainbow81/seat4-r8-photon-phonon-electronic-factorial-20261015.hbp) and an SHA sidecar, then tightened every OS job to require freshly regenerated HBP bytes match that committed stone. The first successful run must not be conflated with the final post-stone confirmation run; check latest Actions status before claiming second confirmation.

## Distinct real physical experiment (not executed)

Follow the [independent optical/acoustic/electronic lab handoff](REAL-PHOTON-PHONON-ELECTRONIC-LAB-HANDOFF.md): precommit blinded random source bit, use calibrated real optical and acoustic stimulus meters, measure temperature/voltage/readout/clock and actual light vs darkness during retention, keep electronic controls fixed and test temperature/electrical-sham matched interventions, seal independent detector RAW prior to unblinding. Real acoustic drive affecting light readback implies coupling only after confounds, not that phonons are stored; optically triggered charge storage could still be electronic memory. A real neuron/organoid hypothesis separately requires genuine electrophysiological data.

**Seat4 verdict:** all classical software factorial arithmetic/provenance probes PASS for frozen source; **real optical/phononic retention and biological neural memory HOLD**. PR stays DRAFT for peer review; no automatic merge, no HF publication and no reinterpretation of previously closed administrative Issue #10 as an optical/biological validation.
