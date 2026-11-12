#!/usr/bin/env python3
"""Cross-language/cross-OS exact-byte acceptance, never a claim of measured photons."""
import hashlib
import json
from pathlib import Path
import sys

EXPECTED_HBP = "332e1eeb2d4de748c2e1da07729944fefe5b63589e9533b4c93b74d7cf3f5527"
EXPECTED_JSON = "5468eeb46d8f349e47f6bfda17bd4ac8ff3a2c3acd4eb896628779decb759ee2"
FILES = ("photon-electron.hbp", "results.json", "photon-electron.hbp.sha256", "results.json.sha256")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    folder = Path(path)
    raw = {name: (folder / name).read_bytes() for name in FILES}
    for name in FILES[:2]:
        digest = sha(raw[name])
        expected = raw[name + ".sha256"].decode("ascii")
        assert expected == f"{digest}  {name}\n", ("BAD_DIGEST_SIDECAR", path, name)
    assert sha(raw["photon-electron.hbp"]) == EXPECTED_HBP, "FROZEN_HBP_DRIFT"
    assert sha(raw["results.json"]) == EXPECTED_JSON, "FROZEN_JSON_DRIFT"
    data = json.loads(raw["results.json"])
    assert data["photon_hbp_sha256"] == EXPECTED_HBP
    assert data["retained_bank_bytes"] == 184815
    assert data["stored_bank_rows"] == 567 and data["original_memory_records"] == 81
    assert data["negative_controls_rejected"] == 12
    assert data["physical_computation_executed"] is True
    for name in ("physical_photon_detection_measured", "optical_storage_measured",
                 "electron_charge_physically_measured", "external_origin_authenticated",
                 "mcp_transport_real_server", "quantum_effect_verified"):
        assert data[name] is False, ("UNSUPPORTED_PHYSICAL_CLAIM", name)
    assert [x["bit_errors"] for x in data["scenarios"]] == [0, 239145, 57, 824, 0]
    assert [x["exact_rows"] for x in data["scenarios"]] == [567, 0, 514, 142, 567]
    hbp = raw["photon-electron.hbp"]
    assert len(hbp) == 6048391
    records = hbp.splitlines()
    assert len(records) == 2835
    count = {x["scenario"]: 0 for x in data["scenarios"]}
    for line in records:
        frame = json.loads(line)
        actual = bytes.fromhex(frame["readback_hex"])
        assert sha(actual) == frame["observed_row_sha256"]
        assert frame["photoelectrons_modeled"] <= frame["emitted_photons_modeled"]
        assert frame["mcp_request"]["method"] == "tools/call"
        assert frame["mcp_request"]["params"]["name"] == "electron.capture"
        assert frame["mcp_response"]["id"] == frame["mcp_request"]["id"]
        count[frame["scenario"]] += 1
    assert set(count.values()) == {567}, "INCOMPLETE_FRAME_SET"
    return raw


def main():
    assert len(sys.argv) in (3, 5), "usage: verify_dual.py py node [otheros-py otheros-node]"
    groups = [read(arg) for arg in sys.argv[1:]]
    for group in groups[1:]:
        for name in FILES:
            assert group[name] == groups[0][name], ("CROSS_LANGUAGE_OR_OS_DRIFT", name)
    print(json.dumps({"status": "PASS", "runs_compared": len(groups),
                      "frames": 2835, "full_bank_bytes": 184815,
                      "hbp_sha256": EXPECTED_HBP,
                      "photon_model_is_measured_hardware_photon_storage": False}, sort_keys=True))


if __name__ == "__main__":
    main()
