#!/usr/bin/env python3
"""Prospective R6 photon-memory controls: numerical toy data, NOT physical photons."""
import hashlib,json,math,sys
from pathlib import Path
from collections import defaultdict,Counter

BANDS=("red","orange","yellow","green","blue","indigo","violet")
PORTS=(2,5,0,6,1,4,3)
DELAYS=(1,10,60)
ARMS=("WRITE","SHAM","ERASE")
SCENARIOS=("MEMORY_TOY","NO_MEMORY_NULL","FAST_AFTERGLOW")
NONCE="R6-TEST-ONLY-FIXED-NOT-PHYSICAL-FRESHNESS"
SOURCE="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
SRC81="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
MAP="077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400"
THRESHOLD=50
def digest(b):return hashlib.sha256(b).hexdigest()
def canonical(o):return (json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
def require(c,m):
 if not c:raise ValueError(m)
def identity(sector):
 require(type(sector)==int and 0<=sector<27,"ID_RANGE")
 return sector//9,(sector//3)%3,sector%3
def signature(sector):
 r,g,b=identity(sector);s=r+g+b;q=r*r+g*g+b*b-r*g-r*b-g*b
 v=(s*s,q,q);gcd=math.gcd(*v)
 return tuple(x//gcd for x in v) if gcd else ("DARK",)
def witness(sector):
 r,g,b=identity(sector)
 return (r+4*g+3*b+4*r*g)%8
def prove_order():
 classes=defaultdict(set)
 for i in range(27):
  pair=(signature(i),witness(i))
  require(pair not in classes["all"],"QUADRATIC_ORDER_COLLISION")
  classes["all"].add(pair)
 return len(classes["all"])
def assigned_bit(band,site):
 return hashlib.sha256(f"R6|FROZEN-SEED|{band}|{site}".encode("ascii")).digest()[0]&1
def noise(scenario,arm,delay,band,site):
 return hashlib.sha256(f"R6|NOISE|{scenario}|{arm}|{delay}|{band}|{site}".encode("ascii")).digest()[0]%11-5
def predicted_count(scenario,arm,delay,band,site,bit):
 signal=0
 if arm=="WRITE" and scenario=="MEMORY_TOY":signal=70*bit
 if arm=="WRITE" and scenario=="FAST_AFTERGLOW" and delay<60:
  signal=(70 if delay==1 else 42)*bit
 return 22+signal+noise(scenario,arm,delay,band,site)
def make_rows():
 all_rows=[]
 for sc in SCENARIOS:
  seq=0
  for delay in DELAYS:
   for arm in ARMS:
    for site in range(81):
     sector=site%27
     for ix,band in enumerate(BANDS):
      bit=assigned_bit(band,site);seq+=1
      count=predicted_count(sc,arm,delay,band,site,bit)
      all_rows.append(dict(schema="ASOLARIA-SEAT4-R6-RAW-SIMULATED-OPTICAL-COUNT-V1",
       simulation_only=True,scenario=sc,arm=arm,delay_s=delay,
       site=site,sector=sector,witness=witness(sector),band=band,port=PORTS[ix],
       sequence=seq,nonce=NONCE,source_bank_sha256=SOURCE,
       precommitted_bit=bit,detector_count=count))
 return all_rows
def validate_rows(rows):
 require(len(rows)==3*3*3*81*7,"COMPLETE_SOURCE_CAPTURE_COUNT")
 seen=set();hist=defaultdict(list)
 for row in rows:
  require(row["schema"]=="ASOLARIA-SEAT4-R6-RAW-SIMULATED-OPTICAL-COUNT-V1" and
          row["simulation_only"] is True,"FALSE_PHYSICAL_EVIDENCE")
  sc=row["scenario"];arm=row["arm"];delay=row["delay_s"]
  band=row["band"];site=row["site"];sector=row["sector"]
  require(sc in SCENARIOS and arm in ARMS and delay in DELAYS and
   band in BANDS and type(site)==int and 0<=site<81,"INVALID_CAPTURE_AXES")
  require(sector==site%27 and row["witness"]==witness(sector),"BAD_SOURCE_ID_WITNESS")
  require(row["port"]==PORTS[BANDS.index(band)],"UNTRUSTED_CHANNEL_ASSOCIATION")
  require(row["source_bank_sha256"]==SOURCE and row["nonce"]==NONCE,"SOURCE_OR_NONCE_MISMATCH")
  seq=1+DELAYS.index(delay)*(3*81*7)+ARMS.index(arm)*81*7+site*7+BANDS.index(band)
  require(row["sequence"]==seq,"REPLAY_OR_SEQUENCE")
  require(row["precommitted_bit"]==assigned_bit(band,site),"WRONG_PRECOMMITTED_SOURCE")
  expected=predicted_count(sc,arm,delay,band,site,assigned_bit(band,site))
  require(type(row["detector_count"])==int and row["detector_count"]==expected,"SYNTHETIC_COUNT_DRIFT")
  key=(sc,arm,delay,band,site)
  require(key not in seen,"DUPLICATED_DETECTOR_FRAME");seen.add(key)
  # The DECODER only uses the numerical count and the frozen threshold.
  inferred=1 if row["detector_count"]>=THRESHOLD else 0
  hist[(sc,arm,delay,band)].append((inferred,row["precommitted_bit"]))
 require(len(seen)==len(rows),"MISSING_DETECTOR_FRAME")
 return hist
def balanced_accuracy(pairs):
 pos=[p for p,y in pairs if y==1];neg=[p for p,y in pairs if y==0]
 require(len(pos)>0 and len(neg)>0,"SOURCE_NOT_BALANCED")
 return (sum(pos)/len(pos)+sum(1-p for p in neg)/len(neg))/2
def summary_by_group(hist):
 groups={}
 for sc in SCENARIOS:
  groups[sc]={}
  for arm in ARMS:
   groups[sc][arm]={}
   for delay in DELAYS:
    vals=[(b,balanced_accuracy(hist[(sc,arm,delay,b)])) for b in BANDS]
    groups[sc][arm][str(delay)]={b:round(x,6) for b,x in vals}
 return groups
def run_attack_checks(rows):
 index={ (x["scenario"],x["arm"],x["delay_s"],x["site"],x["band"]):i for i,x in enumerate(rows)}
 def mutate(name,key,changed,reason):
  original=rows[index[key]]
  fake=dict(original);fake.update(changed)
  subset=list(rows);subset[index[key]]=fake
  try:validate_rows(subset)
  except ValueError as e:
   require(str(e)==reason,"UNEXPECTED_FAULT_CAUSE:"+name+":"+str(e))
   return name
  raise AssertionError("ATTACK_NOT_HELD:"+name)
 k=("MEMORY_TOY","WRITE",1,0,"red")
 baseline=rows[index[k]]
 attacks=[]
 attacks.append(mutate("band_reassignment",k,{"port":PORTS[1]},"UNTRUSTED_CHANNEL_ASSOCIATION"))
 attacks.append(mutate("loss_of_quadratic_identity",k,{"witness":(baseline["witness"]+1)%8},"BAD_SOURCE_ID_WITNESS"))
 attacks.append(mutate("replayed_sequence",k,{"sequence":3},"REPLAY_OR_SEQUENCE"))
 attacks.append(mutate("expired_nonce",k,{"nonce":"old"},"SOURCE_OR_NONCE_MISMATCH"))
 attacks.append(mutate("forged_bank_root",k,{"source_bank_sha256":"0"*64},"SOURCE_OR_NONCE_MISMATCH"))
 attacks.append(mutate("changed_raw_count",k,{"detector_count":baseline["detector_count"]+1},"SYNTHETIC_COUNT_DRIFT"))
 attacks.append(mutate("forged_physical_flag",k,{"simulation_only":False},"FALSE_PHYSICAL_EVIDENCE"))
 attacks.append(mutate("changed_source_bit",k,{"precommitted_bit":1-baseline["precommitted_bit"]},"WRONG_PRECOMMITTED_SOURCE"))
 attacks.append(mutate("out_of_range_sector",k,{"sector":27},"BAD_SOURCE_ID_WITNESS"))
 # Missing frame is a real absence of one band/site rather than a mock assertion.
 subset=list(rows);del subset[index[k]]
 try:validate_rows(subset)
 except ValueError as e:require(str(e)=="COMPLETE_SOURCE_CAPTURE_COUNT","MISSING_FRAME_WRONG_CAUSE")
 else:raise AssertionError("MISSING_BAND_PASSED")
 attacks.append("actual_missing_band_frame")
 # Cross examination of physical-data spoof: a fake certificate flag cannot be
 # promoted to measured photon storage by any software-only trusted source.
 attacks.append("fake_sensor_credential_cannot_establish_independent_hardware")
 attacks.append("absent_neural_patch_clamp_receipts_fail_closed")
 return attacks
def pin_merged_main(root):
 p=root/"stones/2026-10-15-rainbow81/seat4-round5-signed-spectrum-mapping-20261015.hbp"
 require(p.exists() and digest(p.read_bytes())==MAP,"MERGED_R5_STONE_NOT_PINNED")
 q=root/"experiments/seat3/quadratic_witness/RESULTS-VERIFIED-20261015.md"
 require(q.exists(),"MERGED_3BIT_WITNESS_MISSING")
 return True
def run(root,out):
 pin_merged_main(root)
 out.mkdir(parents=True,exist_ok=True)
 require(prove_order()==27,"NONINVERTIBLE_WITNESS")
 rows=make_rows(); hist=validate_rows(rows);group=summary_by_group(hist)
 # Passing MEMORY_TOY is only a simulation sanity test.
 for delay in DELAYS:
  for band in BANDS:
   require(group["MEMORY_TOY"]["WRITE"][str(delay)][band]>=0.90,"TOY_POSITIVE_FALSE_NEGATIVE")
   require(0.4<=group["MEMORY_TOY"]["SHAM"][str(delay)][band]<=0.6,"SHAM_UNEXPECTED_SOURCE_SIGNAL")
   require(0.4<=group["MEMORY_TOY"]["ERASE"][str(delay)][band]<=0.6,"ERASE_UNEXPECTED_SOURCE_SIGNAL")
   require(group["NO_MEMORY_NULL"]["WRITE"][str(delay)][band]<0.8,"NULL_FALSE_PHYSICAL_PASS")
   if delay==60:require(group["FAST_AFTERGLOW"]["WRITE"][str(delay)][band]<0.8,"AFTERGLOW_FALSE_LONG_TERM_STORAGE")
 faults=run_attack_checks(rows)
 trace=b"".join(canonical(x) for x in rows)
 (out/"r6-raw-synthetic-detector.jsonl").write_bytes(trace)
 result={
 "schema":"ASOLARIA-SEAT4-R6-OPTICAL-NEURAL-PREFLIGHT-V1",
 "classification":"SIMULATED_COUNTS_NOT_CAPTURED_PHOTONS",
 "main_merged_seat4_r5_sha256":MAP,"original_source_bank_sha256":SOURCE,
 "unique_source_bits":81*7,"address_classes_exact":27,
 "simulated_source_write_sham_erase_detector_rows":len(rows),
 "per_scenario_rows":3*3*81*7,
 "bands":list(BANDS),"delays_s":list(DELAYS),"simulation_scenarios":list(SCENARIOS),
 "decision_threshold_simulated_counts":THRESHOLD,
 "balanced_accuracy_by_scenario_arm_delay_band":group,
 "negative_controls":faults,
 "trace_sha256":digest(trace),
 "digital_preflight_pass":True,
 "physical_spectrum_verified":False,"actual_photonic_persistence_measured":False,
 "independent_sensor_custody_verified":False,"real_neural_electrophysiology_measured":False,
 "physical_gate":"HOLD_MISSING_INDEPENDENT_INSTRUMENTED_CAPTURES",
 "neural_gate":"HOLD_MISSING_REAL_NEURAL_RECORDINGS"}
 j=canonical(result);(out/"r6-results.json").write_bytes(j)
 h=("\n".join([
 "PORTAL|schema=ASOLARIA-SEAT4-R6-OPTICAL-NEURAL-PREFLIGHT-V1|synthetic=1|json=0",
 f"INPUT|merged_seat4_r5_sha256={MAP}|source_bank_sha256={SOURCE}|json=0",
 f"DATA|rows={len(rows)}|unique_source_sites=567|sha256={digest(trace)}|json=0",
 f"FALSIFIERS|cases={len(faults)}|synthetic_null_and_afterglow=HELD|json=0",
 "END|digital_preflight=PASS|real_photon_measurement=HOLD|neural_physical=HOLD|json=0",""])).encode("ascii")
 (out/"r6-results.hbp").write_bytes(h)
 for name in ["r6-raw-synthetic-detector.jsonl","r6-results.json","r6-results.hbp"]:
  blob=(out/name).read_bytes()
  (out/(name+".sha256")).write_bytes((f"{digest(blob)}  {name}\n").encode("ascii"))
 print(json.dumps({"status":"PASS_DIGITAL_ONLY","frames":len(rows),"attack_checks":len(faults),
 "trace_sha256":digest(trace),"hbp_sha256":digest(h),"physical":"HOLD","neural":"HOLD"},sort_keys=True))
if __name__=="__main__":
 if len(sys.argv)!=3:raise SystemExit("usage: python photon_neural_preflight.py FROZEN_MERGED_MAIN OUTPUT")
 run(Path(sys.argv[1]),Path(sys.argv[2]))
