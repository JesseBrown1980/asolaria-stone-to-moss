#!/usr/bin/env python3
"""Read ORIGINAL published Proxima observations, without altering their bytes.
Published CDS J/A+A/700/A11 fixed-width records, and NASA/HST released TIFF.
No scientific result or simulated planet is emitted by acquisition alone.
"""
import datetime as dt
import hashlib
import os
import pathlib
import time
import urllib.error
import urllib.request

BASE=pathlib.Path(os.environ.get("ASOLARIA_DATA_OUT","real_observations/output"))
BASE.mkdir(parents=True,exist_ok=True)
CATALOG="J/A+A/700/A11"
ROOTS=[
 "https://cdsarc.cds.unistra.fr/ftp/J/A+A/700/A11/",
 "https://cdsarc.cds.unistra.fr/ftp/J/A%2BA/700/A11/",
 "https://cdsarc.cfa.harvard.edu/ftp/J/A+A/700/A11/",
 "https://cdsarc.u-strasbg.fr/ftp/J/A+A/700/A11/",
 "https://cdsarc.u-strasbg.fr/ftp/J/A%2BA/700/A11/",
]
HUBBLE="https://assets.science.nasa.gov/dynamicimage/assets/science/missions/hubble/releases/2013/06/STScI-01EVVCFQQJEH75APX7EQSDAGD9.tif"

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Asolaria-Source-Audit/1.0 (scientific provenance)","Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=35) as response:
        final=response.geturl()
        if not final.startswith("https://"):raise ValueError("non-HTTPS redirect")
        data=response.read(12_000_000)
        if len(data)>=12_000_000:raise ValueError("source unexpectedly large")
        return data,final,response.headers.get("content-type","")

def get_catalog(filename,expected_len,expected_rows):
    errors=[]
    for base in ROOTS:
        try:
            body,final,mime=fetch(base+filename)
            # A newline is not part of the fixed-width 120/43-byte logical record.
            lines=body.splitlines()
            if len(lines)!=expected_rows:
                raise ValueError(f"Expected {expected_rows} rows; got {len(lines)}; content head {body[:75]!r}")
            if any(len(line)!=expected_len for line in lines):
                actual=[len(line) for line in lines[:6]]
                raise ValueError(f"Wrong fixed-width source rows {actual} vs {expected_len}")
            sourcefile=BASE/filename
            sourcefile.write_bytes(body)
            return {"dataset":CATALOG+"/"+filename,"url":final,
              "file":filename,"size_bytes":len(body),"logical_records":len(lines),
              "record_width":expected_len,"sha256":hashlib.sha256(body).hexdigest(),
              "content_type":mime, "first_line":lines[0].decode("ascii")}
        except Exception as e:
            errors.append(f"{base}: {str(e)[:150]}")
    raise RuntimeError("Cannot download authentic "+filename+"\n"+"\n".join(errors))

def get_hubble():
    try:
        body,final,mime=fetch(HUBBLE)
        if body[:4] in (b"II*\x00",b"MM\x00*"):kind="tif"
        elif body.startswith(b"\xff\xd8\xff"):kind="jpg"
        elif body.startswith(b"\x89PNG\r\n\x1a\n"):kind="png"
        elif body.startswith(b"RIFF") and body[8:12]==b"WEBP":kind="webp"
        else:raise ValueError("unrecognized image magic:"+body[:16].hex())
        filename="HUBBLE_2012_F555W_PUBLICATION."+kind
        (BASE/filename).write_bytes(body)
        return {"source":final,"file":filename,"encoded_format":kind,
          "sha256":hashlib.sha256(body).hexdigest(),"bytes":len(body),
          "observation_date_utc":"2012-10-01","camera":"HST WFC3/UVIS",
          "filter":"F555W","exposure_seconds":175,
          "source_type":"NASA public image returned as dynamically encoded image, NOT original calibrated FITS science observation",
          "available":True}
    except Exception as e:
        return {"source":HUBBLE,"available":False,"error":str(e)[:220],
        "observation_date_utc":"2012-10-01","camera":"HST WFC3/UVIS","filter":"F555W"}

def main():
    manifest={
       "schema":"ASOLARIA-REAL-PROXIMA-ORIGINAL-CATALOG-V1",
       "retrieved_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
       "bibliography":"Suarez Mascareno et al., Astron. Astrophys. 700 A11 (2025)",
       "catalog_readme":"https://cdsarc.cds.unistra.fr/viz-bin/ReadMe/J/A%2BA/700/A11?format=html",
       "source_claim":"PUBLIC INDEPENDENT OBSERVATIONS; not Asolaria-generated spectra",
       "scientific_limits":"NASA Hubble TIFF cannot locate Proxima b/d. RV times span years, not 3^k years.",
       "files":[get_catalog("spec.dat",120,722),get_catalog("photo.dat",43,2212)],
       "image":get_hubble()
    }
    # No JSON payloads or hidden JSON sidecars. Versioned HBP text only.
    def cleaned(value):
        return str(value).replace("|","%7C").replace("\\r"," ").replace("\\n"," ")
    lines=["HBP1|schema=ASOLARIA-REAL-PROXIMA-ORIGINAL-CATALOG-V2|format=HBP|trits=-1,0,+1|json=0",
      "META|catalog="+cleaned(CATALOG)+"|retrieved_utc="+cleaned(manifest["retrieved_utc"])+
       "|bibliography="+cleaned(manifest["bibliography"])+"|raw_observations=UNCHANGED|json=0"]
    for source in manifest["files"]:
        lines.append("SOURCE|"+"|".join(f"{key}={cleaned(source[key])}" for key in
          ("file","dataset","url","size_bytes","logical_records","record_width","sha256"))+"|json=0")
    image=manifest["image"]
    image_keys=("file","encoded_format","sha256","bytes","observation_date_utc","camera","filter","exposure_seconds","source")
    lines.append("IMAGE|available="+("true" if image["available"] else "false")+
      "|"+"|".join(f"{key}={cleaned(image.get(key,''))}" for key in image_keys)+"|json=0")
    lines.append("BOUNDARY|hubble_rendered_image_is_not_calibrated_fits=TRUE|nine_optical_image_epochs=UNAVAILABLE|new_planet_claim=NONE|json=0")
    (BASE/"ORIGINAL-SOURCE-MANIFEST.hbp").write_bytes(("\\n".join(lines)+"\\n").encode("utf-8"))

    for item in manifest["files"]:
        print("AUTHENTIC_SOURCE",item["dataset"],item["logical_records"],item["size_bytes"],"SHA256",item["sha256"],"URL",item["url"])
    print("HUBBLE_IMAGE",manifest["image"])
    print("OBSERVATIONAL_SOURCE_ACQUIRED_PASS")
if __name__=="__main__":main()
