#!/usr/bin/env python3
"""Seat4 R8 light/vibration factorial *simulation*: never optical or acoustic measurements."""
import hashlib,json,sys
from pathlib import Path
BANDS=("red","orange","yellow","green","blue","indigo","violet")
DELAYS=(1,10,60); ARMS=((0,0),(1,0),(0,1),(1,1))
REGIMES=("NULL","OPTICAL_ONLY","INTERACTION_TOY","THERMAL_CONFOUND")
ROOTS={"source":"02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22",
"bank":"52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345",
"index":"6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"}
def sha(x):return hashlib.sha256(x).hexdigest()
def enc(x):return (json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")
def require(ok,name):
 if not ok:raise ValueError(name)
def read_sources(folder):
 paths={"source":"base-evidence/lightbank-memories.json",
        "bank":"rainbow-evidence/rainbow7-bank.jsonl",
        "index":"rainbow-evidence/rainbow7-index.hbi"}
 data={k:(folder/rel).read_bytes() for k,rel in paths.items()}
 for k,blob in data.items():require(sha(blob)==ROOTS[k],"ORIGINAL_SOURCE_PIN_"+k)
 original=json.loads(data["source"])["records"]
 require(len(original)==81 and len(data["bank"])==184815 and len(data["index"])==70043,"ORIGINAL_SOURCE_BOUNDS")
 rows={}
 for line in data["index"].decode("ascii").splitlines():
  cols=line.split("|");require(cols[0]=="MEM" and len(cols)==6,"INDEX_SCHEMA")
  d=dict(x.split("=",1) for x in cols[1:])
  band=d["band"];site=int(d["id"].removeprefix("site-"))
  require(band in BANDS and 0<=site<81 and d["id"]==f"site-{site:03d}","INDEX_ID")
  offset=int(d["offset"]);size=int(d["length"]);require(0<=offset and size>0 and offset+size<=len(data["bank"]),"ROW_BOUNDS")
  blob=data["bank"][offset:offset+size]
  require(sha(blob)==d["sha256"] and json.loads(blob)["record"]==original[site],"ORIGINAL_ROW_CUSTODY")
  require((band,site) not in rows,"DUPLICATE_ROW")
  rows[(band,site)]=d["sha256"]
 require(len(rows)==567,"ROW_COUNT")
 return rows
def bit(row_sha):
 return hashlib.sha256(("ASOLARIA-R8-FROZEN-BIT|"+row_sha).encode("ascii")).digest()[0]&1
def roll(band,site,delay,rep):
 text=f"ASOLARIA-R8-COMMON-POTENTIAL-NOISE|{ROOTS['bank']}|{band}|{site}|{delay}|{rep}"
 return int.from_bytes(hashlib.sha256(text.encode("ascii")).digest()[:8],"big")%1000
def threshold(regime,light,acoustic):
 if regime=="NULL":return 880
 if regime=="OPTICAL_ONLY":return 880-300*light
 if regime=="INTERACTION_TOY":return 880-40*(light+acoustic)-340*light*acoustic
 if regime=="THERMAL_CONFOUND":return 880-75*(light+acoustic)**2
 raise ValueError("REGIME")
def row(regime,delay,band,site,rep,light,acoustic,root):
 require(regime in REGIMES and delay in DELAYS and band in BANDS and type(site)==int and 0<=site<81 and type(rep)==int and 0<=rep<8,"SOURCE_AXES")
 require((light,acoustic) in ARMS,"INTERVENTION_AXES")
 source=bit(root);success=roll(band,site,delay,rep)<threshold(regime,light,acoustic)
 return {"schema":"ASOLARIA-SEAT4-R8-LIGHT-VIBRATION-SIMULATED-V1",
         "simulation_only":True,"regime":regime,"delay_label_s":delay,"band":band,"site":site,
         "rep":rep,"light":light,"acoustic":acoustic,"source_leaf_sha256":root,"source_bit":source,
         "readout_bit":source if success else 1-source,"correct":int(success),
         "sim_optical_meter_nw":1000*light,"sim_accelerometer_mg":100*acoustic,
         "sim_temperature_mK":25000+250*(light+acoustic) if regime=="THERMAL_CONFOUND" else 25000,
         "sim_supply_uV":3300000,"actual_photons_measured":False,"actual_phonons_measured":False}
def verify_row(candidate,reference):
 expected=row(reference["regime"],reference["delay_label_s"],reference["band"],
    reference["site"],reference["rep"],reference["light"],reference["acoustic"],reference["source_leaf_sha256"])
 require(candidate==expected,"UNTRUSTED_FACTORIAL_OBSERVATION")
def exercise_faults(ref):
 mutants=[
  ("source_leaf_swap",{"source_leaf_sha256":"0"*64}),
  ("wrong_light",{"light":1-ref["light"]}),
  ("wrong_acoustic",{"acoustic":1-ref["acoustic"]}),
  ("false_retention",{"delay_label_s":60}),
  ("replayed_rep",{"rep":7}),
  ("wrong_site",{"site":80}),
  ("wrong_band",{"band":"violet"}),
  ("tampered_detected_bit",{"readout_bit":1-ref["readout_bit"]}),
  ("fake_physical_photon",{"actual_photons_measured":True}),
  ("forged_detector_temp",{"sim_temperature_mK":ref["sim_temperature_mK"]+100}),
  ("forged_supply",{"sim_supply_uV":1}),
  ("fake_optical_meter",{"sim_optical_meter_nw":100}),
  ("false_neural_evidence",{"biological_neural_measured":True})]
 failed=[]
 for name,update in mutants:
  c={**ref,**update}
  try:verify_row(c,ref)
  except ValueError as e:
   require(str(e)=="UNTRUSTED_FACTORIAL_OBSERVATION",name+"_WRONG_ERROR");failed.append(name)
  else:raise AssertionError("FAULT_ACCEPTED_"+name)
 return failed
def run(root,out):
 out.mkdir(parents=True,exist_ok=True)
 indexed=read_sources(root)
 census={s:{str(t):{f"{l}{a}":0 for l,a in ARMS} for t in DELAYS} for s in REGIMES}
 total=0;sample=None
 with (out/"r8-synthetic-factorial.jsonl").open("wb") as f:
  for regime in REGIMES:
   for delay in DELAYS:
    for band in BANDS:
     for site in range(81):
      for rep in range(8):
       for light,acoustic in ARMS:
        x=row(regime,delay,band,site,rep,light,acoustic,indexed[(band,site)])
        if sample is None:sample=x
        f.write(enc(x));total+=1
        census[regime][str(delay)][f"{light}{acoustic}"]+=x["correct"]
 require(total==4*3*7*81*8*4,"TOTAL_FACTORIAL_FRAME_COUNT")
 faults=exercise_faults(sample)
 N=7*81*8
 metrics={}
 for regime in REGIMES:
  metrics[regime]={}
  for delay in DELAYS:
   cells={name:census[regime][str(delay)][name]/N for name in ("00","10","01","11")}
   metrics[regime][str(delay)]={
    "p_correct_00":round(cells["00"],6),
    "p_correct_10":round(cells["10"],6),
    "p_correct_01":round(cells["01"],6),
    "p_correct_11":round(cells["11"],6),
    "D_light":round(cells["10"]-cells["00"],6),
    "D_acoustic":round(cells["01"]-cells["00"],6),
    "D_interaction":round(cells["11"]-cells["10"]-cells["01"]+cells["00"],6)}
   d=metrics[regime][str(delay)]
   if regime=="NULL":require(all(d[k]==0 for k in ("D_light","D_acoustic","D_interaction")),"NULL_SPURIOUS_ASSOCIATION")
   if regime=="OPTICAL_ONLY":require(d["D_light"]<-.2 and d["D_acoustic"]==0 and d["D_interaction"]==0,"OPTICAL_NEGATIVE")
   if regime=="INTERACTION_TOY":require(d["D_interaction"]<-.2,"MISSING_INTERACTION")
   if regime=="THERMAL_CONFOUND":require(d["D_interaction"]<-.07,"CONFOUND_NOT_OBSERVED")
 raw=(out/"r8-synthetic-factorial.jsonl").read_bytes()
 result={"schema":"ASOLARIA-SEAT4-R8-LIGHT-ACOUSTIC-FACTORIAL-V1","classification":"SOFTWARE_POTENTIAL_OUTCOME_FIXTURE_ONLY",
  "original_bank_sha256":ROOTS["bank"],"distinct_original_memories":81,"stored_band_site_references":567,
  "total_factorial_rows":total,"rows_per_regime":total//len(REGIMES),"frozen_simulation_regimes":list(REGIMES),
  "real_retention_seconds_elapsed":False,"original_source_bits_per_band_site":567,
  "measurement_arms":["00","10","01","11"],"statistical_contrasts_by_regime_and_delay":metrics,
  "thermal_confounded_apparent_interaction_has_optical_mechanism":False,
  "correlation_proves_photon_phonon_storage":False,"source_fake_waveforms_measured":False,
  "digital_negative_controls":faults,"trace_sha256":sha(raw),
  "photonic_memory_verified":False,"phononic_memory_verified":False,
  "biological_neural_memory_verified":False,"external_independent_instrument_custody":False,
  "physical_verdict":"HOLD_NO_REAL_OPTICAL_ACOUSTIC_DETECTOR_INPUT"}
 summary=enc(result)
 (out/"r8-results.json").write_bytes(summary)
 hbp=("\n".join([
 "PORTAL|seat=4|round=8|light_acoustic_factorial=SIMULATED|json=0",
 f"SOURCE|original_bank_sha256={ROOTS['bank']}|stored_bank_entries=567|json=0",
 f"FACTOR|synthetic_rows={total}|regimes=4|time_labels=1,10,60|trace_sha256={sha(raw)}|json=0",
 "ATTACKS|semantic_mutations=13|thermal_confound=OBSERVED_IN_TOY|json=0",
 "END|digital_preflight=PASS|actual_photon_or_phonon_storage=UNVERIFIED|neural_real=UNVERIFIED|json=0",""])).encode("ascii")
 (out/"r8-results.hbp").write_bytes(hbp)
 for name in ("r8-synthetic-factorial.jsonl","r8-results.json","r8-results.hbp"):
  data=(out/name).read_bytes()
  (out/(name+".sha256")).write_bytes((sha(data)+"  "+name+"\n").encode("ascii"))
 print(json.dumps({"digital":"PASS","frames":total,"faults":len(faults),"per_delay":metrics,
                   "trace_sha256":sha(raw),"hbp_sha256":sha(hbp),"physical":"HOLD"},sort_keys=True))
if __name__=="__main__":
 if len(sys.argv)!=3:raise SystemExit("usage: python producer.py UPSTREAM_PR80_ARTIFACT OUT")
 run(Path(sys.argv[1]),Path(sys.argv[2]))
