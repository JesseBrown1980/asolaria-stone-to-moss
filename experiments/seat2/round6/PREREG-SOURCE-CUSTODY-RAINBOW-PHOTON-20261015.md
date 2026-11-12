# Seat 2 Round 6 — independent signer-custody and light-bank provenance attack preregistration

2026-10-15. Frozen BEFORE Round 6 implementation and results. Scope: synthetic **digital** evidence, not measured photons, optical retention, biological neural memory or independent host custody.

## Immutable upstream anchors
- This branch starts from main `5d3e3a1147ad7af84c1b5b1ba482dfddd9832c86`.
- Seat4 PR #88 exact producer head `76a47f94174076b80f53a7f5db2fbb694866607a`; signer source Git blob `36e8f399b851a5c8d16596ab7a21397e1bef35d6`, verifier source Git blob `767c312791624ebd8d768cb3394c0905b9646122`. Do not edit these historical files.
- Seat3 PR #90 head `4db24bc72e6852bc2363501c59b7c0240f5c357d`. Ordered identity witness `W=(r+4g+3b+4rg) mod 8`.
- Seat1 PR #89 head `e66d9a3d48f4d6115bce969e46cbcd2ab1d3f689`. Archived source roots: source `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`, bank `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`.

## Independent falsifiable predictions
1. Independently derive both Ed25519 **fixture** public keys from the disclosed reproducible test seed formula. Predict exact equal raw public keys `9c64cddd3be7b57eb498f3809f78a346fa3e4ce5bc80869adb867edec8b21c6f` and `eba347587f749f6a0e58e7a6be83081cf1a204e880fe527f82a38063f1da1a0d`. An adversary can sign different content that passes the fixture public-key signature check. This falsifies any claim that fixture signatures *alone* prove independently held custody.
2. Independently enumerate all 27 ordered ternary positions, normalized-or-dark classes, and `W`. Predict 7 classes with sizes [1,2,3,3,6,6,6], 27/27 inversions only given both class and W, and at least one wrong in-class W that constitutes another valid codeword. Separate decoding correctness from origin authentication.
3. Run all 5,039 nonidentity permutations of seven synthetic logical ports. Pinned original port binding must reject ALL; a self-signed adversary-replaced mapping may pass bare signature validation but MUST NOT pass external-root verification.
4. Signed synthetic frames: altered observations with original signature must fail signature check. Re-signed changes by recreated fixture private keys may pass bare signature checks; external trusted source-root, mapping, ordered identity and expected challenge must reject changed origin, stale nonce/epoch, erasure and duplicated sequences. Explicitly report cases that cannot be proven without real independent signer custody.
5. New private unpredictably generated local verifier challenge must reject an old signed frame. A recycled deterministic test nonce cannot by itself prevent whole-session replay when verifier freshness state is reset.
6. A single missing synthetic band is not evidence of seven-band observation, even if ordered identity metadata is retained.

## Outputs / verdict contract
- Independently authored Python cryptography source only; no import of producer code.
- Executable unittest/CLI, an append-only canonical JSON receipt and SHA256SUMS, plus Python >=3.11 Ubuntu/Windows CI. Cross-platform binary evidence should be compared.
- Each case records gate, result, and whether it was actually exercised. `mathematical_recovery`, `digital_integrity`, `signature_consistency`, `independently_authenticated_origin`, `physical_photon_retention`, and `trained_neural_memory` are **separate flags**.
- No secret keys in logs. The fixture seeds are already public in source; test only fixture derivation. Never use a credential pasted into chat.
- Preserve old stones untouched. Do not merge/release before external review; Issue #10's physical/source gates are not promoted by a software PASS.
