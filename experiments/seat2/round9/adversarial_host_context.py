#!/usr/bin/env python3
"""Seat2 PR111: real adversarial Node referrer tests over altered artifact bytes.

Creates coherent SHA-sidecar forgeries, invokes *the actual* Node source reviewer,
and requires each altered positive-looking record to FAIL. Never overwrites the
original CI host evidence. Case output is deterministic and cross-OS identical.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

CORE=("digital.json","host-activity.json","instrument-status.json")
CASES=("counter_cpu_positive",
       "run_id_numeric_wrong",
       "producer_sha_valid_40_wrong",
       "runner_os_and_platform_consistent_but_wrong",
       "github_job_valid_looking_wrong",
       "fake_device_current_with_forged_sidecar",
       "combined_counter_and_run_and_sha")


def canon(obj):
    return (json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")


def sha(b): return hashlib.sha256(b).hexdigest()


def prepare(origin, dest, case):
    dest.mkdir(parents=True,exist_ok=True)
    for filename in CORE:
        shutil.copyfile(origin/filename,dest/filename)
        shutil.copyfile(origin/(filename+".sha256"),dest/(filename+".sha256"))
    target=dest/"host-activity.json"
    host=json.loads(target.read_bytes())
    if case in ("counter_cpu_positive","combined_counter_and_run_and_sha"):
        host["cpu_elapsed_ns"]+=10_000_000
    if case in ("run_id_numeric_wrong","combined_counter_and_run_and_sha"):
        host["github_run_id"]=str(int(host["github_run_id"])+17)
    if case in ("producer_sha_valid_40_wrong","combined_counter_and_run_and_sha"):
        host["producing_git_sha"]="f"*40 if host["producing_git_sha"]!="f"*40 else "e"*40
    if case=="runner_os_and_platform_consistent_but_wrong":
        opposite = "Windows" if host["runner_os"]=="Linux" else "Linux"
        host["runner_os"]=opposite
        host["platform_system"]=opposite
    if case=="github_job_valid_looking_wrong":
        host["github_job"]="a-different-legitimate-job"
    if case=="fake_device_current_with_forged_sidecar":
        target=dest/"instrument-status.json"
        instrument=json.loads(target.read_bytes())
        instrument["channels"]["device_current_a"]={
           "measured":True,"value":1.2,"instrument_id":"FAKE-TEST-METER",
           "raw_capture_sha256":"0"*64}
        new=canon(instrument)
    else:
        new=canon(host)
    target.write_bytes(new)
    (dest/(target.name+".sha256")).write_bytes(
        (sha(new)+"  "+target.name+"\n").encode("ascii"))


def invoke(node_source, frozen, evidence):
    # Let Node read real SHA-sidecar-mutated file bytes. Capture only status;
    # no reliance on its output phrases; no platform-dependent transcript SHA.
    return subprocess.run(["node",str(node_source),str(frozen),str(evidence)],
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                          text=True,check=False,timeout=120)


def main(frozen,original,output,node_source):
    origin=Path(original).resolve()
    target=Path(output).resolve()
    node_source=Path(node_source).resolve()
    assert all((origin/f).is_file() for f in CORE),"MISSING_ORIGINAL_EVIDENCE"
    assert all((origin/(f+".sha256")).is_file() for f in CORE),"MISSING_ORIGINAL_SIDECAR"
    assert len(os.environ.get("GITHUB_SHA",""))==40
    assert os.environ.get("GITHUB_RUN_ID","").isdigit()
    with tempfile.TemporaryDirectory(prefix="seat2-adversarial-") as tmp:
        folder=Path(tmp)
        clean=folder/"clean"
        clean.mkdir()
        for filename in CORE:
            shutil.copyfile(origin/filename,clean/filename)
            shutil.copyfile(origin/(filename+".sha256"),clean/(filename+".sha256"))
        clean_status=invoke(node_source,frozen,clean)
        assert clean_status.returncode==0,(
            "VALID_SOURCE_UNEXPECTEDLY_REJECTED",
            clean_status.stderr[-1400:])
        outcomes=[]
        for label in CASES:
            candidate=folder/label
            prepare(origin,candidate,label)
            check=invoke(node_source,frozen,candidate)
            assert check.returncode!=0,(
               "FORGED_UNSIGNED_HOST_REPORT_ACCEPTED",label)
            # Ensure each case actually exercised a changed file and rebuilt
            # its matching *untrusted* sidecar, not a broken checksum shortcut.
            changed=tuple(f for f in CORE
                          if (candidate/f).read_bytes()!=(origin/f).read_bytes())
            assert changed, ("NO_INPUT_MUTATION",label)
            for name in changed:
                data=(candidate/name).read_bytes()
                side=(candidate/(name+".sha256")).read_bytes()
                assert side==(sha(data)+"  "+name+"\n").encode("ascii"),(
                    "SIDECAR_NOT_RECALCULATED",label)
            outcomes.append({"case":label,"recomputed_local_sha256_sidecar":True,
                             "mutated_file_fields":list(changed),
                             "actual_node_reviewer_rejected":True})
    report={"schema":"ASOLARIA-SEAT2-R9-FORGED-TELEMETRY-NODE-REVIEW-V1",
            "source_fixture_sha256":
              "077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400",
            "status":"ALL_HOST_CONTEXT_FORGERIES_REJECTED_WITH_AUTHENTIC_RUN_ENV",
            "untainted_reference_accepted":True,
            "falsification_cases":outcomes,
            "case_count":len(outcomes),
            "source_authentication_scope":"GITHUB_RUNNER_ENVIRONMENT_PLATFORM_MEDIATED",
            "hardware_measurement_signature_independently_validated":False}
    out=canon(report)
    dest=Path(target)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(out)
    dest.with_name(dest.name+".sha256").write_bytes(
        (sha(out)+"  "+dest.name+"\n").encode("ascii"))
    print(json.dumps({"status":report["status"],
                      "tested":len(outcomes),
                      "receipt_sha256":sha(out)},sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("usage: adversarial_host_context.py <frozen> <original_artifact_dir> <receipt.json> <node_verifier.js>")
    main(*sys.argv[1:])
