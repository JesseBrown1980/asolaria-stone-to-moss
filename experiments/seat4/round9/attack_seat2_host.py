#!/usr/bin/env python3
"""Seat4 independent active attacks on Seat2 frozen real-OS telemetry validators.
Execute ORIGINAL Seat2 pinned code, not a mock. No physical instrument exists here.
"""
import importlib.util,copy,json,hashlib,sys,tempfile
from pathlib import Path
RUN="38777263894";PR_HEAD="8e597ae4c8d5d1ff76a2d25ad394ec49e601afc4"
MERGE="5969b7de9ada80e8feaa18b497c1932c009d90db"
ROOT="077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400"
def sha(x):return hashlib.sha256(x).hexdigest()
def canonical(x):return (json.dumps(x,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")
def must(c,s):
 if not c:raise AssertionError(s)
def run(source,archives,out):
 path=source/"experiments/seat2/round9/host_bridge.py"
 spec=importlib.util.spec_from_file_location("seat2_original_round9_source",str(path))
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 jobs=[("ubuntu-latest","3.11"),("ubuntu-latest","3.13"),("windows-latest","3.11"),("windows-latest","3.13")]
 real_tests={};coherent_bypasses={}
 for os_name,version in jobs:
  name=f"seat2-r9-{os_name}-py{version}"
  folder=archives/name
  host=json.loads((folder/"host-activity.json").read_bytes())
  instrument=json.loads((folder/"instrument-status.json").read_bytes())
  original_bytes=(folder/"host-activity.json").read_bytes()
  must(sha(original_bytes)+"  host-activity.json\n"==(folder/"host-activity.json.sha256").read_text(),"ARCHIVE_SIDECAR_MISMATCH")
  must(host["source_sha256"]==ROOT and host["github_run_id"]==RUN and
       host["producing_git_sha"]==MERGE and host["python"].startswith(version),"ARCHIVE_RUN_ASSOCIATION")
  must(mod.validate_host(host) and mod.validate_measurements(instrument),"UNMODIFIED_SOURCE_FALSE_REJECT")
  observed=mod.negative_controls(host,instrument)
  expected=["zero_cpu","backward_wall","source_root_switch","missing_runner_identity",
            "negative_host_rss","untouched_memory","fake_optical_detector",
            "fake_current_meter","false_photon_retention"]
  must(observed==expected,"NINE_NEGATIVES_NOT_ACTUALLY_EXECUTED")
  # Additional source-backed adversarial controls with real validator:
  tests=[
   ("forged_source_root",{"source_sha256":"f"*64},False),
   ("zero_cpu",{"cpu_elapsed_ns":0},False),
   ("backward_monotonic",{"wall_elapsed_ns":-1},False),
   ("negative_RSS",{"rss_before_bytes":-1},False),
   ("missing_execution_context",{"github_run_id":""},False),
   ("missing_memory_pages",{"memory_pages_touched":0},False),
   # These exact adversarial inputs are *accepted* by the producer's
   # validator, demonstrating a real narrow provenance/authenticity gap.
   ("forged_plausible_producer_SHA",{"producing_git_sha":"f"*40},True),
   ("forged_numeric_run_ID",{"github_run_id":"99999999999"},True),
   ("forged_positive_CPU_counter",{"cpu_elapsed_ns":host["cpu_elapsed_ns"]+1234567},True),
   ("forged_positive_RSS",{"rss_during_bytes":host["rss_during_bytes"]+8192,
                           "rss_after_work_bytes":host["rss_after_work_bytes"]+8192},True),
   ("reversed_UTC_timestamps",{"wall_utc_start":host["wall_utc_end"],
                              "wall_utc_end":host["wall_utc_start"]},True)
  ]
  results={}
  for label,fields,should_accept in tests:
   altered={**host,**fields}
   try:
    mod.validate_host(altered);accepted=True
   except (ValueError,AssertionError):
    accepted=False
   must(accepted==should_accept,"UNEXPECTED_ORIGINAL_VALIDATOR_DECISION:"+label+":"+str(accepted))
   must(sha(canonical(altered))!=sha(original_bytes),"MUTATION_INEFFECTIVE:"+label)
   results[label]="ORIGINAL_VALIDATOR_ACCEPTS" if accepted else "ORIGINAL_VALIDATOR_REJECTS"
  for label,func in [
    ("fabricated_optical_spectrum",lambda m:m["channels"]["optical_spectral_counts"].update({"measured":True,"value":777})),
    ("fabricated_electrical_power",lambda m:m["channels"]["device_power_w"].update({"measured":True,"value":125.0})),
    ("fabricated_physical_retention",lambda m:m.update(optical_retention_measured=True)),
    ("absent_calibrated_instrument",lambda m:m["channels"].pop("optical_spectral_counts"))
  ]:
   x=copy.deepcopy(instrument);func(x)
   try:
    mod.validate_measurements(x);accepted=True
   except (ValueError,AssertionError):
    accepted=False
   must(not accepted,"ORIGINAL_INSTRUMENT_VALIDATOR_ACCEPTS_FALSE_SIGNAL:"+label)
   results[label]="ORIGINAL_VALIDATOR_REJECTS"
  # Physically mutate a TEMPORARY COPY of the true previous archive bytes,
  # retaining the original SHA sidecar; demand a failed full-file readback.
  with tempfile.TemporaryDirectory(prefix="seat4-pr111-negative-") as tmp:
   copy_path=Path(tmp)/"host-activity.json"
   checksum_path=Path(tmp)/"host-activity.json.sha256"
   checksum_path.write_bytes((folder/"host-activity.json.sha256").read_bytes())
   def verify_archived_file():
    blob=copy_path.read_bytes()
    must(checksum_path.read_bytes()==(sha(blob)+"  host-activity.json\n").encode("ascii"),
         "CORRUPTED_HOST_SHA_SIDECAR")
    return json.loads(blob)
   corrupt=bytearray(original_bytes)
   position=corrupt.index(b'"cpu_elapsed_ns"')
   corrupt[position]^=1
   copy_path.write_bytes(corrupt)
   try:verify_archived_file()
   except AssertionError as e:must(str(e)=="CORRUPTED_HOST_SHA_SIDECAR","WRONG_CORRUPTION_REJECT")
   else:raise AssertionError("CORRUPTED_FULL_RAW_FILE_WAS_ACCEPTED")
   results["corrupted_archived_host_file"]="ACTUAL_MODIFIED_RAW_FILE_FAILED_ORIGINAL_SHA"
   # Actually delete the required original-host file; do not count a label as a test.
   copy_path.unlink()
   try:verify_archived_file()
   except FileNotFoundError:pass
   else:raise AssertionError("ABSENT_HOST_RECORD_NOT_DETECTED")
   results["missing_host_file"]="ACTUAL_ABSENT_FILE_HARD_FAILURE"
  real_tests[name]=results
  coherent_bypasses[name]=sum(x=="ORIGINAL_VALIDATOR_ACCEPTS" for x in results.values())
 must(len(real_tests)==4 and all(x==5 for x in coherent_bypasses.values()),"UNKNOWN_SEAT2_TRUST_BEHAVIOR")
 output={"schema":"ASOLARIA-SEAT4-PR111-ACTIVE-ADVERSARIAL-REVIEW-V1",
  "reviewed_head_sha":PR_HEAD,"workflow_run_id":RUN,
  "original_pull_request_merge_commit":MERGE,
  "github_merge_commit_known_parents":["5d3e3a1147ad7af84c1b5b1ba482dfddd9832c86",PR_HEAD],
  "source_HBP_root_sha256":ROOT,
  "archive_count":4,"original_nine_negative_controls":"ACTUALLY_EXECUTED_AND_REJECTED_IN_FOUR_ARCHIVED_RECORDS",
  "original_negative_controls_count":9,"additional_independently_mutated_cases_per_archive":17,
  "per_archive_mutation_results":real_tests,
  "real_source_root_and_claimed_sensor_mutations_rejected":True,
  "source_or_host_full_compromise_resistant":False,
  "coherent_positive_counter_run_sha_forgery_accepted_by_producer_validator":True,
  "physical_compute_and_host_activity":"OS_REPORTED_CONFIRMED",
  "direct_calibrated_current_power_optical_sensor_data":"NOT_CAPTURED_IN_RUN",
  "prior_reported_August_photon_memory":"PRESERVED_AS_OPERATOR_REPORTED",
  "recommendation":"HOLD_MERGE_PENDING_SOURCE_RUN_BINDING_OR_STRICT_SCOPE_LABEL"}
 out.mkdir(parents=True,exist_ok=True)
 blob=canonical(output)
 (out/"pr111-seat4-attacks.json").write_bytes(blob)
 (out/"pr111-seat4-attacks.json.sha256").write_bytes((sha(blob)+"  pr111-seat4-attacks.json\n").encode("ascii"))
 print("SEAT4_PR111_MUTATION_CROSS_EXAM_PASS",len(real_tests),
       "original_negative_cases_per_file=9","additional_cases_per_file=17",
       "coherent_bypasses_per_file=5",sha(blob))
if __name__=="__main__":
 if len(sys.argv)!=4:raise SystemExit("usage: attack_seat2_host.py FROZEN_PR111_SOURCE ARCHIVED_FOUR_HOSTS OUTPUT")
 run(*map(Path,sys.argv[1:]))
