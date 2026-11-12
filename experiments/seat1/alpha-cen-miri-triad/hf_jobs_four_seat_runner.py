#!/usr/bin/env python3
"""Run one Asolaria JWST/MIRI *logical* seat on HF Jobs or any Python host.

Fetches the exact reviewed scripts at a pinned Git commit, validates Git blob
identity, performs read-only MAST metadata inventory and the selected audit.
Does not download/calibrate JWST science FITS, train a model or publish to HF.
Requires only Python standard library and public HTTPS; no token is required.
"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import urllib.request

OWNER = "JesseBrown1980"
REPO = "asolaria-stone-to-moss"
COMMIT = "f9b4263f4ad422d0b561b04e580b40340c3a5fc6"
SOURCE_PATH = "experiments/seat1/alpha-cen-miri-triad"
SCRIPTS = {
    "mast_inventory.py": "593799c03d1f9738be8aeb88f68f13e9f6b621c8",
    "four_seat_audit.py": "b4bdcbc25b160fdf20b26187e20d1eb836570516",
}

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def verified_download(name: str, dest: pathlib.Path) -> None:
    if name not in SCRIPTS:
        raise ValueError("unapproved script")
    url = (f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{COMMIT}/"
           f"{SOURCE_PATH}/{name}")
    req = urllib.request.Request(url, headers={"User-Agent": "Asolaria-HF-Frozen-Seat"})
    with urllib.request.urlopen(req, timeout=75) as response:
        data = response.read(120_000)
    if not 100 < len(data) < 120_000:
        raise RuntimeError("SOURCE_SIZE_REJECT")
    if git_blob_sha(data) != SCRIPTS[name]:
        raise RuntimeError("FROZEN_SOURCE_GIT_BLOB_MISMATCH:" + name)
    dest.write_bytes(data)
    print("VERIFIED_SOURCE", name, "git_blob=" + SCRIPTS[name], flush=True)

def run(args: argparse.Namespace) -> dict:
    destination = pathlib.Path(args.out).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="asolaria-hf-seat-") as tmp:
        folder = pathlib.Path(tmp)
        for name in SCRIPTS:
            verified_download(name, folder / name)
        if not args.skip_self_test:
            for name in SCRIPTS:
                subprocess.run([sys.executable, str(folder / name), "--self-test"],
                               check=True, timeout=180)
        inv = folder / "inventory"
        if args.manifest_dir:
            inv = pathlib.Path(args.manifest_dir).resolve()
            print("MANIFEST_SOURCE", "provided-directory", flush=True)
        else:
            inv.mkdir()
            subprocess.run([sys.executable, str(folder / "mast_inventory.py"),
                            "--out", str(inv)], check=True, timeout=650)
        original = (inv / "MAST-THREE-EPOCH-INVENTORY.hbp").read_bytes()
        expected = (inv / "MAST-THREE-EPOCH-INVENTORY.hbp.sha256").read_text().split()[0]
        root_sha = sha256(original)
        if expected != root_sha:
            raise RuntimeError("MAST_HBP_SOURCE_HASH_MISMATCH")
        if args.expect_inventory_sha and root_sha != args.expect_inventory_sha:
            raise RuntimeError("LIVE_INVENTORY_CHANGED_VS_EXPECTED_SHA")
        subprocess.run([sys.executable, str(folder / "four_seat_audit.py"),
                        "--seat", str(args.seat), "--in-dir", str(inv),
                        "--out-dir", str(destination)], check=True, timeout=180)
    artifact = destination / f"SEAT{args.seat}-MIRI-CATCHUP.hbp"
    data = artifact.read_bytes()
    expected_receipt_sha = (destination / (artifact.name + ".sha256")).read_text().split()[0]
    if sha256(data) != expected_receipt_sha:
        raise RuntimeError("SEAT_RECEIPT_HASH_MISMATCH")
    result = {
        "seat": args.seat, "source_commit": COMMIT,
        "source_inventory_sha256": root_sha,
        "receipt_sha256": expected_receipt_sha,
        "digital_seat_audit": "PASS",
        "original_fits_reconstruction": "PENDING",
        "physical_host_independence": "NOT_ATTESTED",
        "hf_write_readback": "NOT_ATTEMPTED",
    }
    (destination / f"SEAT{args.seat}-HF-JOB-SUMMARY.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("ASOLARIA_HF_RESULT", json.dumps(result, sort_keys=True), flush=True)
    print("HBP_RECEIPT_BEGIN\n" + data.decode() + "HBP_RECEIPT_END", flush=True)
    return result

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seat", type=int, choices=(1, 2, 3, 4), required=True)
    parser.add_argument("--out", default="seat-output")
    parser.add_argument("--manifest-dir", default=None,
                        help="Optional local immutable manifest directory (for offline replay)")
    parser.add_argument("--expect-inventory-sha", default=None,
                        help="Optional pinned expected SHA-256: fail closed if MAST changed")
    parser.add_argument("--skip-self-test", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        assert git_blob_sha(b"hello") == hashlib.sha1(b"blob 5\0hello").hexdigest()
        assert len(COMMIT) == 40
        assert sorted(SCRIPTS) == ["four_seat_audit.py", "mast_inventory.py"]
        assert all(len(d) == 40 for d in SCRIPTS.values())
        print("HF_SEAT_RUNNER_OFFLINE_SELF_TEST_PASS")
        return
    run(args)

if __name__ == "__main__":
    main()
