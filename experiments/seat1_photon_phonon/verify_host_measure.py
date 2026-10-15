#!/usr/bin/env python3
"""Independent audit of live kernel counters, raw samples and linked model data.

CPU/RSS are measured OS process counters. Instrumented AC/DC current, grounding,
light and phonons are separately NOT INSTRUMENTED; no power inference permitted.
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

ORIGINAL = "02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
BANK = "52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
INDEX = "6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"
HBP = "42f3b61117a2e771f4f21958e12771b92b7a5d7251d023dc9ab78b34c65f6058"
RESULTS = "4debac19eb1238bb8495018f115aa53494705934ff304129f2f4807920c99804"
SCHEMA = "ASOLARIA-PHYSICAL-PROCESS-KERNEL-TELEMETRY-V1"
FILE_NAMES = ("receipt.json", "samples.jsonl")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, why):
    if not ok:
        raise AssertionError(why)


def frozen_sources(original, bank, index):
    names = [original, bank, index]
    expected = (ORIGINAL, BANK, INDEX)
    for p, digest in zip(names, expected):
        require(sha(Path(p).read_bytes()) == digest, "ORIGINAL_SOURCE_ROOT_DIFF:" + str(p))
    require(len(Path(bank).read_bytes()) == 184815, "ORIGINAL_BANK_SIZE")
    require(len(Path(index).read_bytes()) == 70043, "ORIGINAL_INDEX_SIZE")


def pinned_model(directory):
    d = Path(directory)
    hbp = (d / "coupling.hbp").read_bytes()
    js = (d / "results.json").read_bytes()
    require(sha(hbp) == HBP and sha(js) == RESULTS, "ORIGINAL_MODEL_DRIFT")
    summary = json.loads(js)
    require(summary["bank_sha256"] == BANK and summary["frames"] == 6804,
            "MODEL_FIXTURE_INVALID")
    return {"hbp": sha(hbp), "json": sha(js)}


def parse_receipt(folder):
    folder = Path(folder)
    blobs = {name: (folder / name).read_bytes() for name in FILE_NAMES}
    for name in FILE_NAMES:
        sidecar = (folder / (name + ".sha256")).read_bytes()
        require(sidecar == (sha(blobs[name]) + "  " + name + "\n").encode("ascii"),
                "SEALED_RECEIPT_OR_SAMPLE_HASH_MISMATCH")
    header = json.loads(blobs["receipt.json"])
    samples = [json.loads(x) for x in blobs["samples.jsonl"].splitlines()]
    return header, samples, blobs


def check_telemetry(header, samples, label, model, expected_os=None):
    require(header["schema"] == SCHEMA and header["label"] == label, "TELEMETRY_SCHEMA_OR_ID")
    require(header["os_kernel_counter_observations"] is True, "MISSING_KERNEL_COUNTERS")
    require(header["instrument_independent_attestation"] is False,
            "FORGED_INDEPENDENT_HARDWARE_ATTESTATION")
    require(header["child_exit_code"] == 0, "CHILD_PROCESS_EXECUTION_FAILED")
    require(header["source_sizes_bytes"]["rainbow7-bank.jsonl"] == 184815,
            "NO_FULL_BANK_LINK")
    require(header["source_sizes_bytes"]["rainbow7-index.hbi"] == 70043,
            "NO_SOURCE_INDEX_LINK")
    if expected_os is not None:
        require(header["host_os"] == expected_os, "UNEXPECTED_HOST_OS")
        require(header["runner_os"].lower() == expected_os.lower(), "MISLABELED_RUNNER")
    require(header["logical_cpu_count_visible"] >= 1
            and header["host_memory_total_bytes_visible"] > 0
            and header["sampled_peak_threads"] > 0,
            "NO_OS_RESOURCE_OBSERVATION")
    require(header["timing_measurement"] == "MONOTONIC_WALL_CLOCK_NANOSECONDS",
            "UNSUPPORTED_TIME_MEASUREMENT")
    require(header["process_cpu_measurement"] == "OS_KERNEL_PROCESS_TIMES_SAMPLED_MICROSECONDS",
            "UNSUPPORTED_CPU_MEASUREMENT")
    require(header["process_memory_measurement"] ==
            "RSS_ON_LINUX_WINDOWS_WORKING_SET_SAMPLED_BYTES",
            "UNSUPPORTED_MEMORY_MEASUREMENT")
    artifact = header["byte_artifact_bindings"]
    require(artifact["source_original_sha256"] == ORIGINAL
            and artifact["source_bank_sha256"] == BANK
            and artifact["source_index_sha256"] == INDEX,
            "SOURCE_NOT_INDEPENDENTLY_PINNED")
    require(artifact["model_hbp_sha256_expected"] == HBP
            and artifact["model_json_sha256_expected"] == RESULTS,
            "TRUST_ANCHOR_CHANGED")
    require(artifact["produced_hbp_sha256"] == model["hbp"]
            and artifact["produced_json_sha256"] == model["json"],
            "MODEL_PROCESS_RECEIPT_DRIFT")
    require(header["sample_count"] == len(samples) and len(samples) >= 2,
            "MISSING_RAW_SAMPLES")
    require(header["elapsed_wall_ns"] > 0
            and header["end_utc_ns"] > header["start_utc_ns"],
            "NO_REAL_TIME_INTERVAL")
    require(header["model_values_are_detector_measurements"] is False,
            "SIMULATION_PROMOTED_TO_PHYSICAL_PHOTONS")
    require(header["hosted_vm_implies_unique_attested_chassis"] is False,
            "ATTESTED_DEVICE_IDENTITY_NOT_ESTABLISHED")
    readings = header["external_physical_instrument_readings"]
    require(len(readings) == 8 and all(
        v == {"measurement_status": "NOT_INSTRUMENTED", "value": None, "units": None}
        for v in readings.values()), "NONEXISTENT_INSTRUMENT_CLAIM")

    previous_time = -1
    previous_cpu = -1
    highest_rss = 0
    highest_threads = 0
    previous_io = None
    for i, s in enumerate(samples):
        require(s["sample_id"] == i, "OUT_OF_ORDER_KERNEL_SAMPLE")
        t = s["elapsed_ns"]
        require(isinstance(t, int) and previous_time < t <= header["elapsed_wall_ns"],
                "NONMONOTONIC_KERNEL_CLOCK")
        cpu = s["process_cpu_user_us"] + s["process_cpu_system_us"]
        require(cpu >= previous_cpu >= -1
                and s["process_cpu_user_us"] >= 0
                and s["process_cpu_system_us"] >= 0,
                "NONMONOTONIC_OR_NEGATIVE_CPU_TIME")
        require(isinstance(s["rss_bytes"], int) and s["rss_bytes"] >= 0
                and isinstance(s["threads"], int) and s["threads"] >= 0,
                "PHYSICALLY_IMPOSSIBLE_MEMORY_OR_THREADS")
        io = (s["io_read_bytes"], s["io_write_bytes"])
        if all(x is not None for x in io):
            require(all(isinstance(x, int) and x >= 0 for x in io),
                    "BAD_KERNEL_IO_COUNTER")
            if previous_io is not None:
                require(io[0] >= previous_io[0] and io[1] >= previous_io[1],
                        "NONMONOTONIC_OS_IO_COUNTER")
            previous_io = io
        highest_rss = max(highest_rss, s["rss_bytes"])
        highest_threads = max(highest_threads, s["threads"])
        previous_cpu = cpu
        previous_time = t
    require(highest_rss > 0 and previous_cpu > 0, "NO_LIVE_PROCESS_USAGE")
    require(header["last_sample_elapsed_ns"] == previous_time
            and header["sampled_peak_rss_bytes"] == highest_rss
            and header["sampled_peak_threads"] == highest_threads
            and (header["last_observed_process_cpu_user_us"]
                 + header["last_observed_process_cpu_system_us"]) == previous_cpu,
            "FABRICATED_RESOURCE_TOTAL")
    return {
        "label": label,
        "os": header["host_os"],
        "sample_count": len(samples),
        "measured_wall_ms": header["elapsed_wall_ns"] // 1000000,
        "sampled_peak_rss_bytes": highest_rss,
        "sampled_cpu_time_ms_lower_bound": previous_cpu // 1000,
        "github_run_id": header["github_run_id"],
        "github_head_sha": header["github_head_sha"],
    }


def mutations(original_header, original_samples, label, model):
    """Modify actual in-memory receipt / sample data and prove semantic rejection.

    SHA mismatch is independently checked at parse_receipt(); coherent resealing
    of the modified sample is NOT enough to defeat these semantic checks.
    """
    mutants = (
        ("counter_rewind", lambda h, s: s[-1].update(process_cpu_user_us=-1)),
        ("negative_rss", lambda h, s: s[0].update(rss_bytes=-42)),
        ("time_reversal", lambda h, s: s[-1].update(elapsed_ns=0)),
        ("wrong_source_root", lambda h, s: h["byte_artifact_bindings"].update(source_bank_sha256="0"*64)),
        ("false_detector", lambda h, s: h.update(model_values_are_detector_measurements=True)),
        ("fabricated_ac_meter", lambda h, s: h["external_physical_instrument_readings"]["ac_mains_voltage_current_or_energy"].update(measurement_status="MEASURED", value=220, units="V")),
        ("forged_external_attestation", lambda h, s: h.update(instrument_independent_attestation=True)),
        ("fake_hbp_binding", lambda h, s: h["byte_artifact_bindings"].update(produced_hbp_sha256="f"*64)),
        ("missing_samples", lambda h, s: s.clear()),
        ("wrong_child_exit", lambda h, s: h.update(child_exit_code=1)),
    )
    held = []
    for name, op in mutants:
        h, s = copy.deepcopy(original_header), copy.deepcopy(original_samples)
        op(h, s)
        try:
            check_telemetry(h, s, label, model)
        except (AssertionError, KeyError, ValueError, TypeError) as exc:
            held.append({"attack": name, "held": True, "reason": str(exc)})
        else:
            raise AssertionError("FORGED_PHYSICAL_METRIC_ACCEPTED:" + name)
    require(len(held) == 10, "INCOMPLETE_MEASUREMENT_FALSIFIERS")
    return held


def main():
    if len(sys.argv) not in (8, 10):
        raise SystemExit(
            "usage: verify_host_measure.py source bank index python-model node-model "
            "python-host node-host [windows-python-host windows-node-host]"
        )
    original, bank, index, py_model_dir, node_model_dir, py_host, node_host = sys.argv[1:8]
    frozen_sources(original, bank, index)
    py_model = pinned_model(py_model_dir)
    node_model = pinned_model(node_model_dir)
    require(py_model == node_model, "INDEPENDENT_PRODUCER_MODEL_DIVERGENCE")

    paths = [py_host, node_host] + sys.argv[8:]
    expect_labels = ["python-coupling", "node-coupling"] * (len(paths) // 2)
    results = []
    proof = None
    original_sample_bytes = []
    for i, (p, label) in enumerate(zip(paths, expect_labels)):
        header, samples, blobs = parse_receipt(p)
        expected_os = None if len(paths) == 2 else ("Linux" if i < 2 else "Windows")
        result = check_telemetry(header, samples, label, py_model, expected_os)
        results.append(result)
        original_sample_bytes.append(sha(blobs["samples.jsonl"]))
        if proof is None:
            proof = mutations(header, samples, label, py_model)

    if len(paths) == 4:
        require(results[0]["github_run_id"] == results[1]["github_run_id"]
                == results[2]["github_run_id"] == results[3]["github_run_id"],
                "CROSS_OS_PROVENANCE_DIFFERENT_RUNS")
        require(len(set(x["github_head_sha"] for x in results)) == 1,
                "CROSS_OS_DIFFERENT_CODE_REVISION")
    print(json.dumps({
        "status": "PASS",
        "independent_semantic_mutations_held": len(proof),
        "measurements": results,
        "sample_file_sha256s": original_sample_bytes,
        "frozen_model_hbp_sha256": HBP,
        "source_full_bank_sha256": BANK,
        "hosted_physical_process_kernel_activity_measured": True,
        "optical_phonon_ac_dc_electrical_instrument_readings_measured": False,
        "independent_chassis_attestation": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
