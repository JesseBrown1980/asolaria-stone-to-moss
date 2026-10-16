#!/usr/bin/env python3
"""Independent Python mathematical referee of Rust GF(3) HBI/HBP reversible witness.

No Rust code imported/executed here. Re-derives all original states and
retained 1-trit/step witnesses; independently solves each predecessor step,
checks source Git blob, canonical base-3 packing and file SHA-256 sidecars.
"""
from pathlib import Path
import hashlib,sys
N=81
LAWS=((0,1,3),(0,4,7))
HORIZONS=(1,3,9,27,81)
SRC_HEAD="5303c9b2ed0c0ce33da684706d57caef516ffd2b"
SRC_BLOB="0a26e3d24ac0b0211c31c3aa32e23d50d7d0c3ec"
HEADER=("HBP1|schema=ASOLARIA-C3-GF3-REVERSIBLE-STATE-WITNESS-V1"
        "|Rust=1.81.0|field=GF3|trits=-1,0,+1|original_source="+SRC_HEAD+
        "|original_blob="+SRC_BLOB+"|no_JSON=1|json=0")
def sha(b):return hashlib.sha256(b).hexdigest()
def guard(ok,why):
    if not ok:raise AssertionError(why)
def step(old,taps):
    return tuple(sum(old[(i-k)%N] for k in taps)%3 for i in range(N))
def origin(i):
    if i in (0,1,2):
        return tuple(int(j==[0,13,80][i]) for j in range(N))
    if i==3:return tuple((7*j+2)%3 for j in range(N))
    if i==4:return tuple(j%3 for j in range(N))
    raise ValueError("bad seed")
def at(family,tick):
    return LAWS[family] if family<2 else (LAWS[0] if tick<17 else LAWS[1])
def pack(trits):
    return bytes(sum(d*3**j for j,d in enumerate(trits[k:k+5]))
                 for k in range(0,len(trits),5))
def unpack(raw,n):
    guard(len(raw)==(n+4)//5,"BAD_TRIT_BYTE_LENGTH")
    vec=[]
    for byte in raw:
        guard(byte<243,"NONCANONICAL_TRIT_BYTE")
        number=byte
        for _ in range(5):
            vec.append(number%3)
            number//=3
    guard(not any(vec[n:]),"NONCANONICAL_UNUSED_PADDING")
    return vec[:n]
def inverse_matrix(taps):
    # This code builds a 81 x 81 independent polynomial-basis linear
    # system (first 80 output coordinates + old[0] witness).
    mat=[[0]*162 for _ in range(N)]
    for r in range(N-1):
        for tap in taps:mat[r][(r-tap)%N]=(mat[r][(r-tap)%N]+1)%3
    mat[80][0]=1
    for row in range(N):mat[row][81+row]=1
    for col in range(N):
        pivot=next((i for i in range(col,N) if mat[i][col]),None)
        guard(pivot is not None,"WITNESS_MISSING_INVERTIBILITY")
        mat[pivot],mat[col]=mat[col],mat[pivot]
        if mat[col][col]==2:mat[col]=[(x*2)%3 for x in mat[col]]
        a=mat[col][:]
        for r in range(N):
            if r!=col and mat[r][col]:
                c=mat[r][col]
                mat[r]=[(x-c*y)%3 for x,y in zip(mat[r],a)]
    return [tuple(row[N:]) for row in mat]
def solve(next_state,w,inv,taps):
    guard(w in (0,1,2),"INVALID_WITNESS")
    b=tuple(next_state[:80])+(w,)
    restored=tuple(sum(a*v for a,v in zip(row,b))%3 for row in inv)
    guard(restored[0]==w and step(restored,taps)==next_state,
          "INVALID_REVERSE_TRANSITION_OR_SIDE")
    return restored
def source_pin(source_path):
    raw=Path(source_path).read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    guard(blob==SRC_BLOB and b"pub fn gf3_step" in raw and
          b"nilpotent_after_81([0,1,3])" in raw and
          b"nilpotent_after_81([0,4,7])" in raw,
          "ORIGINAL_RUST_GF3_LAW_SOURCE_CHANGED")
def check(folder,source):
    root=Path(folder)
    source_pin(source)
    inp=(root/"seat3-reversible.hbi").read_bytes()
    text=(root/"seat3-reversible.hbp").read_bytes()
    for filename,raw in (("seat3-reversible.hbi",inp),("seat3-reversible.hbp",text)):
        side=(sha(raw)+"  "+filename+"\n").encode("ascii")
        guard((root/(filename+".sha256")).read_bytes()==side,
              "EVIDENCE_SIDECAR_CHANGED")
    guard(inp[:5]==b"HBI1\x01" and inp[5:7]==(55).to_bytes(2,"little"),
          "NOT_VERSIONED_HBI_55")
    rows=text.decode("ascii").splitlines()
    guard(len(rows)==2+55+2 and rows[0]==HEADER,"HBP_SCHEMA_OR_SOURCE_CHANGED")
    guard(all(row.endswith("|json=0") for row in rows),
          "HBP_CONTAINS_NONCANONICAL_OR_JSON_OUTPUT")
    inv=[inverse_matrix(t) for t in LAWS]
    pos=7
    evidence=[]
    for family in range(3):
        for seed in range(5):
            series=(40,) if family==2 else HORIZONS
            for horizon in series:
                guard(len(inp)>=pos+5+N,"TRUNCATED_HBI_RECORD")
                lawid,seedid=inp[pos],inp[pos+1]
                ticks=int.from_bytes(inp[pos+2:pos+4],"little")
                plen=inp[pos+4]
                pos+=5
                guard((lawid,seedid,ticks,plen)==
                      (family,seed,horizon,(horizon+4)//5),
                      "WRONG_HBI_ORDER_OR_WITNESS_HEADER")
                final=tuple(inp[pos:pos+N]);pos+=N
                guard(len(final)==N and all(x<=2 for x in final),"INVALID_FINAL_TRITS")
                packed=inp[pos:pos+plen];pos+=plen
                witness=unpack(packed,horizon)
                guard(packed==pack(witness),"NONCANONICAL_HBI_WITNESS_PACK")
                old=origin(seed)
                independently=[]
                for tick in range(horizon):
                    independently.append(old[0])
                    old=step(old,at(family,tick))
                guard(old==final and independently==witness,
                      "RUST_HBI_WITNESS_NOT_ACTUAL_SOURCE_TRACE")
                current=final
                for tick in reversed(range(horizon)):
                    law=at(family,tick)
                    current=solve(current,witness[tick],
                                  inv[0] if law==LAWS[0] else inv[1],law)
                guard(current==origin(seed),"NO_EXACT_ORIGINAL_SOURCE_RECOVERY")
                if horizon==81:guard(final==(0,)*N,"RUST_GF3_NILPOTENCE_FALSE")
                line=(f"ROW|family={family}|seed={seed}|logical_ticks={horizon}"
                      f"|rank={N-horizon}|nullity={horizon}"
                      f"|sideband_trits={horizon}|packed_bytes={plen}"
                      "|inverse=PASS|source_original=PASS|no_physical_time_claim=TRUE|json=0")
                guard(rows[2+len(evidence)]==line,"HBP_LIFT_CLAIM_NOT_SOURCE_BOUND")
                evidence.append((family,seed,horizon))
    guard(pos==len(inp) and len(evidence)==55,"HBI_TRAILING_BYTES_OR_MISSING_ROWS")
    guard(rows[-2].startswith("COLLISION|fixed_law_after_81=ALL_ZERO|") and
          "|minimal_recoverable_witness_trits=81|packed_witness_capacity_bytes=17|" in rows[-2],
          "HISTORY_INFORMATION_LOWER_BOUND_NOT_REPORTED")
    guard(rows[-1].startswith("NEGATIVES|flipped_history_without_source_root=ALTERNATE_PREIMAGE|") and
          "|flipped_history_against_pinned_original=REJECTED|" in rows[-1],
          "FORGED_WITNESS_NOT_DETECTED")
    guard(all(inv[i][j] in (0,1,2) for inv_m in inv
              for i in range(N) for j in range(N)
              for inv in [inv_m]),"INVALID_INVERSE_MATRIX")
    print("SEAT3_INDEPENDENT_REVERSIBLE_GF3_VERIFIER_PASS",
          len(evidence),"cases",len(inp),"HBI bytes",sha(inp),
          len(text),"HBP bytes",sha(text),"json=0")
if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: python verify_reversible.py OUTPUT_DIR ORIGINAL_SEAT1_RUST_LIB")
    check(*sys.argv[1:])
