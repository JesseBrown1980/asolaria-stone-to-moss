#!/usr/bin/env python3
"""Third-party-style independent source bitwise and analytic audit of modeled coupling.

Uses original archived bank and independent full-byte comparisons, not blindly
trusting producer bit_errors, neural verdicts, nonce or self-supplied SHA claims.
"""
import hashlib,json,math,sys
from collections import defaultdict
from pathlib import Path

BANK_SHA="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
INDEX_SHA="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"
SOURCE_SHA="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
ARMS=("reference_bright","baseline_t0","resonant_phase0","resonant_phase180","off_resonance",
      "thermal_sham","detector_dark_noise","optical_dark","acoustic_only",
      "held_t3","held_t3_resonant","held_t3_erased")
BANDS=("red","orange","yellow","green","blue","indigo","violet")
WAVELENGTHS=(650,610,580,530,470,440,405)
FILES=("coupling.hbp","results.json","coupling.hbp.sha256","results.json.sha256")

def sha(b):return hashlib.sha256(b).hexdigest()
def ensure(cond,message):
    if not cond:raise AssertionError(message)
def lif(data):
    v=0,0
    membrane,spikes=v
    windows=[]
    for pos in range(len(data)*8):
        bit=(data[pos//8]>>(7-pos%8))&1
        membrane=(membrane-1 if membrane else 0)+4*bit
        if membrane>=7:
            membrane-=7;spikes+=1
        if pos%32==31:windows.append(spikes);spikes=0
    if len(data)*8%32:windows.append(spikes)
    return bytes(windows)
def trusted(source,bank_path,index_path):
    src=Path(source).read_bytes();bank=Path(bank_path).read_bytes();index=Path(index_path).read_bytes()
    ensure(sha(src)==SOURCE_SHA,"ORIGINAL_QR_SOURCE")
    ensure(sha(bank)==BANK_SHA and len(bank)==184815,"ORIGINAL_BANK")
    ensure(sha(index)==INDEX_SHA and len(index)==70043,"BASE_INDEX")
    parents=json.loads(src);ensure(len(parents["records"])==81,"MEMORY_COUNT")
    rows=[]
    for line in index.decode("ascii").splitlines():
        parts=line.split("|");ensure(len(parts)==6 and parts[0]=="MEM","INDEX_FORMAT")
        a=dict(part.split("=",1) for part in parts[1:])
        off=int(a["offset"]);length=int(a["length"])
        ensure(off>=0 and length>0 and off+length<=len(bank),"INDEX_BOUNDS")
        chunk=bank[off:off+length]
        ensure(sha(chunk)==a["sha256"],"INDEX_SOURCE_SHA")
        obj=json.loads(chunk)
        ensure(obj["record"]==parents["records"][int(a["id"][5:])],"WRONG_SOURCE_ID")
        ensure(obj["band"]==a["band"] and obj["id"]==a["id"],"BANK_ID")
        rows.append({"data":chunk,"sha":sha(chunk),"site":a["id"],
                     "band":a["band"],"fingerprint":lif(chunk)})
    ensure(len(rows)==567,"ORIGINAL_ROW_COUNT")
    ones=sum(b.bit_count() for b in bank)
    ensure((ones,len(bank)*8-ones)==(662443,816077),"SOURCE_BIT_HISTOGRAM")
    return rows,ones,len(bank)*8-ones

def evaluate(folder,rows,ones,zeros):
    folder=Path(folder);raw={f:(folder/f).read_bytes() for f in FILES}
    for f in FILES[:2]:
        ensure(raw[f+".sha256"]==(sha(raw[f])+"  "+f+"\n").encode("ascii"),"SIDE_CAR_NONCANONICAL")
    summary=json.loads(raw["results.json"])
    blob=raw["coupling.hbp"]
    ensure(sha(blob)==summary["hbp_sha256"] and len(blob)==summary["hbp_bytes"],"HBP_SHA_OR_LENGTH")
    ensure(summary["bank_sha256"]==BANK_SHA and summary["source_sha256"]==SOURCE_SHA
       and summary["index_sha256"]==INDEX_SHA,"SOURCE_ORIGIN_ROOT")
    ensure(summary["frames"]==6804 and summary["scenario_count"]==12,"FRAME_COUNT")
    for flag in ("actual_photon_phonon_coupling_measured","optical_storage_medium_measured",
                 "real_photoelectron_current_measured","biological_neuron_measured",
                 "real_mcp_server_operational"):
        ensure(summary[flag] is False,"UNSUPPORTED_EXPERIMENTAL_CLAIM:"+flag)
    ensure(summary["computational_execution_on_physical_hardware"] is True,"PHYSICAL_CPU_MISCLASSIFIED")
    ensure(len(summary["negative_controls"])==14,"MISSING_ATTACKS")
    ensure(summary["erased_violet_rows"]==81 and
           summary["missing_logical_27_sector_aliases"]==2187,"ERASURE_NOT_HELD")
    records=blob.splitlines();ensure(len(records)==6804,"NUMBER_OF_HBP_FRAMES")
    stats=defaultdict(lambda:{"errors":0,"miss":0,"false":0,"exact":0,"neural":0,"neural_false":0,"auth":0,
        "emitted":0,"electrons":0,"dark":0,"rows":0})
    immediate={}
    for i,line in enumerate(records):
        f=json.loads(line)
        arm=ARMS[i//567];ordinal=i%567
        row=rows[ordinal];data=row["data"]
        ensure(f["arm"]==arm and f["ordinal"]==ordinal,"WRONG_FRAME_ORDER")
        ensure(f["site"]==row["site"] and f["band"]==row["band"] and f["sector"]==ordinal%27,"ADDRESS_FORGED")
        ensure(f["wavelength_nm_assumed"]==WAVELENGTHS[BANDS.index(row["band"])],"SPECTRUM_FORGED")
        ensure(f["reference_sha256"]==row["sha"],"ROOT_NOT_INDEPENDENT")
        nonce=sha(f"ASOLARIA-COUPLING-NONCE|{BANK_SHA}|{arm}|{ordinal}".encode())[:24]
        ensure(f["nonce"]==nonce,"REPLAY_NONCE")
        decoded=bytes.fromhex(f["readback_hex"])
        ensure(len(decoded)==len(data) and sha(decoded)==f["readback_sha256"],"READBACK_CORRUPTED")
        miss=sum(((x&~y)&0xff).bit_count() for x,y in zip(data,decoded))
        false=sum(((~x&y)&0xff).bit_count() for x,y in zip(data,decoded))
        errors=miss+false
        ensure(errors==sum((x^y).bit_count() for x,y in zip(data,decoded)),"ERROR_MATH")
        ensure(errors==f["bit_errors"] and miss==f["missed_one_bits"] and false==f["false_zero_bits"],"REPORTED_ERRORS_FORGED")
        neural=lif(decoded)==row["fingerprint"]
        source_match=sha(decoded)==row["sha"]
        ensure(neural==f["neural_only_match"] and source_match==f["source_byte_exact"],"NEURAL_FALSE_RECOGNITION")
        ensure(f["strict_authorized"]==(neural and source_match),"NEURAL_GATE_FALSE_PASS")
        a=f["mcp_capture"];b=f["mcp_neural_gate"]
        ensure(a["jsonrpc"]=="2.0" and a["method"]=="tools/call" and
               a["params"]["name"]=="electron.capture","ELECTRON_PROTOCOL")
        ensure(b["jsonrpc"]=="2.0" and b["method"]=="tools/call" and
               b["params"]["name"]=="neuron.gate","NEURON_PROTOCOL")
        inputs=a["params"]["arguments"]
        ensure(inputs["bank_sha256"]==BANK_SHA and inputs["source_sha256"]==SOURCE_SHA
               and inputs["index_sha256"]==INDEX_SHA and inputs["site"]==row["site"]
               and inputs["reference_sha256"]==row["sha"] and inputs["nonce"]==nonce,
               "PROTOCOL_UNTRUSTED_SOURCE")
        ensure(inputs["photoelectrons_modeled"]==f["photoelectrons_modeled"] and
               inputs["signal_photons_modeled"]==f["emitted_photons_modeled"] and
               inputs["readback_sha256"]==f["readback_sha256"],"PHYSICAL_COUNT_FORGERY")
        gate=b["params"]["arguments"]
        ensure(gate["trained_fingerprint_sha256"]==sha(row["fingerprint"])
               and gate["observed_fingerprint_sha256"]==sha(lif(decoded))
               and gate["authorized"]==(neural and source_match),"GATE_AUTHORITY")
        count_ones=sum(x.bit_count() for x in data)
        ensure(f["emitted_photons_modeled"]==count_ones*f["photons_per_source_one"],"EMISSION_BUDGET")
        ensure(0<=f["photoelectrons_modeled"]<=f["emitted_photons_modeled"],"ELECTRON_BUDGET")
        ensure(0<=f["dark_electrons_modeled"]<=len(data)*8,"DARK_ELECTRON_BUDGET")
        st=stats[arm]
        st["errors"]+=errors;st["miss"]+=miss;st["false"]+=false
        st["exact"]+=int(source_match);st["neural"]+=int(neural)
        st["neural_false"]+=int(neural and not source_match)
        st["auth"]+=int(neural and source_match)
        st["emitted"]+=f["emitted_photons_modeled"]
        st["electrons"]+=f["photoelectrons_modeled"]
        st["dark"]+=f["dark_electrons_modeled"];st["rows"]+=1
        if arm in ("baseline_t0","off_resonance","optical_dark","acoustic_only","held_t3_erased"):
            immediate[(arm,ordinal)]=decoded
    allresults=summary["scenario_results"];ensure(len(allresults)==12,"SCENARIO_SUMMARIES")
    for name,declared in zip(ARMS,allresults):
        ensure(declared["arm"]==name and declared["rows"]==567
             and declared["source_bytes"]==184815,"SOURCE_INCOMPLETE")
        real=stats[name]
        keys={"bit_errors":"errors","missed_one_bits":"miss","false_zero_bits":"false",
              "exact_rows":"exact","neural_only_matches":"neural",
              "neural_false_greens":"neural_false","authorized_rows":"auth",
              "emitted_photons_modeled":"emitted","photoelectrons_modeled":"electrons",
              "dark_electrons_modeled":"dark"}
        for target,src in keys.items():
            ensure(declared[target]==real[src],name+"_BAD_TOTAL_"+target)
        p=declared["p_num"]/declared["p_den"];n=declared["photons_per_one"]
        dark=declared["dark_per_1000"]/1000
        q1=(1-p)**n*(1-dark);q0=dark
        expectation=ones*q1+zeros*q0
        variance=ones*q1*(1-q1)+zeros*q0*(1-q0)
        ensure(abs(real["errors"]-expectation)<6*math.sqrt(max(1.0,variance))+2,
            "ANALYTIC_FALSIFICATION:"+name)
    for ordinal in range(567):
        ensure(immediate["baseline_t0",ordinal]==immediate["off_resonance",ordinal],
               "SHAM_ACOUSTIC_COUPLING")
        ensure(immediate["optical_dark",ordinal]==immediate["acoustic_only",ordinal]
               ==immediate["held_t3_erased",ordinal],"NO_OPTICAL_INPUT")
    errors={k:stats[k]["errors"] for k in ARMS}
    ensure(errors["resonant_phase0"]<errors["baseline_t0"]<
           errors["resonant_phase180"],"RESONANCE_PREDICTION_FAIL")
    ensure(errors["held_t3_resonant"]<errors["held_t3"] and
           errors["held_t3"]>errors["baseline_t0"],"RETENTION_PREDICTION_FAIL")
    ensure(errors["thermal_sham"]<errors["baseline_t0"],"THERMAL_MIMIC_NOT_FOUND")
    return raw,errors

def main():
    if len(sys.argv) not in (6,8):
        raise SystemExit("usage: verify_coupling.py original81.json rainbow7-bank.jsonl base-index.hbi py-output node-output [windows-py windows-node]")
    rows,ones,zeros=trusted(*sys.argv[1:4])
    verified=[evaluate(p,rows,ones,zeros) for p in sys.argv[4:]]
    first=verified[0][0]
    for other,_ in verified[1:]:
        for filename in FILES:ensure(first[filename]==other[filename],"CROSS_LANGUAGE_OR_OS_DRIFT:"+filename)
    print(json.dumps({"status":"PASS","source_ones":ones,"source_zeros":zeros,
       "frames":6804,"checked_programs":len(verified),
       "hbp_sha256":sha(first["coupling.hbp"]),"results_sha256":sha(first["results.json"]),
       "error_counts":verified[0][1],"measured_photons":False},sort_keys=True))
if __name__=="__main__":main()
