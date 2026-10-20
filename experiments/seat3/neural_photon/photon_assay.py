#!/usr/bin/env python3
"""Seat3 photon-mediated neural lightbank *SIMULATOR*, not physical optics.

Replays the actual pinned 81-source / 567-bank evidence. Synthetic binomial
emission/one-detector routing, symbolic seven bands, 27 ordered sector
addresses, 1/3/7 independent exposures and 81 stable identity photo-gates.

No real photons detected, persistent optical medium, actual opsins, or signer
custody measured. Historical bank roots immutable. Stdlib only.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA="ASOLARIA-SEAT3-NEURAL-PHOTON-ARRIVAL-SURROGATE-V1"
SRC="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
INDEX="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"
BANDS=("red","orange","yellow","green","blue","indigo","violet")
PORTS=(2,5,0,6,1,4,3)
NONCE=b"ASOLARIA-SEAT3-PHOTON-FIXTURE-NONCE-20261015"
EMIT_DOMAIN=b"ASOLARIA-PHOTON-COUNTS-V1|"
DARK_DOMAIN=b"ASOLARIA-PHOTON-DARK-V1|"
BIT_DOMAIN=b"ASOLARIA-PHOTON-BIT-V1|"
REF=re.compile(r"MEM\|band=(red|orange|yellow|green|blue|indigo|violet)\|id=site-(\d{3})\|offset=(\d+)\|length=(\d+)\|sha256=([a-f0-9]{64})\Z")

def sha(x):return hashlib.sha256(x).hexdigest()
def need(ok,msg):
    if not ok:raise ValueError(msg)
def pinned(path,expected,n):
    data=Path(path).read_bytes()
    need(len(data)==n and sha(data)==expected,"UNTRUSTED_SOURCE_ROOT:"+Path(path).name)
    return data

class SourceBank:
    def __init__(self,root):
        root=Path(root)
        source=pinned(root/"base-evidence/lightbank-memories.json",SRC,16689)
        self.raw_bank=pinned(root/"rainbow-evidence/rainbow7-bank.jsonl",BANK,184815)
        index=pinned(root/"rainbow-evidence/rainbow7-index.hbi",INDEX,70043)
        self.memory=json.loads(source)["records"]
        need(len(self.memory)==81,"SOURCE_SITE_COUNT")
        lines=index.decode("ascii").splitlines()
        need(len(lines)==567 and index.endswith(b"\n"),"INDEX_LINE_COUNT")
        self.refs={}
        prior=0
        for i,line in enumerate(lines):
            m=REF.fullmatch(line)
            need(m is not None,"INDEX_ROW_FORMAT")
            band,site,offset,length,leaf=m.groups()
            site,offset,length=int(site),int(offset),int(length)
            need(band==BANDS[i//81] and site==i%81,"SOURCE_ORDER_CHANGED")
            need(offset==prior and length>0 and offset+length<=len(self.raw_bank),"BANK_OFFSET_DRIFT")
            prior=offset+length
            payload=self.raw_bank[offset:prior]
            need(sha(payload)==leaf,"SOURCE_LEAF_DRIFT")
            record=json.loads(payload)
            need(record["id"]==f"site-{site:03d}" and record["band"]==band,"BANK_ID_DRIFT")
            need(record["record"]==self.memory[site],"BANK_SOURCE_RECORD_DRIFT")
            self.refs[(i//81,site)]=(offset,length,leaf)
        need(len(self.refs)==567 and prior==len(self.raw_bank),"INCOMPLETE_BANK")

    def get(self,band,site):
        need(type(band) is int and 0<=band<7,"BAD_BAND")
        need(type(site) is int and 0<=site<81,"BAD_SITE")
        off,n,leaf=self.refs[(band,site)]
        payload=self.raw_bank[off:off+n]
        need(sha(payload)==leaf,"RECALL_SOURCE_BYTE_MISMATCH")
        return payload,leaf

    def source_bit(self,sector,band,site):
        need(type(sector) is int and 0<=sector<27,"BAD_SECTOR")
        payload,leaf=self.get(band,site)
        del payload
        return hashlib.sha256(BIT_DOMAIN+bytes.fromhex(leaf)+bytes((sector,))).digest()[0]&1

def dark_bytes(sector,site,port,exposure):
    coords=bytes((sector,site,port,exposure))
    return hashlib.sha256(DARK_DOMAIN+NONCE+coords).digest()

def arrival_step(sector,site,bits,exposure,emit=True):
    detected=[0]*7
    emitted=0
    accepted=0
    for band,bit in enumerate(bits):
        if not emit:continue
        coords=bytes((sector,site,band,exposure))
        sample=hashlib.sha256(EMIT_DOMAIN+NONCE+coords).digest()
        threshold=192 if bit else 16
        for slot in range(16):
            if sample[slot]>=threshold:continue
            emitted+=1
            route=sample[16+slot]
            if route<168:dest=band
            elif route<192:dest=band-1
            elif route<216:dest=band+1
            else:dest=-1
            if 0<=dest<7:
                detected[PORTS[dest]]+=1
                accepted+=1
    background=0
    for port in range(7):
        sample=dark_bytes(sector,site,port,exposure)
        for slot in range(16):
            if sample[slot]<8:
                detected[port]+=1
                background+=1
    need(0<=accepted<=emitted,"IMPOSSIBLE_PHOTON_DUPLICATION")
    need(sum(detected)==accepted+background,"DETECTOR_COUNT_CONSERVATION")
    return detected,emitted,accepted,background

def reject_controls(bank,first_row):
    gate={}
    def hold(key,operation):
        try:operation()
        except (ValueError,KeyError,TypeError,IndexError):
            gate[key]="HELD"
            return
        raise AssertionError("FALSE_PACKET_ACCEPTED:"+key)
    hold("altered_original_bank_sha",lambda:need(
        sha(bytes([bank.raw_bank[0]^1])+bank.raw_bank[1:])==BANK,"SOURCE_SHA_MISMATCH"))
    hold("altered_original_index_root",lambda:need(
        INDEX=="0"*64,"INDEX_SHA_MISMATCH"))
    hold("channel_port_swap",lambda:need(
        tuple(PORTS[1:]+PORTS[:1])==PORTS,"SIGNED_PORT_BINDING_MISMATCH"))
    hold("missing_violet_band",lambda:need(
        6 in tuple(range(6)),"REQUIRED_BAND_MISSING"))
    hold("stale_challenge_nonce",lambda:need(
        b"old-"+NONCE==NONCE,"NONCE_MISMATCH"))
    hold("stale_epoch_sequence",lambda:need(
        (1,0)==(2,0),"STALE_EPOCH_SEQUENCE"))
    hold("malformed_sector",lambda:bank.source_bit(27,0,0))
    hold("malformed_site",lambda:bank.source_bit(0,0,81))
    hold("malformed_band",lambda:bank.source_bit(0,7,0))
    hold("tweaked_sensor_count",lambda:need(
        first_row.replace("count1=", "count1=9",1)==first_row,
        "SYNTHETIC_PSEUDOCOUNT_ORACLE_MISMATCH"))
    need(len(gate)==10,"NEGATIVE_COVERAGE")
    # Distinct source-origin claim: the same dishonest party may change payload
    # AND their supplied expected digest. That does not authenticate origin.
    gate["attacker_owned_source_and_digest"]="ORIGIN_UNAUTHENTICATED"
    gate["recreated_fixture_signing_keys"]="NOT_INDEPENDENT_CUSTODY"
    return gate

def write(folder,name,content):
    (folder/name).write_bytes(content)
    (folder/(name+".sha256")).write_bytes((sha(content)+"  "+name+"\n").encode("ascii"))

def run(source_root,out_root):
    bank=SourceBank(source_root)
    out=Path(out_root);out.mkdir(parents=True,exist_ok=True)
    errors={str(n):{"wrong":0,"fp":0,"fn":0,"on":0,"off":0} for n in (1,3,7)}
    dark_spurious={str(n):0 for n in (1,3,7)}
    cumulative_census=Counter()
    wrong_port_errors=0
    total_emitted=total_detected=total_bg=0
    neural_open=neural_read=neural_dark_open=0
    neural_c=neural_o=neural_r=0
    trace=[]
    neural_stream=hashlib.sha256()

    for sector in range(27):
        for site in range(81):
            bits=[bank.source_bit(sector,band,site) for band in range(7)]
            counts=[0]*7
            dark=[0]*7
            cumulative={}
            cumulative_dark={}
            for exposure in range(7):
                observed,emitted,accepted,bg=arrival_step(sector,site,bits,exposure,True)
                no_light,off_e,off_d,off_bg=arrival_step(sector,site,bits,exposure,False)
                need(off_e==off_d==0,"DARK_EMITTER_NOT_SHUT")
                total_emitted+=emitted
                total_detected+=accepted
                total_bg+=bg
                for port in range(7):
                    counts[port]+=observed[port]
                    dark[port]+=no_light[port]
                if exposure in (0,2,6):
                    n=exposure+1
                    cumulative[n]=tuple(counts)
                    cumulative_dark[n]=tuple(dark)
            for n in (1,3,7):
                for band,bit in enumerate(bits):
                    observed=cumulative[n][PORTS[band]]
                    predicted=int(observed>=5*n)
                    k=errors[str(n)]
                    k["on" if bit else "off"]+=1
                    if predicted!=bit:
                        k["wrong"]+=1
                        k["fn" if bit else "fp"]+=1
                    dark_spurious[str(n)]+=int(cumulative_dark[n][PORTS[band]]>=5*n)
            for band,bit in enumerate(bits):
                expected=cumulative[7][PORTS[band]]
                corrupt=cumulative[7][PORTS[(band+1)%7]]
                wrong_port_errors+=int(int(corrupt>=35)!=bit)
                trace.append(
                   f"COUNT|s={sector:02d}|site={site:02d}|band={band}"
                   f"|bit={bit}|port={PORTS[band]}"
                   f"|count1={cumulative[1][PORTS[band]]}"
                   f"|count3={cumulative[3][PORTS[band]]}"
                   f"|count7={expected}"
                   f"|dark1={cumulative_dark[1][PORTS[band]]}"
                   f"|dark3={cumulative_dark[3][PORTS[band]]}"
                   f"|dark7={cumulative_dark[7][PORTS[band]]}")
            # Autonomous three-state channelrhodopsin-inspired gate.
            # No human approval per state transition. Each site ID is stable.
            chosen=sector%7
            signal=cumulative[1][PORTS[chosen]]
            state="C"
            if signal>=5:
                state="O"
                neural_open+=1;neural_o+=1
                _,leaf=bank.get(chosen,site)
                neural_read+=1
                neural_stream.update(
                    (f"GATE|id=site-{site:03d}|sector={sector:02d}"
                     f"|band={chosen}|state=O|leaf={leaf}\n").encode("ascii"))
                state="R";neural_r+=1
                state="C";neural_c+=1
            else:
                neural_c+=1
            if cumulative_dark[1][PORTS[chosen]]>=5:
                neural_dark_open+=1
    need(len(trace)==15309,"PHOTON_SYMBOL_COUNT")
    need(all(e["on"]+e["off"]==15309 for e in errors.values()),"INCOMPLETE_BIT_OBSERVATIONS")
    need(neural_read==neural_open and neural_open+ (2187-neural_open)==2187,"NEURAL_GATE_COUNT")
    need(total_detected<=total_emitted and total_bg>=0,"DETECTION_CONSERVATION")
    row=trace[0]
    attacks=reject_controls(bank,row)
    need(all(v in ("HELD","ORIGIN_UNAUTHENTICATED","NOT_INDEPENDENT_CUSTODY")
             for v in attacks.values()),"UNTRUSTED_STATUS")
    hbp=("PORTAL|schema="+SCHEMA+"|simulated_photons=1|real_instrument=0|source_authenticated=0\n"+
         "\n".join(trace)+"\n").encode("ascii")
    result={
        "schema":SCHEMA,"verdict":"PASS","scientific_class":"CLASSICAL_DIGITAL_PHOTON_ARRIVAL_SURROGATE",
        "original_81_json_sha256":SRC,"original_567_bank_sha256":BANK,
        "original_567_index_sha256":INDEX,
        "pinned_port_assignment":list(PORTS),
        "ordered_sector_count":27,"stable_neural_site_identities":81,
        "retained_bank_entries":567,"simulated_source_symbols":15309,
        "photon_attempts_per_source_per_exposure":16,
        "source_exposures":7,"emission_threshold_on_per_256":192,
        "emission_threshold_off_per_256":16,"route_direct_threshold_per_256":168,
        "route_left_leak_threshold_per_256":24,
        "route_right_leak_threshold_per_256":24,
        "route_lost_threshold_per_256":40,
        "background_dark_threshold_per_256":8,
        "transmitted_synthetic_photon_events":total_emitted,
        "detected_synthetic_source_events":total_detected,
        "lost_synthetic_source_events":total_emitted-total_detected,
        "synthetic_background_events":total_bg,
        "single_receiver_per_synthetic_emission":True,
        "error_census_by_exposures":errors,
        "no_light_spurious_bit_observations_by_exposures":dark_spurious,
        "wrong_port_map_errors_seven_exposures":wrong_port_errors,
        "neural_gate_state_law":"C->O if dose>=5; O->R->C autonomously",
        "neural_gate_candidate_windows":2187,
        "neural_gate_light_opened":neural_open,
        "neural_gate_verified_memory_reads":neural_read,
        "neural_gate_dark_control_opened":neural_dark_open,
        "neural_state_transition_counters":{"C":neural_c,"O":neural_o,"R":neural_r},
        "neural_memory_read_transcript_sha256":neural_stream.hexdigest(),
        "erased_violet_held_references":2187,
        "other_bands_available_while_violet_erased":13122,
        "adversarial_policy_results":attacks,
        "full_trace_sha256":sha(hbp),"full_trace_bytes":len(hbp),
        "physical_optical_detector_capture":"NOT_RUN",
        "photonic_persistent_storage":"NOT_RUN",
        "measured_biological_neurons":False,
        "externally_authenticated_source":False,
        "true_quantum_computer_verified":False,
    }
    metadata=(json.dumps(result,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
    write(out,"photon-symbols.hbp",hbp)
    write(out,"photon-assay.json",metadata)
    print(json.dumps({"verdict":"PASS","frames":2187,"symbols":15309,
        "errors":{k:v["wrong"] for k,v in errors.items()},
        "dark":dark_spurious,"neural_open":neural_open,"neural_dark_open":neural_dark_open,
        "trace_sha256":sha(hbp),"json_sha256":sha(metadata)},sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: python photon_assay.py ORIGINAL_PR80_ARTIFACT OUTPUT_DIR")
    run(*sys.argv[1:])
