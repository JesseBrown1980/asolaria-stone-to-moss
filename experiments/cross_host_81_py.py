#!/usr/bin/env python3
"""Cross-host Asolaria 81 SHA portal: independent Python CPU implementation."""
import hashlib
import json
import os
import platform
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

TAG="ASOLARIA-81-CROSS-HOST-PORTAL-V1"
FIELDS=("HBI","HBP","SHA","SH","HASH")

def H(*parts):
    h=hashlib.sha256()
    for part in parts:
        encoded=str(part).encode("utf-8")
        h.update(len(encoded).to_bytes(8,"big"))
        h.update(encoded)
    return h.hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def build(challenge):
    nonce=challenge["nonce"]
    assert challenge["protocol"]==TAG
    assert len(nonce)==32 and all(c in "0123456789abcdef" for c in nonce)
    targets=challenge["targets"]
    scales=challenge["scales"]
    assert targets==[0,1,2,3,9,13,17,25,26]
    assert scales==[1,1000000,1000000000]
    ids=[H("ASOLARIA|ID|HOST-CROSS-V1",i,i//3,i%3) for i in range(27)]
    state=[H("ASOLARIA|BODY|STATE0",item) for item in ids]
    assert len(set(ids))==27
    def root(states):
        return H("ASOLARIA|SOURCE-ROOT",*states)
    def derived(states):
        r=root(states)
        body=[]
        for item in ids:
            for d in (-1,0,1):
                body.append([H("ASOLARIA|CELL|"+name,r,item,d) for name in FIELDS])
        all_hash=H("ASOLARIA|81-CELL-ROOT",*(x for row in body for x in row))
        return r,body,all_hash
    source0,cells0,total0=derived(state)
    rows=[
       "PORTAL|schema="+TAG+"|challenge="+nonce+"|json=0",
       "BASE|source="+source0+"|cells_root="+total0+"|count=81|json=0"
    ]
    for idx,target in enumerate(targets):
        changed=list(state)
        changed[target]=H("ASOLARIA|MUTATION",state[target],nonce,target)
        source,body,total=derived(changed)
        diff=sum(x!=y for old,new in zip(cells0,body)
                 for x,y in zip(old,new))
        modified=sum(a!=b for a,b in zip(cells0,body))
        assert diff==405 and modified==81
        assert source!=source0 and total!=total0
        for scale in scales:
            rows.append(
              f"WAVE|id={idx*3+scales.index(scale)}|leaf={target}|scale={scale}"
              f"|source={source}|root={total}|cell_changes={modified}"
              f"|register_changes={diff}|local_change=1|json=0"
            )
    rows.append("END|waves=27|bodies=81|changes_per_wave=405|json=0")
    return "\n".join(rows)+"\n"

def main():
    ch=Path(sys.argv[1])
    out=Path(sys.argv[2])
    out.mkdir(parents=True,exist_ok=True)
    challenge=json.loads(ch.read_text(encoding="utf-8"))
    started=now()
    body=build(challenge).encode("utf-8")
    (out/"results.hbp").write_bytes(body)
    fingerprint=hashlib.sha256(body).hexdigest()
    metadata={
       "schema":TAG,"source_implementation":"independent_Python_stdlib",
       "lang":"python","runtime":sys.version.split()[0],
       "os":os.environ.get("RUNNER_OS",platform.system()),
       "runner_name":os.environ.get("RUNNER_NAME",socket.gethostname()),
       "hostname":socket.gethostname(),
       "architecture":platform.machine(),"started_utc":started,
       "ended_utc":now(),"run_id":os.environ.get("GITHUB_RUN_ID","local"),
       "git_sha":os.environ.get("GITHUB_SHA",""),
       "challenge_sha256":hashlib.sha256(ch.read_bytes()).hexdigest(),
       "result_sha256":fingerprint,"body_count":81,"wave_count":27,
       "evidence_class":"public GitHub hosted runner or explicitly described local host; software hashes only"
    }
    (out/"host.json").write_text(json.dumps(metadata,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"result_sha256":fingerprint,"waves":27,"runner":metadata["runner_name"],
                      "os":metadata["os"]},sort_keys=True))

if __name__=="__main__":
    main()
