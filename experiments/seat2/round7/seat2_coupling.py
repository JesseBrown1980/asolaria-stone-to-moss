#!/usr/bin/env python3
"""Seat 2 Round 7: independent digital photon/phonon/electronic factorial falsifiers.

The numeric detector values below are SIMULATED mathematical fixtures.
No physical photon, phonon, electronic transducer, or neuronal measurement is made.
"""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

MODELS = ("COHERENT_TOY", "ADDITIVE_NULL", "HEAT_ELECTRONIC_CONFOUND",
          "PHASE_INSENSITIVE_ARTIFACT")
ROOT = "52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
MAP = "077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400"
PHASE = (1, 0, -1, 0)
SCHEMA = "ASOLARIA-SEAT2-R7-PHONON-ELECTRON-OPTICAL-FACTORS-V1"

def sha(data): return hashlib.sha256(data).hexdigest()

def canonical(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":")) + "\n").encode("ascii")

def need(ok, reason):
    if not ok: raise ValueError(reason)

def mock_count(model, optical, acoustic, electronic, thermal, phase_idx, resonance, block):
    base = (100 + 7*optical + 11*acoustic + 5*electronic + 3*thermal
            + ((block + 2*electronic + 3*thermal + 5*resonance) % 7) - 3)
    if model == "COHERENT_TOY":
        return base + 23*optical*acoustic*resonance*PHASE[phase_idx]
    if model == "ADDITIVE_NULL":
        return base
    if model == "HEAT_ELECTRONIC_CONFOUND":
        return base + 23*optical*thermal + 17*acoustic*electronic
    if model == "PHASE_INSENSITIVE_ARTIFACT":
        return base + 23*optical*acoustic
    raise ValueError("UNKNOWN_MODEL")

def make_rows():
    result = []
    for model in MODELS:
        for resonance in range(2):
            for phase_idx in range(4):
                for electronic in range(2):
                    for thermal in range(2):
                        for block in range(8):
                            for optical in range(2):
                                for acoustic in range(2):
                                    y = mock_count(model,optical,acoustic,electronic,
                                        thermal,phase_idx,resonance,block)
                                    result.append(dict(schema=SCHEMA,
                                        model=model,resonance=resonance,
                                        phase_idx=phase_idx,optical=optical,
                                        acoustic=acoustic,electronic=electronic,
                                        thermal=thermal,block=block,detector_mock_units=y,
                                        source_bank_sha256=ROOT,simulation_only=True,
                                        physical_optomechanical_coupling_measured=False))
    return result

def validate(rows):
    need(len(rows) == 4096, "ROW_COUNT")
    seen = set()
    values = defaultdict(dict)
    for row in rows:
        need(row.get("schema") == SCHEMA and row.get("simulation_only") is True
             and row.get("physical_optomechanical_coupling_measured") is False,
             "FALSE_PHYSICAL_PROMOTION")
        need(row.get("source_bank_sha256") == ROOT, "SOURCE_PIN")
        model = row["model"]
        need(model in MODELS, "UNKNOWN_MODEL")
        dims = tuple(row[k] for k in ("resonance","phase_idx","electronic","thermal",
                                     "block","optical","acoustic"))
        resonance,phase_idx,electronic,thermal,block,optical,acoustic = dims
        need(all(type(x) is int for x in dims)
             and resonance in (0,1) and phase_idx in range(4)
             and electronic in (0,1) and thermal in (0,1)
             and block in range(8) and optical in (0,1) and acoustic in (0,1),
             "INVALID_FACTOR")
        key = (model,) + dims
        # Test the measurement at its *claimed* factor values before duplicate
        # checking. A forged detuning can be both wrong-valued and duplicate;
        # this ensures the independently preregistered fault stage is stable.
        expected = mock_count(model,optical,acoustic,electronic,thermal,
                              phase_idx,resonance,block)
        need(type(row["detector_mock_units"]) is int
             and row["detector_mock_units"] == expected, "NUMERIC_MODEL_MISMATCH")
        need(key not in seen, "DUPLICATE_FACTORIAL_CASE")
        seen.add(key)
        values[(model,resonance,phase_idx,electronic,thermal,block)][optical,acoustic] = expected
    need(len(seen)==4096 and len(values)==1024, "INCOMPLETE_FACTORS")
    observed = defaultdict(list)
    for (model,resonance,phase_idx,electronic,thermal,block), four in values.items():
        need(len(four)==4,"MISSING_INTERACTION_ARM")
        delta = four[1,1]-four[1,0]-four[0,1]+four[0,0]
        observed[(model,resonance,phase_idx)].append(delta)
    need(len(observed)==32, "INTERACTION_GRID")
    totals={}
    for model in MODELS:
        totals[model]={}
        for resonance in range(2):
            vals=[]
            for phase_idx in range(4):
                cases=observed[model,resonance,phase_idx]
                need(len(cases)==32, "INSUFFICIENT_BLOCKS")
                need(len(set(cases))==1,"NON_MATCHED_CONTRAST")
                vals.append(cases[0])
            totals[model][str(resonance)]=vals
    expected_patterns = {
        "COHERENT_TOY":{"0":[0,0,0,0],"1":[23,0,-23,0]},
        "ADDITIVE_NULL":{"0":[0,0,0,0],"1":[0,0,0,0]},
        "HEAT_ELECTRONIC_CONFOUND":{"0":[0,0,0,0],"1":[0,0,0,0]},
        "PHASE_INSENSITIVE_ARTIFACT":{"0":[23,23,23,23],"1":[23,23,23,23]},
    }
    need(totals==expected_patterns,"PREREGISTERED_INTERACTION_PATTERN_DRIFT")
    return totals

def negative_checks(rows):
    checks=[]
    first = rows[0]
    def attempt(name,orig_idx,changes,reason):
        modified=list(rows)
        wrong=dict(modified[orig_idx]);wrong.update(changes);modified[orig_idx]=wrong
        try:validate(modified)
        except ValueError as err:
            need(str(err)==reason,name+"_INCORRECT_FAILURE_"+str(err))
            checks.append(name)
        else:raise AssertionError("ATTACK_ACCEPTED_"+name)
    attempt("false_detector",0,{"detector_mock_units":first["detector_mock_units"]+1},
            "NUMERIC_MODEL_MISMATCH")
    attempt("wrong_root",0,{"source_bank_sha256":"f"*64},"SOURCE_PIN")
    attempt("fake_physical",0,{"physical_optomechanical_coupling_measured":True},
            "FALSE_PHYSICAL_PROMOTION")
    attempt("wrong_factor",0,{"phase_idx":5},"INVALID_FACTOR")
    attempt("duplicate_record",1,rows[0],"DUPLICATE_FACTORIAL_CASE")
    try:validate(rows[:-1])
    except ValueError as err:need(str(err)=="ROW_COUNT","MISSING_WRONG_FAILURE");checks.append("missing_case")
    else:raise AssertionError("MISSING_ACCEPTED")
    # Choose an in-resonance coherent case where O=A=1; change phase alone.
    idx = next(i for i,r in enumerate(rows) if r["model"]=="COHERENT_TOY"
               and r["resonance"]==1 and r["phase_idx"]==0
               and r["optical"]==1 and r["acoustic"]==1)
    attempt("wrong_phase",idx,{"phase_idx":1},"NUMERIC_MODEL_MISMATCH")
    attempt("detuning_spoof",idx,{"resonance":0},"NUMERIC_MODEL_MISMATCH")
    idx = next(i for i,r in enumerate(rows) if r["model"]=="COHERENT_TOY"
               and r["resonance"]==1 and r["phase_idx"]==0
               and r["optical"]==1 and r["acoustic"]==0)
    attempt("crossed_optical_acoustic",idx,{"optical":0,"acoustic":1},
            "NUMERIC_MODEL_MISMATCH")
    need(len(checks)==9,"NEGATIVE_COVERAGE")
    return checks

def run(out,merged):
    main_stone = (merged/"stones/2026-10-15-rainbow81/"
                  "seat4-round5-signed-spectrum-mapping-20261015.hbp")
    need(main_stone.is_file() and sha(main_stone.read_bytes())==MAP,
         "MERGED_SPECTRUM_STONE_PIN_FAIL")
    rows=make_rows()
    totals=validate(rows)
    negatives=negative_checks(rows)
    raw=b"".join(map(canonical,rows))
    out.mkdir(parents=True,exist_ok=True)
    report=dict(schema=SCHEMA,classification="SYNTHETIC_FACTORIAL_NOT_REAL_SENSORS",
                rows=len(rows),matched_interaction_contrasts=1024,
                pinned_bank_sha256=ROOT,pinned_spectrum_stone_sha256=MAP,
                interaction_difference_in_differences=totals,
                active_negative_controls=negatives,trace_sha256=sha(raw),
                digital_coherent_fixture_verified=True,
                physical_optomechanical_coupling_measured=False,
                independent_optical_memory_measured=False,
                biological_neural_memory_measured=False,
                phase_only_or_interaction_only_is_physical_proof=False)
    result=canonical(report)
    hbp=("R7|schema="+SCHEMA+"|simulated=1|rows=4096\n"+
         "".join("MODEL|name="+name+"|detuned="+",".join(map(str,totals[name]["0"]))+
         "|resonant="+",".join(map(str,totals[name]["1"]))+"\n" for name in MODELS)+
         "RESULT|digital_coherent_fixture=PASS|real_coupling=HOLD|optical_memory=HOLD|neural_memory=HOLD\n"
         ).encode("ascii")
    for name,data in (("factorial.jsonl",raw),("results.json",result),
                      ("result.hbp",hbp)):
        (out/name).write_bytes(data)
        (out/(name+".sha256")).write_bytes(
            (sha(data)+"  "+name+"\n").encode("ascii"))
    print("SEAT2_R7_DIGITAL_PASS",len(rows),len(negatives),sha(raw),sha(result))
    return report

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: python seat2_coupling.py OUTPUT MERGED_MAIN")
    run(Path(sys.argv[1]),Path(sys.argv[2]))
