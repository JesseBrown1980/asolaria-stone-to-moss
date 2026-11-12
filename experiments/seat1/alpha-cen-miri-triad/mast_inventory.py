#!/usr/bin/env python3
"""Public MAST JWST/MIRI three-program discovery. No token needed; no planet claim."""
import argparse, hashlib, json, pathlib, time, urllib.parse, urllib.request
PROGRAMS=("1618","6797","9252")
COLS=("obsid","obs_id","proposal_id","target_name","filters","t_min","instrument_name")
PCOLS=("obsID","productFilename","dataURI","size","calib_level","productType","dataRights")
def sha(b):return hashlib.sha256(b).hexdigest()
def clean(x):return str(x if x is not None else "").replace("|","/").replace("\n"," ").replace("\r"," ")[:400]
def request(service,params,page=1,pagesize=1500):
    obj=dict(service=service,params=params,format="json",pagesize=pagesize,page=page)
    url="https://mast.stsci.edu/api/v0/invoke?"+urllib.parse.urlencode({"request":json.dumps(obj,separators=(",",":"))})
    if len(url)>5000:raise ValueError("TOO_LONG_URL")
    for n in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Asolaria-MIRI-Public-Inventory-20261016"}),timeout=65) as r:
                j=json.loads(r.read(30_000_000))
            if j.get("status")=="ERROR" or not isinstance(j.get("data"),list):raise RuntimeError("MAST_ERROR")
            return j
        except (OSError,ValueError,RuntimeError):
            if n==2:raise
            time.sleep(n+1)
def role(r):
    name=str(r.get("target_name","")).upper();inst=str(r.get("instrument_name","")).upper()
    if "MIRI/CORON" not in inst:return "OTHER_INSTRUMENT"
    if "BACKGROUND" in name or "BKGND" in name:return "BACKGROUND"
    if "EPS" in name or "MUS" in name or "REF" in name:return "PSF_REFERENCE"
    if any(s in name for s in ("ALPHA","ACEN","ALF","CEN")):return "ALPHACEN_FIELD_ROLE_NOT_PROVEN"
    return "UNCLASSIFIED"
def render(obs,products):
    lines=["HBP1|schema=ASOLARIA-MIRI-S1-THREE-EPOCH-MAST-INVENTORY-V1|archive=MAST_CAOM_PUBLIC|json=0",
    "BOUNDARY|new_planet=NOT_CLAIMED|S1_UNCONFIRMED=TRUE|FITS_REDUCTION=PENDING|HF_TOKEN_USED=NO_PUBLIC_ARCHIVE_DOES_NOT_REQUIRE|json=0"]
    for prop in PROGRAMS:
        observations=obs[prop]; prods=products[prop]
        coron=[r for r in observations if "MIRI/CORON" in str(r.get("instrument_name","")).upper()]
        cal=[p for p in prods if str(p.get("productFilename","")).lower().endswith(("_cal.fits","_crf.fits","_i2d.fits"))]
        lines.append(f"EPOCH|proposal={prop}|observations={len(observations)}|coronagraph_obs={len(coron)}|products={len(prods)}|calibrated_candidates={len(cal)}|json=0")
        for r in observations:
            lines.append("OBS|"+ "|".join(k+"="+clean(r.get(k)) for k in COLS)+"|role="+role(r)+"|json=0")
        for p in prods:
            name=str(p.get("productFilename","")).lower()
            if not name.endswith(("_cal.fits","_crf.fits","_i2d.fits","_rate.fits","_uncal.fits")):continue
            lines.append("PRODUCT|proposal="+prop+"|"+"|".join(k+"="+clean(p.get(k)) for k in PCOLS)+"|downloaded=FALSE|json=0")
    return "\n".join(lines)+"\n"
def get(out):
    obs={}; products={}
    for prop in PROGRAMS:
        params={"columns":",".join(("obs_collection",)+COLS),"filters":[
            {"paramName":"obs_collection","values":["JWST"]},
            {"paramName":"proposal_id","values":[prop]}]}
        q=request("Mast.Caom.Filtered",params)
        rows=q["data"]
        pages=int((q.get("paging") or {}).get("pagesFiltered",1) or 1)
        if pages>10:raise ValueError("UNBOUNDED_OBSERVATIONS")
        for pg in range(2,pages+1):rows+=request("Mast.Caom.Filtered",params,pg)["data"]
        obs[prop]=[r for r in rows if str(r.get("proposal_id"))==prop]
        if not obs[prop]:raise RuntimeError("NO_OBSERVATION_"+prop)
        ids=list(dict.fromkeys(str(r["obsid"]) for r in obs[prop] if "MIRI/CORON" in str(r.get("instrument_name","")).upper() and r.get("obsid")))
        p=[]
        for start in range(0,len(ids),8):
            param={"obsid":",".join(ids[start:start+8])}
            q=request("Mast.Caom.Products",param)
            p+=q["data"]
            pages=int((q.get("paging") or {}).get("pagesFiltered",1) or 1)
            if pages>10:raise ValueError("UNBOUNDED_PRODUCTS")
            for pg in range(2,pages+1):p+=request("Mast.Caom.Products",param,pg)["data"]
        products[prop]=list({str(r.get("dataURI") or r.get("productFilename")):r for r in p}.values())
        print("MAST",prop,"observations",len(obs[prop]),"coronagraph",len(ids),"products",len(products[prop]),flush=True)
    s=render(obs,products);out.mkdir(parents=True,exist_ok=True)
    (out/"MAST-THREE-EPOCH-INVENTORY.hbp").write_text(s)
    (out/"MAST-THREE-EPOCH-INVENTORY.hbp.sha256").write_text(sha(s.encode())+"  MAST-THREE-EPOCH-INVENTORY.hbp\n")
    print("INVENTORY_SHA256",sha(s.encode()))
def test():
    assert role({"target_name":"EPS-MUS-OFFSET","instrument_name":"MIRI/CORON"})=="PSF_REFERENCE"
    assert role({"target_name":"FINAL-ACEN-BKGND","instrument_name":"MIRI/CORON"})=="BACKGROUND"
    obs={k:[] for k in PROGRAMS}; prod={k:[] for k in PROGRAMS}
    obs["1618"]=[dict(obsid=123,obs_id="jw01618",proposal_id="1618",target_name="AlphaCen-A",instrument_name="MIRI/CORON")]
    prod["1618"]=[dict(productFilename="jw01618_cal.fits",dataURI="mast:JWST/product/jw01618_cal.fits")]
    s=render(obs,prod)
    assert s.count("EPOCH|")==3 and s.count("PRODUCT|")==1 and "FITS_REDUCTION=PENDING" in s
    assert sha(s.encode())!=sha(s.replace("S1_UNCONFIRMED=TRUE","S1_UNCONFIRMED=FALSE").encode())
    print("SELF_TEST_PASS|3_epochs=PASS|role=PASS|mutated_hash=REJECT|json=0")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",default="out");p.add_argument("--self-test",action="store_true");a=p.parse_args()
    test() if a.self_test else get(pathlib.Path(a.out))
