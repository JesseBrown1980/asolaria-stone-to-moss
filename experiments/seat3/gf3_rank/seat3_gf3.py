#!/usr/bin/env python3
"""Seat3 independent GF(3) Rust81 rank & fast-forward falsifier. HBP only."""
from __future__ import annotations
from pathlib import Path
import hashlib,sys
N=81
TAPS=((0,1,3),(0,4,7))
HORIZONS=(0,1,3,9,27,81,82)
PR_SOURCE="5303c9b2ed0c0ce33da684706d57caef516ffd2b"
PR_LIB_BLOB="0a26e3d24ac0b0211c31c3aa32e23d50d7d0c3ec"
def require(cond,msg):
    if not cond:raise AssertionError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def step(state,taps):
    return tuple(sum(state[(i-t)%N] for t in taps)%3 for i in range(N))
def advance(state,taps,n):
    for _ in range(n):state=step(state,taps)
    return state
def basis():return [tuple(1 if i==j else 0 for i in range(N)) for j in range(N)]
def gauss(matrix):
    m=[list(row) for row in matrix]
    pivot=0
    for col in range(N):
        choose=next((r for r in range(pivot,N) if m[r][col]),None)
        if choose is None:continue
        m[pivot],m[choose]=m[choose],m[pivot]
        if m[pivot][col]==2:
            m[pivot]=[(2*v)%3 for v in m[pivot]]
        for r in range(N):
            if r!=pivot and m[r][col]:
                factor=m[r][col]
                m[r]=[(u-factor*v)%3 for u,v in zip(m[r],m[pivot])]
        pivot+=1
        if pivot==N:break
    return pivot
def apply(cols,state):
    out=[0]*N
    for j,v in enumerate(state):
        if not v:continue
        for i in range(N):out[i]=(out[i]+v*cols[j][i])%3
    return tuple(out)
def product(a,b):
    return [apply(a,col) for col in b]
def jump(state,taps,horizon):
    M=[step(vec,taps) for vec in basis()]
    squarings=selected=0
    n=horizon
    while n:
        if n&1:
            state=apply(M,state);selected+=1
        n//=2
        if n:
            M=product(M,M);squarings+=1
    return state,squarings,selected
def valuation(taps):
    degree=max(taps)
    p=[0]*(degree+1)
    for k in taps:p[k]=(p[k]+1)%3
    count=0
    while len(p)>1:
        q=[0]*(len(p)-1)
        q[-1]=p[-1]
        for i in range(len(q)-2,-1,-1):q[i]=(p[i+1]+q[i+1])%3
        remainder=(p[0]+q[0])%3
        if remainder:break
        p=q;count+=1
    return count
def hash_state(x,h,taps):
    raw=(b"ASOLARIA-C3-ORIGINAL-RUST181-GF3|"+
         bytes(taps)+h.to_bytes(8,"little")+bytes(x))
    return sha(raw)
def _fmt_taps(x):return "".join(str(t) for t in x)
def main(outdir):
    rows=["HBP1|schema=ASOLARIA-C3-GF3-ORIGINAL81-MATRIX-RANK-V1|field=GF3|trits=-1,0,+1|Rust_source_commit="+PR_SOURCE+"|Rust_lib_blob="+PR_LIB_BLOB+"|json=0",
          "BOUNDARY|logical_time_not_host_clock=TRUE|original_trained_GNN_weights=NOT_LOADED|quantum_photonic_neural_memory=NOT_PROVEN|existing_reported_physical_experiment=PRESERVED|json=0"]
    vectors=basis()
    selected=[vectors[0],vectors[13],vectors[80],
              tuple((i*7+2)%3 for i in range(N)),
              tuple(i%3 for i in range(N))]
    for taps in TAPS:
        v=valuation(taps)
        require(v==1,"POLYNOMIAL_MULTIPLICITY_NOT_ONE")
        history=[list(vec) for vec in vectors]
        prev=0
        for h in HORIZONS:
            for j in range(N):
                for _ in range(h-prev):
                    history[j]=list(step(history[j],taps))
            prev=h
            matrix=[[history[col][row] for col in range(N)] for row in range(N)]
            measured=gauss(matrix)
            expected=N-min(v*h,N)
            require(measured==expected,f"GF3_RANK_MISMATCH:{taps}:{h}:{measured}:{expected}")
            for seed in selected:
                direct=advance(seed,taps,h)
                fast,sq,mul=jump(seed,taps,h)
                require(direct==fast,f"NON_EQUIVALENT_SHORTCUT:{taps}:{h}")
                require(fast==apply(history,seed),"GF3_BASIS_NOT_SAME_POWER")
                require((fast==(0,)*N)==(h>=81 or seed==(0,)*N or all(c==0 for c in direct)),
                        "IMPOSSIBLE_NILPOTENT_REPORT")
            if h>=81:
                require(all(col==(0,)*N for col in history),"81_STEPS_NOT_ZERO_ALL_BASIS")
            s=selected[0]
            final=advance(s,taps,h)
            rows.append(
                f"RANK|taps={_fmt_taps(taps)}|logical_ticks={h}|rank={measured}|nullity={N-measured}"
                f"|theoretical_rank={expected}|poly_valuation={v}|81_basis_reconstructed=PASS"
                f"|matrix_vs_stepwise=PASS|sha256={hash_state(final,h,taps)}|json=0")
        require(step((1,)*N,taps)==step((0,)*N,taps)==(0,)*N,"CONSTANT_COLLISION_WITNESS_MISSING")
        require(all(advance(x,taps,81)==(0,)*N for x in selected),"MISSING_81_NILPOTENCE")
        rows.append(f"COLLISION|taps={_fmt_taps(taps)}|zero_vs_all_ones_after_tick1=SAME_ZERO|kernel_after_27=3^27|kernel_after_81=3^81"
                    "|underlying_source_history_reconstructible_from_surface_only=FALSE|separate_history_required=TRUE|json=0")
    early=17;late=23
    first,second=TAPS
    mismatch=0
    for source in vectors:
        right=advance(advance(source,first,early),second,late)
        shortcut=jump(jump(source,first,early)[0],second,late)[0]
        wrong=jump(source,first,early+late)[0]
        require(shortcut==right,"LAW_AWARE_MATRIX_WRONG")
        mismatch+=int(wrong!=right)
    require(mismatch>0,"LAW_SWITCH_STALE_FALSE_GREEN")
    rows.append(f"LAW_SWITCH|early_law=013|early_ticks={early}|late_law=047|late_ticks={late}"
                f"|basis_checked=81|stale_same_law_fail_count={mismatch}|law_aware_composition=PASS|json=0")
    # A forged hash or source tap cannot substitute a proved state.
    s=selected[0]
    genuine=jump(s,(0,1,3),27)[0]
    fake=jump(s,(0,1,4),27)[0]
    require(genuine!=fake,"ALTERED_TAPS_FAKE_DID_NOT_CHANGE_RESULT")
    require(hash_state(genuine,27,(0,1,3))!=hash_state(fake,27,(0,1,4)),"CORRUPTED_HASH_ACCEPTED")
    rows.append("NEGATIVES|forged_taps_014=REJECTED|forged_final_hash=REJECTED|deleted_original_history_cannot_be_rebuilt=TRUE|json=0")
    body=("\n".join(rows)+"\n").encode("ascii")
    target=Path(outdir);target.mkdir(parents=True,exist_ok=True)
    fn="seat3-gf3-rank-certificate.hbp"
    (target/fn).write_bytes(body)
    (target/(fn+".sha256")).write_bytes((sha(body)+"  "+fn+"\n").encode("ascii"))
    print("SEAT3_C3_GF3_81_RANK_PROOF_PASS",len(rows),"records",sha(body),"stale",mismatch)
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python seat3_gf3.py OUT")
    main(sys.argv[1])
