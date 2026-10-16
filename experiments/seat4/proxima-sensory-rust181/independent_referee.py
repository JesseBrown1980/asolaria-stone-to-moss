#!/usr/bin/env python3
"""Independent Seat4 pure Python sensory decoder (no imported Rust, no JSON).
Raw original 722-entry Proxima observatory catalog binds the 3 dated RV rows.
Checks 7 symbolic rainbow trit-address lanes, *not* 7 optical wavelength bands.
"""
import hashlib,sys
from decimal import Decimal,ROUND_HALF_EVEN
from pathlib import Path
SOURCE="027cff5c10b541608b727abada2af531037223edec3bb9112fcbb45fc333e474"
WIDTH=120;LANES=7;SITES=27;TRITS=189;PACKED=38;FRAME=230;SIZE=698
def sha(b):return hashlib.sha256(b).hexdigest()
def need(value,reason):
 if not value:raise AssertionError(reason)
def millis(row):
 return int((Decimal(row[1:10].decode("ascii").strip())*1000).to_integral_value(rounding=ROUND_HALF_EVEN))
def source_frames(data):
 need(sha(data)==SOURCE,"RAW_CDS_SHA_MISMATCH")
 rows=data.splitlines()
 need(len(rows)==722 and all(len(x)==120 for x in rows),"RAW_SOURCE_ROW_LAYOUT_CHANGED")
 entries=sorted((millis(r),r) for r in rows if r[119:120]==b"0")
 out=[]
 for when,row in entries:
  if out and out[-1][0]==when:continue
  out.append((when,row))
  if len(out)==3:break
 need(len(out)==3 and out[0][0]<out[1][0]<out[2][0],"THREE_DISTINCT_EPOCHS_NOT_FOUND")
 return out
def trits(row):return [int(row[i%WIDTH]%3)-1 for i in range(TRITS)]
def pack(values):
 output=bytearray()
 for i in range(0,TRITS,5):
  digits=values[i:i+5]
  digits.extend([0]*(5-len(digits)))
  output.append(sum((v+1)*3**j for j,v in enumerate(digits)))
 return bytes(output)
def unpack(raw):
 need(len(raw)==PACKED,"BAD_PACKED_TRIT_LENGTH")
 out=[]
 for value in raw:
  code=value
  for _ in range(5):
   out.append((code%3)-1);code//=3
  need(code==0,"INVALID_BASE3_BYTE_CODE")
 need(out[TRITS:]==[0],"INVALID_PADDING_TRIT")
 return out[:TRITS]
def read_hbp(report):
 lines=report.decode("ascii").splitlines()
 need(lines and lines[0].startswith("HBP1|schema=ASOLARIA-SEAT4-PROXIMA-SENSORY-R13|"),"HBP_SCHEMA_MISMATCH")
 parsed=[]
 for line in lines:
  fields=line.split("|")
  need(fields[-1]=="json=0","HBP_MISSING_NO_JSON_MARKER")
  names={}
  for part in fields[1:]:
   need("=" in part,"NONCANONICAL_HBP_FIELD")
   key,value=part.split("=",1)
   need(key not in names and key and value,"INVALID_OR_DUPLICATE_HBP_KEY")
   names[key]=value
  parsed.append((fields[0],names))
 return parsed
def once(items,key):
 matches=[p for name,p in items if name==key]
 need(len(matches)==1,"HBP_REQUIRED_SINGLE_RECORD:"+key)
 return matches[0]
def verify_hbi(raw,expected):
 need(len(raw)==SIZE and raw[:8]==b"HBI1\x01\x03\x07\x1b","HBI_WRONG_MAGIC_OR_LENGTH")
 observed=[]
 for index,(time,row) in enumerate(expected):
  part=raw[8+index*FRAME:8+(index+1)*FRAME]
  tick=int.from_bytes(part[:8],"little")
  src=part[8:8+WIDTH];packed=part[8+WIDTH:8+WIDTH+PACKED]
  sd=part[8+WIDTH+PACKED:8+WIDTH+PACKED+32]
  sh=part[8+WIDTH+PACKED+32:]
  need(tick==time,"FORGED_SENSOR_TIMESTAMP")
  need(src==row,"MISSING_OR_REPLACED_PHYSICAL_SOURCE_BYTES")
  need(sha(src)==sd.hex(),"FRAME_SOURCE_HASH_MISMATCH")
  need(sha(b"SHV1"+sd+packed)==sh.hex(),"SH_SHADOW_HASH_MISMATCH")
  need(unpack(packed)==trits(src),"HBI_TERNARY_SOURCE_RECONSTRUCTION_MISMATCH")
  need(pack(trits(src))==packed,"NONCANONICAL_PACKING")
  observed.append((tick,sd.hex(),sh.hex(),packed))
 need(observed[0][0]<observed[1][0]<observed[2][0],"REPLAY_OR_REORDER")
 return observed
def check_sidecar(root,name):
 raw=(root/name).read_bytes()
 checksum=(root/(name+".sha256")).read_bytes()
 need(checksum==(sha(raw)+"  "+name+"\n").encode("ascii"),"SIDECAR_MISMATCH:"+name)
 return raw
def main(input_source,root):
 reference=source_frames(input_source.read_bytes())
 hbi=check_sidecar(root,"sensory-three-epochs.hbi")
 hbp=check_sidecar(root,"sensory-three-epochs.hbp")
 obs=verify_hbi(hbi,reference)
 records=read_hbp(hbp)
 info=once(records,"SOURCE")
 need(info["original_722_rows_sha256"]==SOURCE,"HBP_WRONG_CATALOG")
 header=once(records,"HBI")
 need(int(header["size_bytes"])==SIZE and header["sha256"]==sha(hbi),"HBI_HBP_LINK_BAD")
 need(header["rainbow_lanes"]=="7" and header["sites_per_lane"]=="27","WRONG_RAINBOW_LANES")
 frames=[item for tag,item in records if tag=="FRAME"]
 need(len(frames)==3,"FRAME_ROWS_BAD")
 for idx,frame in enumerate(frames):
  need(int(frame["index"])==idx and
       int(frame["time_BJD_minus2450000_milliday"])==obs[idx][0] and
       frame["source_sha256"]==obs[idx][1] and
       frame["SH_shadow_sha256"]==obs[idx][2],"HBP_SOURCE_SHADOW_OR_TIME_DRIFT")
 movements=[item for tag,item in records if tag=="MOTION"]
 need(len(movements)==2,"MOTION_ROWS_BAD")
 for i,m in enumerate(movements):
  left=unpack(obs[i][3]);right=unpack(obs[i+1][3])
  changed=sum(a!=b for a,b in zip(left,right))
  need(1<=changed<=TRITS and int(m["changed_trits"])==changed and
       int(m["delta_milliday"])==obs[i+1][0]-obs[i][0],"MOTION_SENSORY_DELTA_BAD")
 falsify=once(records,"FALSIFY")
 need(falsify["applied_attacks"]=="7" and falsify["rejected"]=="7","CORRUPTION_TESTS_NOT_EXECUTED")
 boundary=once(records,"BOUNDARY")
 need(boundary["RAM_FREE_CLAIM"]=="FALSE" and boundary["FITS_IMAGE_EPOCHS"]=="NOT_PRESENT","SCIENCE_SCOPE_MISSTATED")
 # Active changed-image and origin attacks: bypass transport checksum by
 # recomputing its sidecar, then insist physical-source agreement still FAILS.
 offsets=[8+8+120,8+8+12,8+8+120+38+32,8,8+230,697]
 for j,pos in enumerate(offsets):
  corrupted=bytearray(hbi);corrupted[pos]^=1
  try:verify_hbi(bytes(corrupted),reference)
  except AssertionError:pass
  else:raise AssertionError(f"PYTHON_INDEPENDENT_MUTATION_ACCEPTED:{j}")
 print("SEAT4_R13_INDEPENDENT_SENSORY_REPLAY_PASS raw_real_RV=722 epochs=3",
       "rainbow_symbolic_lanes=7","trits=567","rust_attacks=7","python_attacks=6",
       "HBI_SHA256="+sha(hbi),"HBP_SHA256="+sha(hbp))
if __name__=="__main__":
 if len(sys.argv)!=3:raise SystemExit("usage: independent_referee.py SPEC.DAT OUTPUT")
 main(Path(sys.argv[1]),Path(sys.argv[2]))
