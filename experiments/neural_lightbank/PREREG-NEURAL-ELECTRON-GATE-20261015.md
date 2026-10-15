# Frozen protocol — neuron-inspired electronic light-bank gating (2026-10-15)

**Research objective:** Cross-examine whether a *software* leaky integrate-and-fire (LIF) neural-memory fingerprint safely gates the digital recall of a classical modeled photon/photoelectron readback, with electrons serving as modeled MCP-style capture/control messages.

**Stage:** separate follow-on from [photon-electron PR #93](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/93), which already has pinned 2,835 frame SHA256 `332e1eeb2d4de748c2e1da07729944fefe5b63589e9533b4c93b74d7cf3f5527`, original 184,815-byte bank and independent Python/Node cross-OS validation. This document is committed before implementation of the neural follow-on program on this branch.

**Transparency:** Before writing this protocol, an exploratory local Python pilot found that coarse spiking fingerprints can falsely accept corrupted bytes: 27 of 57 corrupted rows under modeled three-tick attenuation and 89 of 425 corrupted rows under dark-count noise. Those numbers are **post-hoc pilot observations**, not blinded or preregistered findings. Freeze them only as regression targets, and demand independent implementation and fresh hosted CI.

## Logical neuron/electron model

- Freeze **567 digital bank records** anchored to original source SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`; one trained model unit per retained bank row, 81 source-site identities and seven symbolic rainbow-band labels. **15,309 aliases still refer to these 567 retained rows.**
- Take the full decoded electronic readback bytes of each of the **5 × 567 photon-electron digital model frames**. Treat every readback bit as an **electronic spike-inducing signal**, not as a measured biological photocurrent or actual photoelectron sample.
- One deterministic recurrent **leaky integrate-and-fire** unit per row: integer membrane `V_0=0`; for each bit `b in {0,1}` in MSB-first order, `V = max(0,V-1)+4*b`; if `V >= 7`, increment spike count and set `V -= 7`. The model has integer time steps, no measured seconds or real neuronal voltage. Record number of spikes in every successive 32-bit window as one byte of the **coarse neural fingerprint**, with V carried continuously across all windows.
- **Training:** reference fingerprint is obtained once from exact source bytes under the same rule. This is digital supervised reference storage; it is not a demonstration of biological synaptic learning.
- **Recognition:** compare observed to trained fingerprint. **Source-correctness:** independent verifier compares each observed decoded row SHA256 against the original trusted bank row SHA256. A neural fingerprint match alone is never sufficient: `ACCEPT = fingerprint_match AND original_row_SHA_matches`. Wrong source root or missing proof produces HELD.
- Electron-MCP semantics: input `tools/call electron.capture` must be source-root/sector/site/band/nonce-bound; output modeled `tools/call neuron.gate` contains fingerprint SHA256, whole-row root, spiking count and `ACCEPT`/ `HELD` status. Both are local software JSON-RPC-like tool envelopes, **not registered independently running MCP servers or physical brain interfaces**.

## Falsifications

1. **Physical software run and portability:** independent Python and Node22 implementations must agree on the complete deterministic neural HBP and JSON summary across Ubuntu and Windows and a fifth cross-platform comparison stage.
2. **Full source count:** 2,835 producer rows, 567 in each scenario, 924,075 observed readback bytes (not merely 81 labels), exact frozen photon HBP digest and original 81/567 digital root.
3. **Recognition vs correctness:** report exact byte rows, neural-only fingerprint matches, false-green matches where bytes are wrong, and source-trust gated authorized rows for all five photon modes; NEVER pool the 27/89 pilot collisions into a claim of physical photon memory.
4. **Live adversarial frame mutation:** flip an actual bit of an anchored reference row so the LIF neural fingerprint **does not change** (coarse signature collision) while the SHA256 **does** change. Require strict gate HELD. Forge both observed hash copies, replay old nonce, swap sector, band or site, corrupt spike count and gate verdict; independent anchored watcher must reject.
5. **Violet band erasure:** remove all 81 violet-band row receipts from the 567-source logical frame set. The expected 2,187 Rainbow27 aliases for violet become unavailable. No fabricated recovered violet payloads or unchanged full-source PASS may be reported.
6. **No numerical truth substitution:** source SHA and frozen photon HBP must be bound to original verified predecessor; a coherent attacker that changes both the source and trusted external root is `ORIGIN_UNAUTHENTICATED` not pass.

## Scientific truth boundary

**Real hosted computation and electronic digital memory = physical hardware-executed test.** There is no connected optogenetic neuron, measured photon source, photon-storage resonator, physical electronic readout instrument, calibrated laser or measured biological membrane potential. Synthetic LIF memory fingerprints and their hash verifier remain software.

A genuine physical follow-up needs calibrated light emission, optical path/delay or storage material, independently measured detector photoelectrons, source custody and an optogenetic/electronic neuron-interface readout. Such an experiment remains separate from these verified software/CPU results.

**Merge:** child PR stays draft until hosted exact-byte replay, independent analytic audit and Seats 2–4 adversarial review. No original source evidence or public mainline commits are rewritten.
