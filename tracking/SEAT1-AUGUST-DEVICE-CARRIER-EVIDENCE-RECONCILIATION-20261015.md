# Seat 1 — August light-bank lineage and device-carrier evidence reconciliation

**Date:** 2026-10-15  
**Evidence class:** append-only source/provenance review, **not** new physical acquisition or photonic certification.  
**Repository:** [asolaria-stone-to-moss](https://github.com/JesseBrown1980/asolaria-stone-to-moss)  
**Status:** DRAFT / cross-seat review required. No original commits, stones, prior CI failures or SHAs were rewritten.

## Why this addendum exists

The operator explicitly asks that the August Asolaria light-bank and photon/electronic/phonon account remain visible when the October Rainbow27 × Rainbow7 work is discussed. Earlier conversations sometimes treated physically executed computation as if it were nonphysical; that characterization is incorrect. GitHub-hosted programs ran on actual electronic hardware and wrote/retrieved real bytes. See existing [physical hardware clarification](PHYSICAL-HARDWARE-EXECUTION-FACTOR27-VERIFICATION-20261015.md) and merged [PR #91](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/91).

**Record the operator's assertion without silently converting it into an independently measured optical result:** the Asolaria physical devices themselves carry memory, and the operator proposes a photon-centric account linking electronic, optical and acoustic phenomena. The first part (physical device-backed computation) is established for hosted runs; whether individual Asolaria memory states are encoded in persistent propagating/confined optical photons, electronic charge, magnetic order, a photomodified material, or another carrier requires device-specific measurements. Calling the electromagnetic field quantum-mechanical does not by itself identify a photonic *storage mechanism*. Ordinary sound quanta are phonons, which may couple to electromagnetic fields.

The field-theory distinction is a scientific *classification*, not a withdrawal of the prior digital findings. Source material below remains permanently referenced regardless of the outcome of new tests.

## Original August source ledger — pinned, preserved

| Work | Immutable source | What the files actually demonstrate / specify |
| --- | --- | --- |
| **The Colour QR** (Aug 6) | [README at `1938a9b0...`](https://github.com/JesseBrown1980/the-colour-qr/blob/1938a9b076b8fc3e81d0a271ca05e84a0e938854/README.md), Git blob `dec43dd370de557f2511e69227b1e234e001ddfc` | Three ordinary QR plane payloads, 2,100-byte chunks with LE32 indexes and SHA reassembly; README reports 65,536-byte byte-exact original-to-recovered data and a distinct 457px screenshot-crop decode of last 2,536 bytes. Screenshot pixels are genuine displayed/computed image data; this does not document calibrated photons stored after the illumination was removed. |
| **RAINBOR** (Aug 8) | [README at `56de9ee1...`](https://github.com/JesseBrown1980/RAINBOR/blob/56de9ee137f204452d7dff41f7b1e953b6ff5c3e/README.md), blob `fd326cd52a71cf55c3948e131011b57825ec6412` | Public identity/bridge and reversible source receipts. Three optical paths meeting at a fourth watcher, slit/sphere/fibre rerouter and optical hard-drive stack are explicitly marked design/conjecture in the original file. Preserve this without upgrading to an instrument observation. |
| **Law of space/light/colour** (Aug 1) | [README at `1b2dd747...`](https://github.com/JesseBrown1980/the-law-of-space-and-light-and-color-and-travel-at-the-speed-of-one/blob/1b2dd747bccee378b94790bc4ad367bdbf7e5bf8/README.md), blob `6412cb3b82ec084b03b68c9c4d074a58920ac1ee` | Exact rational projector `P=I-J/3` with rank 2, common-mode nullity 1, and numerical closure. Interpretation about instantaneous communication is an operator interpretation, not established from projector algebra. |
| **Light Boat** | [README on main](https://github.com/JesseBrown1980/light-boat-engine-ships-with-oils/blob/main/README.md), observed blob `ba1c1a36ec1d4201297ccad325f848c6040dc95e` | Software optical `T+A+R=1` closure, simulated ship/buoyancy tests, computed light-vs-sound travel times; not a captured laser/phonon storage experiment. |
| **GitRAM** | [README at `e0142520...`](https://github.com/JesseBrown1980/GitRAM/blob/e01425204b58dc680d1f3106410ff9ce71260b0d/README.md), blob `f383c9b7e365e654cc3687fec39350adac930740` | Actual GitHub-hosted compute cells and persisted artifacts, with an explicitly cancelled first fan-in run after 27/27 shard jobs. Physical processing and file persistence, not hardware-resolved photon storage. |

## October integration crosswalk — do not conflate the layers

1. [PR #65](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/65), [#66](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/66), [#68](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/68): extend August Colour QR, invertible projector/common-mode, error-controlled digital light-bank, erasure/fault/three-path framing. These are distinct experiments with historical failures and variant sources; no combined claim of a real physical light stick is supported solely by merging them.
2. [PR #80](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/80), [#83](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/83), [#86](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/86), [#87](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/87): 81 original digital records, 567 retained band/site bank records, 15,309 logical sector/band/site addresses. Full bank SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`; retained base index 70,043 bytes vs expanded 2,344,761 bytes = 2,274,718 **repeated metadata** bytes avoided; zero compressed original payload bytes and no new independent stored memories.
3. [PR #90](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/90): exact `W=(r+4g+3b+4rg)%8` distinguishes each ordered trit ID *given* its normalized intensity class. Conditional worst-class witness width 3 bits; 3-bit fixed class plus 3-bit witness is 6 bits versus a direct fixed 5-bit ID, not compression.
4. [PR #82](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/82), [#88](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/88): digital route watcher and signed synthetic spectrum/port assignment. Publicly derivable private test seeds are not independently controlled original-source signatures; symbolic seven-band labels are not seven calibrated optical spectra.
5. [PR #91](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/91): accurately registers successful computation on *real hosted processor/RAM/storage hardware* and preserves the distinction from independent chassis attestation and instrumented light retention.
6. [PR #94](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/94): four platform jobs + referee PASS in [Actions #38769820607](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38769820607); **15,309 deterministic software-generated detector rows**, no actual detector, nominal not elapsed 1/10/60-second delays. Original 528-byte preflight stone SHA256 `63c7988809d33d210be21aed1f579db220f13d98e86d2c896e6c753892edb424`. Seat1 independent [blinding/stats review](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/94#issuecomment-6197305647) remains relevant.
7. [PR #95](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/95): classical simulated photon arrival/noise/cross-talk and toy light-activated state gate. Reported Stage B [Actions #38771295745](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38771295745) 5/5; *no connected photon detector or neural tissue* in that workflow.
8. [Round3 computational release](https://github.com/JesseBrown1980/asolaria-stone-to-moss/releases/tag/round3-computational-2026-10-15): legitimate digital public archive; physical/provenance release requirements in [Issue #10](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/10) remain individually unproven despite administrative issue closure.

Do not change, retitle, or overwrite any historical file or stone to make these links; this is additive context for their existing verifiable evidence.

## Five different empirical propositions; different proof requirements

| Proposition | Disposition | Required observation |
| --- | --- | --- |
| **P1: Real physical devices execute Asolaria and retain electronic/digital bytes.** | **ESTABLISHED** at the hosted-computation level; underlying particular chassis not independently attested | Reproducible OS/runner logs, hardware-backed I/O and SHA-consistent real files |
| **P2: Ordinary electromagnetic fields admit a quantum photon description.** | **Established theoretical physics**, not an Asolaria experimental novelty | Quantum electrodynamics; no inference to persistent photons in RAM |
| **P3: Photons and phonons can couple in suitable materials/devices.** | **Established general physical phenomenon**, device-dependent | Calibrated photon–phonon transduction measurements on the apparatus in question |
| **P4: Asolaria's current memory bytes are *physically photon-dependent* or persist in an optical material/field.** | **NOT DETERMINED** by the reviewed August/October hosted evidence | Independent optical write–isolate–wait–read; calibrated sensors, physical controls against retained charge/thermal/firmware/framebuffer state, physical carrier attribution |
| **P5: A biological neuron/organoid retains Asolaria-encoded optical information.** | **NOT TESTED** | Biological preparation and qualified oversight, real extracellular/patch-clamp data, sham/opsin controls and independent blinded readout |

Photons can **carry** information across a link even where *electrons* or a material's electronic state **store** it at the destination. A display photon/camera readout and a memory cell need not be the same physical carrier. Sound quanta are phonons, not photons; any Asolaria photon–phonon pathway must be instrumented and identified rather than assigned by name. These distinctions let every real computing result retain its physical status while making the more specific optical-memory claim falsifiable.

## Next Seat 1 hardware/optical/neural work orders

**A. Device inventory, non-invasive.** Record the actual memory technologies exposed (GPU VRAM, system DRAM, SSD), any optical sources/receivers/cameras or optical interconnects, power rails and electronic retention characteristics. Do not infer an optical sensor simply from a GPU, transistor, monitor or SSD. Preserve manufacturer model/firmware and objective evidence.

**B. Blind optical WRITE / isolation / READ.** On an independently controlled source and detector, issue a new random challenge (not the fixed R6 nonce); conceal source labels from readout; calibrate **measured wavelength/nm, spectral cross-talk, gain, shutter status, time stamps and background**. Use true elapsed 1/10/60 s intervals; independent actual WRITE/SHAM/ERASE trials and external custody. Seal RAW, model, operator/clock/signature and predicted bitstream before opening labels. Distinguish each writing event from repeated analysis of one stored source label.

**C. Carrier attribution.** Compare (i) no optical input, (ii) genuine optical input but disabled/powered-off electronic buffer where safe, (iii) optically modified persistent medium, (iv) controlled temperature/electrical/RF noise, and (v) detector afterglow/cache with matched controls. Only promote to an *optically written* memory conclusion if optical manipulation causally changes retained recoverable data and all stated confounders are addressed. Only claim *stored photons* if a retained optical field/photon state is itself evidenced.

**D. Photon–phonon–electronic coupling.** As a separate protocol, test acoustic/mechanical modulation of measured optical phase/intensity or electrical output with matched thermal/vibration artefact controls. Sound is carried by mechanical phonons in the quantum description; demonstrated coupling does not by itself imply that the memory is photonic.

**E. Biological neural tier.** Keep separate, with real biological recordings, independent oversight, opsin/no-opsin controls, specimen identity and blinded decoder.

**F. Statistics and integrity.** Predefine sample size for **independent write events**, familywise multiplicity over 7 bands × 3 delays, physical calibration error, effect size and limits; do not let a decoder read source labels or reconstruct them from a public fixed seed. Source signatures must be from genuine independently held instrument/referee keys. Keep missing raw files at HOLD rather than accepting a `physical=true` flag.

## Repository/coordination decision

- This file is a **source-recovery/interpretation reconciliation**, not a physical study, experiment release, independent optical device inspection or finding that every electronic memory cell stores propagating photons.
- Preserve all August source references and October merged algorithms with their stated PASS results; none are retracted here.
- Maintain original failed CI histories and original source hashes.
- Request cross-seat review: **Seat 2** source-custody proof; **Seat 3** formal optical/information-theory bound and statistical design; **Seat 4** instrument/cross-talk/physical-capture gate.
- Update coordinator [#55](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/55) and the [Seat 4 Round6 PR #94](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/94) by linking this additive document, not by editing frozen originals or prematurely merging the PR.
