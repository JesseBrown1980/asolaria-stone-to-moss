#!/usr/bin/env python3
"""Independent full 81,648-record third cross-examination; NO physics inferred.

Reads original source bank directly via independently authored leaf verifier,
not the Python producer class; checks EVERY row, source leaf hash, six
programmed mechanisms, 2x2x2 contrasts and full cross-language parity.
"""
import hashlib,json,re,sys
from pathlib import Path
from verify_photon_assay import original_source_bank,PORTS,BANK,INDEX,SOURCE

SCHEMA="ASOLARIA-SEAT3-PHOTON-PHONON-ELECTRONIC-FACTORIAL-TOY-V1"
MODELS=("NULL","OPTICAL_MAIN_ONLY","ACOUSTIC_MAIN_ONLY",
        "DIRECT_COUPLING_TOY","THERMAL_ELECTRONIC_MIMIC","FAST_AFTERGLOW")
DELAYS=(1,10,60)
ROW=re.compile(
 r"OAE\|model=(NULL|OPTICAL_MAIN_ONLY|ACOUSTIC_MAIN_ONLY|DIRECT_COUPLING_TOY|THERMAL_ELECTRONIC_MIMIC|FAST_AFTERGLOW)"
 r"\|delay=(01|10|60)\|site=(\d{2})\|band=(\d)\|port=(\d)"
 r"\|leaf=([a-f0-9]{64})\|O=([01])\|A=([01])\|E=([01])"
 r"\|electronic=(-?\d+)\|optical=(-?\d+)\|temp=(-?\d+)\Z")
def sha(b):return hashlib.sha256(b).hexdigest()
def gate(ok,reason):
    if not ok:raise ValueError(reason)
def expected(model,site,band,delay,O,A,E):
    # Independent rederivation of intentionally synthetic numeric laws, no
    # source producer import, and no physical photon/acoustic sensors.
    ctx=("ASOLARIA-OAE-NOISE-V1|"+model+"|site="+str(site)+
         "|band="+str(band)+"|delay="+str(delay)).encode("ascii")
    noise=hashlib.sha256(ctx).digest()[0]%7-3
    y=100+noise+4*E
    if model=="OPTICAL_MAIN_ONLY":y+=20*O
    elif model=="ACOUSTIC_MAIN_ONLY":y+=20*A
    elif model in ("DIRECT_COUPLING_TOY","THERMAL_ELECTRONIC_MIMIC","FAST_AFTERGLOW"):
        y+=10*O+6*A
        if model!="FAST_AFTERGLOW" or delay!=60:y+=30*O*A
    elif model!="NULL":raise AssertionError("BAD_MODEL")
    light_sensor=y-30*O*A if model=="THERMAL_ELECTRONIC_MIMIC" else y
    t=25+2*O+A+(5*O*A if model=="THERMAL_ELECTRONIC_MIMIC" else 0)
    return y,light_sensor,t

def verify(src,pydir,jsdir,outdir):
    references=original_source_bank(src)
    p,j=Path(pydir),Path(jsdir)
    names=("photon-phonon-electronic-toy.hbp","photon-phonon-electronic-toy.json")
    for name in names:
        a=(p/name).read_bytes()
        gate(a==(j/name).read_bytes(),"SOURCE_PY_NODE_PARITY_FAIL")
        for d in (p,j):
            want=(sha(a)+"  "+name+"\n").encode("ascii")
            gate((d/(name+".sha256")).read_bytes()==want,"TOY_SIDECAR_INVALID")
    raw=(p/names[0]).read_bytes()
    summary=(p/names[1]).read_bytes()
    report=json.loads(summary)
    gate(report["schema"]==SCHEMA and
         report["verdict"]=="DIGITAL_FACTORIAL_UNIT_TEST_PASS","BAD_MODEL_RECEIPT_SCHEMA")
    gate(report["source_81_sha256"]==SOURCE and
         report["bank_567_sha256"]==BANK and
         report["base_index_sha256"]==INDEX,"SOURCE_DIGESTS_FORGED")
    gate(report["models"]==list(MODELS) and
         report["delays_s_nominal"]==list(DELAYS),"MODEL_AXES_WRONG")
    gate(report["source_stable_site_identities"]==81 and
         report["source_symbolic_spectral_bands"]==7 and
         report["source_bank_stored_entries"]==567,"SOURCE_CARDINALITY_WRONG")
    gate(report["factorial_arms"]==8 and report["rows_per_model"]==13608 and
         report["total_simulated_rows"]==81648,"MISSING_FACTORIAL_CELLS")
    gate(report["model_trace_sha256"]==sha(raw) and
         report["model_trace_bytes"]==len(raw),"HBP_DRIFT")
    for key in ("real_optical_capture","real_acoustic_capture",
                "real_electronic_custody_attested","real_photon_phonon_coupling",
                "physical_optical_memory_retention","biological_neural_memory"):
        gate(report[key]=="NOT_RUN","UNSUPPORTED_PHYSICAL_COUPLING_PROMOTION:"+key)
    gate(report["physical_elapsed_time_measured"] is False,"FALSE_DURATION")
    gate(report["reconstructed_source_leafs_sha256_enforced"] is True,"NO_SOURCE_REPLAY")
    lines=raw.decode("ascii").splitlines()
    gate(raw.endswith(b"\n") and len(lines)==81649 and
         lines[0]=="PORTAL|schema="+SCHEMA+
         "|synthetic_models=6|physical_instrument=NOT_RUN","TOY_ROW_COUNT")

    i=1;result={}
    for model in MODELS:
        count=0;by_delay={}
        for delay in DELAYS:
            contrasts={f"e{e}_{name}":set() for e in (0,1)
                       for name in ("electronic","optical","temperature")}
            for site in range(81):
                for band in range(7):
                    leaf,_=references[(band,site)]
                    arms={}
                    for O in (0,1):
                        for A in (0,1):
                            for E in (0,1):
                                row=ROW.fullmatch(lines[i])
                                gate(row is not None,"TOY_RECORD_MALFORMED")
                                values=row.groups()
                                m,d,s,b,port,sha_leaf,o,a,e,y,light,temp=values
                                gate((m,int(d),int(s),int(b),int(port),sha_leaf,int(o),int(a),int(e))==
                                     (model,delay,site,band,PORTS[band],leaf,O,A,E),
                                     "BANK_LEAF_OR_CAUSAL_ARM_CHANGED")
                                exp=expected(model,site,band,delay,O,A,E)
                                gate((int(y),int(light),int(temp))==exp,"FACTORIAL_RESPONSE_FORGED")
                                arms[(O,A,E)]=exp
                                i+=1;count+=1
                    for E in (0,1):
                        for n,label in enumerate(("electronic","optical","temperature")):
                            delta=(arms[(1,1,E)][n]-arms[(1,0,E)][n]
                                   -arms[(0,1,E)][n]+arms[(0,0,E)][n])
                            contrasts[f"e{E}_{label}"].add(delta)
            per={}
            for key,v in contrasts.items():
                gate(len(v)==1,"FACTORIAL_CONTRAST_NONUNIFORM")
                value=next(iter(v))
                direct=30 if model in ("DIRECT_COUPLING_TOY","THERMAL_ELECTRONIC_MIMIC") or (
                      model=="FAST_AFTERGLOW" and delay!=60) else 0
                expectation=(direct if key.endswith("_electronic") else
                             0 if model=="THERMAL_ELECTRONIC_MIMIC" else direct) if (
                             not key.endswith("_temperature")) else (
                             5 if model=="THERMAL_ELECTRONIC_MIMIC" else 0)
                gate(value==expectation,"WRONG_CAUSAL_INTERACTION_EXPECTATION")
                per[key]=value
            by_delay[str(delay)]=per
        result[model]={"arm_rows":count,"contrast_by_delay":by_delay}
        gate(count==13608,"SOURCE_AXES_COUNT")
    gate(i==len(lines) and report["model_results"]==result,"MODEL_SUMMARIES_NOT_REPRODUCED")
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    for name in names:
        b=(p/name).read_bytes()
        (out/name).write_bytes(b)
        (out/(name+".sha256")).write_bytes((sha(b)+"  "+name+"\n").encode("ascii"))
    audit={
       "verdict":"INDEPENDENT_OAE_FACTORIAL_AUDIT_PASS",
       "models":len(MODELS),"factorial_rows":81648,
       "stable_source_sites":81,"source_band_site_refs":567,
       "raw_sha256":sha(raw),"receipt_sha256":sha(summary),
       "direct_toy_oa_contrast_60s":30,
       "afterglow_oa_contrast_60s":0,
       "thermal_mimic_raw_contrast_60s":30,
       "thermal_mimic_optical_contrast_60s":0,
       "new_external_physical_observations":0
    }
    body=(json.dumps(audit,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")
    name="independent-factorial-audit.json"
    (out/name).write_bytes(body)
    (out/(name+".sha256")).write_bytes((sha(body)+"  "+name+"\n").encode("ascii"))
    print(json.dumps(audit,sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=5:raise SystemExit("usage: python verify_optical_acoustic_factorial.py ORIGINAL_BANK PY_RESULTS JS_RESULTS AUDIT_OUT")
    verify(*sys.argv[1:])
