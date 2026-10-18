# Seat 2 Round 7 — append-only correction ledger

All failed runs remain publicly discoverable. These corrections modify the **test harness**, not the preregistered synthetic coupling laws, source checksum, or previous immutable scientific stones.

## First CI red: incorrect CLI argument order
- Exact PR head `5f105598431ffd4b64e631eb5fc54c74df890316`.
- GitHub Actions [38772913280](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38772913280) failed the expected `MERGED_SPECTRUM_STONE_PIN_FAIL` gate before computing any simulated factorial records.
- Root cause: `__main__` reversed `OUTPUT` and `MERGED_MAIN` while calling `run(out,merged)`; frozen-source SHA and file were present, not corrupted.
- Correction commit `5558bacc9a18982007bdb77dbc4260ac1b9cb35a`, exact Python invocation order fixed.

## Second CI red: ordering of overlapping negative-fault gates
- Exact corrected head `5558bacc9a18982007bdb77dbc4260ac1b9cb35a`.
- GitHub Actions [38773123810](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38773123810) reached actual malicious-factor mutation and failed on `detuning_spoof_INCORRECT_FAILURE_DUPLICATE_FACTORIAL_CASE`, where the source check had correctly rejected an altered record, but **earlier** than the negative-test's stricter expected `NUMERIC_MODEL_MISMATCH`.
- Mechanism: the modified off-resonance factor matched an existing key; both duplicate and numerical inconsistency were true. This is not a false acceptance and not a falsification of the programmed factorial contrast.
- Correction commit `44241d40c0d72137bb1f3b9d9f5d3e06800fc9bb` checks source factor versus claimed detector observation **before** duplicate-key detection, preserving eventual duplicate rejection, and explicitly documents the fault-stage priority.

## Release policy
A passing independent Python/Node and Ubuntu/Windows CI must be observed and its producing SHA pinned *after* both corrections. Red runs remain part of the artifact history. Full fake 4096-row fixture and all numeric coupling factors remain identical to preregistration. No physical source or neuron evidence is present; real coupling / physical optical retention / biological neural memory remain HOLD.
