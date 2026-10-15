# Seat 1 — Three-layer physical evidence bridge: preregistration

**Date:** 2026-10-15. **Scope:** extend [PR #106](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/106), [issue #100](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/100) and the earlier [merged hosted-compute evidence #89](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/89).

**Protocol must be preserved before instrumentation code is authored.** No changes to existing digital source bytes, photon/phonon model equations, PR #106's original 12 scenario results, or 6,804-frame HBP evidence.

## Three distinct observation levels — link, never conflate

**L1 — digital model outputs (verified):** original 81 QR memories and 567 full-byte Rainbow7 bank rows / 184,815 retained source bytes; source bank SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`, full 6,804 frame HBP SHA256 `42f3b61117a2e771f4f21958e12771b92b7a5d7251d023dc9ab78b34c65f6058`. Independent Python/Node and cross-OS results are fixed. A model photon count is a variable in this computer program, *not* a photodetector reading.

**L2 — host process activity (the new directly observed layer):** run the existing frozen Python and Node models as actual child processes on **two GitHub Actions hosted runner environments**, independently sampling OS kernel process counters via Python's `psutil`: monotonic elapsed wall time, child process user and system CPU time, observed resident-memory bytes (RSS/working set), threads and OS I/O counters when available. Record the full time-series; seal the resulting per-OS receipt and raw samples with SHA256 and bind them to the exact model source/output files, CI commit and run ID. This is *measured host activity*, not hypothetical CPU usage. Linux and Windows are two software run environments; do not assert two separately attested underlying physical chassis or externally calibrated hardware power.

**L3 — electrical/optical instrument readings (not connected in this experiment):** actual AC mains voltage/current/watt-hours, DC rail voltage/current/charge, ground potential or impedance, GPU board power, optical source power/spectrum, measured optical detection and acoustic transducer amplitude/frequency require an actual calibrated corresponding sensor/interface. All fields remain explicitly `measurement_status=NOT_INSTRUMENTED` unless such a sensor source and acquisition file are supplied. GPU execution, switching transistors, electromagnetic fields and data-center electricity are physical, but the OS process CPU counter alone is not a calibrated wattmeter, ammeter, photon counter, or oscilloscope.

The three layers are **complementary**. The new L2 data can establish real program activity on OS-managed physical computing infrastructure and strengthen traceability of the frozen outputs without asserting the stronger L3 claims.

## Frozen acceptance checks

1. Take original 81-source QR → 567 full byte-bank chain with exact trusted SHA, rebuild both original PR #106 producers unchanged on Ubuntu and Windows.
2. Wrap the existing producer command in `host_measure.py`, one Python and one Node child per hosted OS. **No change to producer code**. Sample each live child's kernel process CPU times, resident memory, threads and I/O. Use a monotonic clock, record UTC start/end, exit code, sample count and last sampled counters. psutil RSS is a sampled resident set / Windows working set and **not** total GPU VRAM or machine energy.
3. Full cross-language and cross-OS output HBP/JSON must still equal the frozen original digests. Host metrics are *expected to differ by host* and must never be required to match numerically; the invariant is identical modeling output with nonzero, internally consistent measured host activity.
4. Independently parse every raw time-series sample; reject a missing sample ledger, nonmonotonic CPU time, nonmonotonic sample clock, invalid negative RSS, mismatched raw SHA, forged source/HBP manifest association, false `optical_measured=true` claim, and incomplete original source bank. Require at least 2 observed samples, process CPU time >0, RSS >0 and clean subprocess exit on each of four OS/language runs.
5. Negative-control suite actually mutates a real raw sample or header and rejects without relying on a producer self-assertion. A coherent attacker with access to the log and both SHA files is not externally authenticated by these self-generated digests.
6. Link the four provenance receipts to the source bytes, model HBP, original CI head and the new GitHub Actions run. Include *explicitly unmeasured* placeholders for AC/DC, grounding, GPU physical charge/current, optical photons and acoustic phonons. Do not fabricate their numeric readings.
7. Distinguish L2 *process/kernel counters* from external electronics measurements, and `measured_by_os=true` from `externally_physically_attested=false`. Preserve ordinary hardware-compute `PASS`, while photon-state memory or real neural coupling remain separately unmeasured.

## Source snapshot

This child experiment is stacked on the current PR #106 head `48eaf81991c94e9aab1b69e06dad0e05464cea08`, preserving its original prereg, its two full CI passes and all historical receipts. Existing PR #93, #97 and #106 remain reviewable and unmerged. No new optical measurement is claimed in this preregistration.

## Next physically instrumented extension

Attach a calibrated wall power meter and DC bus meter (or independently validated hardware counter), ground test, optical source + detector and accelerometer/phonon transducer to a host or a separate optomechanical device. Link their raw timestamped traces, calibration and acquisition signatures with this same output HBP root. **Electrical draw and optical memory are measured only when an actual instrument records them.**
