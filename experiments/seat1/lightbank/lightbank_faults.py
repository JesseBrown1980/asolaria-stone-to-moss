#!/usr/bin/env python3
"""Real executed mutations of the August *digital* memory experiment."""
import base64,copy,json
import lightbank_python as L

def reject(fn):
    try:fn()
    except (ValueError,AssertionError):return True
    return False

def run():
    results={"plain_single_lane_erasure_rejected":0,"parity_single_lane_recovered":0,
        "two_erasure_rejected":0,"bitflip_rejected":0,"foreign_source_rejected":0,
        "nonconserved_state_rejected":0,"filler_is_not_payload":0,
        "forgery_source_trust_held":0,"projector_ground_noninvertible":0}
    for w in range(27):
        i=(3-w)%4
        raw=L.source(w,i)
        entries,parity,manifest=L.packetize(raw,w,i)
        assert len(entries)==4,("negative control requires four chunks",w,i)
        omit=w%3
        remaining=[x for x in entries if x["index"]!=omit]
        assert reject(lambda:L.read(remaining,parity,manifest,w,i))
        results["plain_single_lane_erasure_rejected"]+=1
        assert L.read(remaining,parity,manifest,w,i,repair=True)==raw
        results["parity_single_lane_recovered"]+=1
        twice=[x for x in entries if x["index"] not in (0,1)]
        assert reject(lambda:L.read(twice,parity,manifest,w,i,repair=True))
        results["two_erasure_rejected"]+=1
        corrupted=copy.deepcopy(entries)
        pkt=corrupted[0]
        body=bytearray(base64.b64decode(pkt["b64"]))
        body[4]^=1
        pkt["b64"]=base64.b64encode(body).decode("ascii")
        assert reject(lambda:L.read(corrupted,parity,manifest,w,i))
        results["bitflip_rejected"]+=1
        from_other=copy.deepcopy(entries)
        from_other[0]["wave"]=(w+1)%27
        assert reject(lambda:L.read(from_other,parity,manifest,w,i))
        results["foreign_source_rejected"]+=1
        assert reject(lambda:L.step((L.S+1,0,0),1))
        results["nonconserved_state_rejected"]+=1
        # Four real packets; pretending the first one is padding is an erasure.
        assert reject(lambda:L.read(entries[1:],parity,manifest,w,i))
        results["filler_is_not_payload"]+=1
        # A coherent adversary who can also change the trusted manifest wins.
        forged=bytearray(raw);forged[0]^=1
        p,m,Lm=L.packetize(bytes(forged),w,i)
        assert L.read(p,m,Lm,w,i)==bytes(forged)
        results["forgery_source_trust_held"]+=1
        vec=(w%3,(w//3)%3,(w//9)%3)
        assert L.mm(vec)==L.mm(tuple(z+5 for z in vec))
        results["projector_ground_noninvertible"]+=1
    assert set(results.values())=={27},results
    report={"status":"PASS","seats":"Seat 1 software only","cases_per_control":27,
        "results":results,"physical_light_evidence":False,
        "coherent_source_watcher_forgery":"EXTERNAL_TRUST_HELD"}
    print(json.dumps(report,sort_keys=True))
if __name__=="__main__":run()
