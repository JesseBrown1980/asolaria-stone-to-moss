#!/usr/bin/env python3
"""Seat 1 August-light-bank DIGITAL challenge. No QR image, photons or neural recordings."""
import base64,hashlib,json,sys
from pathlib import Path
S=10**9
SCHEMA="ASOLARIA-SEAT1-AUGUST-LIGHTBANK-PHOTOCYCLE-V1"
COLORS=("R","G","B"); TIMES=("-","0","+"); SPACES=("X","Y","Z")
ARMS=("dark","open_loop","feedback_now","feedback_delay5","feedback_stale25")
CHECKS=(0,7,8,23,24,39,40,55,56,63)
LENGTHS=(436,2536,4636,6736)
def sha(b):return hashlib.sha256(b).hexdigest()
def source(w,i):
    n=LENGTHS[(w+i)%4];out=b"";counter=0
    while len(out)<n:
        out+=hashlib.sha256(f"LIGHTBANK|AUGUST|V1|{w}|{i}|{counter}".encode("ascii")).digest()
        counter+=1
    return out[:n]
def packetize(raw,w,i):
    chunks=[raw[j:j+2100] for j in range(0,len(raw),2100)]
    packets=[{"index":j,"wave":w,"site":i,"group":j//3,"channel":COLORS[j%3],
              "b64":base64.b64encode(j.to_bytes(4,"little")+b).decode("ascii")}
             for j,b in enumerate(chunks)]
    parity=[]
    for group in range((len(chunks)+2)//3):
        lanes=[(j.to_bytes(4,"little")+chunks[j]) if j<len(chunks) else b""
               for j in range(group*3,group*3+3)]
        row=bytearray(max(map(len,lanes)))
        for lane in lanes:
            for j,b in enumerate(lane):row[j]^=b
        parity.append({"group":group,"lengths":[len(x) for x in lanes],
                       "xor_b64":base64.b64encode(row).decode("ascii")})
    return packets,parity,{"wave":w,"site":i,"count":len(chunks),"size":len(raw),"sha":sha(raw)}
def read(packets,parity,manifest,w,i,repair=False):
    if (manifest["wave"],manifest["site"])!=(w,i):raise ValueError("WRONG_SOURCE")
    seen={}
    for pkt in packets:
        idx=pkt["index"]
        if pkt["wave"]!=w or pkt["site"]!=i:raise ValueError("WRONG_SOURCE")
        if not isinstance(idx,int) or idx<0 or idx>=manifest["count"] or idx in seen:
            raise ValueError("INVALID_OR_DUPLICATE_INDEX")
        if pkt["channel"]!=COLORS[idx%3] or pkt["group"]!=idx//3:raise ValueError("WRONG_RGB_LANE")
        try:raw=base64.b64decode(pkt["b64"],validate=True)
        except Exception as exc:raise ValueError("INVALID_BASE64") from exc
        if len(raw)<4 or int.from_bytes(raw[:4],"little")!=idx:raise ValueError("HEADER_BAD")
        seen[idx]=raw
    missing=[idx for idx in range(manifest["count"]) if idx not in seen]
    if missing:
        if len(missing)!=1 or not repair:raise ValueError("ERASURE")
        idx=missing[0];group=idx//3
        p=parity[group]
        if p["group"]!=group:raise ValueError("WRONG_PARITY")
        row=bytearray(base64.b64decode(p["xor_b64"],validate=True))
        for k in range(group*3,group*3+3):
            if k==idx or k>=manifest["count"]:continue
            if k not in seen:raise ValueError("DOUBLE_ERASURE")
            for n,b in enumerate(seen[k]):row[n]^=b
        recovered=bytes(row[:p["lengths"][idx%3]])
        if len(recovered)<4 or int.from_bytes(recovered[:4],"little")!=idx:
            raise ValueError("BAD_PARITY")
        seen[idx]=recovered
    if len(seen)!=manifest["count"]:raise ValueError("MISSING_CHUNK")
    result=b"".join(seen[k][4:] for k in range(manifest["count"]))
    if len(result)!=manifest["size"] or sha(result)!=manifest["sha"]:raise ValueError("SHA_BAD")
    return result
def mm(x):
    sm=sum(x)
    return tuple(3*t-sm for t in x)
def projector():
    count=0; rows=[]
    for w in range(27):
        x=(w%3,(w//3)%3,(w//9)%3)
        y=mm(x);ground=sum(x)
        assert sum(y)==0
        assert mm(y)==tuple(3*t for t in y)
        assert all((y[i]+ground)%3==0 and (y[i]+ground)//3==x[i] for i in range(3))
        assert mm(tuple(t+5 for t in x))==y and tuple(t+5 for t in x)!=x
        rows.append(f"PROJECTOR|w={w}|x={','.join(map(str,x))}|y={','.join(map(str,y))}|ground={ground}|noninvertible_without_ground=1")
        count+=1
    return rows,count
def prob(r):return S*r*20//(1_000_000+r*20)
PA=prob(800);PB=prob(450);PG=prob(120)
def step(state,light):
    c,o,r=state
    if min(state)<0 or c+o+r!=S:raise ValueError("NONCONSERVATIVE_STATE")
    co=c*(PA if light else 0)//S;orr=o*PB//S;rc=r*PG//S
    result=(c-co+rc,o+co-orr,r+orr-rc)
    if min(result)<0 or sum(result)!=S:raise ValueError("NONCONSERVATIVE_STEP")
    return result
def simulate():
    rows=[f"MODEL|schema={SCHEMA}|waves=27|sites=81|arms=5|ticks=64|chunk=2100|qr_image_pixels=0|photons_measured=0"]
    proj,pc=projector();rows.extend(proj)
    stats={a:{"lit":0,"switches":0,"gate_pass":0,"gate_hold":0,"error":0} for a in ARMS}
    frames=memory=0;root=hashlib.sha256();census={"T":0,"A":0,"R":0}
    for w in range(27):
        census[("T","A","R")[w%3]]+=1
        for i in range(81):
            raw=source(w,i);packets,parity,manifest=packetize(raw,w,i)
            assert read(list(reversed(packets)),parity,manifest,w,i)==raw
            root.update(bytes.fromhex(manifest["sha"]))
            ident=f"site-{i:03d}"
            for arm in ARMS:
                state=(S,0,0);hist=[];last=0
                for tick in range(64):
                    c,o,r=state
                    enabled=(8<=tick<24 or 40<=tick<56)
                    if arm=="dark":light=0
                    elif arm=="open_loop":light=int(enabled)
                    elif arm=="feedback_now":light=int(enabled and o<100_000_000)
                    else:
                        lag=5 if arm=="feedback_delay5" else 25
                        obs=hist[tick-lag] if tick>=lag else 0
                        light=int(enabled and obs<100_000_000)
                    hist.append(o)
                    stats[arm]["lit"]+=light
                    stats[arm]["switches"]+=(light!=last)
                    last=light
                    state=step(state,light)
                    stats[arm]["error"]+=abs(state[1]-(100_000_000 if enabled else 0))
                    if tick in CHECKS:
                        c,o,r=state
                        current=-(120000*o//S)
                        rows.append(f"FRAME|w={w}|id={ident}|arm={arm}|tick={tick}|C={c}|O={o}|R={r}|I_millipA={current}")
                        frames+=1
                gate="PASS" if state[1]>=50_000_000 else "HOLD"
                stats[arm]["gate_pass" if gate=="PASS" else "gate_hold"]+=1
                rows.append(f"MEMORY|w={w}|id={ident}|arm={arm}|chunks={manifest['count']}|bytes={manifest['size']}|sha={manifest['sha']}|gate={gate}")
                memory+=1
    assert census=={"T":9,"A":9,"R":9}
    assert frames==109350 and memory==10935 and pc==27
    rows.append("CENSUS|T=9|A=9|R=9|tritsum=0|digitally_classified=1")
    rows.append("END|frames=109350|memory=10935|projector=27|hardware_readbacks=0")
    trace=("\n".join(rows)+"\n").encode("ascii")
    report={"schema":SCHEMA,"status":"PASS","trace_sha256":sha(trace),"trace_bytes":len(trace),
            "source_sha256_root":root.hexdigest(),"frames":frames,"memory_rows":memory,
            "projector_cases":pc,"optical_hardware":False,"qr_pixel_codec":False,
            "biology_measured":False,"metrics":stats}
    return trace,report
def main():
    if len(sys.argv)!=3:raise SystemExit("usage: python lightbank_python.py output.hbp output.json")
    trace,report=simulate()
    Path(sys.argv[1]).write_bytes(trace)
    Path(sys.argv[2]).write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","sha256":report["trace_sha256"],"frames":report["frames"],
                      "memory":report["memory_rows"],"projector":report["projector_cases"]},sort_keys=True))
if __name__=="__main__":main()
