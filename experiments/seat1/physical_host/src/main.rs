#![forbid(unsafe_code)]
use asolaria_seat1_physical_host::{workload, ADDRESSES_PER_ROUND, FROZEN_DIGEST, ROUNDS};
use std::{env, fs, path::PathBuf, time::{Duration, Instant, SystemTime, UNIX_EPOCH}};

#[derive(Debug)]
struct Sample {
    epoch_ms: u128,
    cpu_ticks: u64,
    rss_kib: u64,
    package_energy_uj: Option<u64>,
}
fn epoch_millis() -> u128 {
    SystemTime::now().duration_since(UNIX_EPOCH).expect("system clock before epoch").as_millis()
}
fn process_cpu_ticks() -> u64 {
    let line = fs::read_to_string("/proc/self/stat").expect("Linux process stat unavailable");
    let rest = line.rsplit_once(") ").expect("invalid process stat").1;
    let fields: Vec<_> = rest.split_ascii_whitespace().collect();
    // /proc/self/stat field 3 -> index 0; fields 14 & 15 are utime/stime.
    let user: u64 = fields[11].parse().expect("invalid user CPU ticks");
    let system: u64 = fields[12].parse().expect("invalid system CPU ticks");
    user.checked_add(system).expect("CPU counter overflow")
}
fn resident_memory_kib() -> u64 {
    let status = fs::read_to_string("/proc/self/status").expect("Linux process status unavailable");
    let line = status.lines().find(|line| line.starts_with("VmRSS:")).expect("VmRSS unavailable");
    line.split_ascii_whitespace().nth(1).expect("VmRSS format").parse().expect("invalid VmRSS")
}
fn package_energy_uj() -> Option<u64> {
    [
        "/sys/class/powercap/intel-rapl:0/energy_uj",
        "/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj",
    ]
    .iter()
    .find_map(|path| fs::read_to_string(path).ok()?.trim().parse::<u64>().ok())
}
fn sample() -> Sample {
    Sample {
        epoch_ms: epoch_millis(),
        cpu_ticks: process_cpu_ticks(),
        rss_kib: resident_memory_kib(),
        package_energy_uj: package_energy_uj(),
    }
}
fn opt_json(value: Option<u64>) -> String {
    value.map_or_else(|| "null".to_owned(), |n| n.to_string())
}
fn phase_json(start: &Sample, end: &Sample, elapsed_ns: u128) -> String {
    format!(
        "{{\"start_epoch_ms\":{},\"end_epoch_ms\":{},\"monotonic_elapsed_ns\":{},\"process_cpu_ticks_delta\":{},\"rss_kib_start\":{},\"rss_kib_end\":{},\"package_energy_uj_start\":{},\"package_energy_uj_end\":{}}}",
        start.epoch_ms, end.epoch_ms, elapsed_ns,
        end.cpu_ticks.saturating_sub(start.cpu_ticks),
        start.rss_kib, end.rss_kib,
        opt_json(start.package_energy_uj), opt_json(end.package_energy_uj),
    )
}
fn measured<T, F: FnOnce() -> T>(operation: F) -> (T, String) {
    let before = sample();
    let monotonic = Instant::now();
    let result = operation();
    let duration = monotonic.elapsed().as_nanos();
    let after = sample();
    (result, phase_json(&before, &after, duration))
}
fn main() {
    let out = PathBuf::from(env::args().nth(1).expect("usage: seat1-host <output-dir>"));
    fs::create_dir_all(&out).expect("cannot create receipt directory");

    let (_, idle) = measured(|| std::thread::sleep(Duration::from_millis(150)));
    let ((digest, addresses), active) = measured(|| workload(ROUNDS));
    assert_eq!(addresses, ADDRESSES_PER_ROUND * u64::from(ROUNDS));
    let digest_hex = format!("{digest:016x}");
    assert_eq!(digest_hex, FROZEN_DIGEST);

    let optical = match env::var("ASOLARIA_OPTICAL_CAPTURE_PATH").ok().filter(|v| !v.is_empty()) {
        None => "{\"status\":\"not_run_no_instrument_interface\",\"phase\":null,\"raw_capture_bytes\":null}".to_string(),
        Some(path) => {
            // The file must already exist, preserving the sensor's original bytes.
            // A file is NOT proof of calibration, photon counts, or source authenticity.
            let metadata = fs::metadata(path).expect("specified optical capture path unavailable");
            assert!(metadata.is_file(), "optical capture must be a regular file");
            let ((optical_digest, optical_addresses), optical_phase) = measured(|| workload(ROUNDS));
            assert_eq!((optical_digest, optical_addresses), (digest, addresses));
            format!("{{\"status\":\"provided_file_unverified\",\"phase\":{optical_phase},\"raw_capture_bytes\":{}}}",metadata.len())
        }
    };

    let commit = env::var("GITHUB_SHA").unwrap_or_default();
    let commit = if commit.len() == 40 && commit.bytes().all(|b| b.is_ascii_hexdigit()) {
        commit
    } else {
        "unavailable".to_owned()
    };
    let receipt = format!(
        "{{\"schema\":\"asolaria.seat1.physical_host.v1\",\"toolchain\":\"rust-1.81.0\",\"source_commit\":\"{commit}\",\"evidence_scope\":\"os_reported_host_process\",\"ternary_digits\":[-1,0,1],\"original_memories\":81,\"bank_entries\":567,\"aliases_per_round\":15309,\"rounds\":{ROUNDS},\"executed_alias_operations\":{addresses},\"deterministic_digest\":\"{digest_hex}\",\"idle\":{idle},\"active\":{active},\"optical\":{optical},\"direct_instruments\":{{\"ac_input_watts\":null,\"dc_rail_millivolts\":null,\"dc_rail_milliamps\":null,\"ground_current_milliamps\":null,\"optical_detector_counts\":null}},\"claims\":{{\"os_reported_physical_execution\":true,\"attested_independent_physical_host\":false,\"direct_electrical_measurement\":false,\"direct_optical_measurement\":false,\"optical_memory_proven\":false}}}}\n"
    );
    fs::write(out.join("receipt.json"), receipt.as_bytes()).expect("cannot write receipt");
    print!("{receipt}");
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn sample_linux_host_counters() {
        let s = sample();
        assert!(s.epoch_ms > 1_000_000_000_000);
        assert!(s.rss_kib > 0);
    }
    #[test]
    fn package_energy_is_never_assumed() {
        assert_eq!(opt_json(None), "null");
        assert_eq!(opt_json(Some(42)), "42");
    }
}
