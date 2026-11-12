#!/usr/bin/env python3
"""Asolaria Seat3 frozen 2x2x2 O/A/E numerical factorial, NOT physical optics.

Original bank bytes from published PR80 artifacts. Programmed direct OA,
thermal/electronic mimics, and fast afterglow alternatives. These are unit
test controls for how a future physically blinded photon-phonon-electronic
experiment should discriminate mechanisms, not evidence coupling occurred.
"""
import hashlib,json,sys
from pathlib import Path
from photon_assay import SourceBank,SRC,BANK,INDEX,PORTS

SCHEMA="ASOLARIA-SEAT3-PHOTON-PHONON-ELECTRONIC-FACTORIAL-TOY-V1"
MODELS=("NULL","OPTICAL_MAIN_ONLY","ACOUSTIC_MAIN_ONLY",
        "DIRECT_COUPLING_TOY","THERMAL_ELECTRONIC_MIMIC","FAST_AFTERGLOW")
DELAYS=(1,10,60)
def sha(b):return hashlib.sha256(b).hexdigest()

def outcomes(model,site,band,delay,O,A,E):
    salt=(f"ASOLARIA-OAE-NOISE-V1|{model}|site={site}|band={band}|delay={delay}").encode("ascii")
    noise=hashlib.sha256(salt).digest()[0]%7-3
    mean=100+noise+4*E
    temp=25+2*O+A
    if model=="NULL":base=mean
    elif model=="OPTICAL_MAIN_ONLY":base=mean+20*O
    elif model=="ACOUSTIC_MAIN_ONLY":base=mean+20*A
    elif model in ("DIRECT_COUPLING_TOY","THERMAL_ELECTRONIC_MIMIC","FAST_AFTERGLOW"):
        active=30 if model!="FAST_AFTERGLOW" or delay!=60 else 0
        base=mean+10*O+6*A+active*O*A
        if model=="THERMAL_ELECTRONIC_MIMIC":temp+=5*O*A
    else:raise ValueError("UNKNOWN_MODEL")
    separate=base-30*O*A if model=="THERMAL_ELECTRONIC_MIMIC" else base
    return base,separate,temp

def main(src,outdir):
    bank=SourceBank(src)
    folder=Path(outdir);folder.mkdir(parents=True,exist_ok=True)
    result={}
    rows=[]
    for model in MODELS:
        count=0
        per_delay={}
        for delay in DELAYS:
            comparisons={"e0_electronic":set(),"e1_electronic":set(),
                         "e0_optical":set(),"e1_optical":set(),
                         "e0_temperature":set(),"e1_temperature":set()}
            for site in range(81):
                for band in range(7):
                    _,leaf=bank.get(band,site)
                    measurements={}
                    for O in (0,1):
                        for A in (0,1):
                            for E in (0,1):
                                y,independent,t=outcomes(model,site,band,delay,O,A,E)
                                measurements[(O,A,E)]=(y,independent,t)
                                rows.append(f"OAE|model={model}|delay={delay:02d}|site={site:02d}"
                                            f"|band={band}|port={PORTS[band]}|leaf={leaf}"
                                            f"|O={O}|A={A}|E={E}"
                                            f"|electronic={y}|optical={independent}|temp={t}")
                                count+=1
                    for E in (0,1):
                        vals={key:measurements[(key[0],key[1],E)] for key in ((0,0),(0,1),(1,0),(1,1))}
                        for i,label in enumerate(("electronic","optical","temperature")):
                            d=vals[(1,1)][i]-vals[(1,0)][i]-vals[(0,1)][i]+vals[(0,0)][i]
                            comparisons[f"e{E}_{label}"].add(d)
            expected=30 if model in ("DIRECT_COUPLING_TOY","THERMAL_ELECTRONIC_MIMIC") or (
                model=="FAST_AFTERGLOW" and delay!=60) else 0
            for e in (0,1):
                assert comparisons[f"e{e}_electronic"]=={expected}
                opt=0 if model=="THERMAL_ELECTRONIC_MIMIC" else expected
                assert comparisons[f"e{e}_optical"]=={opt}
                temp=5 if model=="THERMAL_ELECTRONIC_MIMIC" else 0
                assert comparisons[f"e{e}_temperature"]=={temp}
            per_delay[str(delay)]={k:next(iter(v)) for k,v in comparisons.items()}
        assert count==81*7*3*8
        result[model]={"arm_rows":count,"contrast_by_delay":per_delay}
    assert len(rows)==6*81*7*3*8
    body=("PORTAL|schema="+SCHEMA+"|synthetic_models=6|physical_instrument=NOT_RUN\n"+
          "\n".join(rows)+"\n").encode("ascii")
    report={
       "schema":SCHEMA,
       "verdict":"DIGITAL_FACTORIAL_UNIT_TEST_PASS",
       "models":list(MODELS),
       "delays_s_nominal":list(DELAYS),
       "physical_elapsed_time_measured":False,
       "source_81_sha256":SRC,"bank_567_sha256":BANK,"base_index_sha256":INDEX,
       "source_stable_site_identities":81,
       "source_symbolic_spectral_bands":7,
       "source_bank_stored_entries":567,
       "factorial_arms":8,
       "rows_per_model":13608,
       "total_simulated_rows":len(rows),
       "model_results":result,
       "reconstructed_source_leafs_sha256_enforced":True,
       "real_optical_capture":"NOT_RUN",
       "real_acoustic_capture":"NOT_RUN",
       "real_electronic_custody_attested":"NOT_RUN",
       "real_photon_phonon_coupling":"NOT_RUN",
       "physical_optical_memory_retention":"NOT_RUN",
       "biological_neural_memory":"NOT_RUN",
       "model_trace_bytes":len(body),"model_trace_sha256":sha(body),
    }
    raw=(json.dumps(report,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
    for name,data in (("photon-phonon-electronic-toy.hbp",body),
                      ("photon-phonon-electronic-toy.json",raw)):
        (folder/name).write_bytes(data)
        (folder/(name+".sha256")).write_bytes((sha(data)+"  "+name+"\n").encode("ascii"))
    print(json.dumps({"verdict":report["verdict"],"total":len(rows),
       "trace_sha256":sha(body),"json_sha256":sha(raw)},sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: python optical_acoustic_factorial.py ORIGINAL_PR80_ARTIFACT OUT")
    main(*sys.argv[1:])
