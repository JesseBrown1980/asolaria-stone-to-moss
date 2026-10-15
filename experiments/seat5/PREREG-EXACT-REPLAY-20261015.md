# Seat 5 exact reproduction preregistration (2026-10-15)

Baseline: local original `seat5_referee.py` SHA256 `27e6f496cace6fd641974586e5bec50aa810ed3c961f98b4bf1cda4f09f71c56`; original `results.json` SHA256 `9fb5834996181ff3a240414bb5939293f89b6e6127fef4cff9712d9fff96c0e4`.

This is an **exact output reproduction of Seat 5's own local software fixture**, not a replay of Seat 2/3/4 code or a physical measurement. An isolated-run adaptation writes outputs into a specified temporary directory, leaving tracked files untouched. Require Windows and Ubuntu Python 3.11 and 3.13 jobs; every job must hash raw JSON bytes to the frozen SHA above and verify persistent replay rejection, six substituted sources rejected, alias counts, and all paired synthetic counts. A fifth job downloads all four output artifacts and compares raw bytes. Any divergence is FAIL. No fixture retuning after CI results.

The trust root is an embedded test constant; no externally controlled key, instrument, actual elapsed dark interval, or attested physical host. This scope is explicitly HOLD for real optical and independent custody claims. Do not merge until the workflow succeeds and independent review is completed.
