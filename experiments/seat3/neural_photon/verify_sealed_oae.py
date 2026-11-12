#!/usr/bin/env python3
"""Require append-only OAE proof stone to match FRESH cross-host computation.

The historical original bank and calculated outputs remain separate. This
only seals numerical simulation and explicit NON-physical status.
"""
import hashlib,json,sys
from pathlib import Path

STONE="745eaaf5ccad7df88d01f3a41f4f8030f3bb67671a4beca1e3849397c81be2a2"
HBP="f766c413ac6c959821f2771bf84f61105f68a81f2793f1dee8c2ffa90dc0cc60"
J="4aca572509d12d368f445849f45d4401929e9ab42a5c2dc536138901a356ac59"
AUDIT="66c050514bfe886699f18ac08a7342cd2c69872963a0d6ebc55f1795aa53e04b"
ROOT="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"

def sha(b):return hashlib.sha256(b).hexdigest()
def verify(stone,result):
    stone=Path(stone)
    buf=stone.read_bytes()
    assert len(buf)==1029 and sha(buf)==STONE,"EVIDENCE_STONE_DRIFT"
    side=(stone.parent/(stone.name+".sha256")).read_bytes()
    assert side==(STONE+"  "+stone.name+"\n").encode("ascii"),"STONE_SIDECAR_CHANGED"
    rows=buf.decode("ascii").splitlines()
    assert len(rows)==10
    assert rows[0]=="PORTAL|schema=ASOLARIA-SEAT3-OAE-FACTORIAL-VERIFIED-20261015|digital_simulation=1|external_optics=0"
    assert rows[-1]=="END|main_history_unchanged=1|peer_review=PENDING|pr95=DRAFT"
    out=Path(result)
    names=[
      ("photon-phonon-electronic-toy.hbp",14272434,HBP),
      ("photon-phonon-electronic-toy.json",3538,J),
      ("independent-factorial-audit.json",478,AUDIT)]
    for name,n,h in names:
        data=(out/name).read_bytes()
        assert len(data)==n and sha(data)==h,"COMPUTED_RECEIPT_MISMATCH:"+name
        assert (out/(name+".sha256")).read_bytes()==(h+"  "+name+"\n").encode("ascii")
    d=json.loads((out/"photon-phonon-electronic-toy.json").read_bytes())
    a=json.loads((out/"independent-factorial-audit.json").read_bytes())
    assert d["bank_567_sha256"]==ROOT and d["total_simulated_rows"]==81648
    assert d["model_trace_bytes"]==14272434 and d["model_trace_sha256"]==HBP
    assert a["verdict"]=="INDEPENDENT_OAE_FACTORIAL_AUDIT_PASS"
    assert a["raw_sha256"]==HBP and a["receipt_sha256"]==J
    assert a["new_external_physical_observations"]==0
    assert a["direct_toy_oa_contrast_60s"]==30
    assert a["afterglow_oa_contrast_60s"]==0
    assert a["thermal_mimic_raw_contrast_60s"]==30
    assert a["thermal_mimic_optical_contrast_60s"]==0
    for field in ("real_optical_capture","real_acoustic_capture",
                  "real_photon_phonon_coupling","physical_optical_memory_retention",
                  "biological_neural_memory"):
        assert d[field]=="NOT_RUN"
    required=[
      f"SOURCE|records=81|bank_rows=567|bank_sha256={ROOT}",
      "AXES|O=2|A=2|E=2|bands=7|sites=81|nominal_delays=1,10,60|models=6|rows=81648",
      "INTERACTION|direct_electronic60=30|direct_optical60=30|thermal_mimic_electronic60=30|thermal_mimic_optical60=0|fast_decay60=0",
      f"HBP|bytes=14272434|sha256={HBP}",
      f"JSON|bytes=3538|sha256={J}",
      f"AUDIT|bytes=478|sha256={AUDIT}",
      "BOUNDARY|wavelength_nm=NOT_MEASURED|acoustic_displacement=NOT_MEASURED|electronic_optical_custody=NOT_ATTESTED|real_retention=NOT_RUN|neurons=NOT_MEASURED"
    ]
    assert all(x in rows for x in required),"SEALED_SUMMARY_TO_FRESH_RESULTS_MISMATCH"
    print(json.dumps({"verdict":"SEALED_OAE_DIGITAL_TEST_PASS",
      "stone_sha256":STONE,"full_trace_sha256":HBP,"source_rows":81648,
      "real_physical_observations":0},sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: verify_sealed_oae.py STONE.hbp FRESH_RESULTS_DIR")
    verify(*sys.argv[1:])
