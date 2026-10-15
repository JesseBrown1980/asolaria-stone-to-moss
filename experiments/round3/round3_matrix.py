#!/usr/bin/env python3
"""Round3 exploratory digital memory model; NOT real optical storage."""
import hashlib
import json
import struct
from pathlib import Path

N=81
EPOCHS=27
SCALE=1024
MODELS=("3state","4state")
LIGHT=("dark","pulse","steady")
ATTACKS=("honest","bit_flip","stale","forged")
PREFIX=b"ASOLARIA-R3-MEMORY-V1|synthetic|"

def sha(b):
    return hashlib.sha256(b).hexdigest()

def payload(address,wave):
    key=PREFIX+struct.pack("<II",address,wave)
    return struct.pack("<II",address,wave)+b"".join(
        hashlib.sha256(key+bytes([i])).digest() for i in range(4)
    )

def projection_tests():
    pass_count=0
    not_injective_count=0
    for a in range(N):
        for b in range(EPOCHS):
            v=((5*a+b)%240,(11*a+3*b)%240,(7*a+9*b)%240)
            s=sum(v)
            q=tuple(3*x-s for x in v)
            assert sum(q)==0
            assert tuple((x+s)//3 for x in q)==v
            assert all((x+s)%3==0 for x in q)
            shifted=tuple(x+1 for x in v)
            assert tuple(3*x-sum(shifted) for x in shifted)==q
            assert tuple((x+s+3)//3 for x in q)==shifted
            pass_count+=1
            not_injective_count+=1
    return {"reconstruction_with_sideband":pass_count,
            "same_projection_different_source":not_injective_count}

def gate_simulation(model,light):
    state=[SCALE,0,0] if model=="3state" else [SCALE,0,0,0]
    peak=0
    for tick in range(24):
        lit=light=="steady" or (light=="pulse" and tick%4==0)
        if model=="3state":
            c,o,r=state
            a=c//4 if lit else 0
            b=o//16
            g=r//32
            state=[c-a+g,o+a-b,r+b-g]
            opened=state[1]
        else:
            c,o1,o2,r=state
            a=c//4 if lit else 0
            b=o1//8
            d=o2//16
            g=r//32
            state=[c-a+g,o1+a-b,o2+b-d,r+d-g]
            opened=state[1]+state[2]
        assert min(state)>=0 and sum(state)==SCALE
        peak=max(peak,opened)
    return peak>0,peak

def main():
    bank={(a,w):payload(a,w) for a in range(N) for w in range(EPOCHS)}
    hashes={k:sha(v) for k,v in bank.items()}
    source=sha(PREFIX+b"fixed-truth-schedule")
    accepted=held=wrong=0
    by_condition={}
    for model in MODELS:
        for light in LIGHT:
            enabled,peak=gate_simulation(model,light)
            count=0
            for a in range(N):
                for w in range(EPOCHS):
                    original=bank[a,w]
                    for attack in ATTACKS:
                        report=original
                        origin=source
                        if attack=="bit_flip":
                            report=bytes([original[0]^1])+original[1:]
                        elif attack=="stale":
                            report=bank[a,(w-1)%EPOCHS]
                        elif attack=="forged":
                            origin=sha(b"forged-untrusted-source")
                        verified=(enabled and origin==source and
                                  report==original and sha(report)==hashes[a,w])
                        expected=(enabled and attack=="honest")
                        wrong+=int(verified!=expected)
                        accepted+=int(verified)
                        held+=int(not verified)
                        count+=1
            by_condition[f"{model}:{light}"]={
                "trial_count":count,"peak_synthetic_open":peak,"mass":SCALE}
    projection=projection_tests()
    result={"schema":"ASOLARIA-R3-LIGHTBANK-DIGITAL-MATRIX-V1",
            "status":"PASS" if wrong==0 else "FAIL",
            "classification":"EXPLORATORY_DIGITAL_MODEL_NOT_MEASURED_PHYSICAL_LIGHT",
            "cases":N*EPOCHS*len(MODELS)*len(LIGHT)*len(ATTACKS),
            "accepted":accepted,"held":held,"unexpected":wrong,
            "projection":projection,"gate_conditions":by_condition,
            "real_photons":False,"physical_storage":False,
            "cryptographically_attested_host":False,
            "biologically_calibrated_rates":False}
    assert result["cases"]==52488 and accepted==8748 and held==43740
    assert wrong==0 and projection["reconstruction_with_sideband"]==2187
    path=Path("round3-matrix-results.json")
    path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"cases":result["cases"],
                      "accepted":accepted,"held":held,"unexpected":wrong,
                      "receipt_sha256":sha(path.read_bytes())},sort_keys=True))

if __name__=="__main__":
    main()
