# Seat 2 Round 9 — source-linked real hosted process activity: verified results

**October 15, 2026. Actual OS-reported host CPU/RAM measurement; electrical and photon instruments not connected.**

## Why this matters

Asolaria source-verified computations execute in the real physical world. CPU time, electronic state changes and RAM allocation happen in powered machines, whether the process is inside a VM/container or not. We must not discard independently verified computational evidence as "nonphysical." Equally, **software-reported process CPU/RAM use is not a direct oscilloscoped voltage, current, photon count or optical memory readback**, and cannot assign a microscopic physical storage carrier by itself.

This is a supplemental **Seat 2 provenance bridge** to Seat 1 physical-device carrier lineage [draft #103](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/103); it does not change previously merged #89/#91 results and does not run the full legacy Rainbow7 bank reconstruction.

## Chronology and trust roots

1. Frozen source in `main` at Git SHA `5d3e3a1147ad7af84c1b5b1ba482dfddd9832c86`, **701-byte merged Seat4 R5 HBP** SHA256 `077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400`; this HBP names the prior original bank SHA `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`. **The HBP itself**, not the original complete 184,815-byte bank, is the new test's measured-workload input.
2. [Preregistered protocol](PREREG-PHYSICAL-HOST-EVIDENCE-BRIDGE-20261015.md) committed **before** executable at `c8f347d9c2644930a6f6f0498d44e93812064b81`.
3. Python source `3334e8e497c30dc2739a63c0d38b4dc3555fbb87`, independent Node review `1e9a3eb4dad9866253dab5e0e67f23c4826cb630`, CI workflow `d463265ea6490b7a0b5f83aefb3db22a0f02bff0`.
4. **Preserved first red attempt**: [Actions #38776850476](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38776850476) failed Node canonical JSON on literal Unicode multiplication symbol in a source algorithm label, while Ubuntu Python had **actually collected** OS CPU/RSS readings. This was a cross-language encoding/serialization bug, not a failure to physically execute.
5. Correction `f6aa867484fb22361e5f21c8eb463fdae7fa2130` substituted an ASCII mathematical label **without modifying the actual deterministic workload, physical counter probe, frozen source or measurements**.
6. **Corrected hosted [Actions #38776972990](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38776972990) 5/5 PASS:** 4 independent Ubuntu/Windows Python3.11/3.13 hosted jobs collected genuine OS process measurements, independently reproduced the exact source-derived 256×2MiB SHA calculation with Node22; fifth job downloaded all four complete artifact bundles, demanded identical **deterministic** digital/Node/instrument-status JSON bytes, and validated each **different actual host-telemetry** JSON SHA individually.

## Measured host execution

OS-reported `psutil.Process.cpu_times()` user+system versus `time.perf_counter_ns()`; 24 MiB real page-touched allocation and `psutil.Process.memory_info().rss` before/during. Values reflect OS-reported process use, with platform-specific timing resolution, **not energy consumption**.

| GitHub hosted environment | Process CPU ns | Monotonic elapsed ns | Observed RSS increase bytes | Per-run host telemetry SHA256 |
|---|---:|---:|---:|---|
| Ubuntu Python3.11 | 350,000,000 | 341,861,467 | 25,169,920 | `f3080ce2003531c499dfc14683d900d001b50b659c1550c905cf64f9ed143608` |
| Ubuntu Python3.13 | 350,000,000 | 347,231,852 | 25,169,920 | `6be6887bdd87292b68608b793a26bc40f2c329b26d18784167410d59a64a2e9a` |
| Windows Python3.11 | 390,625,000 | 389,314,200 | 25,186,304 | `08bba55172f033b981a81e16141e1acb6dc510d493c61243232fadac7062ffeb` |
| Windows Python3.13 | 265,625,000 | 257,441,500 | 25,178,112 | `ae9513a805f3e876031372c6683f018bb0c15f51648485a09947488772b06123` |

Reported CPU time may slightly exceed monotonic wall-time due to OS counter granularity or timing boundaries; it was **not** used to calculate electrical power. Actual host telemetry files intentionally differ because runtime, PID and timestamps are not deterministic. The test did not identify independent underlying physical chassis or measure energy rails.

## Verified four-host deterministic artifacts

- Source-derived deterministic workload SHA256 `ae3474a94a03e024ad41bd6d0c508a18cbb3ed43c551da0ed3c6ec701e5b61cf`, computed on all 4 hosts and separately in Node22.
- `digital.json` 938 bytes, SHA256 `7b47c0270c5818c9d134fe81abcf767e2bacfb10ca72c4b1cae8afec0a17b73b`.
- `instrument-status.json` 1,123 bytes, SHA256 `762bea2272ec6fabcc20e80c0ef540151e90db931ccb37413dff5d727f33591f`.
- `node-review.json` 1,054 bytes, SHA256 `0d2260d3ce712b0bcbe61312d3f8dc1edf47cd3b33261bd909ebaf1cf1ae3023`.
- All canonical SHA sidecars compared in the fifth job. Nine named negative controls rejected **falsified** CPU/elapsed/source/RSS memory and self-declared unmeasured electric/optical readings. These are input/data-integrity negatives, not physical sensor faults.

## Three-layer evidence decision

| Layer | What was measured | Verdict |
|---|---|---|
| Source-bound deterministic computation | Pinned input/read bytes and cross-language output SHA | PASS |
| Execution on a host using physical electronic resources | Real OS process CPU time, elapsed time, resident working-set change | PASS — measured via OS counters, not independently attested hardware meters |
| Instrumented mains AC → regulated DC rails, current/power, protective earth/return, calibrated acoustic or optical signal, photon memory write–dark–read | No attached trusted hardware instruments or raw analog/spectral records | NOT MEASURED |

Power supply architecture is physically meaningful. **Protective earth, chassis ground, circuit common and DC return need not be identical nodes**; measure the appropriate referenced voltages/currents under safe qualified electrical engineering procedures rather than equating all grounds or treating an OS resource counter as a power meter.

The next step is synchronized, independently witnessed sensor capture with calibrated hardware, independently issued challenges, blinded optical storage and sensor evidence; genuine photons/phonons/charge and biological neural activity must not be inferred from synthetic counts alone. Keep PR draft for independent review, no silent source or old-stone changes.
