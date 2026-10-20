# Seat 1 — Physical-host execution evidence protocol (preregistered)

**Scope:** A real computation on an electrically powered CPU is a physical event. The three evidence layers must not be collapsed into one: (A) verified program outputs, (B) independently obtained OS/host counters, (C) direct calibrated electrical and optical instrument recordings. This experiment obtains **A and selected B** on GitHub Actions Linux hosts and intentionally marks **C NOT MEASURED**.

## Pinned system

- Rust **1.81.0**, offline, no external crates, with `cargo clippy --locked --offline --all-targets -- -D warnings`.
- All experimental arithmetic integer only. Balanced ternary trits `-1, 0, +1`, with unique 27-valued ordered triplet address; 81 base memories × 7 bands × 27 sectors = **15,309 logical references per round**, **not** 15,309 stored memories.
- 128 workload rounds; 1,959,552 deterministic address operations. Prior independent integer calculation freezes workload digest `3b6fe647a64e065f` (unsigned 64-bit hex), using explicit 64-bit rotate and wrapping addition.
- No new optical-memory claims, no simulated detector readings presented as physical data.

## Conditions

1. **Idle control:** sleep 150 ms; record wall-clock epoch milliseconds, monotonic elapsed ns, Linux process CPU ticks, VmRSS (KiB), and optional package energy `energy_uj` if exposed.
2. **Active ternary compute:** execute exactly the frozen integer Rust workload and record the same telemetry plus deterministic output digest.
3. **Active with optical interface:** Only execute if operator sets `ASOLARIA_OPTICAL_CAPTURE_PATH` to an already existing raw capture file. Its existence and byte count do **not** authenticate the sensor or count photons. Record a second active host interval and label `provided_file_unverified`. With no capture input, label `not_run_no_instrument_interface` and null phase: do **not** synthesize readings.

## Physical-custody promotion gate — separate lab evidence required

For a physical-electrical claim, measure AC input and DC rail readings using a calibrated isolated instrument, with device model/serial, calibration date, wiring diagram, uncertainty, raw timestamped capture, signed operator and raw SHA256. An OS package-energy counter (when available) is a *kernel-reported package counter*, not mains AC meter or direct DC measurement.

For optical claims, use a calibrated photodiode/spectrometer with source/sensor identity, dark/baseline/sham/write/erase conditions, acquisition timing and uncertainty. Capture raw detector bytes without preprocessing, their SHA256, calibration, provenance/custody, and blinded labels. A sensor-file path alone remains **UNVERIFIED**. Do not probe live mains or DC rails without qualified personnel and appropriate isolation.

For host counter claims, process `/proc/self/stat` and `/proc/self/status` represent operating-system observations, not direct oscilloscope or ammeter measurements. On shared virtualized GitHub Actions runners, do not claim exclusive access, bare-metal attestation, or three independent physical hosts.

## Precommitted outcomes and failure gates

- `cargo test` must pass frozen-digest, ternary unique-27, invalid-trit and capacity-count checks.
- Clippy `-D warnings` and both debug/release host measurement jobs pass with exact Rust 1.81.0.
- Raw receipt artifacts independently downloaded and SHA256 validated. **Telemetry bytes are not expected to match across jobs** because timestamps, memory allocations and scheduler timing differ. Only the frozen mathematical fields and explicit scope/claims are required to match.
- At least one OS-reported CPU and RAM reading per phase; absent counters are failure rather than invented zeros. Optional RAPL access missing is honest `null`.
- Instrument fields AC input watts, DC rail mV/mA, ground current and detector counts must remain `null` unless actual separately verified capture exists. The hosted workflow deliberately does not attach such equipment.
- This release gate stays **SOFTWARE + OS HOST** even if CI is green, until separate witnessed instrument captures pass custody and calibration review.

No merges in this branch until hosted checks and cross-seat review. PR #105 and all other work untouched.
