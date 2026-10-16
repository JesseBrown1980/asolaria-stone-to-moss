#!/usr/bin/env python3
"""Read-only public JWST Alpha Cen source acquisition, save exact originals and HBP.
NASA published composite is PROCESSED; MAST lists raw/calibrated science candidates.
No secrets, cost, model inference, image synthesis, or Git writes.
"""
import pathlib,urllib.request,urllib.parse,json,time,hashlib,os
OUT=pathlib.Path(os.environ.get("SOURCE_OUT","jwst-source"));OUT.mkdir(parents=True,exist_ok=True)
UA="Asolaria-AlphaCen-Public-Source-Audit/1.0"
ASSETS=[
 ("NASA_MIRI_PUBLISHED_5037_JPEG","https://assets.science.nasa.gov/dynamicimage/assets/science/missions/webb/science/2025/08/STScI-01K1EGCCN75KGPW4KSQVRHQ58C.jpg?crop=faces%2Cfocalpoint&fit=clip&h=1800&w=5037","webb_miri_5037_composite.jpg"),
 ("NASA_MIRI_PUBLISHED_UNRESIZED_JPEG","https://assets.science.nasa.gov/dynamicimage/assets/science/missions/webb/science/2025/08/STScI-01K1EGCCN75KGPW4KSQVRHQ58C.jpg","webb_miri_native_composite.jpg"),
 ("ESA_MIRI_PUBLIC_ORIGINAL_TIFF","https://cdn.esawebb.org/archives/images/original/weic2515c.tif","webb_miri_esa_original.tif"),
 ("ESA_MIRI_PUBLIC_LARGE_JPG","https://cdn.esawebb.org/archives/images/large/weic2515c.jpg","webb_miri_esa_large.jpg"),
]
def pull(url,limit=250_000_000):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
 with urllib.request.urlopen(req,timeout=75) as r:
  data=r.read(limit+1)
  if len(data)>limit:raise ValueError("EXCEEDS_LIMIT")
  if not (r.geturl().startswith("https://")):raise ValueError("HTTPS_REQUIRED")
  return data,r.geturl(),r.headers.get("content-type","")
def clean(s):return str(s).replace("|","/").replace("\n"," ").replace("\r"," ")
lines=["HBP1|schema=ASOLARIA-ALPHACEN-WEBB-ORIGINAL-SOURCE-ACQUISITION-V1|source_archive=NASA_STSCI_AND_ESA|json=0",
 "BOUNDARY|original_observation=MIRI_F1550C_PROGRAM_1618|public_relase_image=DERIVED_COMPOSITE|pixels_enhanced=FALSE|planet_confirmed=FALSE|json=0"]
for label,url,name in ASSETS:
 try:
  data,final,ctype=pull(url)
  if data[:3]!=b"\xff\xd8\xff" and data[:4] not in (b"II*\0",b"MM\0*"):raise ValueError("NOT_JPEG_OR_TIFF:"+data[:20].hex())
  (OUT/name).write_bytes(data)
  digest=hashlib.sha256(data).hexdigest()
  lines.append(f"ACQUIRED|label={label}|file={name}|bytes={len(data)}|sha256={digest}|mime={clean(ctype)}|url={clean(final)}|science_pixels=NO_PROCESSED_RELEASE|json=0")
  print("ACQUIRED",label,len(data),digest,flush=True)
 except Exception as e:
  lines.append(f"HELD|label={label}|reason={clean(type(e).__name__+':'+str(e))[:200]}|json=0")
  print("HELD",label,type(e).__name__,str(e)[:170],flush=True)
# MAST filter metadata read-only; do not presume candidate product selection
endpoint="https://mast.stsci.edu/api/v0/invoke"
for proposal in ("1618","6797","9252"):
 req={"service":"Mast.Caom.Filtered","params":{"columns":"obsid,obs_id,proposal_id,target_name,filters,t_min,t_max,obs_collection,instrument_name,dataproduct_type",
  "filters":[{"paramName":"obs_collection","values":["JWST"]},{"paramName":"proposal_id","values":[proposal]}]},
  "format":"json","pagesize":500,"page":1}
 try:
  body=urllib.parse.urlencode({"request":json.dumps(req,separators=(",",":"))}).encode()
  data,final,_=pull(endpoint+"?"+urllib.parse.urlencode({"request":json.dumps(req)}),10_000_000)
  response=json.loads(data)
  if response.get("status")=="ERROR":raise RuntimeError(str(response.get("msg")))
  items=response.get("data",[])
  lines.append(f"MAST_QUERY|proposal={proposal}|rows={len(items)}|json=0")
  for row in items[:40]:
   fields=("obsid","obs_id","proposal_id","target_name","filters","instrument_name","t_min","dataproduct_type")
   lines.append("MAST_OBSERVATION|"+("|".join(k+"="+clean(row.get(k,"")) for k in fields))+"|json=0")
  print("MAST",proposal,len(items),flush=True)
 except Exception as e:
  lines.append(f"MAST_HELD|proposal={proposal}|reason={clean(type(e).__name__+':'+str(e))[:220]}|json=0")
(OUT/"SOURCE-PROVENANCE.hbp").write_text("\n".join(lines)+"\n")
if not any(line.startswith("ACQUIRED") for line in lines):raise SystemExit("NO_PUBLIC_IMAGE_DOWNLOADED")
print("SOURCE_IMAGES_AT_LEAST_ONE_PASS",flush=True)
