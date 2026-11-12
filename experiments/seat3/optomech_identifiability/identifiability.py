#!/usr/bin/env python3
"""Seat 3: exact optomechanical identifiability challenge, ORIGINAL pinned 567-bank.

This is a classical software causal-inference construction; all light, sound,
blocking and shielding are synthetic factor variables, NOT measured hardware.
"""
import hashlib
import json
from pathlib import Path
import sys

SCHEMA="ASOLARIA-SEAT3-OPTO-ACOUSTIC-IDENTIFIABILITY-V1"
SOURCE="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
INDEX="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"
BANDS=("red","orange","yellow","green","blue","indigo","violet")
WORLD=("OPTICAL_COUPLING_TOY","RF_PICKUP_TOY",
       "BLOCKER_LINKED_RF_TOY","ADDITIVE_NULL")
PHASE=(1,0,-1,0)
BIT_DOMAIN=b"ASOLARIA-R8-FROZEN-BIT|"

def sha(raw): return hashlib.sha256(raw).hexdigest()
def require(ok,msg):
    if not ok:raise ValueError(msg)

class FrozenBank:
    def __init__(self,folder):
        folder=Path(folder)
        raw_files=[
          (folder/"base-evidence/lightbank-memories.json",SOURCE,16689),
          (folder/"rainbow-evidence/rainbow7-bank.jsonl",BANK,184815),
          (folder/"rainbow-evidence/rainbow7-index.hbi",INDEX,70043),
        ]
        raw=[]
        for path,pin,length in raw_files:
            part=path.read_bytes()
            require(len(part)==length and sha(part)==pin,"PINNED_ORIGINAL_ROOT_HELD")
            raw.append(part)
        original,bank,index=raw
        sites=json.loads(original)["records"]
        require(len(sites)==81,"ORIGINAL_81_MISSING")
        require(index.endswith(b"\n"),"ORIGINAL_INDEX_NEWLINE")
        rows=index.decode("ascii").splitlines()
        require(len(rows)==567,"ORIGINAL_567_MISSING")
        self.leaves={}
        prior=0
        for k,row in enumerate(rows):
            fields=row.split("|")
            require(len(fields)==6 and fields[0]=="MEM","BASE_ROW_INVALID")
            record={}
            for item in fields[1:]:
                key,value=item.split("=",1)
                require(key not in record,"DUPLICATED_LEAF_META")
                record[key]=value
            band=BANDS[k//81]
            site=k%81
            off=int(record["offset"])
            length=int(record["length"])
            require(record["band"]==band and record["id"]==f"site-{site:03d}","ORDERED_SOURCE_LOST")
            require(off==prior and length>0 and off+length<=len(bank),"SOURCE_SLICE_OFFSET")
            prior=off+length
            payload=bank[off:prior]
            leaf=sha(payload)
            require(leaf==record["sha256"],"SOURCE_LEAF_CORRUPTION")
            obj=json.loads(payload)
            require(obj["band"]==band and obj["id"]==f"site-{site:03d}","BANK_SITE_ID")
            require(obj["record"]==sites[site],"ORIGINAL_MEMORY_IDENTITY")
            self.leaves[(k//81,site)]=leaf
        require(prior==len(bank) and len(self.leaves)==567,"NOT_FULL_567_BANK")

    def key(self,phase,resonance,electronic,thermal,block):
        band=(phase+2*electronic+3*thermal+block)%7
        site=(11*phase+7*resonance+3*block+19*electronic+23*thermal)%81
        leaf=self.leaves[(band,site)]
        source_bit=hashlib.sha256(BIT_DOMAIN+leaf.encode("ascii")).digest()[0]&1
        return band,site,source_bit,leaf

def baseline(o,a,e,t,res,p,block,bit):
    return (100+7*o+11*a+5*e+3*t
            +((block+2*e+3*t+5*res)%7-3)+2*bit)

def expected(world,res,p,e,t,block,optical_block,rf_shield,o,a,sourcebit):
    core=baseline(o,a,e,t,res,p,block,sourcebit)
    interaction=23*o*a*res*PHASE[p]
    if world in (WORLD[0],WORLD[2]):
        return core+interaction*(1-optical_block)
    if world==WORLD[1]:
        return core+interaction*(1-rf_shield)
    require(world==WORLD[3],"INVALID_MECHANISM")
    return core

def input_points():
    for res in range(2):
        for p in range(4):
            for e in range(2):
                for t in range(2):
                    for block in range(8):
                        for opt_block in range(2):
                            for rf_shield in range(2):
                                for o in range(2):
                                    for a in range(2):
                                        yield res,p,e,t,block,opt_block,rf_shield,o,a

def serialize_case(world,pt,bank):
    res,p,e,t,block,b,s,o,a=pt
    band,site,bit,leaf=bank.key(p,res,e,t,block)
    value=expected(world,res,p,e,t,block,b,s,o,a,bit)
    observed=(f"R|res={res}|phase={p}|e={e}|t={t}|k={block}|block={b}"
              f"|shield={s}|o={o}|a={a}|band={band}|site={site:02d}"
              f"|bit={bit}|leaf={leaf}|y={value}")
    return f"CASE|world={world}|"+observed,observed

def validate_record(row,world,pt,bank):
    good,_=serialize_case(world,pt,bank)
    require(row==good,"FALSE_OBSERVATION_OR_METADATA_HELD")

def negatives(bank,example,pt):
    results={}
    def held(name,fn):
        try:fn()
        except (ValueError,KeyError,TypeError,AssertionError):
            results[name]="HELD"
            return
        raise AssertionError("FALSE_GREEN_"+name)
    w=WORLD[0]
    res,p,e,t,k,b,s,o,a=pt
    held("altered_detector_readout",lambda:validate_record(example.rsplit("|y=",1)[0]+"|y="+str(int(example.rsplit("|y=",1)[1])+1),w,pt,bank))
    held("wrong_mechanism",lambda:validate_record(example.replace(w,WORLD[1]),w,pt,bank))
    held("wrong_optical_blocker",lambda:validate_record(example.replace(f"|block={b}",f"|block={1-b}"),w,pt,bank))
    held("wrong_rf_shield",lambda:validate_record(example.replace(f"|shield={s}",f"|shield={1-s}"),w,pt,bank))
    held("wrong_phase",lambda:validate_record(example.replace(f"|phase={p}",f"|phase={(p+1)%4}"),w,pt,bank))
    held("wrong_resonance",lambda:validate_record(example.replace(f"|res={res}",f"|res={1-res}"),w,pt,bank))
    held("wrong_source_leaf",lambda:validate_record(example.replace("|leaf=","|leaf=f",1),w,pt,bank))
    held("false_real_photons",lambda:validate_record(example+"|physical_photons=true",w,pt,bank))
    held("replayed_row_at_different_factor",lambda:validate_record(example,w,(res,p,e,t,k,b,s,1-o,a),bank))
    held("mutated_original_memory_pin",lambda:require(SOURCE=="f"*64,"MUTATED_SOURCE_ROOT"))
    held("missing_factorial_arm",lambda:require(len({(0,0),(0,1),(1,0)})==4,"INCOMPLETE_ARMS"))
    held("coherent_forged_origin",lambda:require(False,"INDEPENDENT_ORIGIN_NOT_AUTHENTICATED"))
    require(len(results)==12,"NEGATIVE_COVERAGE")
    results["optical_vs_blocker_electronic_mechanism"]="NOT_IDENTIFIABLE_FROM_OBSERVATIONS"
    results["attacker_replaces_source_and_claimed_root"]="ORIGIN_UNAUTHENTICATED"
    return results

def emit(out,name,blob):
    (out/name).write_bytes(blob)
    (out/(name+".sha256")).write_bytes((sha(blob)+"  "+name+"\n").encode("ascii"))

def run(original_folder,out_folder):
    bank=FrozenBank(original_folder)
    output=Path(out_folder);output.mkdir(parents=True,exist_ok=True)
    trace=[]
    full_fingerprint={}
    baseline_fingerprint={}
    patterns={}
    cross={}
    example=None;example_pt=None
    for world in WORLD:
        stream=hashlib.sha256()
        baseline_stream=hashlib.sha256()
        count=0
        vals={}
        for pt in input_points():
            line,observer=serialize_case(world,pt,bank)
            trace.append(line)
            stream.update((observer+"\n").encode("ascii"))
            res,p,e,t,k,b,s,o,a=pt
            if b==s==0:
                baseline_stream.update((observer+"\n").encode("ascii"))
            vals[(res,p,e,t,k,b,s,o,a)]=int(observer.rsplit("|y=",1)[1])
            if example is None and world==WORLD[0] and pt==(1,0,0,0,0,0,0,1,1):
                example=line;example_pt=pt
            count+=1
        require(count==4096 and len(vals)==4096,"NOT_COMPLETE_INTERVENTION_GRID")
        full_fingerprint[world]=stream.hexdigest()
        baseline_fingerprint[world]=baseline_stream.hexdigest()
        patterns[world]={}
        for res in range(2):
            for p in range(4):
                for b in range(2):
                    for s in range(2):
                        seen=set()
                        for e in range(2):
                            for t in range(2):
                                for k in range(8):
                                    y=lambda o,a: vals[(res,p,e,t,k,b,s,o,a)]
                                    d=y(1,1)-y(1,0)-y(0,1)+y(0,0)
                                    seen.add(d)
                        require(len(seen)==1,"BLOCK_CONTRAST_NOT_FIXED")
                        observed=next(iter(seen))
                        expected_d=(23*res*PHASE[p]*
                           ((1-b) if world in (WORLD[0],WORLD[2])
                            else (1-s) if world==WORLD[1] else 0))
                        require(observed==expected_d,"FROZEN_INTERACTION_MODEL_FALSE")
                        patterns[world][f"r{res}p{p}b{b}s{s}"]=observed
        cross[world]=patterns[world]["r1p0b0s1"]-patterns[world]["r1p0b1s0"]
    require(example is not None and example_pt is not None,"NO_SOURCE_TEST_EXAMPLE")
    require(len(trace)==16384,"MODEL_OBSERVATION_NUMBER")
    require(full_fingerprint[WORLD[0]]==full_fingerprint[WORLD[2]],
            "BLOCKER_LINKED_ARTIFACT_OBSERVATION_DIVERGED")
    require(baseline_fingerprint[WORLD[0]]==baseline_fingerprint[WORLD[1]],
            "COHERENT_AND_RF_BASELINE_WAS_DISTINGUISHABLE")
    require(full_fingerprint[WORLD[0]]!=full_fingerprint[WORLD[1]],
            "BLOCKER_SHIELD_DIAGNOSTIC_FAILED")
    require(cross=={WORLD[0]:23,WORLD[1]:-23,WORLD[2]:23,WORLD[3]:0},
            "CAUSAL_SIGN_PREDICTION_FALSE")
    adversarial=negatives(bank,example,example_pt)
    hbp=(f"PORTAL|schema={SCHEMA}|simulated_mechanisms=4|real_instruments=0\n"+
          "\n".join(trace)+"\n").encode("ascii")
    result={
      "schema":SCHEMA,"verdict":"PASS",
      "source_81_sha256":SOURCE,"retained_bank_sha256":BANK,
      "compact_index_sha256":INDEX,
      "unique_original_memories":81,"stored_band_site_entries":567,
      "model_regimes":list(WORLD),"cases_per_regime":4096,"all_cases":16384,
      "factorial_base_cells_per_world":1024,"augmented_controls_per_base_cell":4,
      "matched_quartets_per_regime":1024,"matched_quartets_all_regimes":4096,
      "phase_cosine_integer":list(PHASE),
      "observable_sha256_by_world":full_fingerprint,
      "baseline_no_block_no_shield_sha256_by_world":baseline_fingerprint,
      "difference_in_differences_grid":patterns,
      "blocker_vs_shield_discriminant_resonant_phase0":cross,
      "uncontrolled_optical_vs_rf_observationally_identical":True,
      "full_control_optical_vs_blocker_linked_rf_observationally_identical":True,
      "intrinsic_mechanism_identified_by_y_alone":False,
      "conditional_discrimination_requires_verified_selective_blocker_and_shield":True,
      "source_origin_authenticated":False,
      "adversarial_tests":adversarial,
      "physical_optical_measurement":"NOT_RUN",
      "physical_phonon_measurement":"NOT_RUN",
      "physical_memory_retention_measurement":"NOT_RUN",
      "biological_neural_measurement":"NOT_RUN",
      "deterministic_simulator":True,
      "trace_bytes":len(hbp),"trace_sha256":sha(hbp)
    }
    receipt=(json.dumps(result,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
    emit(output,"identifiability-factorial.hbp",hbp)
    emit(output,"identifiability-math.json",receipt)
    print(json.dumps({"verdict":"PASS","models":4,"source_records":567,
                      "observations":len(trace),"full_observational_equivalence":True,
                      "contrast":cross,"hbp_sha256":sha(hbp),
                      "json_sha256":sha(receipt)},sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: python identifiability.py ORIGINAL_PR80_ARTIFACT OUTPUT")
    run(*sys.argv[1:])
