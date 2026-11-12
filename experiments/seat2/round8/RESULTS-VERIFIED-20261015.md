# Seat 2 Round 8 — verified signed-history equivocation and rollback falsifiers

**2026-10-15. Scientifically scoped digital test, not a real optical memory measurement.**

## Publication and source chronology
1. Initial main baseline `5d3e3a1147ad7af84c1b5b1ba482dfddd9832c86`.
2. Frozen hypothesis/preregistration FIRST: `e71f97aed66e2d6d6b570dba738c5ef125c3a004`.
3. Independently written Python Ed25519 fixture producer `5b2a6ca3eea10bdffa4614802430e2e62634a985`; independently written Node22 Ed25519 verifier `0da11e25cfbe39c3d253eaab46aa04883db5ec59`; first workflow commit `3abd252290441dff9185bd28457d1bb4d6bceff1`.
4. **First exact-head hosted [CI #38774754199](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38774754199) 5/5 PASS**: Ubuntu/Windows × Python3.11/3.13 plus fifth downloaded full signed-history JSON/Node raw byte parity.
5. Confirmatory **post-hoc** pins committed **after** observing the first run at `6646c3ca04961704599be8fdd59f0fe8362fec64`; they are version-controlled reference data, **not independently held physical witness anchors**. A separate new Node verifier `3c0e71c6d713cf818e8da3257e7cae3aab7af340` tests the independent argument against this frozen reference. Workflow widened at `1d39d559e0130135464b2e2f1aedb931db4947d0`.
6. **Confirmatory exact-head hosted [CI #38775253851](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38775253851) 5/5 PASS**, with 4/4 OS matrix jobs executing Python/Node/post-hoc pin verifier and fifth downloaded full byte equality.

## Independently executed digital findings
- Three Ed25519 roles SOURCE, DETECTOR, CHECKPOINT using **publicly reproducible private-key fixture seeds** and a deterministic nonce. Digital code verifies real classical Ed25519 math, not independently held private keys.
- Two **distinct** four-frame signed detector histories have the same signed source, session and first two records, then fork at sequence 3. Every individual signature and both complete per-fork hash chains are internally valid. They cannot both equal the same externally expected tip.
- Without independent checkpoint/monotone progress: an old signed full session passes again after resetting the local replay ledger; an alternate chain is valid against its own internals. A source/witness-compromised actor can sign both stories. **Signatures alone do not supply temporal or origin truth.**
- Fixed externally **provided** tip rejects competing fork; externally persistent last sequence 4 rejects duplicate old session. Distinct source-root and physical-channel expected pins block *coherently re-signed* substituted source or port assignment. R8 fixture references are pinned in Git during the confirmatory test, but no true externally operated log is present.
- Python exercised **19 recorded conditions** including positive baseline, actual twin-fork and replay demonstrations and negative holds. New Node confirmatory audit checked **16 distinct planned checks** including re-signed answer-leak metadata and forged signed CHECKPOINT. These are simulated digital observations; no separate photon readout or authenticated real custody was measured.
- Source-blinded protocol strictly rejects `precommitted_bit` and predictable source-seed fields in detector-side signed packet schemas. This prevents these two trivial leakage routes in this *toy interface*, but cannot prove real-world operator blinding or stop side-channel leakage.

## Exact artifacts, 4/4 full-file byte-identical in CI
| Item | Bytes | SHA256 |
|---|---:|---|
| Signed test fixture incl. both histories | 6,595 | `091ab42989b7b0a66a771af5f937bfe1929575d6697be3fe8dadd80c38db0cf7` |
| Python verdict and case ledger | 1,446 | `f0114ee56366b4f13e51b1ea8f1c969f2e5e20d8ef5668ecd132f17b311d525c` |
| Independent Node full-chain verification | 700 | `2a868f30459719885751bd01a4c9e53a0257ac460f391c162c8fcfd74d4f1b91` |
| Confirmatory separate pinned-head referee | 1,154 | `7012ee92e83047190b2ae97704d9d806f0e6dabe5822ec814bc31c2e9a3205ea` |

Signed genuine (fixture) history tip: `f1fcc6155336e4422e3775427e44d07c55a627c58e169b9a3fb6b60b24cec9b5`.
Signed competing (fixture) fork tip: `7a608d10458236d6946c77676f42409f25fe15285cb553df81f6f9a4a39c4144`.

The PINNED-POSTHOC-BASELINE.json is a Git repository reference to the original digital result, **not an authentic independently issued checkpoint**. A malicious repository contributor who can change both verifier and reference can evade it; protection requires independently controlled pins and an external append-only monitor.

## Next external physical/source acquisition requirements
1. Independent source-custodian and detector-custodian key provisioning; publicly authenticated pinned root certificates, independently logged rotation/revocation and separate physical custody. No fixture signer may choose its own trusted root.
2. Referee-issued unpredictable challenge; externally monotonic append-only final checkpoint and fork/notary gossip with persistence across process restarts and independent host reconciliation.
3. Random source bits concealed from detector/decoder, sealed predictions before bit reveal, independent seven-band calibrated spectral capture and physical 1/10/60s dark retention with proper sham, erase, thermal, vibration and electrical nuisance sensors.
4. Independently verify **what physical medium stores the information**. A measured opto-acoustic interaction alone does not establish long-lived photon storage; actual biological neural memory requires instrumented neuronal evidence.

**Verdict:** Software signature/fork/checkpoint falsifiers PASS, real independent source custody HOLD, measured photon/phonon/electronic coupling HOLD, physically written-and-recalled light-bank memory HOLD, biological neural memory HOLD.

Leave PR draft for independent reviewers. No source baseline, historical stone, physical publication or other seat branch modified.
