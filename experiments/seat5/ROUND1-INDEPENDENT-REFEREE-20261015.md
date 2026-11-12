# Seat 5 independent referee — preliminary execution, 2026-10-15

Status: **local independent software smoke test completed; full cross-seat reproduction pending**.

Separate local Python fixture tested: six coherent source substitutions against an externally fixed SHA256 root (6 rejected), nonce replay after loading durable JSON state (rejected), and missing-band cardinalities (81 original rows, 567 seven-band rows, 15,309 logical aliases, 2,187 aliases missing for one band, 27 for one original row).

Two **new simplified synthetic** 15,309-symbol readout simulations (not the Seat3 simulator) used a fixed seven-channel correction. At seven exposures, nominal raw errors 4, corrected 0; changed leakage/background raw errors 488, corrected 5. These counts are preliminary model behavior, **not measured photons, not an independent replication of Seat3's model, and not an authenticated source experiment**.

Local source SHA256: `27e6f496cace6fd641974586e5bec50aa810ed3c961f98b4bf1cda4f09f71c56`.
Local JSON SHA256: `9fb5834996181ff3a240414bb5939293f89b6e6127fef4cff9712d9fff96c0e4`.
These local hashes have not been independently downloaded or replayed from a GitHub-hosted CI artifact.

## Required next referee gates
1. Commit runnable test source, frozen preregistration and CI workflow on this isolated branch, then perform hosted Ubuntu/Windows execution with full raw-byte parity.
2. Verify Seat2 real Ed25519 canonicalization with independently controlled trust roots, not just a digest comparison; durable replay state and verifier-issued nonce.
3. Independently replay Seat3's exact model on a third precommitted seed and changed leakage/noise matrix. Report false positives, false negatives, paired degradation and wrong-map controls at all exposure counts.
4. Audit Seat4's target-dependent toy signal generation; require blinded real sensor data and measured dark intervals before physical claims.

No other seat branches touched. Do not merge until independent review.