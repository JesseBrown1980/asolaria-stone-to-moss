#!/usr/bin/env python3
"""Independent readback of two distinct PREVIOUSLY hosted physical CPU/RAM reports.
Not electrical/power/optical instrument data; no original source or stones modified.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
HBP="077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400"
DIGEST_2="ae3474a94a03e024ad41bd6d0c508a18cbb3ed43c551da0ed3c6ec701e5b61cf"
DIGEST_4="7aead6f883579d8228341d2a16751b9f51e9fe622a48693315dbcd1a19fa6a1a"
SHA_2="8e597ae4c8d5d1ff76a2d25ad394ec49e601afc4"
SHA_4="5b2f3c9ad550c652a1e4a5d537ba6ae2b5f57176"
RUN_2="38777263894";RUN_4="38777543919"
FROZEN="5d3e3a1147ad7af84c1b5b1ba482dfddd9832c86"
BANK_ORIGINAL_SOURCE="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
SLOTS=(("ubuntu-latest","3.11","Linux"),("ubuntu-latest","3.13","Linux"),
       ("windows-latest","3.11","Windows"),("windows-latest","3.13","Windows"))
def sha(blob):return hashlib.sha256(blob).hexdigest()
def check(cond,msg):
 if not cond:raise AssertionError(msg)
def encode(obj):return (json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
def audited_json(dir,name):
 blob=(dir/name).read_bytes(); expected=sha(blob)+"  "+name+"\n"
 check((dir/(name+".sha256")).read_bytes()==expected.encode("ascii"),"INVALID_ARCHIVED_SHA_SIDECAR:"+str(dir/name))
 parsed=json.loads(blob)
 check(encode(parsed)==blob,"NONCANONICAL_ARCHIVED_JSON:"+str(dir/name))
 return parsed,blob
def mutated_negative(blob,field,value):
 data=json.loads(blob)
 data[field]=value
 changed=encode(data)
 check(changed!=blob and sha(changed)!=sha(blob),"MUTATION_FAILED_TO_CHANGE_DIGEST")
 return True
def main(d2,d4,source_root,output):
 output.mkdir(parents=True,exist_ok=True)
 bank=(source_root/"rainbow-evidence/rainbow7-bank.jsonl").read_bytes()
 source=(source_root/"base-evidence/lightbank-memories.json").read_bytes()
 hbp=(source_root/"frozen-main"/"stones/2026-10-15-rainbow81/seat4-round5-signed-spectrum-mapping-20261015.hbp").read_bytes()
 check(len(bank)==184815 and sha(bank)==BANK,"PINNED_FULL_BANK_CHANGED")
 check(sha(source)==BANK_ORIGINAL_SOURCE,"PINNED_81_SOURCE_CHANGED")
 check(len(hbp)==701 and sha(hbp)==HBP and BANK.encode("ascii") in hbp,"PINNED_SIGNED_SOURCE_CHANGED")
 payload=(hbp*((2*1024*1024+len(hbp)-1)//len(hbp)))[:2*1024*1024]
 h=hashlib.sha256()
 for i in range(256):
  h.update(payload);h.update(i.to_bytes(4,"little"))
 check(h.hexdigest()==DIGEST_2,"SEAT2_WORKLOAD_BAD")
 g=hashlib.sha256()
 for _ in range(4096):g.update(bank)
 check(g.hexdigest()==DIGEST_4,"SEAT4_WORKLOAD_BAD")
 observations=[]
 stable2={};stable4={}
 for osname,py,system in SLOTS:
  key=f"{osname}-py{py}"
  folder2=d2/("seat2-r9-"+key)
  folder4=d4/("seat4-r9-"+key)
  check(folder2.is_dir() and folder4.is_dir(),"MISSING_ARCHIVED_HOST_JOB:"+key)
  files2={name:audited_json(folder2,name) for name in
       ("digital.json","node-review.json","instrument-status.json","host-activity.json")}
  files4={name:audited_json(folder4,name) for name in
       ("r9-science.json","r9-independent-node.json","r9-host.json")}
  for name,(_,blob) in files2.items():
   if name!="host-activity.json":
    if name in stable2:check(blob==stable2[name],"SEAT2_HOST_DEPENDENT_SCIENCE:"+name)
    else:stable2[name]=blob
  for name,(_,blob) in files4.items():
   if name!="r9-host.json":
    if name in stable4:check(blob==stable4[name],"SEAT4_HOST_DEPENDENT_SCIENCE:"+name)
    else:stable4[name]=blob

  digital=files2["digital.json"][0];node2=files2["node-review.json"][0]
  instr=files2["instrument-status.json"][0];h2=files2["host-activity.json"][0]
  c4=files4["r9-science.json"][0];n4=files4["r9-independent-node.json"][0]
  h4=files4["r9-host.json"][0]
  check(digital["source_sha256"]==HBP and
        digital["source_git_commit"]==FROZEN and
        digital["original_bank_sha256_as_declared_in_hbp"]==BANK and
        digital["deterministic_workload_sha256"]==DIGEST_2,"SEAT2_SOURCE_ASSOCIATION_MISMATCH")
  check(node2["deterministic_workload_sha256"]==DIGEST_2 and
        node2["original_bank_sha256_reference_only"]==BANK,"SEAT2_INDEPENDENT_REPLAY_MISMATCH")
  check(h2["source_sha256"]==HBP and h2["source_commit"]==FROZEN and
        h2["producing_git_sha"]==SHA_2 and h2["github_run_id"]==RUN_2 and
        h2["runner_os"]==system and h2["python"].startswith(py),
        "SEAT2_HOST_REPORTED_IDENTITY_MISMATCH:"+json.dumps({"found":{"source_sha256":h2["source_sha256"],"source_commit":h2["source_commit"],"producing_git_sha":h2["producing_git_sha"],"github_run_id":h2["github_run_id"],"runner_os":h2["runner_os"],"python":h2["python"]},"expected":{"head_sha":SHA_2,"run":RUN_2,"OS":system,"py":py}},sort_keys=True))
  check(h2["cpu_elapsed_ns"]>0 and h2["wall_elapsed_ns"]>0 and
        h2["rss_during_bytes"]-h2["rss_before_bytes"]>=1024*1024 and
        h2["memory_allocated_bytes"]==24*1024*1024 and
        h2["memory_pages_touched"]==6144,"SEAT2_HOST_COUNTER_MISSING")
  check(instr["externally_attested_instrument_data"] is False and
        instr["optical_retention_measured"] is False and
        instr["biological_neural_memory_measured"] is False,"SEAT2_FALSE_INSTRUMENT")
  for k,x in instr["channels"].items():
   check(x=={"measured":False,"value":None,"instrument_id":None,"raw_capture_sha256":None},
         "SEAT2_UNVERIFIED_INSTRUMENT:"+k)
  check(c4["source_bank_sha256"]==BANK and c4["workload_sha256"]==DIGEST_4 and
        c4["hash_iterations"]==4096 and
        c4["original_bank_bytes_processed"]==184815*4096,"SEAT4_SCIENCE_ASSOCIATION_MISMATCH")
  check(n4["science_workload_sha256"]==DIGEST_4 and
        n4["source_bank_sha256"]==BANK,"SEAT4_NODE_REPLAY_MISMATCH")
  check(h4["source_bank_sha256"]==BANK and h4["workload_sha256"]==DIGEST_4 and
        h4["git_sha"]==SHA_4 and h4["git_run_id"]==RUN_4 and
        h4["environment_os"]==system and h4["python_version"].startswith(py),
        "SEAT4_HOST_REPORTED_IDENTITY_MISMATCH:"+json.dumps({"found":{"git_sha":h4["git_sha"],"git_run_id":h4["git_run_id"],"environment_os":h4["environment_os"],"python_version":h4["python_version"]},"expected":{"head_sha":SHA_4,"run":RUN_4,"OS":system,"py":py}},sort_keys=True))
  check(h4["host_process_cpu_time_ns_OS"]>0 and h4["monotonic_elapsed_ns_OS"]>0 and
        h4["tracemalloc_peak_python_allocation_bytes"]>=4*1024*1024 and
        h4["scratch_allocation_bytes"]==4*1024*1024,
        "SEAT4_HOST_COUNTER_MISSING")
  for k in ("measured_ac_wall_energy_joules","measured_dc_rail_voltage_volts",
             "measured_dc_current_amperes","measured_optical_photon_counts",
             "measured_acoustic_phonon_counts","spectrometer_raw_sha256"):
   check(h4.get(k) is None,"SEAT4_UNVERIFIED_INSTRUMENT:"+k)
  check(mutated_negative(files2["host-activity.json"][1],"github_run_id","FAKE") and
        mutated_negative(files4["r9-host.json"][1],"git_sha","f"*40) and
        mutated_negative(files2["instrument-status.json"][1],"externally_attested_instrument_data",True),
        "NOT_DETECTING_INPUT_ALTERATION")
  observations.append({
   "environment":key,
   "seat2_hbp_cpu_ns":h2["cpu_elapsed_ns"],
   "seat2_hbp_monotonic_ns":h2["wall_elapsed_ns"],
   "seat2_hbp_rss_delta_bytes":h2["rss_during_bytes"]-h2["rss_before_bytes"],
   "seat2_original_host_file_sha256":sha(files2["host-activity.json"][1]),
   "seat4_bank_cpu_ns":h4["host_process_cpu_time_ns_OS"],
   "seat4_bank_monotonic_ns":h4["monotonic_elapsed_ns_OS"],
   "seat4_bank_peak_rss_bytes":h4["observed_process_peak_resident_bytes"],
   "seat4_original_host_file_sha256":sha(files4["r9-host.json"][1])})
 report={"schema":"ASOLARIA-SEAT4-R9B-INDEPENDENT-ARCHIVED-HOST-EVIDENCE-AUDIT-V1",
         "seat2_original_run_id":RUN_2,"seat2_original_git_head":SHA_2,
         "seat4_original_run_id":RUN_4,"seat4_original_git_head":SHA_4,
         "seat2_pinned_hbp_sha256":HBP,"original_full_bank_sha256":BANK,
         "seat2_recomputed_workload_sha256":DIGEST_2,
         "seat4_recomputed_workload_sha256":DIGEST_4,
         "frozen_archive_sets_checked":8,
         "separate_host_measurements":observations,
         "evidence_level1_original_source_computations":"PASS",
         "evidence_level2_OS_reported_CPU_RAM":"PASS",
         "evidence_level3_CALIBRATED_SENSOR_READINGS":"NOT_COLLECTED_IN_EITHER_CI_RUN",
         "historical_operator_reported_photon_memory_measurement":"PRESERVED_AS_REPORTED_NOT_REEXAMINED",
         "distinct_workloads_must_not_be_directly_timing_compared":True,
         "physical_photon_memory_newly_confirmed":False}
 wire=encode(report);(output/"cross-seat-archive-review.json").write_bytes(wire)
 (output/"cross-seat-archive-review.json.sha256").write_bytes(
  (sha(wire)+"  cross-seat-archive-review.json\n").encode("ascii"))
 print("SEAT4_CROSS_SEAT_R9B_VERIFIED_ARCHIVED_HOST_ACTIVITY",len(observations),
       "SHA2",DIGEST_2,"SHA4",DIGEST_4,"out_sha256",sha(wire))
if __name__=="__main__":
 if len(sys.argv)!=5:raise SystemExit("usage: audit.py DOWNLOADED_SEAT2 DOWNLOADED_SEAT4 SOURCES OUT")
 main(*map(Path,sys.argv[1:]))
