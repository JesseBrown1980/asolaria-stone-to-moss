#!/usr/bin/env python3
"""Seat1 preregistered, CLASSICAL SOFTWARE photon-phonon-photoelectron memory model.

The processes run on real CPU hardware. Photons, phonons, electronic captures and
neural gate messages here are *numerical model values*, NOT optical measurements.
"""
import bisect
import hashlib
import json
import math
import sys
from pathlib import Path

BANK_ROOT="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
INDEX_ROOT="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"
SOURCE_ROOT="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
BANDS=("red","orange","yellow","green","blue","indigo","violet")
WAVELENGTHS=(650,610,580,530,470,440,405)
SCHEMA="ASOLARIA-SEAT1-PHOTON-PHONON-ELECTRON-MEMORY-MODEL-V1"
# label, photons for b=1, numerator, denominator, dark per 1000, acoustic condition, phase, hold ticks
ARMS=(
 ("reference_bright",24,64,100,0,"OFF","NONE",0),
 ("baseline_t0",8,32,100,0,"OFF","NONE",0),
 ("resonant_phase0",8,44,100,0,"RESONANT","0",0),
 ("resonant_phase180",8,20,100,0,"RESONANT","180",0),
 ("off_resonance",8,32,100,0,"OFF_RESONANCE","0",0),
 ("thermal_sham",8,36,100,0,"THERMAL_SHAM","NONE",0),
 ("detector_dark_noise",8,32,100,1,"OFF","NONE",0),
 ("optical_dark",0,0,100,0,"OFF","NONE",0),
 ("acoustic_only",0,0,100,0,"RESONANT","0",0),
 ("held_t3",8,16,100,0,"OFF","NONE",3),
 ("held_t3_resonant",8,22,100,0,"RESONANT","0",3),
 ("held_t3_erased",0,0,100,0,"OFF","NONE",3),
)

def sha(data): return hashlib.sha256(data).hexdigest()
def canon(obj):
    return (json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
def check(ok,msg):
    if not ok:raise AssertionError(msg)

class RNG:
    def __init__(self,ordinal,lane):
        seed=hashlib.sha256(f"ASOLARIA-COUPLING-A|{BANK_ROOT}|{ordinal}|{lane}".encode()).digest()
        self.s=int.from_bytes(seed[:4],"little") or 0x6d2b79f5
    def draw(self):
        x=self.s
        x^=(x<<13)&0xffffffff
        x^=x>>17
        x^=(x<<5)&0xffffffff
        self.s=x&0xffffffff
        return self.s

def cdf(n,pnum,pden):
    if n==0:return [1<<32]
    total=pden**n
    acc=0
    out=[]
    for k in range(n+1):
        acc+=math.comb(n,k)*pnum**k*(pden-pnum)**(n-k)
        out.append(acc*(1<<32)//total)
    check(out[-1]==1<<32,"CDF_MASS")
    return out

def lif(data):
    membrane=0;spikes=0;sig=bytearray()
    for i,byte in enumerate(data):
        for shift in range(7,-1,-1):
            bit=(byte>>shift)&1
            membrane=max(0,membrane-1)+4*bit
            if membrane>=7:
                spikes+=1
                membrane-=7
            if (i*8+7-shift)%32==31:
                sig.append(spikes)
                spikes=0
    if len(data)*8%32:sig.append(spikes)
    return bytes(sig)

def load(original,bankfile,indexfile):
    source=Path(original).read_bytes()
    bank=Path(bankfile).read_bytes()
    index=Path(indexfile).read_bytes()
    check(sha(source)==SOURCE_ROOT,"ORIGINAL_QR_SHA")
    check(sha(bank)==BANK_ROOT and len(bank)==184815,"BANK_ROOT")
    check(sha(index)==INDEX_ROOT and len(index)==70043,"INDEX_ROOT")
    raw_source=json.loads(source)
    check(len(raw_source["records"])==81,"ORIGINAL_MEMORIES")
    result=[];seen=set()
    for ordinal,line in enumerate(index.decode("ascii").splitlines()):
        v=line.split("|");check(len(v)==6 and v[0]=="MEM","INDEX_ROW")
        f=dict(part.split("=",1) for part in v[1:])
        check(set(f)=={"band","id","offset","length","sha256"},"INDEX_FIELDS")
        band=f["band"];site=f["id"];start=int(f["offset"]);length=int(f["length"])
        check(band in BANDS and len(site)==8 and site.startswith("site-"),"SOURCE_LABEL")
        check((site,band) not in seen,"REPEATED_SOURCE")
        seen.add((site,band))
        check(start>=0 and length>0 and start+length<=len(bank),"INDEX_BOUNDS")
        data=bank[start:start+length]
        check(sha(data)==f["sha256"],"INDEX_ROW_HASH")
        obj=json.loads(data)
        check(obj["record"]==raw_source["records"][int(site[5:])]
              and obj["band"]==band and obj["id"]==site,"SOURCE_ANCESTRY")
        result.append((ordinal,site,band,data,sha(data),lif(data)))
    check(len(result)==567 and len(seen)==567,"MISSING_MEMORY")
    return result,bank

def make_frame(row,arm,draw_signal,draw_dark,table):
    ordinal,site,band,data,trusted,trained=row
    name,n,pnum,pden,dark,acoustic,phase,hold=arm
    recovered=bytearray()
    emitted=0;electrons=0;dark_e=0;bit_errors=0
    ones_miss=0;zeros_false=0
    position=0
    for byte in data:
        observed=0
        for shift in range(7,-1,-1):
            bit=(byte>>shift)&1
            u=draw_signal[position];v=draw_dark[position]
            position+=1
            photo=bisect.bisect_right(table,u) if bit and n else 0
            # For n=0, the number of signal photons is always 0.
            if bit:emitted+=n
            electrons+=photo
            de=int(dark>0 and v<((1<<32)*dark//1000))
            dark_e+=de
            result=int(photo+de>0)
            observed=(observed<<1)|result
            bit_errors+=int(bit!=result)
            ones_miss+=int(bit==1 and result==0)
            zeros_false+=int(bit==0 and result==1)
        recovered.append(observed)
    check(position==len(data)*8 and electrons<=emitted,"PHOTON_ELECTRON_BUDGET")
    fp=lif(recovered)
    neural_match=fp==trained
    byte_match=sha(recovered)==trusted
    authorized=neural_match and byte_match
    nonce=sha(f"ASOLARIA-COUPLING-NONCE|{BANK_ROOT}|{name}|{ordinal}".encode())[:24]
    wave=WAVELENGTHS[BANDS.index(band)]
    arguments={"bank_sha256":BANK_ROOT,"source_sha256":SOURCE_ROOT,"index_sha256":INDEX_ROOT,
        "site":site,"band":band,"sector":ordinal%27,"wavelength_nm_assumed":wave,
        "phonon_drive":acoustic,"phase_deg":phase,"hold_ticks_assumed":hold,
        "signal_photons_modeled":emitted,"photoelectrons_modeled":electrons,
        "dark_electrons_modeled":dark_e,"readback_sha256":sha(recovered),
        "reference_sha256":trusted,"nonce":nonce}
    gate={"trained_fingerprint_sha256":sha(trained),"observed_fingerprint_sha256":sha(fp),
          "fingerprint_match":neural_match,"source_hash_match":byte_match,"authorized":authorized}
    return {"schema":SCHEMA,"arm":name,"ordinal":ordinal,"site":site,"band":band,
        "sector":ordinal%27,"wavelength_nm_assumed":wave,
        "phonon_drive":acoustic,"phase_deg":phase,"hold_ticks_assumed":hold,
        "photons_per_source_one":n,"detection_probability_numerator":pnum,
        "detection_probability_denominator":pden,"dark_per_1000":dark,
        "emitted_photons_modeled":emitted,"photoelectrons_modeled":electrons,
        "dark_electrons_modeled":dark_e,
        "reference_sha256":trusted,"readback_sha256":sha(recovered),
        "readback_hex":recovered.hex(),"bit_errors":bit_errors,
        "missed_one_bits":ones_miss,"false_zero_bits":zeros_false,
        "neural_only_match":neural_match,"source_byte_exact":byte_match,
        "strict_authorized":authorized,"nonce":nonce,
        "mcp_capture":{"jsonrpc":"2.0","id":f"electron:{name}:{ordinal}",
            "method":"tools/call","params":{"name":"electron.capture","arguments":arguments}},
        "mcp_neural_gate":{"jsonrpc":"2.0","id":f"neuron:{name}:{ordinal}",
            "method":"tools/call","params":{"name":"neuron.gate","arguments":gate}}}

def validate(frame,row,arm,signal,dark,table):
    # Always rederive against original pinned data: no local self-signed digest is trusted.
    check(canon(frame)==canon(make_frame(row,arm,signal,dark,table)),"INDEPENDENT_SOURCE_REPLAY_FAIL_CLOSED")
    check(frame["mcp_capture"]["params"]["name"]=="electron.capture"
        and frame["mcp_neural_gate"]["params"]["name"]=="neuron.gate","INVALID_MCP_TOOL")
    check(frame["strict_authorized"]==
        (frame["source_byte_exact"] and frame["neural_only_match"]),"FALSE_AUTHORIZATION")

def negatives(row,arm,draw_signal,draw_dark,table,original):
    import copy
    mutants=(
        ("changed_row_payload",lambda x:x.update(readback_hex="00"+x["readback_hex"][2:])),
        ("coherent_local_readback_forgery",lambda x:(x.update(readback_sha256="f"*64),
            x["mcp_capture"]["params"]["arguments"].update(readback_sha256="f"*64))),
        ("swapped_band",lambda x:x.update(band="violet")),
        ("swapped_wavelength",lambda x:x.update(wavelength_nm_assumed=405)),
        ("swapped_site",lambda x:x.update(site="site-080")),
        ("bad_sector",lambda x:x.update(sector=(x["sector"]+1)%27)),
        ("phase_spoof",lambda x:x.update(phase_deg="180")),
        ("phonon_spoof",lambda x:x.update(phonon_drive="RESONANT")),
        ("impossible_electrons",lambda x:x.update(photoelectrons_modeled=x["emitted_photons_modeled"]+1)),
        ("replayed_nonce",lambda x:x.update(nonce="stale")),
        ("forged_bank_root",lambda x:x["mcp_capture"]["params"]["arguments"].update(bank_sha256="0"*64)),
        ("forged_capture_tool",lambda x:x["mcp_capture"]["params"].update(name="electron.bypass")),
        ("forged_neural_gate",lambda x:x["mcp_neural_gate"]["params"]["arguments"].update(authorized=False)),
        ("missing_frame",lambda x:x.clear()),
    )
    rejects=[]
    for name,mutation in mutants:
        x=copy.deepcopy(original)
        mutation(x)
        try:validate(x,row,arm,draw_signal,draw_dark,table)
        except (AssertionError,KeyError,TypeError) as exc:
            rejects.append({"attack":name,"held":True,"why":str(exc)})
        else:raise AssertionError("ATTACK_ACCEPTED:"+name)
    check(len(rejects)==14,"MUTATION_COVERAGE")
    return rejects

def run(original,bankfile,indexfile,outpath):
    rows,bank=load(original,bankfile,indexfile)
    ones=sum(byte.bit_count() for byte in bank)
    zeros=len(bank)*8-ones
    check((ones,zeros)==(662443,816077),"BANK_BIT_DISTRIBUTION")
    tables={arm[0]:cdf(arm[1],arm[2],arm[3]) for arm in ARMS}
    summaries=[dict(arm=a[0],photons_per_one=a[1],p_num=a[2],p_den=a[3],
         dark_per_1000=a[4],phonon_drive=a[5],phase_deg=a[6],hold_ticks=a[7],
         rows=0,source_bytes=0,bit_errors=0,missed_one_bits=0,false_zero_bits=0,
         exact_rows=0,neural_only_matches=0,neural_false_greens=0,authorized_rows=0,
         emitted_photons_modeled=0,photoelectrons_modeled=0,dark_electrons_modeled=0) for a in ARMS]
    chunks=[[] for _ in ARMS]
    recorded_negatives=None
    erasure_rows=0
    for row in rows:
        ordinal,site,band,data,trusted,trained=row
        signal=RNG(ordinal,"signal");dark=RNG(ordinal,"dark")
        draw_signal=[signal.draw() for _ in range(len(data)*8)]
        draw_dark=[dark.draw() for _ in range(len(data)*8)]
        for i,arm in enumerate(ARMS):
            frame=make_frame(row,arm,draw_signal,draw_dark,tables[arm[0]])
            validate(frame,row,arm,draw_signal,draw_dark,tables[arm[0]])
            if recorded_negatives is None:
                recorded_negatives=negatives(row,arm,draw_signal,draw_dark,tables[arm[0]],frame)
            chunks[i].append(canon(frame))
            s=summaries[i]
            s["rows"]+=1;s["source_bytes"]+=len(data)
            s["bit_errors"]+=frame["bit_errors"]
            s["missed_one_bits"]+=frame["missed_one_bits"]
            s["false_zero_bits"]+=frame["false_zero_bits"]
            s["exact_rows"]+=int(frame["source_byte_exact"])
            s["neural_only_matches"]+=int(frame["neural_only_match"])
            s["neural_false_greens"]+=int(frame["neural_only_match"] and not frame["source_byte_exact"])
            s["authorized_rows"]+=int(frame["strict_authorized"])
            for k in ("emitted_photons_modeled","photoelectrons_modeled","dark_electrons_modeled"):
                s[k]+=frame[k]
        if band=="violet":erasure_rows+=1
    check(erasure_rows==81 and 567-erasure_rows==486,"ERASURE_COUNT")
    for s in summaries:check(s["rows"]==567 and s["source_bytes"]==184815,"MISSING_SOURCE_BYTES")
    by_name={s["arm"]:s for s in summaries}
    get=lambda name:by_name[name]["bit_errors"]
    check(get("reference_bright")<get("baseline_t0")
        and get("resonant_phase0")<get("baseline_t0")
        and get("resonant_phase180")>get("baseline_t0")
        and get("held_t3")>get("baseline_t0")
        and get("held_t3_resonant")<get("held_t3")
        and get("thermal_sham")<get("baseline_t0")
        and get("detector_dark_noise")>get("baseline_t0"),"COUPLING_ORDER_FALSIFIED")
    check(b"".join(chunks[1])!=b"".join(chunks[4]),"SCENARIO_METADATA_MUST_CHANGE")
    # Byte-identical payload recovery is required in the off-resonant control,
    # even though metadata (acoustic treatment, arm) changes.
    for i in range(567):
        a=json.loads(chunks[1][i]);b=json.loads(chunks[4][i])
        check(a["readback_hex"]==b["readback_hex"],"OFF_RESONANCE_CONFOUNDER")
        zero_a=json.loads(chunks[7][i]);zero_b=json.loads(chunks[8][i]);zero_c=json.loads(chunks[11][i])
        check(zero_a["readback_hex"]==zero_b["readback_hex"]==zero_c["readback_hex"],"NO_OPTICAL_INPUT_SHOULD_NOT_TRANSDUCE")
        check(zero_a["photoelectrons_modeled"]==zero_b["photoelectrons_modeled"]==
          zero_c["photoelectrons_modeled"]==0,"PHOTONLESS_ELECTRON_FALSE_POSITIVE")
    # Real destructive test: actually omit all violet-source frames; a complete
    # 567-row bank check must HALT, not treat vanished aliases as retained data.
    retained=[frame for i,frame in enumerate(chunks[1]) if rows[i][2]!="violet"]
    check(len(retained)==486 and len(retained)!=567,"VIOLET_ERASURE_NOT_HELD")
    flat=b"".join(b"".join(group) for group in chunks)
    check(len(flat.splitlines())==567*len(ARMS),"MISSING_EXPERIMENT_FRAMES")
    analytic=[]
    for s in summaries:
        p=s["p_num"]/s["p_den"];d=s["dark_per_1000"]/1000
        q1=(1-p)**s["photons_per_one"]*(1-d)
        q0=d
        expected=ones*q1+zeros*q0
        variance=ones*q1*(1-q1)+zeros*q0*(1-q0)
        limit=6*math.sqrt(max(1.0,variance))+2
        check(abs(s["bit_errors"]-expected)<limit,"MODEL_ANALYTIC_EXPECTATION_FAIL:"+s["arm"])
        analytic.append({"arm":s["arm"],"expected_errors":round(expected,6),
            "observed_errors":s["bit_errors"],"six_sigma_limit":round(limit,6)})
    manifest={"schema":SCHEMA,"source_sha256":SOURCE_ROOT,"bank_sha256":BANK_ROOT,
      "index_sha256":INDEX_ROOT,"original_source_memories":81,"bank_rows":567,"bank_bytes":184815,
      "source_ones":ones,"source_zeros":zeros,"scenario_count":len(ARMS),"frames":567*len(ARMS),
      "wavelengths_nm_assumed":dict(zip(BANDS,WAVELENGTHS)),
      "computational_execution_on_physical_hardware":True,
      "actual_photon_phonon_coupling_measured":False,
      "optical_storage_medium_measured":False,"real_photoelectron_current_measured":False,
      "biological_neuron_measured":False,"real_mcp_server_operational":False,
      "model_type":"DECLARED_CLASSICAL_BINOMIAL_PROBABILITY_WITH_SYNTHETIC_PHONON_DRIVE",
      "negative_controls":recorded_negatives,"erased_violet_rows":erasure_rows,
      "missing_logical_27_sector_aliases":erasure_rows*27,
      "scenario_results":summaries,"analytic_model_checks":analytic,
      "hbp_sha256":sha(flat),"hbp_bytes":len(flat)}
    directory=Path(outpath);directory.mkdir(parents=True,exist_ok=True)
    for name,raw in {"coupling.hbp":flat,"results.json":canon(manifest)}.items():
        (directory/name).write_bytes(raw)
        (directory/(name+".sha256")).write_bytes(f"{sha(raw)}  {name}\n".encode("ascii"))
    print(json.dumps({"status":"PASS","hbp_sha256":sha(flat),"hbp_bytes":len(flat),
      "frames":567*len(ARMS),"attack_controls_held":len(recorded_negatives),
      "scenario_error_counts":{s["arm"]:s["bit_errors"] for s in summaries},
      "measured_photons":False},sort_keys=True))
    return manifest

if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("usage: coupling.py original81.json retained567.jsonl base.hbi result_dir")
    run(*sys.argv[1:])
