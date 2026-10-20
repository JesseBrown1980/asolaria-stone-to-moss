# Seat 2 Round 8 — authenticated light-bank histories, equivocation and rollback preregistration

Date: 2026-10-15. **Committed before implementation**. This is a NEW source-custody protocol falsification; unrelated published stones and ongoing Seat 1/3/4/5 branches must remain unchanged. Baseline `main` commit `5d3e3a1147ad7af84c1b5b1ba482dfddd9832c86`; previous Seat 2 Round 6 draft PR #96 and Round 7 draft PR #104 remain independent. Seat 4 signed digital mapping baseline merged PR #88; original 81-memory source root `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`; 567-bank SHA `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`. These externally *configured* expected values never come from the candidate frame.

## Question
Can valid Ed25519 signatures and a local SHA256 hash chain guarantee that a reported optical observation is unique, fresh and ordered? **No**: under control of the signing-key fixture, an attacker may produce a competing fully signed chain (equivocation) or roll back local state. Can an **externally pinned, independently maintained sequence/head checkpoint** detect these two classes of deception? Test with explicit same-key and same-sequence forks.

## Frozen synthetic protocol
- Three **role-separated fixture** Ed25519 keypairs SOURCE, DETECTOR, CHECKPOINT. For deterministic cross-OS replay, privately derived seeds are deliberately hardcoded from public constants in the test implementation; all three keys are COMPROMISABLE FIXTURES and cannot prove real independent physical custody.
- Domain separation: `ASOLARIA-SEAT2-R8-SOURCE-V1\n`, `ASOLARIA-SEAT2-R8-OBS-V1\n`, `ASOLARIA-SEAT2-R8-CHECKPOINT-V1\n`. Canonical sorted-key compact UTF-8 JSON followed by LF is the signed material.
- Signed SOURCE manifest binds protocol version, original source SHA, seven-label ordered map, 27 ordered sectors, session ID and challenge nonce. Source identity roots are verified against **out-of-band pins**, not supplied by the candidate packet.
- Signed DETECTOR envelopes bind an opaque trial ID, logical band, sector, site, externally supplied challenge nonce, sequence, previous chain digest, timestamp *label only*, detector count as a **synthetic integer**, and digest of the signed SOURCE manifest. **No true bit / deterministic source-bit seed / precommitted_bit field** is allowed on readout side.
- Header genesis `SHA256(domain || signed SOURCE bytes)`. Each frame link is `SHA256(domain || canonical signed DETECTOR envelope)`. Local frame verification requires Ed25519, consecutive sequence, signed source-root/map, known nonce, exact previous link, duplicate prevention and allowed fields.
- Independently signed CHECKPOINT binds session ID, source manifest digest, exact final seq and chain tip. Its digest/expected trusted public key must be pinned outside the candidate report. A signed checkpoint is still not independently trusted when the test key is publicly reproducible.

## Required 12+ adversarial controls
1. Genuine signed four-record chain: PASS *synthetic protocol consistency*; external exact tip+seq check PASS.
2. Two *different* fully valid and correctly signed histories with same SOURCE, sequence numbers and shared history before a fork. Both pass pure signature+local hash-chain checks. Joint fork checker MUST flag equivocation. Only one matches independently pinned canonical tip.
3. Replaying previous chain with restored/reset local ledger: locally passes again; independent external checkpoint with monotone last seq MUST reject rollback/replay.
4. Same nonce from old session, old sequence, substituted SOURCE/root, altered ordered port mapping, altered detector count without signature, missing record, reordering, changed prior link, wrong opaque trial ID, invalid band, invalid sector, duplicate record all must fail closed under explicit independent pins and sequence invariants.
5. Inject `precommitted_bit` or a reproducible public bit seed into a detector readout: strict detector schema rejection. This is a boundary to prevent a trivial decoder shortcut, not full real-world blinding or source-custody verification.
6. Forging entire signed checkpoint with **public fixture checkpoint key** may pass signature verification but MUST fail comparison to an out-of-band pinned checkpoint digest. A true external signer + durable external log is REQUIRED for authenticity.

## Expected digital evidence
Source + detector + independent checkpoint fixtures, two competing signed four-record histories, 12+ actual negative controls, deterministic canonical source/chain/checkpoint hashes, separate verification of both chains, and independent Node22 Ed25519 checker that does not import Python code. Every OS/Python job must independently execute and verify, and the fifth CI job must download and compare all canonical artifacts byte-for-byte. No full physical spectrum, photons, measurable wall-clock retention, NIST-style optomechanical device, neuron, or independent remote signer appears in this test. `SOURCE_INDEPENDENTLY_ATTESTED=false`, `PHOTON_RETENTION_MEASURED=false`, `BIOLOGICAL_NEURAL_MEMORY_MEASURED=false` always.

## Promotion and failure policy
Any fork, rollback, public bit leak, or altered external expectation accepted at the same strict trust boundary is a FAIL; failure must be logged and corrected in append-only ledger, NEVER silently relabeled. Source commits/hosted CI SHA and raw receipts are mandatory. No automatic merge; leave PR draft until cross-seat review. Administrative status of release Issue #10 does not certify optics.
