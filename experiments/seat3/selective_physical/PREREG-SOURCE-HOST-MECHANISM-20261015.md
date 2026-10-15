# Seat 3 — Physically executed computation, source continuity, and selective intervention: frozen protocol

**Frozen 2026-10-15 before implementation.** Stacked on draft PR #109 at exact parent `414d4746982449e85ab6ac8ebb71388850fc2842`, preserving all prior mathematical and source evidence. No scheduled paid external jobs, no merges, no physical-device control from CI.

## Correct operator-reported historical evidence classification

| Evidence | Classification | Gate |
| --- | --- | --- |
| Asolaria computation and device-backed memory operations | **Verified**: CPU/software ran on real powered electronic hardware | Previous source-pinned CI, original source/payload bytes |
| Historical August optical / neural light-bank experiments | **Historical public records located**, retain priority and original context | Distinguish digital receipts, local observations and original reported experiments |
| Physical photon-memory experiment | **OPERATOR-REPORTED COMPLETED** | Exact instrument raw records, measured write-dark-read times, controls and calibration need independent examination; do **not** label experiment NEVER PERFORMED |
| Independent validation of this particular instrument capture | **NOT YET ESTABLISHED from files inspected** | Acquire original instrument/time/uncertainty chain with independent witness |
| LIRIS SH pre-light repeated local observation | **OPERATOR_OBSERVED / LIRIS_MEASURED_REPEATED, reported local result** | Public numeric timing trace and external validation unsealed; avoid falsely classifying as an unperformed experiment |

**Historical source pins independently found by Seat3**:
- [LIRIS SH Pre-Light Quantum Receipt](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT/tree/69af655d7c52ddfffcfa62948737cc334d890725) at public pinned commit `69af655d7c52ddfffcfa62948737cc334d890725`; [PUBLIC-MEASUREMENT.hbp](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT/blob/69af655d7c52ddfffcfa62948737cc334d890725/PUBLIC-MEASUREMENT.hbp) is 1642 bytes, published HBP SHA256 `d9b20742592e6fdcb26c03278bd9d574636f4f9f05b24cf502ad173d20e5579f`. It claims a repeated, locally observed `ONE_SHADOW_KEY_CHANGE → INSTANT_PLAY_FREEZE_CHANGE` with `LIGHT_ARRIVAL_GATE=0` and explicit source/operator `QUANTUM_BY_DEFINITION` interpretation; the public packet states `t_sh_ns,t_light_ns,delta_t_ns,uncertainty_ns,trials=UNSEALED`, `independently_remeasured=0`, and `third_party_validated=0`. This is genuine published **reported experimental history**, not a calibrated photon-memory retention trace or independently confirmed quantum/FTL effect.
- [Metatagging public history pointer](https://github.com/JesseBrown1980/Metatagging-data-for-a-Quantum-universe/blob/99f9c52ac1706b395dcc1910006fc2a29bd6d9be/docs/LIRIS-SH-PRELIGHT-PUBLIC-POINTER-2026-08-04.hbp) at commit `99f9c52ac1706b395dcc1910006fc2a29bd6d9be`. Keep the five distinct named HBI/HBP/SHA/SH/HASH slots intact; do not collapse SH into SHA or HASH.
- LIRIS independent timing test is precisely defined in original `PROTOCOL.md`: one calibrated clock; PRE_LIGHT_SEPARATED only if `t_SH+u_SH < t_light-u_light`. Values absent from public record remain **UNSEALED**, not zero, instantaneous measured nanoseconds, or an inferred FTL channel.

## The new exact mathematical falsifier

Old PR #109 blocker B vs RF shield S intervention design: optical component `alpha(1-B)`, independent electronic pickup `beta(1-S)`, blocker-linked electronic pickup `gamma(1-B)`: rank2 in the 3 coefficients, null `(1,0,-1)`. Add new selective optical attenuator Z whose **electronic pickup cross-sensitivity eta** is declared, not assumed to be absent:

`y(B,S,Z)=alpha(1-B)(1-Z)+beta(1-S)+gamma(1-B)(1-eta*Z)`

**Exact rational preregistered tests:**
1. Compute rank of all eight binary B,S,Z rows at eta `0,1/4,1/2,3/4,7/8,15/16,1`: rank3 for eta != 1, rank2 for eta = 1. Baseline B/S 4-row (Z=0) rank2.
2. For three rows `(0,0,0),(0,0,1),(0,1,0)`, matrix determinant **1−eta**. For eta near 1, parameter recovery is ill conditioned.
3. Recover from Y at `(0,1,0),(0,1,1),(1,0,0)` via gamma = Y(0,1,1)/(1−eta), alpha=Y(0,1,0)−gamma, beta=Y(1,0,0) for eta != 1. Use test coefficients (alpha,beta,gamma)=(23,7,11), exact rational outcomes.
4. If eta uncertainty interval contains 1, publish `CALIBRATION_HOLD`. A 1-unit independently bounded error in each matched contrast leads to worst-case parameter-gamma amplification `1/(1−eta)` and alpha bound `1+1/(1−eta)` for exact eta. These are modeled error bounds, not observed uncertainty.
5. At eta=1 explicit distinct mechanisms (alpha,beta,gamma)=(23,7,11) vs (29,7,5) yield all eight identical y observations.
6. Thermal confound original four light/acoustic arms `[1,L,A,LA,(L+A)^2]` rank4/5 due to `T²=L+A+2LA`. Include independently varied H=0/1 with `T=L+A+H` and six columns `[1,L,A,LA,T,T²]`. Check rank **before** claiming independence (whether rank6 is actual should be established by test, not assumed); H constrained to 0 should remain rank-deficient. Do not present an imaginary H switch as an actual heater measurement.

## Physical host process resource evidence (separate from calibrated electrical measurement)

Execute a source-bound fixed real computation on GitHub Actions; collect **actual OS process** monotonic elapsed_ns (timer resolution as reported), CPU time_ns from process_time_ns, `ru_maxrss` (OS native units and conversion labeled), Python `tracemalloc` peak allocated bytes and OS/VM identity labels. Record workload SHA and source pins, start/stop timestamps, pseudonymous run/workload ID. Apply resource counters to the **same process that performs** 567 SHA checks and exhaustive rational tests. An OS process-reported CPU time or RSS is physical host usage **proxy**, not calibrated volts/amperes/joules/watts or proof of a physically unique machine; GitHub-hosted VMs need not provide host physical chassis IDs. The counters are expected NOT to be byte-identical across OS runs. Therefore separate them in a **volatile telemetry** file; keep deterministic exact math receipt/stone byte-for-byte across Ubuntu/Windows. Record telemetry per matrix job and audit schema/ranges, not exact equality.

### Physical evidence join schema and external gates

Document `source_sha256, code_commit, run_id, vm_context, monotonic_wall_ns, process_cpu_ns, peak_rss_bytes_or_native_unit, traced_python_alloc_peak_bytes, instrument_calibration_id, optical_detector_original_raw_hash, real_electrical_meter_trace_hash, mechanical_sensor_raw_hash, physical_write_dark_read_actual_elapsed_s, independent_sensor_signature`. Never fabricate direct instrument fields. If absent, `NOT_MEASURED` or `OPERATOR_REPORTED_INSTRUMENT_DATA_PENDING_REVIEW` where appropriate. Consistent with existing published history: past reported photon-memory run is **not** reclassified as nonexistent simply because we cannot access its raw sensor files.

## Acceptance and peer review

Implement pure independent Python and Node22 exact rational rank/inverse calculations with a third independent verifier; actual source bank all 567 SHA-verified; hosted Ubuntu/Windows × Python3.11/3.13, fifth exact deterministic receipt byte parity and per-job host telemetry semantic validation. Negative controls include corrupt original bank, modified receipt, malformed calibration eta and deliberately false claim that telemetry proves photon power. No physical optical/phonon sensor is connected **to this new GitHub CI**; that is `NOT_INSTRUMENTED_IN_THIS_RUN` rather than a statement that the operator's earlier physical experiment did not take place. Challenge source authority and mechanism in independent cross-seat comments; keep PR DRAFT pending peer review and independent external instrument verification.
