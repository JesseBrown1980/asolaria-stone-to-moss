#!/usr/bin/env python3
"""Post-hoc Seat3 EXACT mathematical mechanism-identifiability challenge.

Peer-review target: Seat2 R7 synthetic coherent-vs-EMI phase response and
Seat4 R8 synthetic thermal-nonlinearity factorial. No physical experiment.
These constructions were derived after inspecting their code and are marked
POSTHOC, not a blinded preregistered discovery.
"""
import hashlib,json
from fractions import Fraction
from itertools import product
from pathlib import Path
import sys

ROOT="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
SCHEMA="ASOLARIA-C3-FACTORIZED-MECHANISM-NONIDENTIFIABILITY-V1"
PHASE=(1,0,-1,0)

def rank_int(a):
    m=[[Fraction(c) for c in row] for row in a]
    piv=0
    for col in range(len(m[0])):
        k=next((i for i in range(piv,len(m)) if m[i][col]),None)
        if k is None:continue
        m[piv],m[k]=m[k],m[piv]
        d=m[piv][col]
        m[piv]=[v/d for v in m[piv]]
        for i in range(len(m)):
            if i!=piv and m[i][col]:
                f=m[i][col]
                m[i]=[v-f*w for v,w in zip(m[i],m[piv])]
        piv+=1
        if piv==len(m):break
    return piv

def see_two_mechanisms():
    comparisons=0
    diffs={}
    for resonance,phase_idx,e,t,block,o,a in product(range(2),range(4),
                                                       range(2),range(2),
                                                       range(8),range(2),range(2)):
        # Exactly the source-listed Seat2 R7 modeled baseline, including
        # source-independent electronic/thermal nuisance factors.
        baseline=(100+7*o+11*a+5*e+3*t+
                 ((block+2*e+3*t+5*resonance)%7)-3)
        # Competing CAUSAL EXPLANATIONS of the SAME scalar readout:
        # A: coherent optical/phonon mediated modulation, purely a toy law.
        optomechanical=baseline+23*o*a*resonance*PHASE[phase_idx]
        # B: electronic RF/microphonic pickup mixed by identical oscillators.
        # This is a MODEL counterexample, not a claim such an EMI was measured.
        emi=baseline+23*o*a*resonance*PHASE[phase_idx]
        assert optomechanical==emi
        comparisons+=1
        if e==0 and t==0 and block==0:
            key=(resonance,phase_idx)
            # All four counterfactual intervention arms share the same
            # baseline; source has no effect on the interaction.
            row=diffs.setdefault(key,{})
            row[(o,a)]=optomechanical
    assert comparisons==2*4*2*2*8*2*2==1024
    contrast={}
    for resonance in (0,1):
        contrast[str(resonance)]=[]
        for phase_idx in range(4):
            cell=diffs[(resonance,phase_idx)]
            contrast[str(resonance)].append(
                 cell[1,1]-cell[1,0]-cell[0,1]+cell[0,0])
    assert contrast=={"0":[0,0,0,0],"1":[23,0,-23,0]}
    return comparisons,contrast

def seat4_thermal_design_rank():
    # Seat4 R8: thermal nuisance source is (L+A)^2. Binary L,A satisfy
    # (L+A)^2=L+A+2LA exactly, making mediator T a linear combination of
    # direct factorial L,A,LA. This is structural rank deficiency.
    m=[]
    for l,a in product((0,1),repeat=2):
        interaction=l*a
        t=(l+a)**2
        assert t==l+a+2*interaction
        m.append([1,l,a,interaction,t])
    k=rank_int(m)
    assert k==4 and len(m[0])==5
    # Without an independently randomized thermal-matched sham, no
    # observational decomposition of "direct OA" and thermal-mediated OA.
    return m,k

def run(out):
    n,contrasts=see_two_mechanisms()
    matrix,r=seat4_thermal_design_rank()
    report={
      "schema":SCHEMA,
      "posthoc_mathematical_counterexample":True,
      "source_tested_seat2_r7":True,
      "source_tested_seat4_r8":True,
      "seat2_coherent_vs_electronic_emi_all_rows_equal":n,
      "seat2_observed_contrast_both_explanations":contrasts,
      "seat4_thermal_column_relation":"T=(L+A)^2=L+A+2*L*A for binary L,A",
      "seat4_design_matrix_columns":["intercept","light","acoustic","light_acoustic","thermal"],
      "seat4_design_matrix":matrix,
      "seat4_rank":r,"seat4_column_count":5,
      "consequence":"MECHANISM_NOT_IDENTIFIABLE_FROM_CURRENT_FACTORIAL_RESPONSE_ALONE",
      "required_further_intervention":"Independent thermal and EMI matched sham or mediator intervention with actual calibrated optics/electronics and time stamps",
      "physical_photon_or_phonon_measurements":0,
      "source_hashes_alone_are_physical_custody":False,
      "mathematical_theorem":"PASS"
    }
    text=(json.dumps(report,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")
    path=Path(out);path.mkdir(parents=True,exist_ok=True)
    name="identifiability-counterexample.json"
    (path/name).write_bytes(text)
    (path/(name+".sha256")).write_bytes(
        (hashlib.sha256(text).hexdigest()+"  "+name+"\n").encode("ascii"))
    print(json.dumps({"theorem":"PASS","equivalent_seat2_rows":n,
                      "seat4_design_rank":r,"seat4_columns":5,
                      "sha256":hashlib.sha256(text).hexdigest()},sort_keys=True))
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python identifiability_counterexamples.py OUTPUT_DIR")
    run(sys.argv[1])
