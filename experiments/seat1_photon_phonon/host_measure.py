#!/usr/bin/env python3
"""Physical compute activity bridge: measure REAL child kernel CPU/RSS counters.

Each child runs the original pinned mathematical experiment unchanged.
Kernel-reported CPU/RSS/IO are measured host-process activity, NOT AC/DC power,
charge movement, individual transistors, GPU current or photonic detection.

Usage:
  python host_measure.py --label python-coupling --output host-python \
      --original original-evidence/lightbank-memories.json \
      --bank rainbow-evidence/rainbow7-bank.jsonl \
      --index rainbow-evidence/rainbow7-index.hbi \
      --hbp py-coupling/coupling.hbp --result py-coupling/results.json \
      -- python experiments/seat1_photon_phonon/coupling.py ...
"""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import psutil

PIN_ORIGINAL = "02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
PIN_BANK = "52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
PIN_INDEX = "6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"
PIN_HBP = "42f3b61117a2e771f4f21958e12771b92b7a5d7251d023dc9ab78b34c65f6058"
PIN_RESULTS = "4debac19eb1238bb8495018f115aa53494705934ff304129f2f4807920c99804"
SCHEMA = "ASOLARIA-PHYSICAL-PROCESS-KERNEL-TELEMETRY-V1"
READINGS = (
    "ac_mains_voltage_current_or_energy",
    "regulated_dc_bus_voltage_current",
    "ground_potential_or_return_current",
    "semiconductor_charge_flow",
    "gpu_board_power_or_optical_interconnect",
    "optical_photon_power_or_counts",
    "phonon_or_acoustic_transducer_output",
    "optical_write_hold_read_retention",
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canon(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def read_pinned(path, expected):
    data = Path(path).read_bytes()
    if sha(data) != expected:
        raise ValueError("IMMUTABLE_SOURCE_SHA_MISMATCH:" + str(path))
    return len(data)


def read_child(proc, started_ns, i):
    """Snapshot a live process. Resource samples are a *sampled lower bound*."""
    try:
        with proc.oneshot():
            cpu = proc.cpu_times()
            memory = proc.memory_info()
            threads = proc.num_threads()
            try:
                io = proc.io_counters()
            except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError, NotImplementedError):
                io = None
        return {
            "sample_id": i,
            "elapsed_ns": max(0, time.monotonic_ns() - started_ns),
            "process_cpu_user_us": max(0, round(cpu.user * 1000000)),
            "process_cpu_system_us": max(0, round(cpu.system * 1000000)),
            "rss_bytes": int(memory.rss),
            "threads": int(threads),
            "io_read_bytes": None if io is None else int(getattr(io, "read_bytes", 0)),
            "io_write_bytes": None if io is None else int(getattr(io, "write_bytes", 0)),
        }
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
        return None


def store(directory, file_name, data):
    (directory / file_name).write_bytes(data)
    (directory / (file_name + ".sha256")).write_bytes(
        (sha(data) + "  " + file_name + "\n").encode("ascii")
    )


def run(args):
    argv = list(args.command)
    if argv and argv[0] == "--":
        argv.pop(0)
    if len(argv) < 2:
        raise ValueError("EXPLICIT_CHILD_COMMAND_REQUIRED")
    if args.label not in ("python-coupling", "node-coupling"):
        raise ValueError("UNEXPECTED_EXECUTABLE_LABEL")
    source_paths = (
        (args.original, PIN_ORIGINAL),
        (args.bank, PIN_BANK),
        (args.index, PIN_INDEX),
    )
    source_sizes = {Path(p).name: read_pinned(p, digest) for p, digest in source_paths}
    if source_sizes["rainbow7-bank.jsonl"] != 184815:
        raise ValueError("WRONG_FULL_BANK_SIZE")
    if source_sizes["rainbow7-index.hbi"] != 70043:
        raise ValueError("WRONG_PINNED_INDEX_SIZE")

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    created_utc_ns = time.time_ns()
    started_ns = time.monotonic_ns()
    child = subprocess.Popen(argv)
    process = psutil.Process(child.pid)
    samples = []
    while True:
        sample = read_child(process, started_ns, len(samples))
        if sample is not None:
            samples.append(sample)
        code = child.poll()
        if code is not None:
            break
        time.sleep(0.05)
    exit_code = child.wait()
    ended_ns = time.monotonic_ns()
    ended_utc_ns = time.time_ns()
    if len(samples) < 2:
        raise RuntimeError("PROCESS_TOO_SHORT_FOR_MEASURED_SERIES")
    if not any(s["rss_bytes"] > 0 for s in samples):
        raise RuntimeError("NO_KERNEL_RESIDENT_MEMORY_MEASURED")
    if not any((s["process_cpu_user_us"] + s["process_cpu_system_us"]) > 0 for s in samples):
        raise RuntimeError("NO_KERNEL_PROCESS_CPU_TIME_MEASURED")
    if any(s["elapsed_ns"] > ended_ns - started_ns for s in samples):
        raise RuntimeError("CLOCK_SAMPLE_OUT_OF_INTERVAL")

    raw_samples = b"".join(canon(s) for s in samples)
    store(out, "samples.jsonl", raw_samples)

    # The hosted source SHA and output bytes are bound into the same receipt.
    artifact = {
        "source_original_sha256": PIN_ORIGINAL,
        "source_bank_sha256": PIN_BANK,
        "source_index_sha256": PIN_INDEX,
        "model_hbp_sha256_expected": PIN_HBP,
        "model_json_sha256_expected": PIN_RESULTS,
        "produced_hbp_sha256": sha(Path(args.hbp).read_bytes()) if Path(args.hbp).exists() else None,
        "produced_json_sha256": sha(Path(args.result).read_bytes()) if Path(args.result).exists() else None,
    }
    receipt = {
        "schema": SCHEMA,
        "label": args.label,
        "os_kernel_counter_observations": True,
        "instrument_independent_attestation": False,
        "child_exit_code": exit_code,
        "child_pid_at_run": child.pid,
        "command": argv,
        "runner_os": os.environ.get("RUNNER_OS", "LOCAL"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_head_sha": os.environ.get("GITHUB_SHA"),
        "host_os": platform.system(),
        "machine_architecture": platform.machine(),
        "logical_cpu_count_visible": psutil.cpu_count(logical=True),
        "host_memory_total_bytes_visible": int(psutil.virtual_memory().total),
        "process_cpu_measurement": "OS_KERNEL_PROCESS_TIMES_SAMPLED_MICROSECONDS",
        "process_memory_measurement": "RSS_ON_LINUX_WINDOWS_WORKING_SET_SAMPLED_BYTES",
        "io_measurement": "OS_PROCESS_IO_COUNTERS_NOT_PHYSICAL_DISK_ENERGY",
        "timing_measurement": "MONOTONIC_WALL_CLOCK_NANOSECONDS",
        "start_utc_ns": created_utc_ns,
        "end_utc_ns": ended_utc_ns,
        "elapsed_wall_ns": ended_ns - started_ns,
        "sample_count": len(samples),
        "last_sample_elapsed_ns": samples[-1]["elapsed_ns"],
        "sampled_peak_rss_bytes": max(s["rss_bytes"] for s in samples),
        "sampled_peak_threads": max(s["threads"] for s in samples),
        "last_observed_process_cpu_user_us": samples[-1]["process_cpu_user_us"],
        "last_observed_process_cpu_system_us": samples[-1]["process_cpu_system_us"],
        "raw_samples_sha256": sha(raw_samples),
        "source_sizes_bytes": source_sizes,
        "byte_artifact_bindings": artifact,
        "external_physical_instrument_readings": {
            k: {"measurement_status": "NOT_INSTRUMENTED", "value": None, "units": None}
            for k in READINGS
        },
        "model_values_are_detector_measurements": False,
        "hosted_vm_implies_unique_attested_chassis": False,
    }
    store(out, "receipt.json", canon(receipt))
    print(json.dumps({
        "measurement_status": "PHYSICAL_HOST_PROCESS_ACTIVITY_OBSERVED",
        "child_exit_code": exit_code,
        "label": args.label,
        "elapsed_wall_ms": (ended_ns - started_ns) // 1000000,
        "samples": len(samples),
        "peak_rss_bytes": receipt["sampled_peak_rss_bytes"],
        "observed_user_system_cpu_us":
            receipt["last_observed_process_cpu_user_us"] + receipt["last_observed_process_cpu_system_us"],
        "hbp_sha256": artifact["produced_hbp_sha256"],
        "samples_sha256": sha(raw_samples),
        "ac_dc_optical_phonon_sensors": "NOT_INSTRUMENTED"
    }, sort_keys=True))
    if exit_code != 0:
        raise SystemExit(exit_code)
    if artifact["produced_hbp_sha256"] != PIN_HBP or artifact["produced_json_sha256"] != PIN_RESULTS:
        raise SystemExit("MODEL_OUTPUT_SHA_DRIFT")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--original", required=True)
    parser.add_argument("--bank", required=True)
    parser.add_argument("--index", required=True)
    parser.add_argument("--hbp", required=True)
    parser.add_argument("--result", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    run(parser.parse_args())
