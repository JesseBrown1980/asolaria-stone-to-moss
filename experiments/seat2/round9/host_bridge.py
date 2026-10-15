#!/usr/bin/env python3
"""Seat2 R9 physical host-activity bridge, real OS metrics + digital source SHA.

OS-reported CPU time/RSS are actual host-process counters, NOT electric
power, currents, AC/DC rail voltages, photons, or optical storage.
"""
from __future__ import annotations
import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import psutil

SOURCE_SHA="077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400"
BANK_SHA="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
SOURCE_COMMIT="5d3e3a1147ad7af84c1b5b1ba482dfddd9832c86"
SOURCE_REL="stones/2026-10-15-rainbow81/seat4-round5-signed-spectrum-mapping-20261015.hbp"
CHANNELS=("mains_ac_voltage_v","dc_supply_voltage_v","device_current_a",
          "device_power_w","ground_potential_v","optical_spectral_counts",
          "acoustic_displacement_m","physical_optical_retention_bits")
MEMORY_SIZE=24*1024*1024
PAYLOAD_SIZE=2*1024*1024
HASH_LOOPS=256

def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()
def canonical(obj)->bytes:
    return (json.dumps(obj,sort_keys=True,ensure_ascii=True,separators=(",",":"))+"\n").encode("ascii")
def require(predicate,code):
    if not predicate:raise ValueError(code)

def instruments():
    return {"schema":"ASOLARIA-SEAT2-R9-INSTRUMENT-MEASUREMENT-STATUS-V1",
            "channels":{name:{"measured":False,"value":None,"instrument_id":None,"raw_capture_sha256":None}
                        for name in CHANNELS},
            "externally_attested_instrument_data":False,
            "optical_retention_measured":False,
            "biological_neural_memory_measured":False,
            "explanation":"No calibrated external electrical, optical, acoustic or neural instrument connected to CI."}

def validate_measurements(m):
    require(m.get("schema")=="ASOLARIA-SEAT2-R9-INSTRUMENT-MEASUREMENT-STATUS-V1",
            "INSTRUMENT_SCHEMA")
    require(set(m.get("channels",{}))==set(CHANNELS),"INCOMPLETE_INSTRUMENT_CHANNELS")
    for name in CHANNELS:
        row=m["channels"][name]
        require(row=={"measured":False,"value":None,"instrument_id":None,"raw_capture_sha256":None},
                "FORGED_INSTRUMENT_READING:"+name)
    require(m.get("externally_attested_instrument_data") is False
            and m.get("optical_retention_measured") is False
            and m.get("biological_neural_memory_measured") is False,
            "FALSE_PHYSICAL_PROMOTION")
    return True

def validate_host(sample):
    require(sample["schema"]=="ASOLARIA-SEAT2-R9-REAL-OS-PROCESS-METRICS-V1","METRICS_SCHEMA")
    require(sample["source_sha256"]==SOURCE_SHA and sample["source_commit"]==SOURCE_COMMIT,
            "SOURCE_ASSOCIATION")
    require(isinstance(sample["process_pid"],int) and sample["process_pid"]>0,"INVALID_PID")
    require(sample["wall_elapsed_ns"]>0 and sample["cpu_elapsed_ns"]>0,"INVALID_CPU_OR_WALL_DURATION")
    require(sample["rss_before_bytes"]>0 and sample["rss_during_bytes"]>=sample["rss_before_bytes"],
            "INVALID_RSS_COUNTERS")
    require(sample["rss_during_bytes"]-sample["rss_before_bytes"]>=1024*1024,
            "MEMORY_ALLOC_NOT_OBSERVED")
    require(sample["rss_during_bytes"]>=sample["rss_after_work_bytes"]-1024*1024,
            "MISORDERED_MEMORY_COUNTERS")
    require(sample["memory_allocated_bytes"]==MEMORY_SIZE
            and sample["memory_pages_touched"]==MEMORY_SIZE//4096,"MEMORY_INTERVENTION_MISSING")
    require(len(sample["producing_git_sha"])==40 and sample["github_run_id"].isdigit()
            and sample["runner_os"] in ("Linux","Windows"),"INCOMPLETE_CI_CONTEXT")
    return True

def negative_controls(sample,inst):
    good=validate_host(sample) and validate_measurements(inst)
    require(good,"BASELINE_REJECTED")
    conditions=[]
    def rejects(name,target,mutate,validator):
        changed=json.loads(json.dumps(target))
        mutate(changed)
        try:validator(changed)
        except ValueError:
            conditions.append(name)
            return
        raise AssertionError("FAIL_OPEN:"+name)
    rejects("zero_cpu",sample,lambda s:s.update(cpu_elapsed_ns=0),validate_host)
    rejects("backward_wall",sample,lambda s:s.update(wall_elapsed_ns=-5),validate_host)
    rejects("source_root_switch",sample,lambda s:s.update(source_sha256="f"*64),validate_host)
    rejects("missing_runner_identity",sample,lambda s:s.update(github_run_id=""),validate_host)
    rejects("negative_host_rss",sample,lambda s:s.update(rss_before_bytes=-1),validate_host)
    rejects("untouched_memory",sample,lambda s:s.update(memory_pages_touched=0),validate_host)
    def forge_claim(i):
        i["channels"]["optical_spectral_counts"]["measured"]=True
        i["channels"]["optical_spectral_counts"]["value"]=123
    rejects("fake_optical_detector",inst,forge_claim,validate_measurements)
    def forge_current(i):
        i["channels"]["device_current_a"]["measured"]=True
        i["channels"]["device_current_a"]["value"]=1.2
    rejects("fake_current_meter",inst,forge_current,validate_measurements)
    rejects("false_photon_retention",inst,lambda i:i.update(optical_retention_measured=True),
            validate_measurements)
    require(len(conditions)==9,"NEGATIVE_COVERAGE_DRIFT")
    return conditions

def run(frozen:Path,output:Path):
    source_path=frozen/SOURCE_REL
    require(source_path.is_file(),"SOURCE_NOT_PRESENT")
    source=source_path.read_bytes()
    require(len(source)==701 and sha(source)==SOURCE_SHA,"FROZEN_SOURCE_SHA")
    require(BANK_SHA.encode("ascii") in source,"BANK_LINK_MISSING")
    # Construct deterministic digital workload outside of the timed phase.
    payload=(source*((PAYLOAD_SIZE+len(source)-1)//len(source)))[:PAYLOAD_SIZE]
    process=psutil.Process(os.getpid())
    base_rss=process.memory_info().rss
    start=datetime.now(timezone.utc).isoformat()
    cpu0=process.cpu_times()
    tick0=time.perf_counter_ns()
    # Physically allocate and touch real process memory pages, keeping them
    # present while measuring RSS. OS reports a working set, not bytes of
    # individual charge measured with instrumentation.
    allocation=bytearray(MEMORY_SIZE)
    for i in range(0,MEMORY_SIZE,4096):
        allocation[i]=(i//4096)%256
    during_rss=process.memory_info().rss
    h=hashlib.sha256()
    for i in range(HASH_LOOPS):
        h.update(payload)
        h.update(i.to_bytes(4,"little"))
    work_digest=h.hexdigest()
    cpu1=process.cpu_times()
    tick1=time.perf_counter_ns()
    after_rss=process.memory_info().rss
    end=datetime.now(timezone.utc).isoformat()
    # Keep allocation alive and verify actual contents were touched.
    require(all(allocation[i]==(i//4096)%256 for i in range(0,MEMORY_SIZE,4096)),
            "MEMORY_WRITEBACK_FAILED")
    cpu_ns=round(((cpu1.user+cpu1.system)-(cpu0.user+cpu0.system))*1_000_000_000)
    elapsed=tick1-tick0
    measured={"schema":"ASOLARIA-SEAT2-R9-REAL-OS-PROCESS-METRICS-V1",
              "measurement_type":"OS_PROCESS_COUNTERS_NOT_INSTRUMENTED_RAIL_POWER",
              "source_sha256":SOURCE_SHA,"source_commit":SOURCE_COMMIT,
              "producing_git_sha":os.environ.get("GITHUB_SHA",""),
              "github_run_id":os.environ.get("GITHUB_RUN_ID",""),
              "runner_os":os.environ.get("RUNNER_OS",""),
              "github_job":os.environ.get("GITHUB_JOB",""),
              "process_pid":os.getpid(),"python":platform.python_version(),
              "platform_system":platform.system(),
              "wall_utc_start":start,"wall_utc_end":end,
              "wall_elapsed_ns":elapsed,"cpu_elapsed_ns":cpu_ns,
              "rss_before_bytes":base_rss,"rss_during_bytes":during_rss,
              "rss_after_work_bytes":after_rss,
              "memory_allocated_bytes":MEMORY_SIZE,
              "memory_pages_touched":MEMORY_SIZE//4096}
    instrument=instruments()
    tests=negative_controls(measured,instrument)
    digital={"schema":"ASOLARIA-SEAT2-R9-PINNED-DIGITAL-WORKLOAD-V1",
             "source_git_commit":SOURCE_COMMIT,"source_sha256":SOURCE_SHA,
             "original_bank_sha256_as_declared_in_hbp":BANK_SHA,
             "input_file_bytes":len(source),
             "deterministic_payload_size_bytes":len(payload),
             "deterministic_payload_sha256":sha(payload),
             "hash_loops":HASH_LOOPS,
             "algorithm":"SHA256(concat[256 * (source-derived 2MiB payload || little-endian u32 loop-index)])",
             "deterministic_workload_sha256":work_digest,
             "negative_controls":tests,
             "physical_optical_storage_measured":False}
    output.mkdir(parents=True,exist_ok=True)
    for name,obj in (("digital.json",digital),("host-activity.json",measured),
                     ("instrument-status.json",instrument)):
        body=canonical(obj)
        (output/name).write_bytes(body)
        (output/(name+".sha256")).write_bytes((sha(body)+"  "+name+"\n").encode("ascii"))
    print("SEAT2_R9_OS_MEASURED_DIGITAL_PINNED",
          json.dumps({"digest":work_digest,"rss_delta_bytes":during_rss-base_rss,
          "cpu_ns":cpu_ns,"wall_ns":elapsed,"digital_sha256":sha(canonical(digital)),
          "electrical_optical_instruments":"NOT_MEASURED"},sort_keys=True))
    return digital,measured

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: python host_bridge.py FROZEN_MAIN OUTPUT_DIR")
    run(Path(sys.argv[1]),Path(sys.argv[2]))
