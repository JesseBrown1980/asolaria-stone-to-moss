#!/usr/bin/env python3
"""Public four-seat release audit. No private keys, credentials or hardware claims.

Verifies all published SHA-256 sidecars in the four computational seat receipts,
the consistent reported test counts, and the explicit physical/publication
limitations. Cryptographic checks of supported Ed25519 formats run separately
in the matching GitHub Actions job; Seat 2's original signed-byte encoding
remains unresolved and is NOT reported as verified.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"publication"/"2026-10-14"
STONE=ROOT/"stones"/"2026-10-14-rainbow81"
CK=ROOT/"tracking"/"checkins"
BASENAMES=[
 CK/"seat-1"/"20261014T163705Z"/"checkin.json",
 CK/"seat-1"/"20261014T163705Z"/"commit.json",
 STONE/"seat-1-20261014-computational-readiness.json",
 STONE/"seat-1-20261014-computational-readiness.hbp",
 STONE/"seat-1-20261014-computational-readiness.hbi",
 CK/"seat-2"/"20261014T160538Z.json",
 CK/"seat-2"/"20261014T160538Z.hbp",
 STONE/"seat-2-20261014-readiness.json",
 STONE/"seat-2-20261014-readiness.hbp",
 CK/"seat-3"/"20261014T163350Z"/"checkin.json",
 CK/"seat-3"/"20261014T163350Z"/"commit.json",
 STONE/"seat-3-20261014-local-preflight.json",
 STONE/"seat-3-20261014-local-preflight.hbp",
 CK/"seat-4"/"20261014T161859Z.json",
 CK/"seat-4"/"20261014T161859Z.hbp",
 STONE/"seat-4-20261014-readiness.json",
 STONE/"seat-4-20261014-readiness.sig.json",
 STONE/"stone-seat4-public-precommit-audit-20261014.hbp",
 STONE/"stone-seat4-public-precommit-audit-20261014.hbi",
 STONE/"quantum-gravity-81-full-CI-result.json",
 STONE/"quantum-gravity-81-compact-receipt.json",
 STONE/"stone-seat3-81-quantum-gravity-2026-10-14.hbp",
 STONE/"stone-seat3-81-quantum-gravity-2026-10-14.hbi",
]
HASH="031367b1da1a368dc7471141a9799b79c694a0c9900f65a047438ccaa5f76600"
def sha(data):
    return hashlib.sha256(data).hexdigest()
def verify(path):
    assert path.is_file(),f"Missing {path.relative_to(ROOT)}"
    side=path.with_name(path.name+".sha256")
    assert side.is_file(),f"Missing checksum {side.relative_to(ROOT)}"
    fields=side.read_text(encoding="ascii").strip().split()
    assert len(fields)==2 and fields[1]==path.name, f"Bad sidecar naming: {side}"
    digest=sha(path.read_bytes())
    assert digest==fields[0],f"Digest mismatch for {path}"
    return {"path":str(path.relative_to(ROOT)),"sha256":digest}
def read(path):
    return json.loads(path.read_text(encoding="utf-8"))
def main():
    files=[verify(path) for path in BASENAMES]
    registry=read(P/"STATUS.json")
    assert registry["schema"]=="ASOLARIA-FOUR-SEAT-COMPUTATIONAL-COMPLETION-V1"
    assert len(registry["seats"])==4
    assert all(s["physical_host_independently_attested"] is False for s in registry["seats"])
    assert registry["experimental_conclusions"]["three_physically_independent_hosts"]==0
    assert registry["experimental_conclusions"]["physical_common_challenge_issued"] is False
    assert registry["publication"]["huggingface_verified"]=="not_done"

    s1=read(STONE/"seat-1-20261014-computational-readiness.json")
    s2=read(STONE/"seat-2-20261014-readiness.json")
    s3=read(STONE/"seat-3-20261014-local-preflight.json")
    s4=read(STONE/"seat-4-20261014-readiness.json")
    assert s1["python_vs_node_agreement"]==4860 and s1["output_sha256"]==HASH
    assert s1["physical_host_independence_verified"] is False
    assert s2["agreements"]==s2["cases_python_vs_node"]==1620
    assert s2["explicit_smallstep_controls"]==1215
    assert s2["physical_host_independence_verified"] is False
    assert s3["agreements"]==4860 and s3["python_node_byte_agreement"] is True
    assert s3["independent_physical_host"] is False
    assert s4["result"]["csv_sha256"]=="e949b8560c9150d3c8a446bf5f675644439fcf7b29ab976b32ad3731337cfd43"
    assert (ROOT/"experiments"/"seat4"/"B-CHALLENGE.json").exists()
    qg=read(STONE/"quantum-gravity-81-full-CI-result.json")
    assert qg["bodies"]==81 and qg["status"]=="PASS"
    assert len(qg["sha_seeded_local_hidden_variable_waves"])==9
    assert len(qg["geometry_and_gravity_controls"]["spatial_waves"])==9
    assert "emergent physical gravity" in qg["not_tested"]
    doc=(P/"REPORT.md").read_text(encoding="utf-8")
    for fragment in ("1,620","4,860","729","42,688","Hugging Face","physical"):
        assert fragment in doc
    summary={
        "schema":"ASOLARIA-FOUR-SEAT-RELEASE-AUDIT-V1",
        "status":"PASS",
        "sha256_sidecars_verified":len(files),
        "seat1_parity":4860,
        "seat2_reported_parity":1620,
        "seat3_parity":4860,
        "seat4_parity":729,
        "seat2_signature_independently_verified":False,
        "physical_hosts_witnessed":0,
        "fresh_physical_challenge_issued":False,
        "hf_publication_verified":False,
        "result_sha256_seat1_seat3":HASH,
        "file_manifest":files,
        "note":"public computational results integrity; does not measure physical quantum/gravity/FTL"
    }
    print(json.dumps(summary,sort_keys=True,indent=2))
if __name__=="__main__":
    main()
