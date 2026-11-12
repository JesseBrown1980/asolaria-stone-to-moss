# Seat2 append-only correction — positive CPU counter is unauthenticated by CI context

October 15, 2026. This correction is committed **before** editing the adversarial test acceptance logic. Preserve original successful [run 38777263894](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38777263894), and first attempted new-review run [38782110065](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38782110065), which observed a real **failed negative test**: the actual Node verifier **accepted** a positive CPU-time value increased by 10,000,000 ns when the corresponding unsigned JSON SHA256 sidecar was recomputed. Exact initial failure: `AssertionError: ('FORGED_UNSIGNED_HOST_REPORT_ACCEPTED', 'counter_cpu_positive')` (Ubuntu3.11). This is expected under the model: GitHub job context authenticates which job reports bytes, but not the internal truth of an arbitrary CPU counter inside an untrusted/malicious producing process.

## Disposition and revised falsification matrix

Keep the original seven constructed attacks (each changes actual JSON bytes and recalculates its local SHA sidecar):

- `counter_cpu_positive`: **EXPECTED LIMITATION** — Node source/context/format check accepts a plausible positive number; record `UNSIGNED_CPU_COUNTER_PROVENANCE_UNATTESTED`, not `COUNTER_FORGERY_REJECTED`.
- `run_id_numeric_wrong`: **MUST REJECT** against current `GITHUB_RUN_ID`.
- `producer_sha_valid_40_wrong`: **MUST REJECT** against current `GITHUB_SHA`, which is PR synthetic merge SHA, not source branch head.
- `runner_os_and_platform_consistent_but_wrong`: **MUST REJECT** against `RUNNER_OS`.
- `github_job_valid_looking_wrong`: **MUST REJECT** against `GITHUB_JOB`.
- `fake_device_current_with_forged_sidecar`: **MUST REJECT** unsupported instrument readings.
- `combined_counter_and_run_and_sha`: **MUST REJECT** because run and merge identifiers are false, even though counter itself is not externally attested.

**Acceptance:** 6/6 source-context/sensor identity attacks rejected plus 1/1 expected unauthenticated positive-counter attack **accepted** and explicitly documented as a known measurement-authenticity gap. 5/5 hosted CI, source deterministic SHA unchanged, all 9 original negative controls still rejected; physical running CPU remains established. Future hardware-secured counter signatures/attested hypervisor telemetry may address counter-level custody; don't invent sensors. All originally reported photon-memory August history retained separately.

This correction is non-retroactive. Do not rewrite the original first failed run or claim all 7 attacks rejected. Keep PR111 draft, cross-seat Issue #117 open, and let other seats review independently.
