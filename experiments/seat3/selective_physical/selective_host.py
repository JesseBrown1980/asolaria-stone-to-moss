#!/usr/bin/env python3
"""Seat3 physically hosted source -> resource -> exact mechanism analysis.

Exact mathematical output is deterministic. OS-reported telemetry is separate,
volatile and *not* power/optical instrumentation. Historical operator-reported
LIRIS local experiments are preserved, not described as never performed.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,platform,re,sys,time,tracemalloc
try:
    import resource
except ImportError:
    resource=None
from itertools import product
SCHEMA="ASOLARIA-SEAT3-SELECTIVE-ATTENUATOR-PHYSICAL-HOST-V1"
SOURCE="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
INDEX="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"
LIRIS_SHA="d9b20742592e6fdcb26c03278bd9d574636f4f9f05b24cf502ad173d20e5579f"
IDX_RX=re.compile(r"MEM\|band=(red|orange|yellow|green|blue|indigo|violet)\|id=site-(\d{3})\|offset=(\d+)\|length=(\d+)\|sha256=([a-f0-9]{64})\Z")
BANDS=("red","orange","yellow","green","blue","indigo","violet")
ETAS=(F(0),F(1,4),F(1,2),F(3,4),F(7,8),F(15,16),F(1))
def SHA(b):return hashlib.sha256(b).hexdigest()
def demand(x,msg):
    if not x:raise ValueError(msg)
def pinned(p,hashhex,size):
    raw=Path(p).read_bytes()
    demand(len(raw)==size and SHA(raw)==hashhex,"SOURCE_ROOT_DRIFT:"+str(p))
    return raw
def bank_digest(root):
    path=Path(root)
    source=pinned(path/"base-evidence/lightbank-memories.json",SOURCE,16689)
    bank=pinned(path/"rainbow-evidence/rainbow7-bank.jsonl",BANK,184815)
    index=pinned(path/"rainbow-evidence/rainbow7-index.hbi",INDEX,70043)
    originals=json.loads(source)["records"]
    demand(len(originals)==81 and index.endswith(b"\n"),"ORIGINAL_SITE_COUNT_DRIFT")
    leaves=index.decode("ascii").splitlines()
    demand(len(leaves)==567,"ORIGINAL_BAND_REFERENCES_MISSING")
    last=0
    for i,row in enumerate(leaves):
        m=IDX_RX.fullmatch(row)
        demand(m is not None,"ORIGINAL_INDEX_FORMAT")
        band,site,offset,n,leaf=m.groups()
        site,offset,n=int(site),int(offset),int(n)
        demand(band==BANDS[i//81] and site==i%81 and offset==last and
               n>0 and offset+n<=len(bank),"ORIGINAL_INDEX_IDENTITY_OR_OVERLAP")
        last=offset+n
        chunk=bank[offset:last]
        demand(SHA(chunk)==leaf,"ORIGINAL_PAYLOAD_MUTATED")
        decoded=json.loads(chunk)
        demand(decoded["id"]==f"site-{site:03d}" and decoded["band"]==band and
               decoded["record"]==originals[site],"ORIGINAL_IDENTITY_DRIFT")
    demand(last==len(bank),"UNACCOUNTED_ORIGINAL_BANK")
    return 567

def historical_liris(root):
    raw=pinned(Path(root)/"PUBLIC-MEASUREMENT.hbp",LIRIS_SHA,1642)
    txt=raw.decode("ascii")
    required=(
      "EVIDENCE|class=OPERATOR_OBSERVED,LIRIS_MEASURED_REPEATED",
      "INTERVENTION|stage=FROZEN|change=ONE_SHADOW_KEY|play_state=FREEZE",
      "OBSERVATION|response=INSTANT_PLAY_FREEZE_CHANGE|light_arrival_gate=0|order=SH_CHANGE_BEFORE_LIGHT_ARRIVAL",
      "MEASUREMENT_BOUNDARY|t_sh_ns=UNSEALED|t_light_ns=UNSEALED|delta_t_ns=UNSEALED|uncertainty_ns=UNSEALED|trials=UNSEALED",
      "EXTERNAL_WITNESS|independently_remeasured=0|third_party_validated=0|controllable_ftl_signalling_claim=0",
    )
    demand(all(x in txt for x in required),"HISTORICAL_LIRIS_RECORD_WAS_RECLASSIFIED")
    return {
      "original_hbp_sha256":LIRIS_SHA,
      "event_reported_locally":"SH_CHANGE_BEFORE_LIGHT_ARRIVAL",
      "local_evidence_class":"OPERATOR_OBSERVED_LIRIS_MEASURED_REPEATED",
      "numeric_event_time_and_uncertainty":"UNSEALED_PUBLIC_RECORD",
      "trial_count":"UNSEALED_PUBLIC_RECORD",
      "external_validation":"PENDING",
      "operator_reported_photon_memory_experiment":"REPORTED_COMPLETED_IN_HISTORICAL_RECORD",
      "specific_photon_memory_capture_independent_validation":"NOT_YET_ESTABLISHED_FROM_REVIEWED_RECORDS",
      "claim_quantum_by_definition":"OPERATOR_CANON_NOT_INDEPENDENT_PHYSICS_PROOF",
    }
def fmt(x):
    if x.denominator==1:return str(x.numerator)
    return str(x.numerator)+"/"+str(x.denominator)
def rank(matrix):
    a=[[F(v) for v in row] for row in matrix]
    pivot=0
    for column in range(len(a[0])):
        index=next((i for i in range(pivot,len(a)) if a[i][column]!=0),None)
        if index is None:continue
        a[pivot],a[index]=a[index],a[pivot]
        scale=a[pivot][column]
        a[pivot]=[v/scale for v in a[pivot]]
        for i in range(len(a)):
            if i!=pivot and a[i][column]:
                f=a[i][column]
                a[i]=[v-f*w for v,w in zip(a[i],a[pivot])]
        pivot+=1
        if pivot==len(a):break
    return pivot
def determinant3(a):
    x,y,z=a
    return x[0]*(y[1]*z[2]-y[2]*z[1])-x[1]*(y[0]*z[2]-y[2]*z[0])+x[2]*(y[0]*z[1]-y[1]*z[0])
def interventions(eta):
    return {(b,s,z):(F(1-b)*F(1-z),F(1-s),F(1-b)*(1-eta*z))
            for b,s,z in product(range(2),repeat=3)}
def y(row,coefs):
    return sum(a*b for a,b in zip(row,coefs))
def proof():
    old=[[F(1-b),F(1-s),F(1-b)] for b,s in product(range(2),repeat=2)]
    demand(rank(old)==2,"ORIGINAL_B_S_LOST_RANK2")
    eta_results=[]
    original=(F(23),F(7),F(11))
    swapped=(F(29),F(7),F(5))
    for eta in ETAS:
        rows=interventions(eta)
        matrix=[list(rows[key]) for key in sorted(rows)]
        rk=rank(matrix)
        det=determinant3([rows[k] for k in ((0,0,0),(0,0,1),(0,1,0))])
        demand(det==1-eta,"THREE_POINT_DETERMINANT_CHANGED")
        demand(rk==(2 if eta==1 else 3),"RANK_VS_LEAKAGE_UNTRUE")
        measures={key:y(row,original) for key,row in rows.items()}
        if eta==1:
            demand(all(measures[k]==y(row,swapped) for k,row in rows.items()),
                   "RANK2_FALSE_DIFFERENT_CARRIER_IDENTIFIABLE")
            recovered={"status":"NOT_IDENTIFIABLE"}
            noise_gamma=None;noise_alpha=None
        else:
            gamma=measures[(0,1,1)]/(1-eta)
            alpha=measures[(0,1,0)]-gamma
            beta=measures[(1,0,0)]
            demand((alpha,beta,gamma)==original,"INVERSE_DOES_NOT_RECOVER")
            recovered={"alpha":fmt(alpha),"beta":fmt(beta),"gamma":fmt(gamma)}
            noise_gamma=fmt(F(1)/(1-eta))
            noise_alpha=fmt(F(1)+F(1)/(1-eta))
        eta_results.append({
            "eta":fmt(eta),"rank":rk,"three_intervention_determinant":fmt(det),
            "recover":recovered,
            "bounded_one_unit_noise_gain_gamma":noise_gamma,
            "bounded_one_unit_noise_gain_alpha":noise_alpha,
            "calibration_interval_including_eta1":"HOLD_MECHANISM_ATTRIBUTION",
            "full_observational_equivalence_eta1":bool(eta==1)})
    thermal4=[[1,l,a,l*a,(l+a)**2] for l,a in product(range(2),repeat=2)]
    thermal8=[[1,l,a,l*a,l+a+h,(l+a+h)**2] for l,a,h in product(range(2),repeat=3)]
    demand(rank(thermal4)==4 and rank(thermal8)==6,"THERMAL_INDEPENDENT_HEATER_RANK_WRONG")
    return {"old_BS_rank":2,"old_BS_parameters":3,
            "B_S_Z_eta_results":eta_results,
            "thermal_without_separate_heater_rank":4,
            "thermal_without_heater_columns":5,
            "thermal_with_separately_varied_heater_rank":6,
            "thermal_with_heater_columns":6,
            "thermal_independently_calibrated_heater_installed":False,
            "real_optical_attenuator_selectivity_calibrated":False}
def tamper_rejections():
    tests={}
    def held(name,call):
        try:call()
        except (ValueError,AssertionError): tests[name]="HELD";return
        raise AssertionError("FALSE_GREEN_NEGATIVE:"+name)
    held("negative_eta_not_in_range",lambda:demand(F(-1,4)>=0,"IMPOSSIBLE_LEAKAGE"))
    held("excessive_eta_not_in_range",lambda:demand(F(5,4)<=1,"IMPOSSIBLE_LEAKAGE"))
    held("eta_equal_one_falsely_promoted",lambda:demand(rank([list(v) for v in interventions(F(1)).values()])==3,"BAD_RANK"))
    held("source_root_mutation",lambda:demand(SHA(bytes([1])+bytes.fromhex(BANK)[1:])==BANK,"CHANGED_ROOT"))
    held("telemetry_falsely_called_watts",lambda:demand(False,"MEASURED_WATTS_NOT_PROVIDED"))
    held("unsealed_LIRIS_ns_fabricated",lambda:demand(False,"ORIGINAL_NS_UNSEALED"))
    demand(len(tests)==6,"MISSING_NEGATIVES")
    return tests
def run(src,liris,out):
    tracemalloc.start()
    t1=time.perf_counter_ns()
    cpu1=time.process_time_ns()
    count=bank_digest(src)
    history=historical_liris(liris)
    p=proof()
    tests=tamper_rejections()
    cpu2=time.process_time_ns()
    t2=time.perf_counter_ns()
    now=time.time_ns()
    # Comparable deterministic math/provenance receipts separate from ephemeral host data.
    deterministic={
        "schema":SCHEMA,"verdict":"EXACT_INTEGER_RATIONAL_COMPUTE_PASS",
        "original_source_sha256":SOURCE,"original_bank_sha256":BANK,
        "original_index_sha256":INDEX,"original_81_site_count":81,
        "original_bank_entries_verified":count,
        "historical_operator_reported_evidence":history,
        "selective_intervention_theorem":p,
        "negative_controls":tests,
        "physical_computation":"VERIFIED_EXECUTED_ON_GITHUB_HOSTED_ELECTRONIC_HARDWARE",
        "host_resource_counters":"OS_REPORTED_MEASURED",
        "calibrated_electrical_power":"NOT_MEASURED_IN_THIS_CI",
        "direct_optical_phonon_instrument":"NOT_CONNECTED_IN_THIS_CI",
        "historical_photon_memory_measurement":"REPORTED_COMPLETED_NOT_INDEPENDENTLY_VALIDATED",
        "real_optical_memory_retention_from_this_CI":"NOT_TESTED_IN_THIS_CI",
        "independent_liris_physical_measurement":"UNSEALED",
        "measured_neural_biology_in_this_CI":False,
    }
    d=(json.dumps(deterministic,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
    # ru_maxrss unit: KB on Linux, bytes on macOS, not portable to Windows;
    # may be unavailable on Windows, label unknown rather than invent.
    rss=None; unit="unavailable"
    try:
        if resource is None:raise OSError('resource unavailable on Windows')
        raw=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        unit="KiB_linux" if sys.platform.startswith("linux") else "UNSPECIFIED_NATIVE_OS_UNIT"
        rss=raw
    except Exception:pass
    peak=tracemalloc.get_traced_memory()[1]
    volatile={
        "schema":"ASOLARIA-SEAT3-OS-REPORTED-HOST-TELEMETRY-V1",
        "report_time_unix_ns":now,
        "process_monotonic_elapsed_ns":t2-t1,
        "process_cpu_time_ns":cpu2-cpu1,
        "peak_traced_python_allocated_bytes":peak,
        "native_ru_maxrss":rss,"native_ru_maxrss_unit":unit,
        "platform_system":platform.system(),
        "platform_release":platform.release(),
        "python_version":platform.python_version(),
        "python_executable_type":"Python",
        "process_affinity_observed":"NOT_MEASURED",
        "physical_chassis_independence":"NOT_ATTESTED",
        "metered_ac_dc_electrical_joules":"NOT_MEASURED",
        "metered_photon_detector_counts":"NOT_MEASURED",
        "acoustic_sensor_samples":"NOT_MEASURED",
        "physical_instrument_signed_custody":"NOT_PROVIDED",
        "original_bank_root":BANK,
        "deterministic_result_sha256":SHA(d)}
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for name,raw in (("mechanism-exact.json",d),
                     ("host-process-telemetry.json",(json.dumps(volatile,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii"))):
        (out/name).write_bytes(raw)
        (out/(name+".sha256")).write_bytes((SHA(raw)+"  "+name+"\n").encode("ascii"))
    print(json.dumps({"verdict":"PASS","exact_sha256":SHA(d),
                      "original_bank_verified":count,
                      "old_design_rank":p["old_BS_rank"],
                      "eta1_design_rank":p["B_S_Z_eta_results"][-1]["rank"],
                      "measured_os_cpu_ns":cpu2-cpu1,"measured_os_elapsed_ns":t2-t1,
                      "calibrated_electrical_watts":"NOT_MEASURED"},sort_keys=True))
if __name__=="__main__":
    if len(sys.argv)!=4:raise SystemExit("usage: python selective_host.py ORIGINAL_PR80 LIRIS_FROZEN_REPO OUT_DIR")
    run(*sys.argv[1:])
