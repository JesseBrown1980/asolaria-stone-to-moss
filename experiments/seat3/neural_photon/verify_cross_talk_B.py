#!/usr/bin/env python3
"""Read-only independent entire-source validation-B cross-talk audit."""
import hashlib,json,re,sys
from pathlib import Path
from verify_photon_assay import original_source_bank, BIT_DOMAIN, PORTS, BANK, INDEX, SOURCE
SCHEMA="ASOLARIA-SEAT3-SPECTRAL-CROSSTALK-SECOND-NONCE-V1"
NONCE="ASOLARIA-SEAT3-PHOTON-UNSEEN-COUNTS-VALIDATION-B-20261015"
THRESH={"1":28,"3":78,"7":182}
RX=re.compile(r"CROSSTALK\|s=(\d{2})\|site=(\d{2})\|band=(\d)"
              r"\|bit=([01])\|port=(\d)"
              r"\|c1=(\d+)\|s1=(-?\d+)\|d1=(\d+)\|ds1=(-?\d+)"
              r"\|c3=(\d+)\|s3=(-?\d+)\|d3=(\d+)\|ds3=(-?\d+)"
              r"\|c7=(\d+)\|s7=(-?\d+)\|d7=(\d+)\|ds7=(-?\d+)\Z")
def sha(raw):return hashlib.sha256(raw).hexdigest()
def gate(ok,msg):
    if not ok:raise ValueError(msg)
def verify(src,py_path,js_path,dest_path):
    refs=original_source_bank(src)
    py,js=Path(py_path),Path(js_path)
    names=("photon-cross-talk-B.hbp","photon-cross-talk-B.json")
    for name in names:
        left=(py/name).read_bytes()
        gate(left==(js/name).read_bytes(),"ENGINES_DIVERGED")
        side=(sha(left)+"  "+name+"\n").encode("ascii")
        for folder in (py,js):
            gate((folder/(name+".sha256")).read_bytes()==side,"SIDECAR_DRIFT")
    hbp=(py/names[0]).read_bytes()
    raw=(py/names[1]).read_bytes()
    data=json.loads(raw)
    gate(data["schema"]==SCHEMA and data["verdict"]=="PASS","BAD_SCHEMA")
    gate(data["fixture_nonce"]==NONCE and data["frozen_thresholds"]==THRESH,"NONCE_OR_THRESH_CHANGED")
    gate(data["original_source_sha256"]==SOURCE and data["original_bank_sha256"]==BANK and
         data["original_base_index_sha256"]==INDEX,"BANK_SOURCE_REPLACED")
    gate(data["source_port_map"]==list(PORTS) and data["source_symbols"]==15309 and
         data["frames"]==2187 and data["stable_source_identities"]==81,"CHANNEL_ID_LOSS")
    gate(data["correction_law"]=="score=7*c_own-c_prev-c_next(no_wrap)","CROSSTALK_LAW_CHANGED")
    gate(data["raw_thresholds"]=={"1":5,"3":15,"7":35},"RAW_THRESHOLD_CHANGED")
    gate(data["full_trace_sha256"]==sha(hbp) and data["full_trace_bytes"]==len(hbp),"TRACE_SHA")
    gate(data["source_emission_events"]==data["one_detector_source_events"]+
         data["lost_source_events"] and data["conserved_one_receiver_per_event"] is True,
         "MULTIPLIED_PHOTON_EVENT")
    gate(data["violet_band_erasure_status"]=="HELD_2187_MISSING" and
         data["six_band_available_symbols"]==13122,"VIOLET_ERASURE_MISREPORT")
    gate(data["real_optical_capture_status"]=="NOT_RUN" and
         data["physical_photonic_retention_status"]=="NOT_RUN" and
         data["source_ownership_authenticated"] is False,"FAKE_PHYSICAL_CLAIM")
    gate(data["thresholds_frozen_before_validation_data"] is True and
         data["threshold_selection_was_exploratory_original_fixture"] is True,"INVALID_HOLDOUT_DISCLOSURE")
    lines=hbp.decode("ascii").splitlines()
    gate(hbp.endswith(b"\n") and len(lines)==15310 and
         lines[0]=="PORTAL|schema="+SCHEMA+"|validation_B=1|synthetic_arrivals=1|real_sensor=0","TRACE_FORMAT")
    stats={str(n):{"raw_wrong":0,"corrected_wrong":0,"raw_fp":0,"raw_fn":0,
                   "corrected_fp":0,"corrected_fn":0} for n in (1,3,7)}
    dark={str(n):{"raw_spurious":0,"corrected_spurious":0} for n in (1,3,7)}
    wrong=0
    for frame in range(2187):
        sector,site=divmod(frame,81)
        seven=[]
        for band in range(7):
            row=RX.fullmatch(lines[1+frame*7+band])
            gate(row is not None,"BAD_DETECTOR_ROW")
            s,i,j,bit,port,c1,sc1,d1,ds1,c3,sc3,d3,ds3,c7,sc7,d7,ds7=map(int,row.groups())
            gate((s,i,j,port)==(sector,site,band,PORTS[band]),"ORDER_OR_CHANNEL_MISMATCH")
            leaf,_=refs[(band,site)]
            expect=hashlib.sha256(BIT_DOMAIN+bytes.fromhex(leaf)+bytes((sector,))).digest()[0]&1
            gate(bit==expect,"UNTRUSTED_SOURCE_BIT")
            gate(0<=c1<=c3<=c7 and 0<=d1<=d3<=d7,"IMPOSSIBLE_CUMULATIVE_COUNT")
            seven.append((bit,{1:c1,3:c3,7:c7},{1:sc1,3:sc3,7:sc7},
                          {1:d1,3:d3,7:d7},{1:ds1,3:ds3,7:ds7}))
        for band,(bit,counts,scores,dc,ds) in enumerate(seven):
            for n in (1,3,7):
                left=seven[band-1][1][n] if band>0 else 0
                right=seven[band+1][1][n] if band<6 else 0
                gate(scores[n]==7*counts[n]-left-right,"SPECTRAL_CORRECTION_FORGED")
                dl=seven[band-1][3][n] if band>0 else 0
                dr=seven[band+1][3][n] if band<6 else 0
                gate(ds[n]==7*dc[n]-dl-dr,"DARK_CORRECTION_FORGED")
                st=stats[str(n)]
                if int(counts[n]>=5*n)!=bit:
                    st["raw_wrong"]+=1
                    st["raw_fn" if bit else "raw_fp"]+=1
                if int(scores[n]>=THRESH[str(n)])!=bit:
                    st["corrected_wrong"]+=1
                    st["corrected_fn" if bit else "corrected_fp"]+=1
                dark[str(n)]["raw_spurious"]+=int(dc[n]>=5*n)
                dark[str(n)]["corrected_spurious"]+=int(ds[n]>=THRESH[str(n)])
            wrong+=int(int(seven[(band+1)%7][1][7]>=35)!=bit)
    gate(data["source_counts_by_exposure"]==stats,"UNREPRODUCIBLE_ERROR_COUNTS")
    gate(data["dark_counts_by_exposure"]==dark,"UNREPRODUCIBLE_DARK_CONTROLS")
    gate(data["wrong_receiver_map_error_count_at_7"]==wrong,"UNREPRODUCIBLE_WRONG_PORT_ERRORS")
    dest=Path(dest_path);dest.mkdir(parents=True,exist_ok=True)
    for name in names:
        buf=(py/name).read_bytes()
        (dest/name).write_bytes(buf)
        (dest/(name+".sha256")).write_bytes((sha(buf)+"  "+name+"\n").encode("ascii"))
    report={
      "verdict":"INDEPENDENT_UNSEEN_B_CROSSTALK_PASS","source_symbols":15309,
      "frozen_nonce":NONCE,
      "raw_errors":{k:v["raw_wrong"] for k,v in stats.items()},
      "fixed_errors":{k:v["corrected_wrong"] for k,v in stats.items()},
      "dark_controls":dark,"wrong_port_error_count":wrong,
      "trace_sha256":sha(hbp),"json_sha256":sha(raw),
      "physical_optical_observed":False
    }
    artifact=(json.dumps(report,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")
    name="independent-cross-talk-B.json"
    (dest/name).write_bytes(artifact)
    (dest/(name+".sha256")).write_bytes((sha(artifact)+"  "+name+"\n").encode("ascii"))
    print(json.dumps(report,sort_keys=True))
if __name__=="__main__":
    if len(sys.argv)!=5:raise SystemExit("usage: python verify_cross_talk_B.py PR80 PY_NODE JS_NODE VERIFIED")
    verify(*sys.argv[1:])
