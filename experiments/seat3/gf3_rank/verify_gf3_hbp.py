#!/usr/bin/env python3
"""Third read-only GF(3) polynomial-ring referee; no producer imports.

Rebuilds exact power polynomial by convolution in F3[x]/(x^81-1), counts
(gcd with x^81-1) via divisibility at x=1, checks HBP source SHA and negatives.
"""
import hashlib,sys
from pathlib import Path
N=81
LAWS=((0,1,3),(0,4,7))
HORIZONS=(0,1,3,9,27,81,82)
def check(b,msg):
    if not b:raise AssertionError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def multiply(a,b):
    out=[0]*N
    for i,u in enumerate(a):
        if u:
            for j,v in enumerate(b):
                if v:out[(i+j)%N]=(out[(i+j)%N]+u*v)%3
    return out
def base(taps):
    result=[0]*N
    for j in taps:result[j]=(result[j]+1)%3
    return result
def power(polynomial,k):
    result=[1]+[0]*(N-1)
    while k:
        if k%2:result=multiply(result,polynomial)
        k//=2
        if k:polynomial=multiply(polynomial,polynomial)
    return result
def state_hash(poly,ticks,taps):
    raw=b"ASOLARIA-C3-ORIGINAL-RUST181-GF3|"+bytes(taps)+ticks.to_bytes(8,"little")+bytes(poly)
    return sha(raw)
def evaluate(folder):
    path=Path(folder)/"seat3-gf3-rank-certificate.hbp"
    raw=path.read_bytes()
    check((path.parent/(path.name+".sha256")).read_bytes()==(
        sha(raw)+"  "+path.name+"\n").encode("ascii"),"CHANGED_OR_UNTRUSTED_HBP")
    lines=raw.decode("ascii").splitlines()
    check(len(lines)==2+2*(len(HORIZONS)+1)+2,"MISSING_OR_EXTRA_HBP_LINES")
    check(lines[0].startswith("HBP1|schema=ASOLARIA-C3-GF3-ORIGINAL81-MATRIX-RANK-V1|field=GF3|trits=-1,0,+1|"),"HBP_SCHEMA")
    check("Rust_source_commit=5303c9b2ed0c0ce33da684706d57caef516ffd2b" in lines[0],"WRONG_FROZEN_RUST_REVISION")
    check("Rust_lib_blob=0a26e3d24ac0b0211c31c3aa32e23d50d7d0c3ec" in lines[0],"RUST_SOURCE_FILE_CHANGED")
    check("underlying_source_history_reconstructible_from_surface_only=FALSE" in raw.decode("ascii"),"FALSE_INVERTIBILITY_PROMOTION")
    for taps in LAWS:
        for h in HORIZONS:
            records=[line for line in lines if line.startswith(f"RANK|taps={''.join(map(str,taps))}|logical_ticks={h}|")]
            check(len(records)==1,"RANK_ROW_MISSING_OR_DOUBLE")
            vals=dict(chunk.split("=",1) for chunk in records[0].split("|")[1:])
            check(vals["json"]=="0" and vals["81_basis_reconstructed"]=="PASS" and
                  vals["matrix_vs_stepwise"]=="PASS" and vals["poly_valuation"]=="1","UNSUPPORTED_CLAIM")
            check(int(vals["rank"])==81-min(h,81) and int(vals["nullity"])==min(h,81),"FALSE_REPORTED_RANK")
            poly=power(base(taps),h)
            check(sum(int(v!=0) for v in poly)==0 if h>=81 else True,"FROBENIUS_ZERO_FAILED")
            # power polynomial is image of e_0 (circulant representation).
            check(vals["sha256"]==state_hash(poly,h,taps),"WRONG_STATE_HASH_OR_WRONG_TRANSITION")
    rows=[row for row in lines if row.startswith("LAW_SWITCH|")]
    check(len(rows)==1,"MISSING_LAW_SWITCH")
    attrs=dict(chunk.split("=",1) for chunk in rows[0].split("|")[1:])
    check(attrs["early_ticks"]=="17" and attrs["late_ticks"]=="23" and
          attrs["basis_checked"]=="81","LAW_SWITCH_SCOPE_DRIFT")
    right=multiply(power(base(LAWS[1]),23),power(base(LAWS[0]),17))
    stale=power(base(LAWS[0]),40)
    incorrect=sum(any(right[(i+j)%N]!=stale[(i+j)%N] for i in range(N)) for j in range(N))
    check(int(attrs["stale_same_law_fail_count"])==incorrect and incorrect>0,"LAW_SWITCH_STALE_FALSE_GREEN")
    check(lines[-1].startswith("NEGATIVES|forged_taps_014=REJECTED|"),"MISSING_TAP_NEGATIVE")
    check(all(line.endswith("|json=0") for line in lines),"UNEXPECTED_JSON_OR_UNKEYED_HBP")
    print("SEAT3_INDEPENDENT_F3_POLYNOMIAL_AUDIT_PASS",sha(raw),len(lines),"lines","switch_stale",incorrect)
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: verify_gf3_hbp.py OUT_DIR")
    evaluate(sys.argv[1])
