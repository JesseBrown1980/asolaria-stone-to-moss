# Photon → Photoelectron → Electron MCP Light-bank — Independent Round 1 Review

**Date:** October 15, 2026
**Experiment:** preregistered at `d0cff331384ef4b085222924ebb552906f3559a5` before code.
**Research mode:** physically executed deterministic computational test of a **classical photon/electron detector and storage-loss model**, not an optical experiment with instrument-measured photons.

## Inputs and material behavior modeled

The frozen digital bank contains **81 original synthetic QR memory sources**, **567 full-byte band-labeled bank entries** and **184,815 retained bytes**. All 567 records and their complete payloads were used in every scenario, totaling **924,075 readback bytes** and **7,392,600 decoded source-bit decisions**, before five-fold detector replication in the protected regime. The existing **15,309 Rainbow27 addresses** remain derived logical aliases, not 15,309 independent payload memories.

The assumed light detector is on-off keyed: each 1 bit emits `N` modeled photons and each 0 emits none. Emitted photons survive assumed transport, modeled retention loss and photoelectric detection with total probability `p=(4/5)^(t+2)`. A digital detector declares 1 upon `count(photoelectrons + dark electrons)>0`, with independently modeled `d=0` or `0.001` dark electron probability. The five-detector regime votes by majority; no physical detector or neural tissue was used. Declared spectral labels and wavelength values are **inputs**, not measured source wavelengths. Pseudorandom outputs come from a fixed SHA-rooted deterministic xorshift32 stream; they are not measured quantum randomness.

The modeled electron signal is represented as a strict `JSON-RPC 2.0 tools/call` object with `name: electron.capture`, source root, band, site, sector, assumed wavelength, frame nonce, modeled emitted/detected counts and digital byte readback. **This is an MCP-style software tool envelope, not a working independent MCP server or an electron-controlled physical network transport.**

## Independently executed local evidence and exact trace

Python and independently written Node.js versions generated **byte-identical 6,048,391-byte, 2,835-frame HBP traces** and identically serialized JSON summaries; full HBP SHA-256:

`332e1eeb2d4de748c2e1da07729944fefe5b63589e9533b4c93b74d7cf3f5527`

Full result summary SHA-256:

`5468eeb46d8f349e47f6bfda17bd4ac8ff3a2c3acd4eb896628779decb759ee2`

The modeled bank has **662,443 one-bits** and **816,077 zero-bits**. A third separately implemented Python audit recalculated every decoded bit error directly by XORing each original byte with the readback byte; this was not a trust in the producer's numeric `bit_errors` declaration. It also recomputed the mathematical expectations from binomial detector laws and checked every frame's source SHA, site, band, wavelength, ordered sector, nonce, MCP tool name, modeled photoelectron bounds and summary consistency.

| Modeled channel | Expected bit errors from declared law | Observed fixed software trace errors | Completely correct 567-source rows | Residual / model sigma |
|---|---:|---:|---:|---:|
| 24 photons per 1-bit, 0-tick | 0.000015 | 0 | 567 | ≈0 |
| 1 photon per 1-bit, 0-tick | 238,479.48 | 239,145 | 0 | +1.7035 |
| 24 photons per 1-bit, 3-tick modeled loss | 48.191812 | 57 | 514 | +1.2689 |
| 24 photons per 1-bit, 0-tick, d=0.001 | 816.077015 | 824 | 142 | +0.2775 |
| 5-fold 24-photon per-bit majority, 3 ticks, d=0.001 | 0.008151 | 0 | 567 | ≈0 |

These mathematical expectation comparisons are **model self-consistency checks**, not measured validation of detector characteristics. The 6-sigma anomaly screen is descriptive, not an independent scientific evidence threshold. Zero errors on a finite test fixture is not a proof of perfect readback in arbitrary noise.

The error formula for source 1 in one detector window is `q1=(1-p)^N(1-d)`. The false-positive rate for source 0 is `q0=d`. For five independent replicas, the majority-failure rate is `sum_{k=3}^5 C(5,k) q^k (1-q)^(5-k)`. The expected error total weights those probabilities by the exact original source's 662443 one-bits and 816077 zero-bits.

## Adversarial and provenance review

Both languages execute **12 actual mutated-frame negative controls**: wrong band, wrong symbolic wavelength, changed ordered sector, forged source root, wrong expected row digest, impossible electron count, stale nonce, malicious tool name, altered readback bytes, response disagreement, missing frame and coherent local hash spoofing. These fail against the pinned reference in the bounded software experiment.

**Important falsification:** The frozen digital source root and outputs are reproducible, but a compromised authority controlling both source and independently supplied trust anchors could produce a mathematically consistent false origin. This experiment does not authenticate a natural photon emitter or measured detector outside the model.

## Hosted CI gate

CI [workflow](../../.github/workflows/photon-electron-mcp.yml) must regenerate the exact input roots from image QR pixels, run independent Python and Node on actual Ubuntu and Windows hosts, pass full-byte/replay and analytical review, upload the *complete* HBP/JSON artifacts, then compare the complete file bytes across both OS artifacts. **Report local execution as distinct from hosted CI until that CI finishes on its exact PR head.**

## Optical and neural follow-up experiment

This round tests an electronic `electron.capture` software interface and source memory reconstruction under an idealized photon detector law. **It does not establish synaptic plasticity, an active biological neuron, or optical persistent storage.**

Next preregistration (new experiment, not retroactive rebranding): use a calibrated photon pulse emitter/attenuator; a physically measured photodiode/photomultiplier or photonic chip; measured delay/retention; and real electron-signal digitization, separately timed and calibrated. Also implement a neuron-inspired integrate-and-fire electronic feedback *model* under the same frozen source, compare its memory recall against the simple majority vote, and challenge adversarial injected photoelectron spikes; label these two modalities separately.

**Decision pending:** do not merge this scientific PR automatically. Accept as a replicated mathematical computer experiment after hosted CI and cross-seat external review; optical, quantum or biological device measurements remain separate.
