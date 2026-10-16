#!/usr/bin/env python3
"""Download three original STScI MAST WFC3/UVIS F555W FLC exposures.
No JSON science artifacts: transient archive transport is decoded in memory,
while original FITS bytes, canonical SHA sidecars and HBP custody are retained.
"""
from __future__ import annotations
import hashlib,datetime,pathlib,re,sys,time,urllib.parse,urllib.request
from discover_hst import mast
SELECTION=(
  (12985,24810128,"ic3j01a8q","ic3j01a8q_flc.fits",42526080),
  (13466,24812930,"icdc03lzq","icdc03lzq_flc.fits",42341760),
  (13847,24980896,"icpc01xwq","icpc01xwq_flc.fits",42393600),
)
def require(v,msg):
 if not v:raise RuntimeError(msg)
def clean(t):
 return str(t).replace("|","/").replace("\n","_").replace("\r","_")
def header(data,at=0):
 require(at>=0 and at<len(data) and at%2880==0,"FITS_HDU_NOT_2880_ALIGNED")
 h={};cards=0
 while True:
  x=data[at+cards*80:at+(cards+1)*80]
  require(len(x)==80 and x.isascii(),"FITS_MALFORMED_CARD")
  key=x[:8].decode("ascii").strip()
  cards+=1
  if key=="END":break
  if x[8:10]==b"= ":
   val=x[10:].decode("ascii").split("/")[0].strip().strip("'").strip()
   if key in h:
    if key in ("ROOTNAME","PROPOSID","INSTRUME","DETECTOR","FILTER","DATE-OBS","EXPTIME","EXPSTART","NAXIS","BITPIX","EXTNAME","EXTVER"):
     require(h[key]==val,"INCONSISTENT_PROVENANCE_FITS_HEADER:"+key)
   else:
    h[key]=val
  require(cards<=8000,"FITS_HEADER_TOO_LONG")
 header_size=((cards*80+2879)//2880)*2880
 naxis=int(h.get("NAXIS","0"));bitpix=abs(int(h.get("BITPIX","8")))
 n=1 if naxis else 0
 for i in range(1,naxis+1):n*=int(h["NAXIS"+str(i)])
 length=((bitpix//8)*n+int(h.get("PCOUNT","0")))*int(h.get("GCOUNT","1"))
 length=((length+2879)//2880)*2880
 return h,at+header_size,at+header_size+length
def read_sci_head(blob):
 pos=0;primary=None
 for _ in range(16):
  h,first,next_at=header(blob,pos)
  if primary is None:primary=h
  if h.get("EXTNAME")=="SCI" and h.get("EXTVER","1")=="1":
   require(int(h.get("NAXIS","0"))==2 and h.get("BITPIX")=="-32","SCI_NOT_CALIBRATED_FLOAT32")
   require(0<int(h["NAXIS1"])<8192 and 0<int(h["NAXIS2"])<8192,"BAD_FITS_SHAPE")
   require(first<next_at<=len(blob),"SCI_DATA_TRUNCATED")
   return primary,h
  pos=next_at
  require(pos<len(blob),"NO_SCI_IMAGE_HDU")
 raise RuntimeError("NO_SCI_IMAGE_HDU")
def stream_fetch(uri,path,expected):
    url="https://mast.stsci.edu/api/v0.1/Download/file?"+urllib.parse.urlencode({"uri":uri})
    request=urllib.request.Request(url,headers={"User-Agent":"Asolaria-Seat4-hst-raw-provenance/1.0","Accept":"application/fits"})
    errors=[]
    for attempt in range(2):
      try:
       got=0
       with urllib.request.urlopen(request,timeout=110) as resp,open(path,"wb") as f:
        require(resp.geturl().startswith("https://mast.stsci.edu/"),"UNTRUSTED_DOWNLOAD_REDIRECT")
        while True:
         chunk=resp.read(1024*1024)
         if not chunk:break
         got+=len(chunk)
         require(got<=expected,"SOURCE_EXCEEDS_ARCHIVED_PRODUCT_SIZE")
         f.write(chunk)
       require(got==expected,"SOURCE_DOWNLOAD_LENGTH_DISAGREES_ARCHIVE")
       return url
      except Exception as exc:
       errors.append(str(exc)[:200])
       if path.exists():path.unlink()
       if attempt==0:time.sleep(3)
    raise RuntimeError("MAST_FITS_FETCH_FAILED:"+str(errors))
def main(directory):
 dest=pathlib.Path(directory);dest.mkdir(parents=True,exist_ok=True)
 log=["HBP1|schema=ASOLARIA-SEAT4-HST-PROXIMA-THREE-SOURCE-FLC-V1|archive=STSCI_MAST|json=0"]
 dates=set();digest_set=set()
 for idx,(program,obsid,root,name,expected_size) in enumerate(SELECTION):
  matches=mast("Mast.Caom.Products",{"obsid":obsid})
  picked=[p for p in matches if p.get("productFilename")==name
      and str(p.get("productSubGroupDescription"))=="FLC"
      and str(p.get("productType"))=="SCIENCE"
      and int(p.get("size",0))==expected_size
      and str(p.get("dataURI"))=="mast:HST/product/"+name]
  require(len(picked)==1,"ARCHIVE_PRODUCT_PROVENANCE_CHANGED:"+name)
  uri=picked[0]["dataURI"]
  destfile=dest/name
  url=stream_fetch(uri,destfile,expected_size)
  raw=destfile.read_bytes()
  require(raw.startswith(b"SIMPLE  =") and len(raw)%2880==0,"DOWNLOADED_FILE_NOT_FITS")
  primary,sci=read_sci_head(raw)
  require(primary.get("ROOTNAME","").lower()==root,"PRIMARY_ROOTNAME_MISMATCH:"+name)
  require(int(primary.get("PROPOSID","0"))==program,"PRIMARY_PROPOSID_MISMATCH")
  require(primary.get("INSTRUME")=="WFC3","NOT_WFC3")
  require(primary.get("DETECTOR")=="UVIS","NOT_UVIS")
  require(primary.get("FILTER")=="F555W","NOT_PRIMARY_F555W:"+str(primary.get("FILTER")))
  require(primary.get("TARGNAME","").startswith("PROXIMA"),"NONPROXIMA_FITS_TARGET")
  date=primary.get("DATE-OBS","")
  require(bool(re.fullmatch(r"20\d\d-\d\d-\d\d",date)) and date not in dates,"NOT_THREE_DISTINCT_ARCHIVED_OBSERVATION_DATES")
  date_utc=datetime.date.fromisoformat(date)
  require(2012<=date_utc.year<=2018,"MISMATCH_EXPECTED_ARCHIVE_EPOCH")
  dates.add(date)
  require("EXPSTART" in primary and "EXPTIME" in primary,"NO_INSTRUMENT_EXP_TIMING")
  source_sha=hashlib.sha256(raw).hexdigest()
  require(source_sha not in digest_set,"DUPLICATED_SOURCE_EXPOSURE")
  digest_set.add(source_sha)
  (dest/(name+".sha256")).write_bytes((source_sha+"  "+name+"\n").encode("ascii"))
  log.append("SOURCE|"+
   "|".join(f"{k}={clean(v)}" for k,v in [
    ("index",idx),("mission","HST"),("instrument","WFC3_UVIS"),
    ("proposal_id",program),("group_obsid",obsid),("rootname",root),
    ("file",name),("source_uri",uri),
    ("obs_date",date),("obs_time_utc",primary.get("TIME-OBS","NA")),
    ("expstart_mjd",primary["EXPSTART"]),("exptime_seconds",primary["EXPTIME"]),
    ("filter","F555W"),("sci_shape",sci["NAXIS1"]+"x"+sci["NAXIS2"]),
    ("sci_bitpix",sci["BITPIX"]),("bytes",len(raw)),
    ("archive_expected_bytes",expected_size),("sha256",source_sha),
    ("retrieval_host","mast.stsci.edu")
   ])+"|json=0")
  print("HST_ORIGINAL_FITS_SOURCE_VERIFIED",idx,name,date,len(raw),source_sha,flush=True)
 require(len(dates)==3,"INSUFFICIENT_DISTINCT_IMAGE_EPOCHS")
 log.append("BOUNDARY|archive_provenance=STSCI_TLS_AND_MAST_PRODUCT_CATALOG|external_independent_raw_detector_signature=NOT_OBTAINED|sky_astrometric_alignment=NOT_PERFORMED|no_json_outputs=TRUE|json=0")
 text=("\n".join(log)+"\n").encode("ascii")
 (dest/"OPTICAL-SOURCE-MANIFEST.hbp").write_bytes(text)
 (dest/"OPTICAL-SOURCE-MANIFEST.hbp.sha256").write_bytes(
   (hashlib.sha256(text).hexdigest()+"  OPTICAL-SOURCE-MANIFEST.hbp\n").encode("ascii"))
 print("THREE_PUBLIC_STSCI_PROXIMA_F555W_FLC_EXPOSURES_PASS",len(dates),flush=True)
if __name__=="__main__":
 if len(sys.argv)!=2:raise SystemExit("usage: acquire_flc.py OUTPUT_DIR")
 main(sys.argv[1])
