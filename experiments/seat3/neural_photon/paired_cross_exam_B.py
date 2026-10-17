#!/usr/bin/env python3
"""Seat3 post-hoc paired cross-examination of fixed-threshold unseen fixture B.

Descriptive exact error transitions across a deterministic simulation fixture,
NOT inference on independent physical photons, human neurons, or actual light
storage. Recomputes error indicators from individual source-bound sensor rows.
"""
import hashlib,json,re,sys
from collections import Counter
from pathlib import Path
from verify_cross_talk_B import RX, THRESH, SCHEMA

def sha(raw):return hashlib.sha256(raw).hexdigest()

def paired(source_dir):
    folder=Path(source_dir)
    hbp=(folder/"photon-cross-talk-B.hbp").read_bytes()
    summary=json.loads((folder/"photon-cross-talk-B.json").read_bytes())
    assert summary["schema"]==SCHEMA and summary["full_trace_sha256"]==sha(hbp)
    counts={str(n):Counter() for n in (1,3,7)}
    for line in hbp.decode("ascii").splitlines()[1:]:
        m=RX.fullmatch(line)
        assert m is not None
        p=m.groups()
        bit=int(p[3])
        for n,(c_idx,s_idx) in {1:(5,6),3:(9,10),7:(13,14)}.items():
            observed,corrected=int(p[c_idx]),int(p[s_idx])
            raw_bad=int(observed>=5*n)!=bit
            corrected_bad=int(corrected>=THRESH[str(n)])!=bit
            counts[str(n)][(bool(raw_bad),bool(corrected_bad))]+=1
    result={}
    for n,count in counts.items():
        both_ok=count[(False,False)]
        fixed_only=count[(True,False)]
        degraded=count[(False,True)]
        both_wrong=count[(True,True)]
        assert both_ok+fixed_only+degraded+both_wrong==15309
        expected=summary["source_counts_by_exposure"][n]
        assert fixed_only+both_wrong==expected["raw_wrong"]
        assert degraded+both_wrong==expected["corrected_wrong"]
        result[n]={
            "both_correct":both_ok,
            "raw_wrong_corrected_right":fixed_only,
            "raw_right_corrected_wrong":degraded,
            "both_wrong":both_wrong,
            "net_error_reduction":fixed_only-degraded
        }
    return result

def main(input_dir,out):
    source=Path(input_dir)
    output=paired(source)
    payload={
        "verdict":"POSTHOC_PAIRED_CROSSTALK_B_AUDIT_PASS",
        "fixture":"DETERMINISTIC_SIMULATION_B_NOT_PHYSICAL_PHOTON_TRIALS",
        "source_trace_sha256":sha((source/"photon-cross-talk-B.hbp").read_bytes()),
        "comparison":output,
        "new_independent_physical_optical_observations":0,
        "source_bits":15309,
        "thresholds_frozen_before_fixture_B":True,
    }
    body=(json.dumps(payload,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")
    dest=Path(out);dest.mkdir(parents=True,exist_ok=True)
    name="paired-cross-exam-B.json"
    (dest/name).write_bytes(body)
    (dest/(name+".sha256")).write_bytes((sha(body)+"  "+name+"\n").encode("ascii"))
    print(json.dumps(payload,sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: python paired_cross_exam_B.py VERIFIED_B_OUTPUT NEW_OUTPUT")
    main(*sys.argv[1:])
