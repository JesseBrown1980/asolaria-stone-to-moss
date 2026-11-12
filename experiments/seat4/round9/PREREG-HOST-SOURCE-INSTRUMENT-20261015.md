# Seat 4 / Round 9 — Real host-process activity joined to source-pinned computation

Date: 2026-10-15. **Prospective protocol committed before executable code and before results.** This is an independent Seat4 bridge from operator's three-layer evidence standard and physical gate Issue #101. Separate from Seat4 #102 thermal confound, Seat1 #106 source-dependent photon/phonon software model, and Seat3 #109 mechanism rank/identifiability.

## Claim hierarchy and source

**Layer 1 computational:** fetch PREVIOUSLY PUBLISHED original GitHub Actions PR80 run 38745842295 artifact `ordered27-rainbow7-ubuntu-latest`; immutable actual 184,815-byte bank SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`, original 81-source JSON SHA `02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22`. Original producer source git head `7b5faf1103a7b42b603b44b08a5a5bfa994d0f76` pinned. Preserve originals.

**Layer 2 actual OS-reported work:** perform 4,096 repeats of SHA256 update over full original 184,815-byte bank, i.e. **757,002,240 input byte passes**, plus an explicitly allocated and touched 4 MiB private process buffer while benchmark is active. Record Python process CPU time monotonic `process_time_ns`, elapsed monotonic wall time `perf_counter_ns`, tracemalloc allocation peak and process peak resident memory (Linux resource maxRSS in KiB; Windows WinAPI PSAPI process peak WorkingSet bytes). Record OS/version, interpreter, GitHub run ID, runner name, declared container/VM indicators when visible, audit root and work-hash. No assumptions that four CI combinations are four distinct privately owned machines: hosts may be VMs, reused or colocated; guest CPU counters may be virtualized and are **not calibrated wattmeters**. Host identity fields are CI provider claims, not independent hardware signatures.

**Layer 3 optical/electrical:** none currently available in this workflow. Explicit machine-readable `measured_ac_wall_energy_joules=null`, `measured_dc_rail_voltage_volts=null`, `measured_dc_current_amperes=null`, `measured_optical_photon_counts=null`, `measured_acoustic_phonon_counts=null`, `spectrometer_raw_sha256=null`. Neither real OS CPU timing nor successful model SHA proves direct optical or energetic mechanism.

## Protocol acceptance

1. Independently written Node22 verifier recomputes original **same 4096-pass full-bank SHA digest** from input archive without importing Python. Compare exact scientific source/bit-level workload fields on every platform. Avoid requiring same OS-dependent time/memory metrics; these are naturally different, and manufacturing byte-identical values would be a red flag.
2. Four computation jobs Ubuntu/Windows × Python 3.11/3.13. Fifth job downloads full run outputs, independently checks SHA sidecars; all 4 cryptographic work digests must be byte-identical while each host activity report's numeric CPU/wall/tracemalloc remains separate, positive and honest. A fresh wrong bank byte, wrong workload iteration count or changed expected digest must fail.
3. Publish source SHA, stable workload hash and actual host numeric observation reports. The results may support `PHYSICALLY_HOSTED_CPU_WORK_CONFIRMED_BY_PROVIDER_TELEMETRY`, **not independent utility wall meter, DC rail oscilloscope, photodetector, optical storage, quantum physics or real neural electrophysiology**. A process hosted inside a container is a software isolation unit running on physically allocated compute, not a separately attested physical host by itself.
4. Actual power requires instrument-read synchronized W(t) or AC V(t),I(t),phase and integration; PSU inefficiency and rails must be acknowledged. Circuit return paths and protective earth are separate electrical functions; grounding is NOT an additional energy source.

## No physical promotion

This specifically **does not run** a shuttered optical write-dark-retain-read, independently sampled wavelengths, instrumented optomechanical coupling or biological neural memory. If only simulated photon counts from #106 exist, treat those as model outputs linked to physically executed processes, not as optical sensor readings. Keep PR DRAFT, original evidence unchanged and public physical claims explicitly HELD.
