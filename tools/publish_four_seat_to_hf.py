#!/usr/bin/env python3
"""Normal Hugging Face Hub repository upload, without paid HF Jobs.

Manual GitHub Actions workflow, or on your own computer:
    HF_TOKEN=<provided-securely> python tools/publish_four_seat_to_hf.py

The token must be held in an environment secret; never committed to git.
Stages only public, fixed code/results; verifies source .sha256 sidecars,
uploads to two HF repositories and then downloads all remote files to verify.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
STONE=ROOT/"stones"/"2026-10-14-rainbow81"
OWNER="Jessedbrown"
TARGETS=(OWNER+"/asolaria-wasm81-rainbow-audit",OWNER+"/tests")
PREFIX="experiments/2026-10-14/four-seat-release"
CREDIT="public software tests only; no physical host, quantum, gravitational, or FTL measurements"
RECEIPTS=(
 "seat-1-20261014-computational-readiness.hbi",
 "seat-1-20261014-computational-readiness.hbp",
 "seat-1-20261014-computational-readiness.json",
 "seat-2-20261014-readiness.hbp",
 "seat-2-20261014-readiness.json",
 "seat-3-20261014-local-preflight.hbp",
 "seat-3-20261014-local-preflight.json",
 "seat-4-20261014-readiness.json",
 "seat-4-20261014-readiness.sig.json",
 "stone-seat4-public-precommit-audit-20261014.hbp",
 "stone-seat4-public-precommit-audit-20261014.hbi",
 "quantum-gravity-81-full-CI-result.json",
 "quantum-gravity-81-compact-receipt.json",
 "stone-seat3-81-quantum-gravity-2026-10-14.hbp",
 "stone-seat3-81-quantum-gravity-2026-10-14.hbi",
)
DOCUMENTS=(
 "PUBLICATION-INDEX.md",
 "publication/2026-10-14/REPORT.md",
 "publication/2026-10-14/STATUS.json",
 "stones/2026-10-14-rainbow81/RESULTS-INDEX.md",
 "physical/README.md",
 "physical/evolve_gf2_python.py",
 "physical/evolve_gf2_node.js",
 "physical/verify_seat1_computational.py",
 "physical/verify_seat4_public_precommit.py",
 "experiments/seat3/verify_public_seat3.js",
 "experiments/seat4/verify_seat4.py",
 "experiments/seat3/two_horizon_matrix.py",
 "experiments/seat3/two_horizon_polynomial.js",
 "stones/2026-10-14-rainbow81/seat-3-two-horizon-9720-control.json",
 "publication/2026-10-14/SEAT3-9720-ADDENDUM.md",
 "experiments/test_81_quantum_gravity_controls.py",
 "experiments/EVALUATION-81-QUANTUM-GRAVITY-2026-10-14.md",
)
EXPECTED_QG81_SHA="f3c634d62c8ebb634aa6fbd04503f94c2bee3cc1269880a6b69b4db896234dd0"

def digest(data):
    return hashlib.sha256(data).hexdigest()

def stage(folder):
    """Produce a self-contained public package. No token needed to stage."""
    folder=Path(folder)
    inventory={}
    def include(file,relative):
        data=file.read_bytes()
        target=folder/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
        inventory[relative]=digest(data)
    for name in RECEIPTS:
        path=STONE/name
        data=path.read_bytes()
        side=path.with_name(path.name+".sha256")
        fields=side.read_text(encoding="ascii").split()
        if len(fields)!=2 or fields[0]!=digest(data) or fields[1]!=path.name:
            raise ValueError("SHA256 sidecar mismatch: "+name)
        include(path,"stones/"+name)
        include(side,"stones/"+name+".sha256")
    if inventory["stones/quantum-gravity-81-full-CI-result.json"]!=EXPECTED_QG81_SHA:
        raise ValueError("QG81 original multi-Python CI digest mismatch")
    for rel in DOCUMENTS:
        include(ROOT/rel,rel)
    # Recreate the newer Seat 3 9,720-row HBP from two distinct algorithms.
    # This is a follow-on SOFTWARE control; it is not a new physical-host seat.
    followon=json.loads((STONE/"seat-3-two-horizon-9720-control.json").read_text(encoding="utf-8"))
    expected="245ab02b30cbdd9215d161c6561adc6a6c3bf72dd3fa2cb62979b2fb74031cef"
    if not (followon.get("exact_state_agreements")==9720
            and followon.get("disagreements")==0
            and followon.get("modeled_horizons")==[10**13,10**13+1]
            and followon.get("output_sha256_python")==expected
            and followon.get("output_sha256_node")==expected
            and followon.get("physical_host_independent") is False):
        raise ValueError("Seat 3 follow-on receipt disagrees with pinned software classification")
    with tempfile.TemporaryDirectory(prefix="seat3-reproduce-") as temp:
        p=Path(temp)/"python.hbp"
        n=Path(temp)/"node.hbp"
        py=subprocess.run(["python",str(ROOT/"experiments/seat3/two_horizon_matrix.py"),str(p)],
                          cwd=ROOT,capture_output=True,text=True,check=True,timeout=120)
        node=subprocess.run(["node",str(ROOT/"experiments/seat3/two_horizon_polynomial.js"),str(n)],
                            cwd=ROOT,capture_output=True,text=True,check=True,timeout=120)
        sp=json.loads(py.stdout.strip())
        sn=json.loads(node.stdout.strip())
        if sp!=sn or sp.get("records")!=9720 or sp.get("sha256")!=expected:
            raise ValueError("Seat 3 follow-on independent output summary mismatch")
        raw=p.read_bytes()
        if len(raw)!=1195980 or raw!=n.read_bytes() or digest(raw)!=expected:
            raise ValueError("Seat 3 follow-on two-language HBP byte/SHA mismatch")
        full=folder/"computed"/"seat3-two-horizon-9720.hbp"
        full.parent.mkdir(parents=True,exist_ok=True)
        full.write_bytes(raw)
        inventory["computed/seat3-two-horizon-9720.hbp"]=expected
    readme=(
        "# Asolaria — four-seat computational reproducibility archive\n\n"
        "Software verification receipts with SHA256 manifests and test code.\n"
        "Seat 1: 4,860-case parity (new five-tap fixture).\n"
        "Seat 2: 1,620 reported cases (original Ed25519 serialization unresolved).\n"
        "Seat 3: 4,860-case parity (new five-tap fixture).\n"
        "Seat 4: 729-case parity (older public B-challenge).\n"
        "Separate Seat 3 follow-on: 9,720 two-horizon rows under new stress taps;\n"
        "independently rebuilt full HBP and exact hash are in computed/.\n\n"
        "**No independently attested physical three-host experiment, entanglement,\n"
        "physical gravity or faster-than-light communication is claimed.**\n"
        "The source report distinguishes incompatible inputs and law sets.\n\n"
        "Source: https://github.com/JesseBrown1980/asolaria-stone-to-moss\n"
        "Independent release CI: https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38644568103\n"
    ).encode()
    (folder/"README.md").write_bytes(readme)
    inventory["README.md"]=digest(readme)
    manifest={
        "schema":"ASOLARIA-FOUR-SEAT-HF-HUB-RELEASE-V1",
        "date":"2026-10-14",
        "source_repo":"JesseBrown1980/asolaria-stone-to-moss",
        "git_revision":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "scope":CREDIT,
        "destinations":list(TARGETS),
        "path_prefix":PREFIX,
        "files_sha256":inventory,
        "post_upload_verified":False,
    }
    (folder/"MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return manifest

def publish():
    # Import only on upload; staging remains stdlib-only and free.
    from huggingface_hub import HfApi,hf_hub_download
    token=os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("Missing HF_TOKEN protected GitHub Actions secret. Upload not attempted.")
    api=HfApi(token=token)
    if api.whoami().get("name","").casefold()!=OWNER.casefold():
        raise RuntimeError("Hub token belongs to another account; no upload attempted.")
    with tempfile.TemporaryDirectory(prefix="asolaria-release-") as d:
        manifest=stage(d)
        print("LOCAL_STAGE_OK",len(manifest["files_sha256"]),"files")
        for repo in TARGETS:
            api.create_repo(repo_id=repo,repo_type="model",private=False,exist_ok=True)
            api.upload_folder(
                folder_path=d,repo_id=repo,repo_type="model",
                path_in_repo=PREFIX,
                commit_message="Asolaria four-seat software reproducibility release")
            found=set(api.list_repo_files(repo_id=repo,repo_type="model"))
            for rel,expected in manifest["files_sha256"].items():
                remote=PREFIX+"/"+rel
                if remote not in found:
                    raise RuntimeError("Uploaded file absent: "+remote)
                actual=Path(hf_hub_download(repo_id=repo,repo_type="model",
                                            filename=remote,token=token,
                                            force_download=True)).read_bytes()
                if digest(actual)!=expected:
                    raise RuntimeError("Remote SHA256 mismatch: "+remote)
            if PREFIX+"/MANIFEST.json" not in found:
                raise RuntimeError("Remote manifest missing")
            print("PUBLISHED_AND_REMOTE_SHA_VERIFIED",
                  "https://huggingface.co/"+repo+"/tree/main/"+PREFIX,
                  "files",len(manifest["files_sha256"])+1)
        print("HF_FOUR_SEAT_BOTH_REPOS_PUBLISHED_VERIFIED")

if __name__=="__main__":
    if os.environ.get("HF_PUBLISH_DRY_RUN")=="1":
        with tempfile.TemporaryDirectory(prefix="asolaria-release-dryrun-") as d:
            m=stage(d)
            print("LOCAL_STAGE_ONLY_PASS",len(m["files_sha256"]),"hash-checked files")
            print("PHYSICAL_EXPERIMENT_COMPLETE false")
    else:
        publish()
