#!/usr/bin/env python3
"""C3 independent third implementation: rederive EVERY simulated photon event.

Does NOT import or run either producer. Reads original GitHub Actions source
artifacts and verifies fixed SHA, all 567 actual source bank leaf payloads,
every 30,618 source bit+sensor row, sampled emission/routing, source/binomial
conservation, paired false positives/negatives, band split and dark controls.
"""
from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path

SCHEMA="ASOLARIA-C3-THIRD-SEED-SPECTRAL-DRIFT-V1"
SEED=b"ASOLARIA-C3-HOLDOUT-THIRD-SEED-20261015-V1"
SOURCE="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
INDEX="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"
NAMES=("red","orange","yellow","green","blue","indigo","violet")
PORTS=(2,5,0,6,1,4,3)
SPECS={"C":{"own":168,"left":24,"right":24,"lost":40,"dark":8},
       "D":{"own":120,"left":40,"right":40,"lost":56,"dark":16}}
T={1:28,3:78,7:182}
IDX=re.compile(r"MEM\|band=(red|orange|yellow|green|blue|indigo|violet)\|id=site-(\d{3})\|offset=(\d+)\|length=(\d+)\|sha256=([a-f0-9]{64})\Z")
R=re.compile(r"FRAME\|arm=([CD])\|s=(\d{2})\|site=(\d{2})\|band=(\d)"
             r"\|bit=([01])\|port=(\d)"
             r"\|c1=(\d+)\|x1=(-?\d+)\|dark1=(\d+)\|dx1=(-?\d+)"
             r"\|c3=(\d+)\|x3=(-?\d+)\|dark3=(\d+)\|dx3=(-?\d+)"
             r"\|c7=(\d+)\|x7=(-?\d+)\|dark7=(\d+)\|dx7=(-?\d+)\Z")
def hashb(b):return hashlib.sha256(b).digest()
def sha(b):return hashlib.sha256(b).hexdigest()
def verify(ok,msg):
    if not ok:raise ValueError(msg)
def raw_source(root):
    root=Path(root)
    spec=[("base-evidence/lightbank-memories.json",SOURCE,16689),
          ("rainbow-evidence/rainbow7-bank.jsonl",BANK,184815),
          ("rainbow-evidence/rainbow7-index.hbi",INDEX,70043)]
    original,bank,index=tuple((root/p).read_bytes() for p,_,_ in spec)
    for (_,expected,length),raw in zip(spec,(original,bank,index)):
        verify(len(raw)==length and sha(raw)==expected,"THIRD_ORIGINAL_SHA_NOT_TRUSTED")
    site=json.loads(original)["records"]
    verify(len(site)==81 and index.endswith(b"\n"),"THIRD_INVALID_SOURCE")
    rows=index.decode("ascii").splitlines()
    verify(len(rows)==567,"THIRD_MISSING_ROWS")
    leaves={}
    last=0
    for i,row in enumerate(rows):
        m=IDX.fullmatch(row)
        verify(m is not None,"THIRD_INDEX_ROW")
        band,site_id,off,n,leaf=m.groups()
        site_id,off,n=int(site_id),int(off),int(n)
        verify(band==NAMES[i//81] and site_id==i%81 and off==last
               and n>0 and off+n<=len(bank),"THIRD_INDEX_ORDER")
        last=off+n
        payload=bank[off:last]
        verify(sha(payload)==leaf,"THIRD_LEAF_SHA")
        b=json.loads(payload)
        verify(b["id"]==f"site-{site_id:03d}" and b["band"]==band and
               b["record"]==site[site_id],"THIRD_SOURCE_RECORD_INCOMPATIBLE")
        leaves[(i//81,site_id)]=bytes.fromhex(leaf)
    verify(last==len(bank) and len(leaves)==567,"THIRD_ALL_SOURCE_BYTES")
    return leaves
def bit(leaves,sector,site,band):
    return hashb(b"ASOLARIA-PHOTON-BIT-V1|"+leaves[(band,site)]+bytes((sector,)))[0]&1
def reconstruct(arm,sector,site,bits):
    m=SPECS[arm]
    signal=[0]*7;dark=[0]*7
    seen={};darkseen={}
    e_total=d_total=b_total=0
    for epoch in range(7):
        for band,b in enumerate(bits):
            sample=hashb(b"ASOLARIA-PHOTON-COUNTS-V1|"+SEED+arm.encode("ascii")+
                         bytes((sector,site,band,epoch)))
            limit=192 if b else 16
            for k in range(16):
                if sample[k]>=limit:continue
                e_total+=1
                u=sample[k+16]
                if u<m["own"]:dest=band
                elif u<m["own"]+m["left"]:dest=band-1
                elif u<m["own"]+m["left"]+m["right"]:dest=band+1
                else:dest=-1
                if 0<=dest<7:
                    signal[PORTS[dest]]+=1
                    d_total+=1
        for port in range(7):
            noise=hashb(b"ASOLARIA-PHOTON-DARK-V1|"+SEED+arm.encode("ascii")+
                        bytes((sector,site,port,epoch)))
            for k in range(16):
                if noise[k]<m["dark"]:
                    signal[port]+=1
                    dark[port]+=1
                    b_total+=1
        if epoch in (0,2,6):
            seen[epoch+1]=tuple(signal)
            darkseen[epoch+1]=tuple(dark)
    verify(e_total>=d_total,"THIRD_IMPOSSIBLE_DETECTOR")
    return seen,darkseen,(e_total,d_total,e_total-d_total,b_total)

def empty():return dict(both_correct=0,fixed_only=0,degraded=0,both_wrong=0,
                        raw_wrong=0,fixed_wrong=0,raw_fp=0,raw_fn=0,
                        fixed_fp=0,fixed_fn=0)
def dark_empty():return dict(raw_spurious=0,fixed_spurious=0)
def score(c,j):return 7*c[j]-(c[j-1] if j>0 else 0)-(c[j+1] if j<6 else 0)

def check(original,python_dir,node_dir,dest_dir):
    leaves=raw_source(original)
    a,b=Path(python_dir),Path(node_dir)
    filenames=("c3-third-seed.hbp","c3-results.json")
    for f in filenames:
        left=(a/f).read_bytes();right=(b/f).read_bytes()
        verify(left==right,"PYTHON_NODE_FULL_BYTE_DIVERGENCE_"+f)
        want=(sha(left)+"  "+f+"\n").encode("ascii")
        for parent in (a,b):
            verify((parent/(f+".sha256")).read_bytes()==want,"SOURCE_RECEIPT_SIDECAR_MISMATCH")
    full=(a/filenames[0]).read_bytes()
    output=(a/filenames[1]).read_bytes()
    m=json.loads(output)
    verify(m["schema"]==SCHEMA and m["verdict"]=="SIMULATION_PASS","THIRD_SIMULATION_STATUS")
    verify((m["source_sha256"],m["bank_sha256"],m["index_sha256"])==(SOURCE,BANK,INDEX),"THIRD_BANK_CHANGED")
    verify(m["seed"]==SEED.decode("ascii") and m["conditions"]==["C","D"] and
           m["models"]==SPECS,"THIRD_MODEL_PARAMS_REWRITTEN")
    verify(m["source_port_map"]==list(PORTS) and
           m["source_identities"]==81 and m["stored_bank_refs"]==567 and
           m["symbol_count_per_model"]==15309,"THIRD_SOURCE_SCOPE")
    verify(m["seven_exposure_repeats"]==7 and m["frozen_raw_thresholds"]==
           {"1":5,"3":15,"7":35} and m["frozen_corrected_thresholds"]==
           {"1":28,"3":78,"7":182},"THIRD_DECODER_WAS_RETUNED")
    verify(m["first_fixture_thresholds_exploratory"] is True and
           m["third_fixture_thresholds_frozen_before_generation"] is True,"THIRD_BLINDNESS_DISCLOSURE")
    verify(m["hbp_sha256"]==sha(full) and m["hbp_bytes"]==len(full),"THIRD_TRACE_ROOT")
    verify(m["new_real_optical_measurements"]==0 and
           m["physical_optical_storage_test"]=="NOT_RUN" and
           m["biological_neural_memory_test"]=="NOT_RUN" and
           m["external_source_custody_authenticated"] is False,"FRAUDULENT_PHYSICAL_SCIENCE")
    gates=m["source_binding_controls"]
    verify(gates=={"changed_source_byte":"HOLD","channel_reassignment":"HOLD",
           "missing_violet_2187_aliases":"HOLD",
           "self_consistent_attacker_owned_digest":"ORIGIN_UNAUTHENTICATED",
           "stale_fixture_nonce":"HOLD"},"THIRD_MISSING_NEGATIVE_POLICY")
    rows=full.decode("ascii").splitlines()
    verify(len(rows)==2*15309+1 and full.endswith(b"\n"),"THIRD_ROW_COUNT")
    verify(rows[0]==f"PORTAL|schema={SCHEMA}|source_root={BANK}|fixture=THIRD_C_D|simulated_arrivals=1|real_photons=0",
           "THIRD_UNTRUSTED_SENSOR_MODE")
    agg={arm:{str(n):empty() for n in (1,3,7)} for arm in ("C","D")}
    bands={arm:{str(n):[empty() for _ in range(7)] for n in (1,3,7)} for arm in ("C","D")}
    dark={arm:{str(n):dark_empty() for n in (1,3,7)} for arm in ("C","D")}
    wrongmap={"C":0,"D":0}
    eventcount={arm:{"emitted":0,"detected":0,"lost":0,"background":0} for arm in ("C","D")}
    for ai,arm in enumerate(("C","D")):
        for frame in range(2187):
            sector,site=divmod(frame,81)
            bits=[bit(leaves,sector,site,j) for j in range(7)]
            live,no_light,book=reconstruct(arm,sector,site,bits)
            for field,n in zip(("emitted","detected","lost","background"),book):
                eventcount[arm][field]+=n
            for j,truth in enumerate(bits):
                row=rows[1+ai*15309+frame*7+j]
                mat=R.fullmatch(row)
                verify(mat is not None,"THIRD_CAPTURE_ROW_PARSE_ERROR")
                a1,s,l,k,received,port,*tail=mat.groups()
                verify((a1,int(s),int(l),int(k),int(received),int(port))==
                       (arm,sector,site,j,truth,PORTS[j]),"THIRD_SOURCE_OR_PORT_REPLACED")
                numbers=tuple(map(int,tail))
                verify(len(numbers)==12,"THIRD_OBS_COUNT")
                for idx,n in enumerate((1,3,7)):
                    obs=tuple(live[n][PORTS[k]] for k in range(7))
                    darkobs=tuple(no_light[n][PORTS[k]] for k in range(7))
                    c,corrected,d,dc=numbers[idx*4:idx*4+4]
                    verify((c,corrected,d,dc)==
                           (obs[j],score(obs,j),darkobs[j],score(darkobs,j)),
                           "THIRD_PHOTON_EVENT_OR_CORRECTION_FALSE")
                    raw=int(c>=5*n);fix=int(corrected>=T[n])
                    label=("both_wrong" if raw!=truth and fix!=truth else
                           "fixed_only" if raw!=truth else
                           "degraded" if fix!=truth else "both_correct")
                    for rowstats in (agg[arm][str(n)],bands[arm][str(n)][j]):
                        rowstats[label]+=1
                        rowstats["raw_wrong"]+=int(raw!=truth)
                        rowstats["fixed_wrong"]+=int(fix!=truth)
                        rowstats["raw_fp"]+=int(raw==1 and truth==0)
                        rowstats["raw_fn"]+=int(raw==0 and truth==1)
                        rowstats["fixed_fp"]+=int(fix==1 and truth==0)
                        rowstats["fixed_fn"]+=int(fix==0 and truth==1)
                    dark[arm][str(n)]["raw_spurious"]+=int(d>=5*n)
                    dark[arm][str(n)]["fixed_spurious"]+=int(dc>=T[n])
                wrongmap[arm]+=int(int(live[7][PORTS[(j+1)%7]]>=35)!=truth)
    verify(agg==m["paired_census_by_model"] and bands==m["per_band_by_model"] and
           dark==m["no_light_dark_by_model"] and
           wrongmap==m["wrong_map_errors_by_model_at_7"] and
           eventcount==m["event_conservation_by_model"],
           "THIRD_NOT_REPRODUCIBLE_C3_STATISTICS")
    dest=Path(dest_dir);dest.mkdir(parents=True,exist_ok=True)
    for name in filenames:
        body=(a/name).read_bytes()
        (dest/name).write_bytes(body)
        (dest/(name+".sha256")).write_bytes((sha(body)+"  "+name+"\n").encode("ascii"))
    summary={"verdict":"INDEPENDENT_C3_D_FULL_SOURCE_AUDIT_PASS",
             "symbols_per_model":15309,"source_bank_entries":567,
             "third_seed":SEED.decode("ascii"),
             "raw_error_counts":{arm:{n:v["raw_wrong"] for n,v in agg[arm].items()} for arm in ("C","D")},
             "corrected_error_counts":{arm:{n:v["fixed_wrong"] for n,v in agg[arm].items()} for arm in ("C","D")},
             "paired_crossovers":{arm:{n:{"repaired":v["fixed_only"],"degraded":v["degraded"],
                                            "both_wrong":v["both_wrong"]}
                                    for n,v in agg[arm].items()} for arm in ("C","D")},
             "dark_controls":dark,
             "hbp_sha256":sha(full),"results_json_sha256":sha(output),
             "measured_photons":0,"optical_retention_not_run":True}
    body=(json.dumps(summary,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
    name="independent-c3-check.json"
    (dest/name).write_bytes(body)
    (dest/(name+".sha256")).write_bytes((sha(body)+"  "+name+"\n").encode("ascii"))
    print(json.dumps(summary,sort_keys=True))
if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("usage: python verify_c3_third_seed.py ORIGINAL_PR80 PY_DIR JS_DIR VERIFIED_DIR")
    check(*sys.argv[1:])
