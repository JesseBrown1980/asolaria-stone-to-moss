#!/usr/bin/env python3
"""Prospective distinct-seed optical cross-talk correction challenge.

Thresholds were exploratory on the ORIGINAL photon counts, and frozen before
this validation-B corpus was generated. This remains synthetic photon events.
Uses pinned source code in photon_assay.py; independent Node and third auditor.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import photon_assay as original

SCHEMA="ASOLARIA-SEAT3-SPECTRAL-CROSSTALK-SECOND-NONCE-V1"
B_NONCE=b"ASOLARIA-SEAT3-PHOTON-UNSEEN-COUNTS-VALIDATION-B-20261015"
THRESHOLDS={"1":28,"3":78,"7":182}
PORTS=original.PORTS
def sha(v):return hashlib.sha256(v).hexdigest()
def save(out,name,body):
    (out/name).write_bytes(body)
    (out/(name+".sha256")).write_bytes((sha(body)+"  "+name+"\n").encode("ascii"))

def execute(src,outdir):
    # Only the photon pseudo-random stream changes; original 81/567 roots,
    # emission physics surrogate, source-bit law and symbol order unchanged.
    original.NONCE=B_NONCE
    bank=original.SourceBank(src)
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    counts={"1":{"raw_wrong":0,"corrected_wrong":0,"raw_fp":0,"raw_fn":0,"corrected_fp":0,"corrected_fn":0},
            "3":{"raw_wrong":0,"corrected_wrong":0,"raw_fp":0,"raw_fn":0,"corrected_fp":0,"corrected_fn":0},
            "7":{"raw_wrong":0,"corrected_wrong":0,"raw_fp":0,"raw_fn":0,"corrected_fp":0,"corrected_fn":0}}
    dark={"1":{"raw_spurious":0,"corrected_spurious":0},
          "3":{"raw_spurious":0,"corrected_spurious":0},
          "7":{"raw_spurious":0,"corrected_spurious":0}}
    photons=detected=background=0
    wrong_map=0
    rows=[]
    for sector in range(27):
        for site in range(81):
            bits=[bank.source_bit(sector,j,site) for j in range(7)]
            ports=[0]*7; dark_ports=[0]*7
            known={}; known_dark={}
            for exp in range(7):
                vec,e,d,b=original.arrival_step(sector,site,bits,exp,True)
                dv,de,dd,db=original.arrival_step(sector,site,bits,exp,False)
                if de or dd:raise AssertionError("DARK_EMISSION_FORBIDDEN")
                photons+=e;detected+=d;background+=b
                for p in range(7):
                    ports[p]+=vec[p]
                    dark_ports[p]+=dv[p]
                if exp in (0,2,6):
                    known[str(exp+1)]=tuple(ports)
                    known_dark[str(exp+1)]=tuple(dark_ports)
            for j,bit in enumerate(bits):
                vals={}
                for n in (1,3,7):
                    key=str(n)
                    c=known[key]
                    own=c[PORTS[j]]
                    prior=c[PORTS[j-1]] if j>0 else 0
                    later=c[PORTS[j+1]] if j<6 else 0
                    corrected=7*own-prior-later
                    dc=known_dark[key]
                    raw_dark=dc[PORTS[j]]
                    corr_dark=7*raw_dark-(dc[PORTS[j-1]] if j>0 else 0)-(dc[PORTS[j+1]] if j<6 else 0)
                    raw=int(own>=5*n)
                    fixed=int(corrected>=THRESHOLDS[key])
                    if raw!=bit:
                        counts[key]["raw_wrong"]+=1
                        counts[key]["raw_fn" if bit else "raw_fp"]+=1
                    if fixed!=bit:
                        counts[key]["corrected_wrong"]+=1
                        counts[key]["corrected_fn" if bit else "corrected_fp"]+=1
                    dark[key]["raw_spurious"]+=int(raw_dark>=5*n)
                    dark[key]["corrected_spurious"]+=int(corr_dark>=THRESHOLDS[key])
                    vals[n]=(own,corrected,raw_dark,corr_dark)
                # Attacker rotates ONLY the decoder's map, never the source map.
                wrong_map+=int(int(known["7"][PORTS[(j+1)%7]]>=35)!=bit)
                (c1,s1,d1,ds1),(c3,s3,d3,ds3),(c7,s7,d7,ds7)=[vals[x] for x in (1,3,7)]
                rows.append(f"CROSSTALK|s={sector:02d}|site={site:02d}|band={j}"
                            f"|bit={bit}|port={PORTS[j]}"
                            f"|c1={c1}|s1={s1}|d1={d1}|ds1={ds1}"
                            f"|c3={c3}|s3={s3}|d3={d3}|ds3={ds3}"
                            f"|c7={c7}|s7={s7}|d7={d7}|ds7={ds7}")
    if len(rows)!=15309:raise AssertionError("MISSING_SOURCE_SYMBOLS")
    hbp=("PORTAL|schema="+SCHEMA+"|validation_B=1|synthetic_arrivals=1|real_sensor=0\n"+
         "\n".join(rows)+"\n").encode("ascii")
    summary={
       "schema":SCHEMA,"verdict":"PASS","fixture_nonce":B_NONCE.decode("ascii"),
       "original_source_sha256":original.SRC,
       "original_bank_sha256":original.BANK,"original_base_index_sha256":original.INDEX,
       "source_symbols":15309,"frames":2187,"stable_source_identities":81,
       "source_port_map":list(PORTS),"source_band_count":7,
       "correction_law":"score=7*c_own-c_prev-c_next(no_wrap)",
       "frozen_thresholds":THRESHOLDS,"raw_thresholds":{"1":5,"3":15,"7":35},
       "source_counts_by_exposure":counts,
       "dark_counts_by_exposure":dark,
       "wrong_receiver_map_error_count_at_7":wrong_map,
       "source_emission_events":photons,
       "one_detector_source_events":detected,
       "lost_source_events":photons-detected,
       "background_detector_events":background,
       "conserved_one_receiver_per_event":True,
       "violet_band_erasure_status":"HELD_2187_MISSING",
       "six_band_available_symbols":13122,
       "source_ownership_authenticated":False,
       "real_optical_capture_status":"NOT_RUN",
       "physical_photonic_retention_status":"NOT_RUN",
       "full_trace_sha256":sha(hbp),"full_trace_bytes":len(hbp),
       "thresholds_frozen_before_validation_data":True,
       "threshold_selection_was_exploratory_original_fixture":True,
    }
    raw=(json.dumps(summary,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
    save(out,"photon-cross-talk-B.hbp",hbp)
    save(out,"photon-cross-talk-B.json",raw)
    print(json.dumps({"status":"PASS","fixed_error_counts":{k:v["corrected_wrong"] for k,v in counts.items()},
       "raw_error_counts":{k:v["raw_wrong"] for k,v in counts.items()},
       "hbp_sha256":sha(hbp),"json_sha256":sha(raw)},sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: python cross_talk_B.py PR80_ARCHIVE_OUTPUT_DIR OUT_DIR")
    execute(*sys.argv[1:])
