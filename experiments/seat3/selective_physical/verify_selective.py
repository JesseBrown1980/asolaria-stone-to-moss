#!/usr/bin/env python3
"""Independent third-party read-only validation of source→host→math receipts.

Does not import either implementation. Algebra by direct selected 3x3
determinant and modular rank, independent fresh 567 leaf-source checks.
Volatile process counters are checked separately, NOT byte compared across OS.
"""
from __future__ import annotations
import hashlib,json,itertools,re,sys
from pathlib import Path
from fractions import Fraction as F
SCHEMA="ASOLARIA-SEAT3-SELECTIVE-ATTENUATOR-PHYSICAL-HOST-V1"
SRC="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
INDEX="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"
LIRIS="d9b20742592e6fdcb26c03278bd9d574636f4f9f05b24cf502ad173d20e5579f"
BANDS=["red","orange","yellow","green","blue","indigo","violet"]
IDX=re.compile(r"MEM\|band=(red|orange|yellow|green|blue|indigo|violet)\|id=site-(\d{3})\|offset=(\d+)\|length=(\d+)\|sha256=([a-f0-9]{64})\Z")
def sha(b):return hashlib.sha256(b).hexdigest()
def require(ok,why):
    if not ok:raise ValueError(why)
def source_check(pr80,liris):
    root=Path(pr80)
    paths=[
        (root/"base-evidence/lightbank-memories.json",SRC,16689),
        (root/"rainbow-evidence/rainbow7-bank.jsonl",BANK,184815),
        (root/"rainbow-evidence/rainbow7-index.hbi",INDEX,70043),
        (Path(liris)/"PUBLIC-MEASUREMENT.hbp",LIRIS,1642)]
    blobs=[]
    for p,s,n in paths:
        data=p.read_bytes()
        require(len(data)==n and sha(data)==s,"HISTORICAL_ROOT_MISMATCH")
        blobs.append(data)
    originals=json.loads(blobs[0])["records"]
    require(len(originals)==81,"MISSING_ORIGINAL_IDENTITIES")
    entries=blobs[2].decode("ascii").splitlines()
    require(len(entries)==567 and blobs[2].endswith(b"\n"),"NOT_567_ORIGINAL_LEAVES")
    prev=0
    for i,row in enumerate(entries):
        m=IDX.fullmatch(row)
        require(m is not None,"BAD_FROZEN_INDEX_ROW")
        name,site,offset,n,leaf=m.groups()
        site,offset,n=int(site),int(offset),int(n)
        require(name==BANDS[i//81] and site==i%81 and offset==prev and n>0,"BAD_INDEX_ORDER")
        prev=offset+n
        raw=blobs[1][offset:prev]
        require(len(raw)==n and sha(raw)==leaf,"HISTORICAL_SOURCE_LEAF_TAMPERED")
        obj=json.loads(raw)
        require(obj["id"]==f"site-{site:03d}" and obj["band"]==name and
                obj["record"]==originals[site],"FROZEN_MEMORY_CHANGED")
    require(prev==len(blobs[1]),"SOURCE_BANK_TRAILING_BYTES")
    receipt=blobs[3].decode("ascii")
    require("LIRIS_MEASURED_REPEATED" in receipt and
            "t_sh_ns=UNSEALED" in receipt and "trials=UNSEALED" in receipt and
            "third_party_validated=0" in receipt,"HISTORICAL_UNSEALED_ERASED")
def minor3(rows):
    a,b,c=rows
    return (a[0]*(b[1]*c[2]-b[2]*c[1])-
            a[1]*(b[0]*c[2]-b[2]*c[0])+
            a[2]*(b[0]*c[1]-b[1]*c[0]))
def modular_rank(rows,p=1000003):
    a=[[int(x)%p for x in row] for row in rows]
    rank=0
    for j in range(len(a[0])):
        index=next((i for i in range(rank,len(a)) if a[i][j]),None)
        if index is None:continue
        a[rank],a[index]=a[index],a[rank]
        inv=pow(a[rank][j],p-2,p)
        a[rank]=[(x*inv)%p for x in a[rank]]
        for i in range(len(a)):
            if i==rank or not a[i][j]:continue
            factor=a[i][j]
            a[i]=[(u-factor*v)%p for u,v in zip(a[i],a[rank])]
        rank+=1
        if rank==len(a):break
    return rank
def mathematical_check(receipt):
    t=receipt["selective_intervention_theorem"]
    require(t["old_BS_rank"]==2 and t["old_BS_parameters"]==3,"OLD_RANK_CHANGE")
    cases=t["B_S_Z_eta_results"]
    etas=[F(0),F(1,4),F(1,2),F(3,4),F(7,8),F(15,16),F(1)]
    require(len(cases)==len(etas),"MISSING_ETA_FAMILY")
    for entry,eta in zip(cases,etas):
        expected=str(eta)
        require(entry["eta"]==expected,"ETA_NOT_PREDECLARED")
        rows={(B,S,Z):[F((1-B)*(1-Z)),F(1-S),F(1-B)*(1-eta*Z)]
              for B,S,Z in itertools.product((0,1),repeat=3)}
        det=minor3([rows[k] for k in [(0,0,0),(0,0,1),(0,1,0)]])
        require(det==1-eta and entry["three_intervention_determinant"]==str(det),
                "SELECTIVE_INTERVENTION_DETERMINANT_FALSE")
        if eta!=1:
            require(entry["rank"]==3 and det!=0,"NEW_DESIGN_MUST_BE_IDENTIFIABLE_IN_STATED_MODEL")
            gamma=(F(23)+F(11)*(1-eta)-F(23))/(1-eta)
            alpha=F(23)+F(11)-gamma
            beta=F(7)
            require(entry["recover"]=={"alpha":str(alpha),"beta":str(beta),"gamma":str(gamma)},
                    "FROZEN_COEFFICIENT_NOT_RECOVERED")
            require(entry["bounded_one_unit_noise_gain_gamma"]==str(1/(1-eta)) and
                    entry["bounded_one_unit_noise_gain_alpha"]==str(1+1/(1-eta)),
                    "UNCERTAINTY_AMPLIFICATION_FALSE")
        else:
            require(entry["rank"]==2 and det==0 and entry["recover"]=={"status":"NOT_IDENTIFIABLE"},
                    "ETA_ONE_FALSE_IDENTIFIABILITY")
            for row in rows.values():
                require(sum(a*b for a,b in zip(row,(23,7,11)))==
                        sum(a*b for a,b in zip(row,(29,7,5))),"RANK2_SWAP_NOT_EQUIVALENT")
        require(entry["calibration_interval_including_eta1"]=="HOLD_MECHANISM_ATTRIBUTION","FRAUDULENT_SELECTIVITY")
    four=[[1,l,a,l*a,(l+a)**2] for l,a in itertools.product(range(2),repeat=2)]
    eight=[[1,l,a,l*a,l+a+h,(l+a+h)**2] for l,a,h in itertools.product(range(2),repeat=3)]
    require(modular_rank(four)==4 and modular_rank(eight)==6 and
            t["thermal_without_separate_heater_rank"]==4 and
            t["thermal_with_separately_varied_heater_rank"]==6,"THERMAL_RANK_MISMATCH")
    require(t["real_optical_attenuator_selectivity_calibrated"] is False and
            t["thermal_independently_calibrated_heater_installed"] is False,
            "FICTITIOUS_REAL_INSTRUMENT")
def audit(pr80,liris,python_out,node_out,dest):
    source_check(pr80,liris)
    py=Path(python_out);node=Path(node_out)
    body=(py/"mechanism-exact.json").read_bytes()
    require(body==(node/"mechanism-exact.json").read_bytes(),"TWO_LANGUAGES_DIFFER")
    for p in (py,node):
        require((p/"mechanism-exact.json.sha256").read_bytes()==
                (sha(body)+"  mechanism-exact.json\n").encode("ascii"),"HASH_SIDECAR_DRIFT")
    result=json.loads(body)
    require(result["schema"]==SCHEMA and result["verdict"]=="EXACT_INTEGER_RATIONAL_COMPUTE_PASS",
            "BAD_MODEL_SCHEMA")
    require(result["original_source_sha256"]==SRC and result["original_bank_sha256"]==BANK and
            result["original_index_sha256"]==INDEX and result["original_bank_entries_verified"]==567,
            "SOURCE_TO_RECEIPT_BROKEN")
    history=result["historical_operator_reported_evidence"]
    require(history["original_hbp_sha256"]==LIRIS and
            history["local_evidence_class"]=="OPERATOR_OBSERVED_LIRIS_MEASURED_REPEATED" and
            history["numeric_event_time_and_uncertainty"]=="UNSEALED_PUBLIC_RECORD" and
            history["trial_count"]=="UNSEALED_PUBLIC_RECORD" and
            history["external_validation"]=="PENDING" and
            history["operator_reported_photon_memory_experiment"]==
                   "REPORTED_COMPLETED_BY_OPERATOR_SEPARATE_FROM_LIRIS_RECEIPT" and
            history["specific_photon_memory_capture_independent_validation"]==
                   "NOT_YET_ESTABLISHED_FROM_REVIEWED_RECORDS",
            "OPERATOR_HISTORY_CONFLATED_OR_ERASED")
    require(result["historical_photon_memory_measurement"]==
            "REPORTED_COMPLETED_NOT_INDEPENDENTLY_VALIDATED","MISREPORTED_HISTORICAL_EXPERIMENT")
    require(result["physical_computation"]=="VERIFIED_EXECUTED_ON_GITHUB_HOSTED_ELECTRONIC_HARDWARE" and
            result["calibrated_electrical_power"]=="NOT_MEASURED_IN_THIS_CI" and
            result["direct_optical_phonon_instrument"]=="NOT_CONNECTED_IN_THIS_CI" and
            result["real_optical_memory_retention_from_this_CI"]=="NOT_TESTED_IN_THIS_CI",
            "FAKE_PHYSICAL_EVIDENCE_PROMOTION")
    mathematical_check(result)
    require(sum(v=="HELD" for v in result["negative_controls"].values())==6,
            "NEGATIVE_CONTROLS_INCOMPLETE")
    telemetry=json.loads((py/"host-process-telemetry.json").read_bytes())
    require(telemetry["schema"]=="ASOLARIA-SEAT3-OS-REPORTED-HOST-TELEMETRY-V1","NO_HOST_TELEMETRY")
    require(telemetry["original_bank_root"]==BANK and
            telemetry["deterministic_result_sha256"]==sha(body),"SOURCE_HOST_JOIN_FAILURE")
    for k in ("process_monotonic_elapsed_ns","process_cpu_time_ns","peak_traced_python_allocated_bytes"):
        require(isinstance(telemetry[k],int) and telemetry[k]>0,"HOST_COUNTER_UNMEASURED:"+k)
    require(telemetry["process_cpu_time_ns"]>=0 and
            telemetry["report_time_unix_ns"]>0,"TELEMETRY_BAD_CLOCK")
    for k in ("metered_ac_dc_electrical_joules","metered_photon_detector_counts",
              "acoustic_sensor_samples"):
        require(telemetry[k]=="NOT_MEASURED","PHYSICAL_MEASUREMENT_WAS_INVENTED")
    require(telemetry["physical_chassis_independence"]=="NOT_ATTESTED" and
            telemetry["physical_instrument_signed_custody"]=="NOT_PROVIDED",
            "FAKE_PHYSICAL_HOST_OR_SENSOR_ATTESTATION")
    path=Path(dest);path.mkdir(parents=True,exist_ok=True)
    (path/"mechanism-exact.json").write_bytes(body)
    (path/"mechanism-exact.json.sha256").write_bytes(
        (sha(body)+"  mechanism-exact.json\n").encode("ascii"))
    # The hardware telemetry genuinely varies by OS/runtime/job.
    telem=(py/"host-process-telemetry.json").read_bytes()
    (path/"host-process-telemetry.json").write_bytes(telem)
    (path/"host-process-telemetry.json.sha256").write_bytes(
        (sha(telem)+"  host-process-telemetry.json\n").encode("ascii"))
    metrics={
        "status":"THIRD_SOURCE_HOST_ALGEBRA_AND_TELEMETRY_PASS",
        "verified_historical_bank_entries":567,
        "liris_local_report_preserved":True,
        "historical_photon_memory_report":"OPERATOR_REPORTED_COMPLETED",
        "calibrated_photon_memory_capture_externally_verified":False,
        "source_to_volatile_os_report_linked":True,
        "rank_old":2,"rank_eta_zero":3,"rank_eta_one":2,
        "thermal_rank_with_independent_heater_model":6,
        "exact_model_sha256":sha(body),
        "real_electrical_or_photon_power_meter":"NOT_CONNECTED_IN_THIS_CI"
    }
    raw=(json.dumps(metrics,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")
    name="independent-exact-audit.json"
    (path/name).write_bytes(raw)
    (path/(name+".sha256")).write_bytes((sha(raw)+"  "+name+"\n").encode("ascii"))
    print(json.dumps(metrics,sort_keys=True))
if __name__=="__main__":
    if len(sys.argv)!=6:raise SystemExit("usage: python verify_selective.py PR80 LIRIS PY_DIR NODE_DIR OUT")
    audit(*sys.argv[1:])
