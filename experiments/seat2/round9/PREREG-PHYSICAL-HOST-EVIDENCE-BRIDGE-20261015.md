# Seat 2 Round 9 — source → executing process → host counters → instrument boundary

**October 15, 2026. Preregistration committed before any executable or results.**

## Physical starting point

The user correctly identifies running computations as physical: host CPU instructions, memory transactions and semiconductor electrical activity occur using powered hardware. Containers and virtual machines are logical isolation mechanisms implemented on physical computers. Supply AC→DC regulation, current paths, ground and return are real physical system aspects, but a CI log alone **does not measure** their individual voltages, currents, power, grounding impedance, photons or energy consumption.

This experiment bridges *existing verified digital computations* to contemporaneous **operating-system-measured host process activity**. It deliberately leaves independently calibrated electrical, optical and photon-retention readings as missing rather than guessing. No previous computational result is retracted.

## Pinned original Asolaria source

Merged `main` exactly at `5d3e3a1147ad7af84c1b5b1ba482dfddd9832c86`; use unmodified 701-byte `stones/2026-10-15-rainbow81/seat4-round5-signed-spectrum-mapping-20261015.hbp`, SHA256 `077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400`. The HBP refers to original retained bank SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`, itself **not** directly copied into the measurement. Original source, prior stones, PR #89/#91, Seat1 #103 and unfinished Seat2/3/4/5 branches remain unchanged.

## Test A — measured real OS process activity, not a simulated detector

Each Ubuntu/Windows Python3.11/3.13 hosted job must:

1. Read and SHA-validate the **same 701-byte frozen source** at the exact frozen Git commit, and separately record the producing PR HEAD via environment.
2. Record its actual process ID, hosted job identifiers, UTC start/end, monotonic elapsed nanoseconds, process CPU user+system time via `psutil.Process.cpu_times()` and process RSS working-set bytes via `psutil.Process.memory_info().rss`. These are **OS-reported process measurements**, not instrumented current/photons.
3. In the measured interval, touch every 4096th byte of an allocated 24-MiB `bytearray`, capture RSS while the allocation is live, and repeatedly SHA256-hash a deterministic, 2-MiB payload derived from the original HBP (`256` consecutive blocks). Output workload SHA independent of OS, actual CPU-time/elapsed-time and measured pre/during RSS. Keep the allocation alive until in-phase measurement. Neither memory RSS nor CPU time can be inferred from the synthetic content.
4. Report whether RSS increased and whether CPU/monotonic time advanced; fail if process resource counters show zero or invalid timing. Small OS jitter is expected; *do not* require identical telemetry across distinct physical hosts. Preserve actual recorded values per job and hash the exact raw host JSON bytes.
5. Store a **separate instrument-status record** for AC input, DC rails, voltage/current/power, supply-ground observations, calibrated optical spectrum, phonon displacement and optical write–dark–read: all `measured=false`, `value=null`, `instrument_id=null`, until external actual sensors and provenance are supplied. A self-declared `physical=true` must not promote a measurement.
6. Independently authored Node 22 reviewer must recompute deterministic digest from the **actual pinned HBP**, validate real process counters and timestamps independently of producer Python, fail on fake missing values and false sensor status, and produce a separate review JSON.

## Test B — adversarial controls

Actively reject mutated HBP source byte/root, changed executable expected workload SHA, zero or backwards CPU/elapsed monotonic counters, unsupported CI run/source association, false optical/electrical "measured" fields without instrument packets, impossible negative RSS or absent independent host context. These are deliberate digital telemetry integrity challenges, not a physical detector spoof test. A reporter that controls the whole filesystem and its software signing keys can forge both telemetry and hashes; OS counters without **separately secured instrumentation** do not constitute trusted physical host attestation.

## Reproducibility and comparison

Four independently hosted jobs: Ubuntu/Windows × Python3.11/3.13, with process readings and two-language deterministic digest comparison. Fifth job downloads all four artifacts; requires byte-identical deterministic digital calculation and **separately valid, correctly hashed per-host telemetry** without requiring telemetry bytes to match. Exact commit SHA and URLs must be reported only after hosted success is observed. Physical host operation is expected by design; no distinct chassis identity is guaranteed by jobs alone.

Results must report THREE separate axes:

- `digital_source_and_output_verified`: SHA and independent recomputation.
- `host_process_activity_measured`: OS timers/CPU time/RSS during this executable on a hosted runner.
- `electrical_or_optical_sensor_readings_measured`: false until calibrated external instrument raw records exist.

Use this bridge alongside Seat1 physical device inventory and future optical-source and electrical rail acquisition, not as a substitute for calibrated actual current/photons, persistent optically stored information, or living neuronal measurements. Draft review required; do not merge or promote optical mechanism merely for CI PASS.
