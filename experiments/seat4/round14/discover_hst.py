#!/usr/bin/env python3
"""Seat4 MAST HST public product discovery. No JSON files, only text HBP log.

The wire API uses JSON internally, as required by MAST; no JSON artifacts are
written into Asolaria. Refuse fabricated exposures or synthesized timestamps.
"""
from __future__ import annotations
import json,urllib.request,urllib.parse,sys,time
PROPOSALS=("12985","13466","13847","16653","16983","17399")
def mast(service,params):
    req={"service":service,"params":params,"format":"json","pagesize":1000,"page":1}
    obj=json.dumps(req,separators=(",",":"))
    body=urllib.parse.urlencode({"request":obj}).encode("ascii")
    url="https://mast.stsci.edu/api/v0/invoke"
    errors=[]
    for mode in ("post","get"):
        try:
            if mode=="post":
                q=urllib.request.Request(url,data=body,headers={"User-Agent":"Asolaria-Seat4-optical-provenance/1.0","Accept":"application/json"})
            else:
                q=urllib.request.Request(url+"?"+urllib.parse.urlencode({"request":obj}),headers={"User-Agent":"Asolaria-Seat4-optical-provenance/1.0","Accept":"application/json"})
            with urllib.request.urlopen(q,timeout=50) as res:
                raw=res.read(4_000_000)
            parsed=json.loads(raw)
            if parsed.get("status")=="ERROR":
                raise ValueError(str(parsed.get("msg")))
            return parsed.get("data",[])
        except Exception as exc:
            errors.append(mode+":"+str(exc)[:200])
    raise RuntimeError("MAST_PUBLIC_API_UNAVAILABLE:"+" / ".join(errors))
def clean(x):
    return str(x if x is not None else "NA").replace("|","/").replace("\n","_")
def main():
    rows=mast("Mast.Caom.Filtered",{"columns":"*","filters":[
     {"paramName":"proposal_id","values":list(PROPOSALS)}]})
    print("HBP1|schema=SEAT4-HST-PROXIMA-OPTICAL-DISCOVERY|role=REMOTE_ARCHIVE_METADATA|json=0",flush=True)
    print("SUMMARY|public_observation_rows="+str(len(rows))+"|candidate_programs="+",".join(PROPOSALS)+"|json=0",flush=True)
    for r in rows:
        filt=str(r.get("filters",""))
        target=str(r.get("target_name",""))
        if ("555" not in filt and "467" not in filt) or r.get("obs_collection")!="HST":continue
        print("OBS|"+("|".join(k+"="+clean(r.get(k)) for k in (
             "obsid","obs_id","proposal_id","target_name","instrument_name",
             "filters","t_min","t_max","t_exptime","dataRights","calib_level"))) + "|json=0",flush=True)
if __name__=="__main__":main()
