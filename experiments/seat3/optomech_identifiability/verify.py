#!/usr/bin/env python3
"""Independent read-only C3 mathematical and source-root adversarial auditor.

Does NOT import either producer module. Reconstructs every bank source leaf and
every 16,384-factor observation, all matched causal contrasts and exact hashes.
"""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

SOURCE="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
INDEX="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"
SCHEMA="ASOLARIA-SEAT3-OPTO-ACOUSTIC-IDENTIFIABILITY-V1"
WORLDS=("OPTICAL_COUPLING_TOY","RF_PICKUP_TOY",
        "BLOCKER_LINKED_RF_TOY","ADDITIVE_NULL")
BANDS=("red","orange","yellow","green","blue","indigo","violet")
PHASE=(1,0,-1,0)
CASE=re.compile(r"CASE\|world=(OPTICAL_COUPLING_TOY|RF_PICKUP_TOY|BLOCKER_LINKED_RF_TOY|ADDITIVE_NULL)"
               r"\|R\|res=([01])\|phase=([0-3])\|e=([01])\|t=([01])\|k=([0-7])"
               r"\|block=([01])\|shield=([01])\|o=([01])\|a=([01])"
               r"\|band=([0-6])\|site=(\d{2})\|bit=([01])"
               r"\|leaf=([a-f0-9]{64})\|y=(-?\d+)\Z")
MEM=re.compile(r"MEM\|band=(red|orange|yellow|green|blue|indigo|violet)"
              r"\|id=site-(\d{3})\|offset=(\d+)\|length=(\d+)\|sha256=([a-f0-9]{64})\Z")
def sha(buf):return hashlib.sha256(buf).hexdigest()
def assertit(cond,msg):
    if not cond:raise ValueError(msg)

def proof_source(path):
    root=Path(path)
    files=[
      (root/"base-evidence/lightbank-memories.json",SOURCE,16689),
      (root/"rainbow-evidence/rainbow7-bank.jsonl",BANK,184815),
      (root/"rainbow-evidence/rainbow7-index.hbi",INDEX,70043)]
    chunks=[]
    for f,h,n in files:
        buf=f.read_bytes()
        assertit(len(buf)==n and sha(buf)==h,"ORIGINAL_SOURCE_PIN")
        chunks.append(buf)
    src,bank,index=chunks
    originals=json.loads(src)["records"]
    assertit(len(originals)==81,"MISSING_81")
    rows=index.decode("ascii").splitlines()
    assertit(len(rows)==567 and index.endswith(b"\n"),"BASE_567_MISSING")
    leaves={}
    previous=0
    for i,row in enumerate(rows):
        m=MEM.fullmatch(row)
        assertit(m is not None,"BASE_FORMAT")
        band,site_s,start_s,n_s,leaf=m.groups()
        site=int(site_s);start=int(start_s);n=int(n_s)
        assertit(band==BANDS[i//81] and site==i%81 and start==previous,
                 "UNANCHORED_BASE_INDEX")
        assertit(n>0 and start+n<=len(bank),"SOURCE_BOUNDS")
        previous=start+n
        payload=bank[start:previous]
        assertit(sha(payload)==leaf,"BAD_BASE_LEAF")
        obj=json.loads(payload)
        assertit(obj["record"]==originals[site] and
                 obj["band"]==band and obj["id"]==f"site-{site:03d}","BAD_BASE_ID")
        leaves[(i//81,site)]=leaf
    assertit(previous==len(bank) and len(leaves)==567,"BASE_INCOMPLETE")
    return leaves

def check(original,py_output,node_output,verified):
    bank=proof_source(original)
    py=Path(py_output);node=Path(node_output);out=Path(verified)
    names=("identifiability-factorial.hbp","identifiability-math.json")
    for name in names:
        a=(py/name).read_bytes()
        assertit(a==(node/name).read_bytes(),"PY_NODE_FULL_BYTE_DIFFERENCE")
        for folder in (py,node):
            side=(folder/(name+".sha256")).read_bytes()
            assertit(side==(sha(a)+"  "+name+"\n").encode("ascii"),"SIDECAR_INVALID")
    full=(py/names[0]).read_bytes()
    raw=(py/names[1]).read_bytes()
    result=json.loads(raw)
    assertit(result["schema"]==SCHEMA and result["verdict"]=="PASS","SOURCE_SCHEMA")
    assertit(result["source_81_sha256"]==SOURCE and result["retained_bank_sha256"]==BANK
             and result["compact_index_sha256"]==INDEX,"ANCHOR_MISMATCH")
    assertit(result["unique_original_memories"]==81
             and result["stored_band_site_entries"]==567,"MEMORY_COPIES_NOT_CAPACITY")
    assertit(result["model_regimes"]==list(WORLDS)
             and result["cases_per_regime"]==4096 and result["all_cases"]==16384,
             "MISSING_FACTORIAL_ROWS")
    assertit(result["factorial_base_cells_per_world"]==1024
             and result["augmented_controls_per_base_cell"]==4
             and result["matched_quartets_per_regime"]==1024
             and result["matched_quartets_all_regimes"]==4096,"MISSING_CONTRAST")
    assertit(result["phase_cosine_integer"]==list(PHASE),"CHANGED_PHASE")
    assertit(result["trace_bytes"]==len(full) and
             result["trace_sha256"]==sha(full),"FULL_TRACE_HASH")
    assertit(full.endswith(b"\n"),"TRUNCATED_TRACE")
    lines=full.decode("ascii").splitlines()
    assertit(len(lines)==16385 and lines[0]==f"PORTAL|schema={SCHEMA}|simulated_mechanisms=4|real_instruments=0",
             "FAKE_HARDWARE_OR_LOST_CASES")
    source_fingerprints={}
    baseline_fingerprints={}
    contrasts={}
    differences={}
    rownum=1
    for world in WORLDS:
        h=hashlib.sha256()
        hb=hashlib.sha256()
        quads=defaultdict(dict)
        for res in range(2):
            for phase in range(4):
                for electronic in range(2):
                    for thermal in range(2):
                        for k in range(8):
                            band=(phase+2*electronic+3*thermal+k)%7
                            site=(11*phase+7*res+3*k+19*electronic+23*thermal)%81
                            leaf=bank[(band,site)]
                            bit=hashlib.sha256(
                              b"ASOLARIA-R8-FROZEN-BIT|"+leaf.encode("ascii")
                              ).digest()[0]&1
                            for block in range(2):
                                for shield in range(2):
                                    for light in range(2):
                                        for acoustic in range(2):
                                            line=lines[rownum];rownum+=1
                                            m=CASE.fullmatch(line)
                                            assertit(m is not None,"RECORD_PARSE")
                                            w=m.group(1)
                                            dims=tuple(map(int,m.groups()[1:13]))
                                            expected=(res,phase,electronic,thermal,k,block,shield,
                                                      light,acoustic,band,site,bit)
                                            assertit(w==world and dims==expected,
                                                     "FACTOR_OR_ORDER_MISMATCH")
                                            assertit(m.group(14)==leaf,"WRONG_BANK_LEAF")
                                            y=int(m.group(15))
                                            base=(100+7*light+11*acoustic+5*electronic
                                                  +3*thermal+((k+2*electronic+3*thermal+5*res)%7-3)
                                                  +2*bit)
                                            K=23*light*acoustic*res*PHASE[phase]
                                            if world in (WORLDS[0],WORLDS[2]):
                                                expected_y=base+K*(1-block)
                                            elif world==WORLDS[1]:
                                                expected_y=base+K*(1-shield)
                                            else:expected_y=base
                                            assertit(y==expected_y,"DETECTOR_VALUE_TAMPERED")
                                            obs=line.split("|R|",1)[1]
                                            h.update(("R|"+obs+"\n").encode("ascii"))
                                            if block==shield==0:
                                                hb.update(("R|"+obs+"\n").encode("ascii"))
                                            key=(res,phase,electronic,thermal,k,block,shield)
                                            quad=quads[key]
                                            assertit((light,acoustic) not in quad,
                                                     "DUPLICATE_FACT")
                                            quad[(light,acoustic)]=y
        assertit(len(quads)==1024 and all(len(q)==4 for q in quads.values()),
                 "MISSING_MATCHED_ARM")
        source_fingerprints[world]=h.hexdigest()
        baseline_fingerprints[world]=hb.hexdigest()
        contrasts[world]={}
        for res in range(2):
            for phase in range(4):
                for block in range(2):
                    for shield in range(2):
                        dset=set()
                        for e in range(2):
                            for t in range(2):
                                for k in range(8):
                                    q=quads[(res,phase,e,t,k,block,shield)]
                                    delta=q[(1,1)]-q[(1,0)]-q[(0,1)]+q[(0,0)]
                                    dset.add(delta)
                        assertit(len(dset)==1,"DID_MISMATCH_IN_MATCHED_BLOCK")
                        observed=next(iter(dset))
                        predicted=(23*res*PHASE[phase]*
                             ((1-block) if world in (WORLDS[0],WORLDS[2])
                              else (1-shield) if world==WORLDS[1] else 0))
                        assertit(observed==predicted,"WRONG_CONTRAST")
                        contrasts[world][f"r{res}p{phase}b{block}s{shield}"]=observed
        differences[world]=contrasts[world]["r1p0b0s1"]-contrasts[world]["r1p0b1s0"]
    assertit(rownum==16385,"ROW_COUNT_MISMATCH")
    assertit(result["observable_sha256_by_world"]==source_fingerprints,"OBSERVATION_ROOTS_DRIFT")
    assertit(result["baseline_no_block_no_shield_sha256_by_world"]==baseline_fingerprints,
             "BASELINE_OBSERVATION_HASH_DRIFT")
    assertit(result["difference_in_differences_grid"]==contrasts,"CONTRAST_LEDGER_DRIFT")
    assertit(result["blocker_vs_shield_discriminant_resonant_phase0"]==differences,
             "INTERVENTION_DISCRIMINANT_DRIFT")
    assertit(differences=={WORLDS[0]:23,WORLDS[1]:-23,WORLDS[2]:23,WORLDS[3]:0},
             "NOT_AN_IDENTIFIABILITY_FALSIFIER")
    assertit(source_fingerprints[WORLDS[0]]==source_fingerprints[WORLDS[2]],
             "CONSTRUCTIVE_COUNTEREXAMPLE_FAILED")
    assertit(baseline_fingerprints[WORLDS[0]]==baseline_fingerprints[WORLDS[1]],
             "PHASE_RESONANCE_ALONE_SEPARATES_ARTIFACT")
    assertit(result["full_control_optical_vs_blocker_linked_rf_observationally_identical"] is True
             and result["intrinsic_mechanism_identified_by_y_alone"] is False,
             "INVALID_MECHANISM_CERTIFICATION")
    controls=result["adversarial_tests"]
    assertit(sum(x=="HELD" for x in controls.values())==12,
             "ACTIVE_NEGATIVE_CONTROL_COVERAGE")
    assertit(controls["optical_vs_blocker_electronic_mechanism"]==
             "NOT_IDENTIFIABLE_FROM_OBSERVATIONS","FORGED_CAUSAL_CERTAINTY")
    assertit(controls["attacker_replaces_source_and_claimed_root"]=="ORIGIN_UNAUTHENTICATED",
             "ORIGIN_FORGERY_ACCEPTED")
    assertit(result["source_origin_authenticated"] is False and
             result["physical_optical_measurement"]=="NOT_RUN" and
             result["physical_phonon_measurement"]=="NOT_RUN" and
             result["physical_memory_retention_measurement"]=="NOT_RUN" and
             result["biological_neural_measurement"]=="NOT_RUN",
             "PHYSICAL_STATUS_FALSE")
    out.mkdir(parents=True,exist_ok=True)
    for name in names:
        blob=(py/name).read_bytes()
        (out/name).write_bytes(blob)
        (out/(name+".sha256")).write_bytes((sha(blob)+"  "+name+"\n").encode("ascii"))
    audit={"verdict":"SEAT3_THIRD_ALGEBRA_AUDIT_PASS",
           "tested_original_source_leaves":567,"cases":16384,
           "matched_factorial_quartets":4096,
           "optical_artifact_full_observational_collision":True,
           "optical_vs_rf_no_intervention_collision":True,
           "full_trace_sha256":sha(full),
           "result_json_sha256":sha(raw),
           "calibrated_physical_coupling_observed":False}
    artifact=(json.dumps(audit,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")
    name="independent-identifiability-audit.json"
    (out/name).write_bytes(artifact)
    (out/(name+".sha256")).write_bytes((sha(artifact)+"  "+name+"\n").encode("ascii"))
    print(json.dumps(audit,sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("usage: verify.py SOURCE_PR80_DIR PYTHON_OUTPUT NODE_OUTPUT VERIFIED_OUT")
    check(*sys.argv[1:])
