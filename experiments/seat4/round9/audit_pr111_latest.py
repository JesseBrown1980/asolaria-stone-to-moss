#!/usr/bin/env python3
"""Seat4 PR111 exact e253/ e701 independent R9C archival and attack referee.
Uses ORIGINAL Seat2's Node reviewer under a reconstruction of a provider-pinned
PR event context; no physical meter or independent CPU attestation involved.
"""
from __future__ import annotations
import hashlib,json,os,platform,shutil,subprocess,sys,tempfile
from pathlib import Path

REPO="JesseBrown1980/asolaria-stone-to-moss"
RUN=38783337268;ATTEMPT=1;PR=111
HEAD="e2532396bbd42bb2a0bace2f26d4b5d6b8f2e966"
MERGE="e7011fe09868f0a84de0434964cc3dadc205b808"
BASE="5d3e3a1147ad7af84c1b5b1ba482dfddd9832c86"
HBP_SHA="077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400"
BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
EXPECTED="ae3474a94a03e024ad41bd6d0c508a18cbb3ed43c551da0ed3c6ec701e5b61cf"
SLOTS=(("ubuntu-latest","3.11","Linux"),
       ("ubuntu-latest","3.13","Linux"),
       ("windows-latest","3.11","Windows"),
       ("windows-latest","3.13","Windows"))
CHANNELS=("mains_ac_voltage_v","dc_supply_voltage_v","device_current_a","device_power_w",
          "ground_potential_v","optical_spectral_counts","acoustic_displacement_m",
          "physical_optical_retention_bits")
FILES=("digital.json","host-activity.json","instrument-status.json","node-review.json","attack-review.json")
def sha(v):return hashlib.sha256(v).hexdigest()
def dump(x):return (json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
def require(x,msg):
 if not x:raise AssertionError(msg)
def command(args,cwd):
 return subprocess.check_output(args,cwd=str(cwd),text=True).strip()
def audited(directory,name):
 blob=(directory/name).read_bytes()
 require((directory/(name+".sha256")).read_bytes()==
   (sha(blob)+"  "+name+"\n").encode("ascii"),"RAW_ARCHIVE_SIDECAR_MISMATCH:"+name)
 obj=json.loads(blob)
 require(blob==dump(obj),"NON_CANONICAL_ARCHIVE_JSON:"+name)
 return obj,blob
def inspect_api(root,base,merge):
 run=json.loads((root/"pr111-original-run-api.json").read_bytes())
 commit=json.loads((root/"pr111-original-merge-api.json").read_bytes())
 require(run["id"]==RUN and run["run_attempt"]==ATTEMPT and
         run["status"]=="completed" and run["conclusion"]=="success" and
         run["event"]=="pull_request" and run["head_sha"]==HEAD,
         "RUN_API_IDENTITY_NOT_PINNED")
 prs=run.get("pull_requests",[])
 require(any(p["number"]==PR and p["head"]["sha"]==HEAD and
             p["base"]["sha"]==BASE for p in prs),"RUN_API_PR_SCOPE_MISMATCH")
 require(commit["sha"]==MERGE and [x["sha"] for x in commit["parents"]]==[BASE,HEAD],
         "ACTUAL_MERGE_COMMIT_PARENTAGE_MISMATCH")
 require(command(["git","rev-parse","HEAD"],merge)==MERGE and
         command(["git","rev-parse","HEAD^1"],merge)==BASE and
         command(["git","rev-parse","HEAD^2"],merge)==HEAD,
         "ACTUAL_CHECKED_OUT_GIT_PARENTS_MISMATCH")
 require(command(["git","rev-parse","HEAD"],base)==BASE,"SOURCE_MAIN_CHECKOUT_MISMATCH")
 return True
def invoke(node,frozen,merge,dir,ctx,report):
 env=os.environ.copy()
 env.update({"GITHUB_SHA":MERGE,"GITHUB_RUN_ID":str(RUN),
             "GITHUB_RUN_ATTEMPT":str(ATTEMPT),"GITHUB_EVENT_NAME":"pull_request",
             "GITHUB_EVENT_PATH":str(ctx),"GITHUB_JOB":"measured-host-activity",
             "RUNNER_OS":report})
 return subprocess.run(["node",str(node),str(frozen),str(dir)],
          cwd=str(merge),env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
          text=True,timeout=130)
def tamper(directory,case):
 host=directory/"host-activity.json"
 instr=directory/"instrument-status.json"
 dig=directory/"digital.json"
 where=host
 if case=="missing_host":
  where.unlink()
  return
 if case=="raw_bit_corrupted_without_sidecar":
  bad=bytearray(where.read_bytes());bad[12]^=1;where.write_bytes(bad)
  return
 if case.startswith("sensor_") or case=="optical_retention_fake":where=instr
 if case=="wrong_source_root":where=dig
 body=json.loads(where.read_bytes())
 if case=="plausible_cpu":body["cpu_elapsed_ns"]+=10_000_000
 elif case=="plausible_rss":body["rss_during_bytes"]+=8192
 elif case=="plausible_wall":body["wall_elapsed_ns"]+=10_000_000
 elif case=="wrong_pr_head":body["pr_head_sha"]="f"*40
 elif case=="wrong_pr_attempt":body["github_run_attempt"]+=1
 elif case=="wrong_pr_number":body["github_pr_number"]+=1
 elif case=="wrong_run":body["github_run_id"]=str(int(body["github_run_id"])+17)
 elif case=="wrong_merge":body["producing_git_sha"]="f"*40
 elif case=="wrong_os":
  body["runner_os"]="Linux" if body["runner_os"]=="Windows" else "Windows"
 elif case=="wrong_job":body["github_job"]="different-plausible-job"
 elif case=="sensor_current":
  body["channels"]["device_current_a"]={"measured":True,"value":1.2,
        "instrument_id":"FORGED_TEST_METER","raw_capture_sha256":"0"*64}
 elif case=="sensor_optical":
  body["channels"]["optical_spectral_counts"]={"measured":True,"value":8,
        "instrument_id":"FORGED_LIGHT_SENSOR","raw_capture_sha256":"0"*64}
 elif case=="optical_retention_fake":body["optical_retention_measured"]=True
 elif case=="wrong_source_root":body["source_sha256"]="f"*64
 else:raise ValueError("UNKNOWN_CASE:"+case)
 raw=dump(body)
 where.write_bytes(raw)
 (directory/(where.name+".sha256")).write_bytes(
  (sha(raw)+"  "+where.name+"\n").encode("ascii"))
def main(args):
 root,base,merge,archives,out=map(lambda p:Path(p).resolve(),args)
 out.mkdir(parents=True,exist_ok=True)
 inspect_api(root,base,merge)
 hbp=base/"stones/2026-10-15-rainbow81/seat4-round5-signed-spectrum-mapping-20261015.hbp"
 byte_source=hbp.read_bytes()
 require(len(byte_source)==701 and sha(byte_source)==HBP_SHA and
         BANK.encode("ascii") in byte_source,"SOURCE_NOT_ORIGINAL")
 payload=(byte_source*((2*1024*1024+700)//701))[:2*1024*1024]
 h=hashlib.sha256()
 for i in range(256):h.update(payload);h.update(i.to_bytes(4,"little"))
 require(h.hexdigest()==EXPECTED,"INDEPENDENT_WORKLOAD_SHA_MISMATCH")
 node=(merge/"experiments/seat2/round9/review_host_bridge.js").resolve()
 require(node.is_file(),"UPSTREAM_REVIEWER_SOURCE_MISSING")
 cases={"plausible_cpu":True,"plausible_rss":True,"plausible_wall":True,
        "wrong_pr_head":False,"wrong_pr_attempt":False,
        "wrong_pr_number":False,"wrong_run":False,"wrong_merge":False,
        "wrong_os":False,"wrong_job":False,
        "sensor_current":False,"sensor_optical":False,
        "optical_retention_fake":False,"wrong_source_root":False,
        "missing_host":False,"raw_bit_corrupted_without_sidecar":False}
 details=[]
 stable={}
 with tempfile.TemporaryDirectory(prefix="seat4-pr111-r9c-") as tmp:
  temp=Path(tmp);event=temp/"event.json"
  event.write_bytes(dump({"pull_request":{"number":PR,"head":{"sha":HEAD}}}))
  for os_name,py,reported_os in SLOTS:
   name=f"seat2-r9-{os_name}-py{py}"
   folder=archives/name
   require(folder.is_dir(),"MISSING_PRODUCER_ARCHIVE:"+name)
   objects={key:audited(folder,key) for key in FILES}
   d=objects["digital.json"][0];host=objects["host-activity.json"][0]
   instrument=objects["instrument-status.json"][0];attacks=objects["attack-review.json"][0]
   require(d["source_sha256"]==HBP_SHA and d["deterministic_workload_sha256"]==EXPECTED and
           d["source_git_commit"]==BASE,"FROZEN_DIGITAL_ROOT_INVALID")
   for static in ("digital.json","instrument-status.json","node-review.json","attack-review.json"):
    blob=objects[static][1]
    if static in stable:require(stable[static]==blob,"STATIC_SOURCE_DIGEST_DIFFERS:"+static)
    else:stable[static]=blob
   require(host["github_run_id"]==str(RUN) and host["producing_git_sha"]==MERGE and
           host["pr_head_sha"]==HEAD and host["github_run_attempt"]==ATTEMPT and
           host["github_pr_number"]==PR and host["github_event_name"]=="pull_request" and
           host["source_sha256"]==HBP_SHA and host["python"].startswith(py) and
           host["runner_os"]==reported_os and host["platform_system"]==reported_os and
           host["github_job"]=="measured-host-activity","HOST_ORIGINAL_PROVIDER_CONTEXT_MISMATCH")
   require(host["cpu_elapsed_ns"]>0 and host["wall_elapsed_ns"]>0 and
           host["rss_during_bytes"]-host["rss_before_bytes"]>=1024*1024,
           "ORIGINAL_HOST_ACTIVITY_MISSING")
   require(attacks["case_count"]==10 and attacks["forgeries_rejected"]==9 and
           attacks["unsigned_positive_cpu_counter_forgery_accepted_as_expected"] is True,
           "ORIGINAL_AUTHOR_NEGATIVES_NOT_RECORDED")
   require(all(z["measured"] is False and z["value"] is None for z in
               instrument["channels"].values()) and
           instrument["externally_attested_instrument_data"] is False and
           instrument["optical_retention_measured"] is False,
           "FORGED_ACTUAL_INSTRUMENT_STATUS_IN_ORIGINAL")
   good=temp/("clean-"+name);shutil.copytree(folder,good)
   result=invoke(node,base,merge,good,event,reported_os)
   require(result.returncode==0,"AUTHENTIC_ORIGINAL_READBACK_FAILED:"+name+":"+result.stderr[-350:])
   verified_node=(good/"node-review.json").read_bytes()
   require(verified_node==objects["node-review.json"][1],
           "ORIGINAL_NODE_REVIEW_DOES_NOT_REGENERATE")
   if os_name=="ubuntu-latest" and py=="3.11":
    for case,expected in cases.items():
     location=temp/("attacked-"+case)
     shutil.copytree(folder,location)
     tamper(location,case)
     checked=invoke(node,base,merge,location,event,reported_os)
     accepted=checked.returncode==0
     require(accepted==expected,"HOST_OR_SENSOR_FORGERY_UNEXPECTED_VERDICT:"+case+
             ":observed="+str(accepted)+":log="+checked.stderr[-350:])
     details.append({"attack":case,
       "actual_original_node_reviewer_accepts":accepted,
       "unsupported_meter_claim":case.startswith("sensor_")})
 output={"schema":"ASOLARIA-SEAT4-R9C-PR111-EXACT-PROVENANCE-REPLAY-V1",
    "reviewed_pr":PR,"reviewed_original_head":HEAD,
    "actual_merge_commit":MERGE,"actual_merge_commit_parents":[BASE,HEAD],
    "producing_workflow_run":RUN,"run_attempt":ATTEMPT,
    "host_archive_count":4,"source_sha256":HBP_SHA,
    "source_bank_reference_only_sha256":BANK,
    "independent_recomputed_workload_sha256":EXPECTED,
    "original_node_reviewer_baselines_independently_executed":4,
    "source_and_context_attestation":"GITHUB_PROVIDER_AND_GIT_BOUNDED_ONLY",
    "additional_cases_against_original_node":details,
    "expected_accepted_unsigned_plausible_metrics":3,
    "expected_rejected_source_and_sensor_spoofs":len(cases)-3,
    "independent_calibrated_physical_counter_signature":False,
    "real_optical_or_electrical_metrology_captured_in_this_run":False,
    "historical_operator_completed_photon_memory_report":"PRESERVED",
    "result":"DIGITAL_RUN_HEAD_MERGE_ATTEMPT_VERIFIED;UNSIGNED_NUMERIC_CPU_RSS_ELAPSED_UNATTESTED"}
 raw=dump(output);(out/"seat4-pr111-r9c-review.json").write_bytes(raw)
 (out/"seat4-pr111-r9c-review.json.sha256").write_bytes((sha(raw)+"  seat4-pr111-r9c-review.json\n").encode("ascii"))
 print(json.dumps({"result":"R9C_INDEPENDENT_HEAD_MERGE_ATTEMPT_PASS",
       "original_archive_count":4,"actual_node_attack_cases":len(details),
       "referee_accepts_expected_unsigned_counters":3,
       "referee_rejects_bad_source_and_instrument":len(cases)-3,
       "receipt_sha256":sha(raw),"physical_sensor":"NOT_CAPTURED"},sort_keys=True))
if __name__=="__main__":
 if len(sys.argv)!=6:raise SystemExit("usage: audit_latest.py API_DIR FROZEN_MAIN MERGE_WORKTREE ORIGINAL_4_ARCHIVES OUT")
 main(sys.argv[1:])
