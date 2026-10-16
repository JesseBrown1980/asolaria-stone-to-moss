#!/usr/bin/env python3
"""Independent Python HST original source-to-HBI/HBP pixel reconciliation.
No JSON objects/files. All reported sky movement interpretations remain HELD
until proper WCS/PSF sky alignment, not inferred from raw pixel differences.
"""
from __future__ import annotations
import hashlib,sys
from pathlib import Path
SRC=[
 ("ic3j01a8q",12985,20121001,"cc8d0afe69943b5aec7e678a75ac84341138d6343e092a7ab99b276006ab541c"),
 ("icdc03lzq",13466,20140401,"fd8563aaabf0530f3dc5a1ee837c1759493f3015335f85cc36a11d4005217ad0"),
 ("icpc01xwq",13847,20150416,"68a2633f54141cb0d55f1d8a35bbcca20654163a97c75ad408a3169e8e50fc67"),
]
FRAMESIZE=877
WIDTH=756
PACKED=38
def sha(b):return hashlib.sha256(b).hexdigest()
def guard(condition,msg):
 if not condition:raise AssertionError(msg)
def cards(blob,start):
 guard(start%2880==0,"HDU_UNALIGNED")
 info={}
 i=0
 while True:
  p=blob[start+i*80:start+(i+1)*80]
  guard(len(p)==80 and p.isascii(),"INVALID_FITS_CARD")
  key=p[:8].decode("ascii").strip()
  i+=1
  if key=="END":break
  if p[8:10]==b"= ":
   tail=p[10:].decode("ascii").strip()
   val=(tail[1:].split("'")[0] if tail.startswith("'")
       else tail.split("/")[0].strip())
   if key not in info:info[key]=val
  guard(i<=8000,"HDU_TOO_MANY_CARDS")
 start_data=start+((i*80+2879)//2880)*2880
 ndim=int(info["NAXIS"])
 size=0
 if ndim:
  size=abs(int(info["BITPIX"]))//8
  for n in range(1,ndim+1):size*=int(info["NAXIS"+str(n)])
 pcount=int(info.get("PCOUNT",0));gcount=int(info.get("GCOUNT",1))
 if ndim:size=(size+pcount)*gcount
 end=start_data+((size+2879)//2880)*2880
 guard(end<=len(blob),"UNRECOVERABLE_TRUNCATED_FITS")
 return info,start_data,end
def source_science(raw):
 pos=0;parent=None
 for _ in range(16):
  card,base,after=cards(raw,pos)
  if parent is None:parent=card
  if card.get("EXTNAME")=="SCI" and card.get("EXTVER","1")=="1":
   guard(card["BITPIX"]=="-32" and card["NAXIS"]=="2","UNEXPECTED_FITS_SCI")
   return parent,card,base
  pos=after
 raise AssertionError("MISSING_SCI_HDU")
def trits(source):
 return [int.from_bytes(source[i*4:i*4+4],"big")%3-1 for i in range(189)]
def pack(values):
 out=[]
 for i in range(0,189,5):
  digits=values[i:i+5]
  while len(digits)<5:digits.append(0)
  out.append(sum((d+1)*3**j for j,d in enumerate(digits)))
 return bytes(out)
def parse_hbp(data):
 guard(data.startswith(b"HBP1|") and data.endswith(b"\n"),"HBP_NONCANONICAL")
 rows=[]
 for line in data.decode("ascii").splitlines():
  parts=line.split("|")
  guard(parts[-1]=="json=0","JSON_FORBIDDEN_OR_INCORRECT_HBP")
  vals={}
  for p in parts[1:]:
   guard("=" in p,"HBP_MISSING_EQUALS")
   key,val=p.split("=",1)
   guard(key not in vals and key and val,"DUPLICATE_OR_EMPTY_HBP_FIELD")
   vals[key]=val
  rows.append((parts[0],vals))
 return rows
def witness(wire,exposures):
 guard(len(wire)==2639 and wire[:8]==b"HBI1\x01\x03\x07\x1b","INVALID_HBI_HEADER_OR_LENGTH")
 observations=[]
 for i,(root,program,date,blob,primary,sci,base) in enumerate(exposures):
  block=wire[8+i*FRAMESIZE:8+(i+1)*FRAMESIZE]
  guard(block[:9]==root.encode("ascii"),"FALSIFIED_HST_ROOTNAME")
  guard(int.from_bytes(block[9:11],"little")==program,"FALSIFIED_PROPOSAL")
  guard(int.from_bytes(block[11:15],"little")==date,"FALSIFIED_DATE")
  w=int(sci["NAXIS1"]);h=int(sci["NAXIS2"])
  guard(int.from_bytes(block[15:17],"little")==w and
        int.from_bytes(block[17:19],"little")==h,"FALSIFIED_PIXEL_SHAPE")
  digest=hashlib.sha256(blob).digest()
  guard(block[19:51]==digest,"FITS_SHA_ROOT_CHANGED")
  sample=bytearray()
  for lane in range(7):
   for site in range(27):
    x=(lane+1)*w//8;y=(site+1)*h//28
    sourcepos=base+(y*w+x)*4
    sample.extend(blob[sourcepos:sourcepos+4])
  guard(block[51:807]==sample,"DERIVED_SCI_IMAGE_BYTES_MISMATCH")
  tritpack=pack(trits(sample))
  guard(block[807:845]==tritpack,"NONCANONICAL_GF3_TRIT_SOURCE")
  sh=hashlib.sha256(b"SHV1"+digest+date.to_bytes(4,"little")+sample).digest()
  guard(block[845:877]==sh,"UNVERIFIED_SH_WITNESS")
  observations.append((date,trits(sample),sha(sample),sh.hex()))
 guard(len(set(x[0] for x in observations))==3 and
       observations[0][0]<observations[1][0]<observations[2][0],"NOT_INDEPENDENT_CHRONOLOGICAL_EPOCHS")
 return observations
def main(origin,output):
 exposures=[]
 for root,proposal,date,wantsha in SRC:
  fits=origin/(root+"_flc.fits")
  raw=fits.read_bytes()
  guard(sha(raw)==wantsha,"PINNED_MAST_FITS_ORIGIN_CHANGED:"+root)
  guard((origin/(fits.name+".sha256")).read_bytes()==
        (wantsha+"  "+fits.name+"\n").encode("ascii"),"ARCHIVED_SOURCE_SHA_SIDECAR_CHANGED")
  primary,sci,data=source_science(raw)
  guard(primary["ROOTNAME"].lower()==root and
        int(primary["PROPOSID"])==proposal and
        int(primary["DATE-OBS"].replace("-",""))==date and
        primary["FILTER"]=="F555W" and primary["DETECTOR"]=="UVIS" and
        primary["INSTRUME"]=="WFC3" and
        primary["TARGNAME"].startswith("PROXIMA"),"UNTRUSTED_SOURCE_IDENTITY")
  exposures.append((root,proposal,date,raw,primary,sci,data))
 hbi_name="three-original-proxima-optical-epochs.hbi"
 hbp_name="three-original-proxima-optical-epochs.hbp"
 hbi=(output/hbi_name).read_bytes();hbp=(output/hbp_name).read_bytes()
 for name,bytes in [(hbi_name,hbi),(hbp_name,hbp)]:
  guard((output/(name+".sha256")).read_bytes()==
        (sha(bytes)+"  "+name+"\n").encode("ascii"),"MALFORMED_SHA_SIDECAR")
 seen=witness(hbi,exposures)
 parsed=parse_hbp(hbp)
 guard(parsed[0][1]["schema"]=="SEAT4-HST-PROXIMA-THREE-ACTUAL-OPTICAL-IMAGES-R14","WRONG_EVIDENCE_SCHEMA")
 metas=[row for tag,row in parsed if tag=="FRAME"]
 guard(len(metas)==3,"BAD_HBP_FRAMES")
 for i,row in enumerate(metas):
  guard(int(row["index"])==i and row["rootname"]==SRC[i][0]
        and int(row["date_yyyymmdd"])==seen[i][0]
        and row["original_full_fits_sha256"]==SRC[i][3]
        and row["sample_words_sha256"]==seen[i][2]
        and row["SH_shadow_sha256"]==seen[i][3],"HBP_AND_HBI_DO_NOT_AGREE")
 changes=[sum(a!=b for a,b in zip(seen[i][1],seen[i+1][1])) for i in (0,1)]
 reports=[item for tag,item in parsed if tag=="DIFFERENCE"]
 guard(len(reports)==2 and
       all(int(reports[i]["changed_ternary_detector_samples"])==changes[i] for i in (0,1)),"FALSE_DIFFERENCE_COUNT")
 guard(any(tag=="FALSIFY" and item["rejected_corruptions"]=="9" for tag,item in parsed),"RUST_HOSTILE_TESTS_NOT_REPORTED")
 # Actual mutations to original HBI bytes with independent source readback.
 mutations=[8,17,19,27,8+51,8+807,8+845,8+FRAMESIZE+11]
 for index,addr in enumerate(mutations):
  bad=bytearray(hbi);bad[addr]^=1
  try:witness(bytes(bad),exposures)
  except AssertionError:pass
  else:raise AssertionError("PYTHON_CORRUPTION_WENT_UNDETECTED:"+str(index))
 for sample in changes:guard(0<sample<=189,"NO_DIFFERING_SOURCE_DETECTOR_SAMPLES")
 print("SEAT4_R14_INDEPENDENT_ORIGINAL_HST_FITS_REPLAY_PASS",
       "real_f555w_dates="+",".join(str(v[0]) for v in seen),
       "changed_ternary_samples="+",".join(map(str,changes)),
       "python_mutations_rejected="+str(len(mutations)),
       "HBI_SHA256="+sha(hbi),"HBP_SHA256="+sha(hbp))
if __name__=="__main__":
 if len(sys.argv)!=3:raise SystemExit("usage: independent_hst_referee.py RAW_FITS_DIR OUTPUT_DIR")
 main(Path(sys.argv[1]),Path(sys.argv[2]))
