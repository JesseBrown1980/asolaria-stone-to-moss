#!/usr/bin/env python3
"""Independent archived-source LIF/MCP referee: classical byte computation only."""
from __future__ import annotations
import copy,csv,hashlib,io,importlib.util,json,sys,tempfile
from collections import defaultdict
from pathlib import Path
BANDS=("red","orange","yellow","green","blue","indigo","violet")
MODES=("bright_t0","dim_t0","bright_t3","dark_t0","protected_t3")
ROW_EXPECT={"bank":"52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345",
"index":"6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee",
"source":"02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22",
"parent":"332e1eeb2d4de748c2e1da07729944fefe5b63589e9533b4c93b74d7cf3f5527"}
EXPECTED_MATCH=(567,0,541,231,567)
EXPECTED_ORIGINAL=(567,0,514,142,567)
EXPECTED_FALSE=(0,0,27,89,0)
WAVELENGTHS=(650,610,580,530,470,440,405)
FRAME_KEYS={"schema","scenario","ordinal","site","band","sector",
"wavelength_nm_assumed","expected_row_sha256","observed_row_sha256","readback_hex",
"bit_errors","emitted_photons_modeled","photoelectrons_modeled","dark_electrons_modeled",
"emitted_energy_yJ_assumed","context_nonce","mcp_request","mcp_response"}
def sha(x):return hashlib.sha256(x).hexdigest()
def emit(x):return (json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
def require(ok,reason):
 if not ok:raise ValueError(reason)
def pinned(path,digest,size=None):
 b=Path(path).read_bytes()
 require(sha(b)==digest and (size is None or len(b)==size),"FROZEN_INPUT_ROOT_MISMATCH")
 return b
def rows(root):
 bank=pinned(root/"rainbow-evidence/rainbow7-bank.jsonl",ROW_EXPECT["bank"],184815)
 idx=pinned(root/"rainbow-evidence/rainbow7-index.hbi",ROW_EXPECT["index"],70043)
 source=pinned(root/"original-evidence/lightbank-memories.json",ROW_EXPECT["source"],16689)
 originals=json.loads(source)["records"];require(len(originals)==81,"SOURCE_SITE_COUNT")
 result=[];seen=set()
 for line in idx.decode("ascii").splitlines():
  fragments=line.split("|");require(len(fragments)==6 and fragments[0]=="MEM","BANK_INDEX_SCHEMA")
  d=dict(x.split("=",1) for x in fragments[1:]);name=d["id"];band=d["band"]
  site=int(name.removeprefix("site-"));key=(band,name)
  require(band in BANDS and 0<=site<81 and key not in seen,"BAD_OR_DUPLICATE_BANK_ADDRESS")
  offset=int(d["offset"]);length=int(d["length"])
  require(offset>=0 and length>0 and offset+length<=len(bank),"BANK_ROW_BOUNDS")
  blob=bank[offset:offset+length]
  require(sha(blob)==d["sha256"],"ROW_DIGEST")
  record=json.loads(blob)
  require(record["band"]==band and record["id"]==name and record["record"]==originals[site],"ROW_ANCESTRY")
  result.append({"site":name,"band":band,"raw":blob,"sha":d["sha256"]});seen.add(key)
 require(len(result)==567 and len(seen)==567,"MISSING_SOURCE_BANK")
 return result
def spikes(payload):
 v=0;n=0;hist=[]
 for i,c in enumerate(payload):
  for shift in (7,6,5,4,3,2,1,0):
   v=max(0,v-1)+4*((c>>shift)&1)
   if v>=7:v-=7;n+=1
   if (i*8+7-shift)%32==31:hist.append(n);n=0
 if len(payload)*8%32:hist.append(n)
 require(all(0<=x<=32 for x in hist),"SPIKES_OUT_OF_RANGE")
 return bytes(hist)
def check_frame(x,source,mode,ordinal):
 require(set(x)==FRAME_KEYS and x["schema"]=="ASOLARIA-PHOTON-ELECTRON-MCP-CLASSICAL-V1","MODEL_FRAME_SCHEMA")
 require(x["scenario"]==mode and x["ordinal"]==ordinal and x["site"]==source["site"] and
         x["band"]==source["band"] and x["sector"]==ordinal%27,"UNTRUSTED_SOURCE_ADDRESS")
 require(x["expected_row_sha256"]==source["sha"] and
         x["wavelength_nm_assumed"]==WAVELENGTHS[BANDS.index(source["band"])],"UNTRUSTED_SOURCE_ROOT_OR_WAVELENGTH")
 request=x["mcp_request"];reply=x["mcp_response"]
 require(request.get("jsonrpc")=="2.0" and request.get("method")=="tools/call" and
         request.get("params",{}).get("name")=="electron.capture","UNTRUSTED_ELECTRON_TOOL")
 require(reply.get("jsonrpc")=="2.0" and reply.get("id")==request.get("id") and
         request.get("id")==f"{mode}:{ordinal}","UNTRUSTED_RPC_CORRELATION")
 args=request["params"]["arguments"]
 require(args["source_sha256"]==ROW_EXPECT["source"] and args["bank_sha256"]==ROW_EXPECT["bank"] and
         args["sector"]==ordinal%27 and args["band"]==source["band"] and
         args["site"]==source["site"] and args["expected_row_sha256"]==source["sha"],
         "UNTRUSTED_RPC_SOURCE_ANCHOR")
 nonce=sha(f"ASOLARIA-MCP-CAPTURE|{ROW_EXPECT['bank']}|{mode}|{ordinal}".encode())[:24]
 require(x["context_nonce"]==nonce and args["context_nonce"]==nonce,"UNTRUSTED_REPLAY_CONTEXT")
 blob=bytes.fromhex(x["readback_hex"])
 require(len(blob)==len(source["raw"]),"CHANGED_SOURCE_LENGTH")
 require(sha(blob)==x["observed_row_sha256"]==args["observed_row_sha256"]==
         reply["result"]["observed_row_sha256"],"FORGED_OBSERVED_DIGEST")
 error=sum((a^b).bit_count() for a,b in zip(blob,source["raw"]))
 require(error==x["bit_errors"],"FALSE_SOURCE_ERROR_COUNT")
 require(args["emitted_photons_modeled"]==x["emitted_photons_modeled"] and
         args["photoelectrons_modeled"]==x["photoelectrons_modeled"] and
         args["dark_electrons_modeled"]==x["dark_electrons_modeled"] and
         reply["result"]["photoelectrons_modeled"]==x["photoelectrons_modeled"],"UNTRUSTED_ELECTRON_COUNT")
 require(0<=x["photoelectrons_modeled"]<=x["emitted_photons_modeled"] and
         x["dark_electrons_modeled"]>=0,"ELECTRON_CONSERVATION")
 require(reply["result"].get("electron_engine")=="SIMULATED","FALSE_PHYSICAL_ELECTRON_ENGINE")
 expected_status="EXACT_READBACK" if error==0 else "BIT_ERRORS"
 require(reply["result"].get("status")==expected_status,"FALSE_ELECTRON_READBACK_STATUS")
 return blob,error
def fake_capture_test(r6path):
 spec=importlib.util.spec_from_file_location("original_seat4_physical_gate",str(r6path))
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 with tempfile.TemporaryDirectory() as tmp:
  folder=Path(tmp);header=("arm","band","site","delay_s","detector_counts","dark_counts",
                         "integration_ms","raw_capture_id","source_sequence","spectrometer_channel")
  output=io.StringIO(newline="");writer=csv.writer(output,lineterminator="\n");writer.writerow(header)
  n=0
  for delay in (1,10,60):
   for arm in ("WRITE","SHAM","ERASE"):
    for site in range(81):
     for i,band in enumerate(BANDS):
      n+=1;writer.writerow((arm,band,site,delay,22,2,10,"FAKE-NO-SENSOR",n,i))
  assert n==5103
  csvbytes=output.getvalue().encode("utf-8")
  challenge={"schema":"ASOLARIA-R6-PHYSICAL-CHALLENGE-V1","fresh_external_nonce":"FAKE-STATIC-TEST-NOT-FRESH",
   "source_precommit_sha256":"a"*64,"raw_capture_sha256":sha(csvbytes)}
  calibration={"schema":"ASOLARIA-R6-PHYSICAL-SPECTROMETER-CALIBRATION-V1",
    "seven_wavelengths_nm":[650,610,580,530,470,440,405],"spectrometer_model":"FAKE-NO-SPECTROMETER",
    "detector_calibration_sha256":"a"*64}
  custody={"source_custodian":"FAKE-CUSTODIAN","detector_custodian":"FAKE-CUSTODIAN",
    "external_witness":"FAKE-WITNESS"}
  def save():
   (folder/"challenge.json").write_bytes(emit(challenge))
   (folder/"calibration.json").write_bytes(emit(calibration))
   (folder/"custody.json").write_bytes(emit(custody))
   (folder/"detector.csv").write_bytes(csvbytes)
  save()
  base=module.intake(folder)
  require(base["decision"]=="PHYSICAL_HOLD" and base["reason"].startswith("RAW_CAPTURE_FORMAT_VALID"),
          "FAKE_PHYSICAL_CAPTURE_WAS_PROMOTED")
  digest_before=challenge["raw_capture_sha256"]
  challenge["raw_capture_sha256"]="f"*64;save()
  changed=module.intake(folder)
  require(changed["decision"]=="PHYSICAL_HOLD" and "RAW_FILE_DIGEST_MISMATCH" in changed["reason"],
          "TAMPERED_SENSOR_BYTES_ACCEPTED")
  challenge["raw_capture_sha256"]=digest_before;save()
  calibration["seven_wavelengths_nm"]=[600]*7;save()
  bad_waves=module.intake(folder)
  require(bad_waves["decision"]=="PHYSICAL_HOLD" and "DUPLICATE_OR_IMPOSSIBLE_WAVELENGTH" in bad_waves["reason"],
          "FALSE_SPECTRAL_CALIBRATION_ACCEPTED")
  calibration["seven_wavelengths_nm"]=[650,610,580,530,470,440,405];save()
  (folder/"detector.csv").unlink()
  missing=module.intake(folder)
  require(missing["decision"]=="PHYSICAL_HOLD","MISSING_HARDWARE_SOURCE_ACCEPTED")
  return {"synthetic_plausible_5103_record_claim":"PHYSICAL_HOLD",
    "recomputed_digest_attack":"PHYSICAL_HOLD","wrong_wavelength_calibration":"PHYSICAL_HOLD",
    "missing_raw_capture":"PHYSICAL_HOLD","real_measurements":0,
    "digital_negative_controls":4}
def attacks(baseline,source):
 mode="bright_t0";ordinal=0
 def reject(name,fun,reason):
  candidate=copy.deepcopy(baseline);fun(candidate)
  try:check_frame(candidate,source,mode,ordinal)
  except (ValueError,KeyError,TypeError,AssertionError) as err:
   require(str(err)==reason,"FAULT_WRONG_REASON_"+name+":"+str(err))
   return name
  raise AssertionError("MUTATION_ACCEPTED:"+name)
 tests=[]
 tests.append(reject("response_id_replay",lambda x:x["mcp_response"].update(id="old"),"UNTRUSTED_RPC_CORRELATION"))
 tests.append(reject("changed_rpc_method",lambda x:x["mcp_request"].update(method="tools/forged"),"UNTRUSTED_ELECTRON_TOOL"))
 tests.append(reject("fake_electron_tool",lambda x:x["mcp_request"]["params"].update(name="electron.bypass"),"UNTRUSTED_ELECTRON_TOOL"))
 tests.append(reject("band_reassignment",lambda x:x.update(band="violet"),"UNTRUSTED_SOURCE_ADDRESS"))
 tests.append(reject("wrong_sector",lambda x:x.update(sector=2),"UNTRUSTED_SOURCE_ADDRESS"))
 tests.append(reject("altered_source_anchor",lambda x:x["mcp_request"]["params"]["arguments"].update(bank_sha256="0"*64),"UNTRUSTED_RPC_SOURCE_ANCHOR"))
 tests.append(reject("stale_nonce",lambda x:x.update(context_nonce="expired"),"UNTRUSTED_REPLAY_CONTEXT"))
 tests.append(reject("fake_photoelectrons",lambda x:x.update(photoelectrons_modeled=x["emitted_photons_modeled"]+1),"UNTRUSTED_ELECTRON_COUNT"))
 tests.append(reject("unauthorized_physical_claim",lambda x:x.update(physical_measurement_claim=True),"MODEL_FRAME_SCHEMA"))
 # A self-consistent replacement of all local observed SHA values is NOT original source.
 def forge(x):
  mutated=bytearray.fromhex(x["readback_hex"]);mutated[0]^=1
  x["readback_hex"]=mutated.hex();d=sha(mutated)
  x["observed_row_sha256"]=d;x["mcp_request"]["params"]["arguments"]["observed_row_sha256"]=d
  x["mcp_response"]["result"]["observed_row_sha256"]=d
 def false_full(x):
  x["readback_hex"]="00"+x["readback_hex"][2:]
 tests.append(reject("coherent_local_observation_digest_forgery",forge,"FALSE_SOURCE_ERROR_COUNT"))
 tests.append(reject("altered_source_readback_hash",false_full,"FORGED_OBSERVED_DIGEST"))
 # Same record can appear correct without the original source bytes but false meta must fail.
 return tests
def main(root,r6source,out):
 out.mkdir(parents=True,exist_ok=True)
 references=rows(root)
 raw=pinned(root/"py-photon/photon-electron.hbp",ROW_EXPECT["parent"],6048391)
 lines=raw.splitlines();require(len(lines)==2835,"SOURCE_FRAME_COUNT")
 matches=[];strict=[];false=[];compact=[]
 base=None;source0=references[0]
 for mi,mode in enumerate(MODES):
  num=correct=bad=0
  for ordinal,ref in enumerate(references):
   frame=json.loads(lines[mi*567+ordinal])
   obs,errors=check_frame(frame,ref,mode,ordinal)
   if base is None:base=frame
   a=spikes(obs)==spikes(ref["raw"]);b=sha(obs)==ref["sha"]
   num+=a;correct+=b;bad+=a and not b
   compact.append(f"REC|mode={mode}|id={ordinal:03d}|neural={int(a)}|source={int(b)}|errors={errors}|source_sha={ref['sha']}|observed_sha={sha(obs)}\n".encode("ascii"))
  matches.append(num);strict.append(correct);false.append(bad)
 require(tuple(matches)==EXPECTED_MATCH and tuple(strict)==EXPECTED_ORIGINAL and
         tuple(false)==EXPECTED_FALSE,"PEER_LIF_CENSUS_DISAGREEMENT")
 witness=None
 orig=source0["raw"];target=spikes(orig)
 for off in range(min(32,len(orig))):
  for bit in range(8):
   x=bytearray(orig);x[off]^=1<<bit
   if spikes(x)==target and sha(x)!=source0["sha"]:
    witness={"site":source0["site"],"band":source0["band"],"byte_offset":off,
    "bit":bit,"original_sha256":source0["sha"],"corrupt_sha256":sha(x),
    "neural_window_spikes_equal":True,"byte_root_match":False};break
  if witness:break
 require(witness is not None,"NO_REAL_LIF_COLLISION_FOUND")
 assert len([r for r in references if r["band"]=="violet"])==81
 retained=[r for r in references if r["band"]!="violet"]
 require(len(retained)==486,"VIOLET_ERASURE_POLICY_FAIL_OPEN")
 fault=attacks(base,source0)
 fake=fake_capture_test(r6source)
 trace=b"".join(compact)
 summary={"schema":"ASOLARIA-SEAT4-R7-INDEPENDENT-NEURAL-REFEREE-V1",
  "classification":"DIGITAL_ONLY_SOURCE_PINNED_NO_REAL_PHOTONS_OR_NEURONS",
  "original_parent_hbp_sha256":ROW_EXPECT["parent"],
  "source_bank_sha256":ROW_EXPECT["bank"],
  "frames_replayed":len(lines),"full_bank_rows":567,
  "neural_matches":matches,"byte_exact_reads":strict,"neural_false_green":false,
  "false_green_fraction_among_neural_matches":[round(f/m,8) if m else None for f,m in zip(false,matches)],
  "one_bit_fingerprint_collision":witness,"violet_erasure_rows":81,
  "remaining_after_violet_erasure":486,"full_seven_band_read_after_erasure":"HOLD",
  "mcp_envelope_mutations_held":fault,"synthetic_physical_spoof_results":fake,
  "actual_photons_measured":False,"biological_neurons_measured":False,
  "external_signed_instrument_custody":False,"source_identity_verified_by_pinned_original_digest":True,
  "full_trace_sha256":sha(trace)}
 contents={"seat4-r7-trace.hbp":trace,"seat4-r7-results.json":emit(summary)}
 for name,body in contents.items():
  (out/name).write_bytes(body)
  (out/(name+".sha256")).write_bytes((sha(body)+"  "+name+"\n").encode("ascii"))
 print(json.dumps({"status":"INDEPENDENT_DIGITAL_REFEREE_PASS","neural":matches,
   "false_green":false,"strict":strict,"mutations":len(fault),
   "raw_frames":len(lines),"hbp_sha256":sha(trace),
   "physical_capture":"HOLD","neural_physical":"HOLD"},sort_keys=True))
if __name__=="__main__":
 if len(sys.argv)!=4:raise SystemExit("usage: referee.py PR93_ARCHIVED_ARTIFACT FROZEN_PR94_HEAD OUT_DIR")
 main(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
