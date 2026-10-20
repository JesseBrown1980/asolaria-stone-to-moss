#!/usr/bin/env python3
"""Third-seat read-only audit of source-anchored photon-surrogate evidence.

No import of Python/Node producers. Reconstructs all original 567 entries and
source-bit/root proofs; computes BER, dark controls, crosstalk and gate causality
from every newly emitted 15,309 optical-symbol row. The counts are SIMULATED.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA="ASOLARIA-SEAT3-NEURAL-PHOTON-ARRIVAL-SURROGATE-V1"
SOURCE="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
INDEX="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"
PORTS=(2,5,0,6,1,4,3)
BIT_DOMAIN=b"ASOLARIA-PHOTON-BIT-V1|"
RECORD=re.compile(r"COUNT\|s=(\d{2})\|site=(\d{2})\|band=(\d)\|bit=([01])\|port=(\d)\|count1=(\d+)\|count3=(\d+)\|count7=(\d+)\|dark1=(\d+)\|dark3=(\d+)\|dark7=(\d+)\Z")
INDEX_RE=re.compile(r"MEM\|band=(red|orange|yellow|green|blue|indigo|violet)\|id=site-(\d{3})\|offset=(\d+)\|length=(\d+)\|sha256=([0-9a-f]{64})\Z")
NAMES=("red","orange","yellow","green","blue","indigo","violet")

def sha(raw):return hashlib.sha256(raw).hexdigest()
def check(ok,why):
    if not ok:raise ValueError(why)

def original_source_bank(root):
    root=Path(root)
    paths=[root/"base-evidence/lightbank-memories.json",
           root/"rainbow-evidence/rainbow7-bank.jsonl",
           root/"rainbow-evidence/rainbow7-index.hbi"]
    expected=[(SOURCE,16689),(BANK,184815),(INDEX,70043)]
    data=[]
    for p,(h,n) in zip(paths,expected):
        b=p.read_bytes()
        check(len(b)==n and sha(b)==h,"ORIGINAL_SOURCE_NOT_PINNED")
        data.append(b)
    source,bank,index=data
    originals=json.loads(source)["records"]
    check(len(originals)==81,"SOURCE_SITE_COUNT")
    lines=index.decode("ascii").splitlines()
    check(len(lines)==567 and index.endswith(b"\n"),"ORIGINAL_INDEX_COUNT")
    references={}
    prior=0
    for i,line in enumerate(lines):
        m=INDEX_RE.fullmatch(line)
        check(m is not None,"ORIGINAL_REF_FORMAT")
        band,site,off,n,leaf=m.groups()
        site,off,n=int(site),int(off),int(n)
        check(band==NAMES[i//81] and site==i%81,"ORIGINAL_REF_ORDER")
        check(off==prior and n>0 and off+n<=len(bank),"ORIGINAL_REF_OVERLAP")
        prior=off+n
        part=bank[off:prior]
        check(sha(part)==leaf,"ORIGINAL_LEAF_SHA")
        obj=json.loads(part)
        check(obj["record"]==originals[site],"ORIGINAL_RECORD_IDENTITY")
        references[(i//81,site)]=(leaf,part)
    check(prior==len(bank) and len(references)==567,"SOURCE_BYTES_INCOMPLETE")
    return references

def audit(original_dir,python_out,node_out,output):
    refs=original_source_bank(original_dir)
    py,js=Path(python_out),Path(node_out)
    filenames=("photon-symbols.hbp","photon-assay.json")
    for name in filenames:
        a=(py/name).read_bytes()
        b=(js/name).read_bytes()
        check(a==b,"INDEPENDENT_PY_NODE_BYTE_MISMATCH:"+name)
        for src in (py,js):
            side=(src/(name+".sha256")).read_bytes()
            check(side==(sha(a)+"  "+name+"\n").encode("ascii"),"SOURCE_RECEIPT_SHA_DRIFT")
    hbp=(py/filenames[0]).read_bytes()
    metadata=(py/filenames[1]).read_bytes()
    m=json.loads(metadata)
    check(m["schema"]==SCHEMA and m["verdict"]=="PASS","SCHEMA_VERDICT_MISMATCH")
    check(m["scientific_class"]=="CLASSICAL_DIGITAL_PHOTON_ARRIVAL_SURROGATE","IMPROPER_PHYSICAL_PROMOTION")
    check(m["original_81_json_sha256"]==SOURCE and m["original_567_bank_sha256"]==BANK and m["original_567_index_sha256"]==INDEX,"BANK_ROOT_DRIFT")
    check(m["pinned_port_assignment"]==list(PORTS),"UNTRUSTED_CHANNEL_MAP")
    check(m["ordered_sector_count"]==27 and m["stable_neural_site_identities"]==81,"IDENTITY_LOSS")
    check(m["retained_bank_entries"]==567 and m["simulated_source_symbols"]==15309,"MISSING_SYMBOLS")
    check(m["full_trace_sha256"]==sha(hbp) and m["full_trace_bytes"]==len(hbp),"TRACE_ROOT_MISMATCH")
    for n,val in (("photon_attempts_per_source_per_exposure",16),("source_exposures",7),
                  ("route_direct_threshold_per_256",168),("route_left_leak_threshold_per_256",24),
                  ("route_right_leak_threshold_per_256",24),("route_lost_threshold_per_256",40),
                  ("emission_threshold_on_per_256",192),("emission_threshold_off_per_256",16),
                  ("background_dark_threshold_per_256",8)):
        check(m[n]==val,"MODEL_FROZEN_PARAMETER_DRIFT:"+n)
    check(m["single_receiver_per_synthetic_emission"] is True,"PHOTON_DOUBLE_DETECTION")
    check(m["detected_synthetic_source_events"]+
          m["lost_synthetic_source_events"]==
          m["transmitted_synthetic_photon_events"],"PHOTON_CONSERVATION")
    check(m["erased_violet_held_references"]==2187 and
          m["other_bands_available_while_violet_erased"]==13122,"ERASURE_MISREPORT")
    check(m["physical_optical_detector_capture"]=="NOT_RUN" and
          m["photonic_persistent_storage"]=="NOT_RUN","PHYSICAL_SENSOR_ABSENT")
    check(m["measured_biological_neurons"] is False and
          m["externally_authenticated_source"] is False and
          m["true_quantum_computer_verified"] is False,"UNSUPPORTED_PHYSICAL_CLAIM")

    rows=hbp.decode("ascii").splitlines()
    check(hbp.endswith(b"\n") and len(rows)==15310,"HBP_RECORD_COUNT")
    check(rows[0]=="PORTAL|schema="+SCHEMA+"|simulated_photons=1|real_instrument=0|source_authenticated=0","HBP_SIMULATED_GATE")
    errors={str(n):{"wrong":0,"fp":0,"fn":0,"on":0,"off":0} for n in (1,3,7)}
    dark_spurious={"1":0,"3":0,"7":0}
    wrong_map=0
    opened=0;dark_opened=0
    neural_hash=hashlib.sha256()
    for group in range(2187):
        sector=group//81;site=group%81
        frame=[]
        for band in range(7):
            idx=group*7+band
            mat=RECORD.fullmatch(rows[idx+1])
            check(mat is not None,"CAPTURE_ROW_MALFORMED")
            s,loc,ch,bit,port,c1,c3,c7,d1,d3,d7=map(int,mat.groups())
            check((s,loc,ch,port)==(sector,site,band,PORTS[band]),"CAPTURE_BAND_IDENTITY_DRIFT")
            leaf,_=refs[(band,site)]
            expect=hashlib.sha256(BIT_DOMAIN+bytes.fromhex(leaf)+bytes((sector,))).digest()[0]&1
            check(bit==expect,"WRONG_SOURCE_DERIVED_BIT")
            check(0<=c1<=c3<=c7 and 0<=d1<=d3<=d7,"NEGATIVE_OR_NONMONOTONE_COUNT")
            for n,c,d in ((1,c1,d1),(3,c3,d3),(7,c7,d7)):
                stat=errors[str(n)]
                stat["on" if bit else "off"]+=1
                decoded=int(c>=5*n)
                if decoded!=bit:
                    stat["wrong"]+=1
                    stat["fn" if bit else "fp"]+=1
                dark_spurious[str(n)]+=int(d>=5*n)
            frame.append((bit,c1,c3,c7,d1,d3,d7))
        for band,(bit,_,_,_,_,_,_) in enumerate(frame):
            physical_port=PORTS[(band+1)%7]
            wrong_band=PORTS.index(physical_port)
            wrong_map+=int(int(frame[wrong_band][3]>=35)!=bit)
        selected=sector%7
        if frame[selected][1]>=5:
            opened+=1
            leaf,_=refs[(selected,site)]
            neural_hash.update((f"GATE|id=site-{site:03d}|sector={sector:02d}"
                                f"|band={selected}|state=O|leaf={leaf}\n").encode("ascii"))
        if frame[selected][4]>=5:dark_opened+=1

    check(errors==m["error_census_by_exposures"],"BER_ASSERTIONS_NOT_REPRODUCED")
    check(dark_spurious==m["no_light_spurious_bit_observations_by_exposures"],"DARK_CONTROL_NOT_REPRODUCED")
    check(wrong_map==m["wrong_port_map_errors_seven_exposures"],"CROSSTALK_MAP_NOT_REPRODUCED")
    check(m["neural_gate_candidate_windows"]==2187 and
          m["neural_gate_light_opened"]==opened and
          m["neural_gate_verified_memory_reads"]==opened and
          m["neural_gate_dark_control_opened"]==dark_opened,"NEURAL_SOURCE_ID_GATE_MISMATCH")
    check(m["neural_memory_read_transcript_sha256"]==neural_hash.hexdigest(),"NEURAL_READ_TRACE_DRIFT")
    check(m["neural_state_transition_counters"]=={"C":2187,"O":opened,"R":opened},"OPTO_CYCLE_DRIFT")
    atk=m["adversarial_policy_results"]
    check(sum(v=="HELD" for v in atk.values())==10,"NOT_ENOUGH_ACTUAL_NEGATIVES")
    check(atk["attacker_owned_source_and_digest"]=="ORIGIN_UNAUTHENTICATED" and
          atk["recreated_fixture_signing_keys"]=="NOT_INDEPENDENT_CUSTODY","FRAUDULENT_SOURCE_STATUS")
    dest=Path(output);dest.mkdir(parents=True,exist_ok=True)
    for name in filenames:
        blob=(py/name).read_bytes()
        (dest/name).write_bytes(blob)
        (dest/(name+".sha256")).write_bytes((sha(blob)+"  "+name+"\n").encode("ascii"))
    summary={
       "status":"INDEPENDENT_PHOTON_SURROGATE_AUDIT_PASS",
       "original_source_records":81,"retained_band_site_entries":567,
       "simulated_symbols":15309,"source_frames":2187,
       "simulated_bit_errors":{k:v["wrong"] for k,v in errors.items()},
       "dark_spurious_counts":dark_spurious,
       "wrong_channel_map_errors":wrong_map,
       "optical_gate_opens":opened,"dark_gate_opens":dark_opened,
       "hbp_sha256":sha(hbp),
       "json_sha256":sha(metadata),
       "physical_sensor_data_verified":False,
    }
    canonical=(json.dumps(summary,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")
    (dest/"independent-photon-audit.json").write_bytes(canonical)
    (dest/"independent-photon-audit.json.sha256").write_bytes(
       (sha(canonical)+"  independent-photon-audit.json\n").encode("ascii"))
    print(json.dumps(summary,sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=5:raise SystemExit("usage: python verify_photon_assay.py ORIGINAL_PR80_ARTIFACT PY_OUTPUT JS_OUTPUT VERIFIED_OUTPUT")
    audit(*sys.argv[1:])
