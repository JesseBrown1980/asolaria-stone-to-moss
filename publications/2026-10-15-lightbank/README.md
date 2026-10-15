# Asolaria computational light-bank evidence — publication index
**Record prepared 2026-10-15 · public research preprint/index · Hugging Face dataset upload pending**

This is a separate **publication index**, not a merged experimental PR, a peer-certified scientific article or an independently verified photonic-memory device. It records the existing archived outputs and their frozen digests, plus a new upload-ready dataset bundle prepared for [Hugging Face](https://huggingface.co/datasets). The bundle is available to the repository owner for upload; no public HF dataset is claimed to exist until a true remote upload/readback is completed.

## Publication destination

**Recommended type:** Hugging Face **Dataset**, not a trained model or deployed Space.  
**Proposed repo ID:** `Jessedbrown/asolaria-lightbank-four-seat-2026-10-15`.  
**HF public URL after creation:** `https://huggingface.co/datasets/Jessedbrown/asolaria-lightbank-four-seat-2026-10-15`. **NOT YET CREATED / VERIFIED.**

The prepared local dataset bundle is `asolaria-lightbank-four-seat-hf-dataset-20261015.zip`: **11,047,082 bytes**, SHA-256 `0f33c4d65779a5e8ef774f3dfcf65f7c62f559983ad165c4623dabac9c04e1a1`. It holds **45 SHA-256-inventoried files** plus `manifest.json` and `SHA256SUMS`; manifest SHA `6ebec101c729c4f2e43aad9ba49fd7c2c5aa28a245bda191f115e3f36a3a3aa2`. Prepared offline checks PASS (45 file hash checks, 11 RGB composite PNG/32 distinct standard QR symbol decodes/65,536 recovered synthetic bytes, 1,512 snapshot state audit).

The ChatGPT Hugging Face connection available during preparation was authorized for **read-repos**, **not write**, and the local CLI had no publishing session. The dataset bundle has **not** been uploaded on the owner's behalf. Follow [Hugging Face publication instructions](PUBLISH-TO-HUGGING-FACE.md).

## Results included in this scientific record

| Test lane | Exact result | Evidence |
|---|---|---|
| Frozen Phase A optogenetics-inspired benchmark | 8,748 snapshots; SHA `de2c346a92e626403cc5c59b9ffa688d050163fbb48ab8b1cb6a4cde795b0a8b` | [PR #50](../../pull/50) |
| Seat 1 Round2 B synthetic kinetics | 20,412 synthetic snapshots, SHA `208f26fd23f8da5e032b091f238346b386516669c66f3d6ee9323209eafff566` | [PR #64](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/64) · [CI 38727147659](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38727147659) |
| Seat3 four-state/controller research | 2,400 modeled records; HBP SHA `435eccff256d119e608926ba3f3ec46a961d9f0d18801c440de2c3552200101d` | [PR #62](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/62) · [CI 38727513171](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38727513171) |
| Seat4 per-site fault trace | 349,920 site-tick checks; SHA `2b9575a8d46c2d2f0842d590081641ed2b20daddccc7153107d76efa0d597277` | [PR #63](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/63) · [CI 38728353696](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38728353696) |
| Round3 unified synthetic 3/4-state simulation | 4,199,040 transitions, 1,512 full site snapshots; SHA `b4672f15a1003ef1714073eb0664942921f15b6ea8588a39701a42fc9485f8a9` | [PR #70](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/70) · [CI 38734762647](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38734762647) |
| Three-shard checkpoint recovery | 648 exact pair-based recoveries, 9,237,888 synthetic resumed state updates; SHA `f6599677f934509604bcbf0f3a1913ce3f473223cbb08504ef7271e078c55d5f` | same #70 source |
| Colour-QR rendered-software pixel transport | 11 RGB PNGs; 32 actually decoded QR symbols; 65,536 source bytes recovered, SHA `fe3f6f1adb2eb15832bd5d5fd59c2c97bc77b581c5c60f54b768545c756b38c4` | [PR #75](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/75) · [CI 38734983493](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38734983493) |
| Seat4 B3 full bank | 35,608,276-byte archive SHA `2f3a0b27a50a562205a500dd7e38e4318f658cdd05202a4b88312c812ae7ba30`; 27 data banks and separate parity bank | [PR #68](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/68) · [CI 38734811934](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38734811934) |

## Technical interpretation

- The original [Colour QR](https://github.com/JesseBrown1980/the-colour-qr) is three standard indexed QR symbols placed into independently decodable R/G/B pixel channels. Its software PNG readback is **not** optical-material storage.
- The separate [Light Boat](https://github.com/JesseBrown1980/light-boat-engine-ships-with-oils) transmit/absorb/reflect `T+A+R=1` is a classical outcome/closure model, **not** the same 3 channels as the Colour QR or a measured photon memory.
- The projector `P=I-J/3` from the [August space/light/colour source](https://github.com/JesseBrown1980/the-law-of-space-and-light-and-color-and-travel-at-the-speed-of-one) discards the shared RGB mode. Exact recovery needs a retained sideband.
- The new A/B/P digital XOR parity is a two-of-three **erasure recovery**, not authentication, secrecy or an original measured physical memory-stick implementation.
- The synthetic photocycle coefficients, current proxies, optical bank indices and finite control policies are chosen model assumptions, **not fitted measured ion currents, physical photons, hardware hosts, speed-of-light effects or independent biological validation**.
- Identical digest values prove byte identity to a pinned reference, not a trusted external physical source or four independent hardware witnesses.

## Publication conditions

The computational traces are real archived software outputs with uploaded GitHub Actions evidence and selected independent byte-level checks. Still outstanding: cross-seat source/provenance referee objections, *independent four-seat acceptance*, photo-to-camera robustness, physical optical memory write/read and retention, experimental optogenetic calibration, human release authority for physical or external claims. Previous failed CI/correction histories remain linked to their original PRs. **No prior experiment has been merged or relabeled as physical proof by publishing this index.**

[Coordinator #69](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/69) · [Round2 coordinator #55](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/55) · source experiments remain individually reproducible and independent.
