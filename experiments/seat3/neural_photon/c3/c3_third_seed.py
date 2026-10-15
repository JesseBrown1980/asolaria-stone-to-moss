#!/usr/bin/env python3
"""C3/S5-02 prospective source-pinned synthetic photon-noise generalization.

Fresh *fixed* deterministic seed (not physical photons); C=old optical leakage,
D=stronger leakage plus background. No threshold tuning on C/D or real optics.
Source is actual original 81/567 bank archived from PR80, SHA256 pinned.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA = "ASOLARIA-C3-THIRD-SEED-SPECTRAL-DRIFT-V1"
SEED = b"ASOLARIA-C3-HOLDOUT-THIRD-SEED-20261015-V1"
SOURCE_SHA = "02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
BANK_SHA = "52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
INDEX_SHA = "6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"
PORTS = (2,5,0,6,1,4,3)
BANDS = ("red","orange","yellow","green","blue","indigo","violet")
BIT_DOMAIN = b"ASOLARIA-PHOTON-BIT-V1|"
EMIT_DOMAIN = b"ASOLARIA-PHOTON-COUNTS-V1|"
DARK_DOMAIN = b"ASOLARIA-PHOTON-DARK-V1|"
THRESH = {1:28,3:78,7:182}
MODELS = {"C":(168,24,24,40,8),"D":(120,40,40,56,16)}
RECORD = re.compile(r"MEM\|band=(red|orange|yellow|green|blue|indigo|violet)\|id=site-(\d{3})\|offset=(\d+)\|length=(\d+)\|sha256=([a-f0-9]{64})\Z")

def digest(data): return hashlib.sha256(data).hexdigest()
def guard(ok, text):
    if not ok: raise ValueError(text)
def pin(path, sha, length):
    data=Path(path).read_bytes()
    guard(len(data)==length and digest(data)==sha, "UNTRUSTED_OR_CHANGED_SOURCE_ROOT:"+str(path))
    return data

class Bank:
    def __init__(self, root):
        root=Path(root)
        source=pin(root/"base-evidence/lightbank-memories.json", SOURCE_SHA,16689)
        bank=pin(root/"rainbow-evidence/rainbow7-bank.jsonl", BANK_SHA,184815)
        idx=pin(root/"rainbow-evidence/rainbow7-index.hbi", INDEX_SHA,70043)
        original=json.loads(source)["records"]
        guard(len(original)==81 and idx.endswith(b"\n"),"INVALID_ORIGINAL_SOURCE")
        lines=idx.decode("ascii").splitlines()
        guard(len(lines)==567,"BASE_INDEX_COUNT")
        self.leaves={}
        last=0
        for n,line in enumerate(lines):
            mat=RECORD.fullmatch(line)
            guard(mat is not None,"BASE_ROW_INVALID")
            name,site,offset,length,leaf=mat.groups()
            site=int(site);offset=int(offset);length=int(length)
            guard(name==BANDS[n//81] and site==n%81 and offset==last
                  and length>0 and offset+length<=len(bank),"BASE_REFERENCE_CHANGED")
            last=offset+length
            payload=bank[offset:last]
            guard(digest(payload)==leaf,"BASE_LEAF_SHA_MISMATCH")
            record=json.loads(payload)
            guard(record["id"]==f"site-{site:03d}" and record["band"]==name
                  and record["record"]==original[site],"BASE_MEMORY_CONTENT_DRIFT")
            self.leaves[(n//81,site)]=bytes.fromhex(leaf)
        guard(len(self.leaves)==567 and last==len(bank),"SOURCE_BANK_INCOMPLETE")
    def bit(self, sector, site, band):
        guard(type(sector)==int and 0<=sector<27,"BAD_SECTOR")
        guard(type(site)==int and 0<=site<81,"BAD_SITE")
        guard(type(band)==int and 0<=band<7,"BAD_BAND")
        return hashlib.sha256(BIT_DOMAIN+self.leaves[(band,site)]+bytes((sector,))).digest()[0]&1

def exposure(arm, sector, site, bits, epoch, light=True):
    own,left,right,lost,dark_rate=MODELS[arm]
    assert own+left+right+lost==256
    sensors=[0]*7
    emitted=registered=background=0
    if light:
        for band,bit in enumerate(bits):
            random=hashlib.sha256(EMIT_DOMAIN+SEED+arm.encode("ascii")+
                                  bytes((sector,site,band,epoch))).digest()
            limit=192 if bit else 16
            for k in range(16):
                if random[k]>=limit:continue
                emitted+=1
                u=random[k+16]
                if u<own:dest=band
                elif u<own+left:dest=band-1
                elif u<own+left+right:dest=band+1
                else:dest=-1
                if 0<=dest<7:
                    sensors[PORTS[dest]]+=1
                    registered+=1
    for port in range(7):
        random=hashlib.sha256(DARK_DOMAIN+SEED+arm.encode("ascii")+
                              bytes((sector,site,port,epoch))).digest()
        for k in range(16):
            if random[k]<dark_rate:
                sensors[port]+=1
                background+=1
    guard(registered<=emitted and sum(sensors)==registered+background,
          "PHOTON_SURROGATE_CONSERVATION_BROKEN")
    return sensors,emitted,registered,background

def counters():return {"both_correct":0,"fixed_only":0,"degraded":0,"both_wrong":0,
                       "raw_wrong":0,"fixed_wrong":0,"raw_fp":0,"raw_fn":0,
                       "fixed_fp":0,"fixed_fn":0}
def darkc():return {"raw_spurious":0,"fixed_spurious":0}
def record_score(ordered, j):
    return 7*ordered[j]-(ordered[j-1] if j>0 else 0)-(ordered[j+1] if j<6 else 0)

def main(src,dest):
    bank=Bank(src)
    aggregate={arm:{str(n):counters() for n in (1,3,7)} for arm in MODELS}
    perband={arm:{str(n):[counters() for _ in range(7)] for n in (1,3,7)} for arm in MODELS}
    dark={arm:{str(n):darkc() for n in (1,3,7)} for arm in MODELS}
    wrongmap={arm:0 for arm in MODELS}
    conservation={arm:dict(emitted=0,detected=0,lost=0,background=0) for arm in MODELS}
    rows=[]
    for arm in ("C","D"):
        for sector in range(27):
            for site in range(81):
                bits=[bank.bit(sector,site,j) for j in range(7)]
                detector=[0]*7;off=[0]*7
                stages={};darkstages={}
                for epoch in range(7):
                    counts,emit,read,bg=exposure(arm,sector,site,bits,epoch)
                    onlydark,dark_emit,dark_detect,dark_bg=exposure(arm,sector,site,bits,epoch,False)
                    guard(dark_emit==dark_detect==0,"DARK_SOURCE_STILL_EMITTING")
                    ledger=conservation[arm]
                    ledger["emitted"]+=emit;ledger["detected"]+=read
                    ledger["lost"]+=emit-read;ledger["background"]+=bg
                    for p in range(7):
                        detector[p]+=counts[p]
                        off[p]+=onlydark[p]
                    if epoch in (0,2,6):
                        stages[epoch+1]=tuple(detector)
                        darkstages[epoch+1]=tuple(off)
                for j,truth in enumerate(bits):
                    values=[]
                    for n in (1,3,7):
                        physical=tuple(stages[n][PORTS[k]] for k in range(7))
                        darkness=tuple(darkstages[n][PORTS[k]] for k in range(7))
                        count=physical[j];score=record_score(physical,j)
                        dcount=darkness[j];dscore=record_score(darkness,j)
                        raw=int(count>=5*n);fixed=int(score>=THRESH[n])
                        a=aggregate[arm][str(n)];b=perband[arm][str(n)][j]
                        for row in (a,b):
                            row["raw_wrong"]+=int(raw!=truth)
                            row["fixed_wrong"]+=int(fixed!=truth)
                            row["raw_fp"]+=int(raw==1 and truth==0)
                            row["raw_fn"]+=int(raw==0 and truth==1)
                            row["fixed_fp"]+=int(fixed==1 and truth==0)
                            row["fixed_fn"]+=int(fixed==0 and truth==1)
                            label=("both_wrong" if raw!=truth and fixed!=truth else
                                   "fixed_only" if raw!=truth else
                                   "degraded" if fixed!=truth else "both_correct")
                            row[label]+=1
                        dark[arm][str(n)]["raw_spurious"]+=int(dcount>=5*n)
                        dark[arm][str(n)]["fixed_spurious"]+=int(dscore>=THRESH[n])
                        values.extend((count,score,dcount,dscore))
                    wrongmap[arm]+=int(int(stages[7][PORTS[(j+1)%7]]>=35)!=truth)
                    csv="|".join(f"{k}{n}={v}" for ix,n in enumerate((1,3,7))
                                 for k,v in zip(("c","x","dark","dx"),values[ix*4:ix*4+4]))
                    rows.append(f"FRAME|arm={arm}|s={sector:02d}|site={site:02d}|band={j}"
                                f"|bit={truth}|port={PORTS[j]}|{csv}")
    guard(len(rows)==2*15309,"FAILED_COMPLETE_C3_D_SYMBOL_SCOPE")
    for arm in ("C","D"):
        guard(conservation[arm]["emitted"]==
              conservation[arm]["detected"]+conservation[arm]["lost"],"LOST_EVENT_ACCOUNTING")
        for n in (1,3,7):
            x=aggregate[arm][str(n)]
            guard(sum(x[k] for k in ("both_correct","fixed_only","degraded","both_wrong"))==15309,
                  "C3_PAIRED_COVERAGE")
            guard(x["raw_wrong"]==x["fixed_only"]+x["both_wrong"] and
                  x["fixed_wrong"]==x["degraded"]+x["both_wrong"],"C3_PAIRED_MATH")
    hbp=("PORTAL|schema="+SCHEMA+"|source_root="+BANK_SHA+
         "|fixture=THIRD_C_D|simulated_arrivals=1|real_photons=0\n"+
         "\n".join(rows)+"\n").encode("ascii")
    metadata={
      "schema":SCHEMA,"verdict":"SIMULATION_PASS",
      "source_sha256":SOURCE_SHA,"bank_sha256":BANK_SHA,"index_sha256":INDEX_SHA,
      "seed":SEED.decode("ascii"),"conditions":["C","D"],
      "models":{"C":dict(own=168,left=24,right=24,lost=40,dark=8),
                "D":dict(own=120,left=40,right=40,lost=56,dark=16)},
      "symbol_count_per_model":15309,"source_identities":81,"stored_bank_refs":567,
      "source_port_map":list(PORTS),"seven_exposure_repeats":7,
      "frozen_raw_thresholds":{"1":5,"3":15,"7":35},
      "frozen_corrected_thresholds":{"1":28,"3":78,"7":182},
      "deconvolution":"score=7*own-left-neighbor-right-neighbor; edges_zero",
      "paired_census_by_model":aggregate,"per_band_by_model":perband,
      "no_light_dark_by_model":dark,"wrong_map_errors_by_model_at_7":wrongmap,
      "event_conservation_by_model":conservation,
      "source_binding_controls":{"changed_source_byte":"HOLD",
         "channel_reassignment":"HOLD","missing_violet_2187_aliases":"HOLD",
         "self_consistent_attacker_owned_digest":"ORIGIN_UNAUTHENTICATED",
         "stale_fixture_nonce":"HOLD"},
      "first_fixture_thresholds_exploratory":True,
      "third_fixture_thresholds_frozen_before_generation":True,
      "new_real_optical_measurements":0,"physical_optical_storage_test":"NOT_RUN",
      "biological_neural_memory_test":"NOT_RUN","external_source_custody_authenticated":False,
      "hbp_bytes":len(hbp),"hbp_sha256":digest(hbp)
    }
    canonical=(json.dumps(metadata,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
    folder=Path(dest);folder.mkdir(parents=True,exist_ok=True)
    for name,raw in (("c3-third-seed.hbp",hbp),("c3-results.json",canonical)):
        (folder/name).write_bytes(raw)
        (folder/(name+".sha256")).write_bytes((digest(raw)+"  "+name+"\n").encode("ascii"))
    print(json.dumps({"verdict":"SIMULATION_PASS",
          "raw_errors":{a:{k:v["raw_wrong"] for k,v in aggregate[a].items()} for a in ("C","D")},
          "corrected_errors":{a:{k:v["fixed_wrong"] for k,v in aggregate[a].items()} for a in ("C","D")},
          "dark_false_triggers":dark,"hbp_sha256":digest(hbp),
          "json_sha256":digest(canonical)},sort_keys=True))
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: python c3_third_seed.py ORIGINAL_PR80_ARCHIVE OUTPUT_DIR")
    main(*sys.argv[1:])
