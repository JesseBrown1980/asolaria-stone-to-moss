#!/usr/bin/env python3
"""Independent host-side real process resource witness for Seat1.

Measures operating-system-reported CPU time and resident memory while REAL
Python/Node workload runs. The process is electrical hardware backed. No
simulated photon count is promoted into an optical instrument measurement.
No hostnames, serials, IPs, environment or private user data are recorded.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

import psutil


def digest(payload):
    return sha256(payload).hexdigest()


def read_energy_domains():
    """Sample accessible *system-level* energy counters, not process watts."""
    result = {}
    if platform.system() != "Linux":
        return result
    root = Path("/sys/class/powercap")
    if not root.is_dir():
        return result
    for entry in sorted(root.glob("intel-rapl:*")):
        # Avoid double counting nested energy planes as if independent.
        if entry.name.count(":") != 1:
            continue
        power = entry / "energy_uj"
        if not power.is_file():
            continue
        try:
            value = int(power.read_text(encoding="ascii").strip())
            max_file = entry / "max_energy_range_uj"
            maximum = int(max_file.read_text(encoding="ascii").strip()) if max_file.is_file() else None
            if value < 0 or (maximum is not None and maximum <= 0):
                continue
            result[entry.name] = {"energy_uj": value, "max_energy_range_uj": maximum}
        except (OSError, ValueError):
            pass
    return result


def package_deltas(before, after):
    """Counter readings are package-shared; only give deltas when unambiguous."""
    deltas = {}
    for name, old in before.items():
        if name not in after:
            continue
        new = after[name]
        a, b = old["energy_uj"], new["energy_uj"]
        wrap = old["max_energy_range_uj"]
        if b >= a:
            difference = b - a
        elif wrap is not None and 0 <= a < wrap and 0 <= b < wrap:
            difference = wrap - a + b
        else:
            continue
        deltas[name] = difference
    return deltas


def run(arguments):
    dest = Path(arguments.output)
    log = Path(arguments.log)
    dest.parent.mkdir(parents=True, exist_ok=True)
    log.parent.mkdir(parents=True, exist_ok=True)

    command = list(arguments.command)
    if command and command[0] == "--":
        command.pop(0)
    if not command:
        raise ValueError("MISSING_WORKLOAD_COMMAND")

    source = {
        "original_source_sha256":
          "02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22",
        "bank_sha256":
          "52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345",
        "index_sha256":
          "6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee",
    }
    expected_file = {
        "original_source_sha256": Path("original-evidence/lightbank-memories.json"),
        "bank_sha256": Path("rainbow-evidence/rainbow7-bank.jsonl"),
        "index_sha256": Path("rainbow-evidence/rainbow7-index.hbi"),
    }
    for key, file in expected_file.items():
        if not file.is_file() or digest(file.read_bytes()) != source[key]:
            raise AssertionError("HOST_SOURCE_NOT_INDEPENDENTLY_PINNED:" + key)

    host = {
        "os_family": platform.system(),
        "architecture": platform.machine(),
        "logical_cpu_count_reported": psutil.cpu_count(logical=True),
        "virtual_memory_total_bytes_reported": psutil.virtual_memory().total,
        "platform_virtualization_custody": "NOT_ATTESTED",
        "named_physical_chassis_custody": "NOT_ATTESTED",
    }
    require_os = host["os_family"] in ("Linux", "Windows")
    if not require_os:
        raise AssertionError("NO_TARGET_HOST_OS")

    system_before = read_energy_domains()
    start = time.monotonic_ns()
    peak_rss = 0
    max_user = 0
    max_system = 0
    samples = 0
    max_threads = 0
    # Do not capture stdout in a pipe without draining: this workload is large.
    # Redirect it to an existing output log, and hash that log for provenance.
    with log.open("wb") as writer:
        proc = subprocess.Popen(command, stdout=writer, stderr=subprocess.STDOUT)
        ps = psutil.Process(proc.pid)
        while True:
            try:
                with ps.oneshot():
                    cpu = ps.cpu_times()
                    memory = ps.memory_info()
                    nthreads = ps.num_threads()
                samples += 1
                peak_rss = max(peak_rss, int(memory.rss))
                max_user = max(max_user, round(cpu.user * 1_000_000_000))
                max_system = max(max_system, round(cpu.system * 1_000_000_000))
                max_threads = max(max_threads, nthreads)
            except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                pass
            status = proc.poll()
            if status is not None:
                break
            time.sleep(0.035)
        code = proc.wait()
    elapsed = time.monotonic_ns() - start
    system_after = read_energy_domains()
    package = package_deltas(system_before, system_after)

    report = {
        "schema": "ASOLARIA-SEAT1-PHYSICAL-HOST-WITNESS-V1",
        "witness_kind": "OS_PROCESS_CPU_RESIDENT_RAM_AND_ELAPSED_MONOTONIC_TIME",
        "workload_label": arguments.label,
        "os_reported_host": host,
        "source": source,
        "command_identity_note": "Original frozen Seat1 deterministic coupling software on the named runner",
        "cpu_user_time_ns_reported": max_user,
        "cpu_system_time_ns_reported": max_system,
        "cpu_total_time_ns_reported": max_user + max_system,
        "elapsed_monotonic_ns_reported": elapsed,
        "peak_resident_memory_bytes_reported": peak_rss,
        "maximum_os_process_threads_reported": max_threads,
        "successful_process_metric_samples": samples,
        "exit_code": code,
        "stdout_stderr_log_sha256": digest(log.read_bytes()),
        "powercap_shared_package_energy_deltas_uj_if_accessible": package,
        "powercap_status": "SHARED_HOST_DOMAIN_NOT_WORKLOAD_ENERGY" if package else "NOT_EXPOSED",
        "operating_system_metrics_are_real_observations": True,
        "executed_using_real_electrically_powered_host": True,
        "ac_mains_supply_confirmed_by_instrument": False,
        "regulated_dc_rail_current_amperes_measured": False,
        "ground_conductor_current_amperes_measured": False,
        "optical_photon_flux_or_spectrum_measured": False,
        "physical_optical_state_retention_measured": False,
        "mechanism_attribution_status": "HOST_ELECTRONIC_EXECUTION_OBSERVED_OPTICAL_MECHANISM_OPEN",
    }
    if code != 0 or samples < 2 or peak_rss <= 0 or max_user + max_system <= 0 or elapsed <= 0:
        report["status"] = "HOST_OBSERVER_FAILED"
    else:
        report["status"] = "PHYSICAL_HOST_PROCESS_OBSERVATION_PASS"
    dest.write_bytes((json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(json.dumps({
        "status": report["status"],
        "label": arguments.label,
        "os": host["os_family"],
        "cpu_ns": report["cpu_total_time_ns_reported"],
        "wall_ns": report["elapsed_monotonic_ns_reported"],
        "peak_rss_bytes": peak_rss,
        "samples": samples,
        "shared_host_energy_domain_count": len(package),
        "witness_sha256": digest(dest.read_bytes()),
    }, sort_keys=True))
    if report["status"] != "PHYSICAL_HOST_PROCESS_OBSERVATION_PASS":
        raise SystemExit(code if code != 0 else 4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--label", choices=("python-coupling","node-coupling"), required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    run(parser.parse_args())
