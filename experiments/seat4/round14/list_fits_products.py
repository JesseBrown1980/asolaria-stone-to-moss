#!/usr/bin/env python3
"""Probe individual MAST HST calibrated FITS product names, output HBP only."""
from discover_hst import mast,clean
IDS=(24810128,24812930,24980896)
print("HBP1|schema=SEAT4-MAST-INDIVIDUAL-FITS-PRODUCTS|json=0",flush=True)
for ident in IDS:
    rows=mast("Mast.Caom.Products",{"obsid":ident})
    print(f"GROUP|obsid={ident}|candidate_files={len(rows)}|json=0",flush=True)
    c=0
    for x in rows:
        filename=str(x.get("productFilename",""))
        if not filename.lower().endswith(("_flc.fits","_flt.fits","_raw.fits")):continue
        print("FITS|"+("|".join(k+"="+clean(x.get(k)) for k in
              ("obsID","productFilename","productSubGroupDescription","productType","size","dataURI")))+"|json=0",flush=True)
        c+=1
        if c>=12:break
    if c==0:raise RuntimeError("NO_CALIBRATED_SINGLE_EXPOSURES_FOR_OBSID:"+str(ident))
