#!/usr/bin/env python3
"""Seat 1 external readback adjudicator (no coupling.py or coupling.js imports).

Audits all actual per-bit readback bytes against the frozen bank, and the
authorization signals against separately recomputed source hashes/LIF witness.
A pass is *only* a deterministic software-model consistency result.
"""
import hashlib
import json
import sys
from pathlib import Path

PIN_BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
PIN_INDEX="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"
PIN_SOURCE="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
BANDS=("red","orange","yellow","green","blue","indigo","violet")
ARMS=("reference_bright","baseline_t0","resonant_phase0","resonant_phase180",
      "off_resonance","thermal_sham","detector_dark_noise","optical_dark",
      "acoustic_only","held_t3","held_t3_resonant","held_t3_erased")

def sha(b):return hashlib.sha256(b).hexdigest()
def require(x,reason):
    if not x:raise AssertionError(reason)

def LIF(raw):
    # Completely separate byte/bit loop from the producer/Node verifier.
    state=0
    spikes=0
    bins=[]
    for pos in range(8*len(raw)):
        bit=(raw[pos//8]>>(7-(pos%8)))&1
        state=max(0,state-1)+4*bit
        if state>=7:
            spikes+=1
            state-=7
        if pos%32==31:
            bins.append(spikes)
            spikes=0
    if len(raw)*8%32:bins.append(spikes)
    return bytes(bins)

def main(root,output):
    evidence=Path(root)
    original=(evidence/"original-evidence/lightbank-memories.json").read_bytes()
    bank=(evidence/"rainbow-evidence/rainbow7-bank.jsonl").read_bytes()
    index=(evidence/"rainbow-evidence/rainbow7-index.hbi").read_bytes()
    require(sha(original)==PIN_SOURCE,"SOURCE_QR_ORIGIN_PIN")
    require(sha(bank)==PIN_BANK and len(bank)==184815,"BANK_PIN")
    require(sha(index)==PIN_INDEX and len(index)==70043,"INDEX_PIN")
    records=json.loads(original)["records"]
    require(len(records)==81,"BAD_ORIGINAL_RECORD_COUNT")
    roots={}
    rows=[]
    used=set()
    for ordinal,line in enumerate(index.decode("ascii").splitlines()):
        parts=line.split("|")
        require(len(parts)==6 and parts[0]=="MEM","WRONG_INDEX_FORMAT")
        values=dict(part.split("=",1) for part in parts[1:])
        require(set(values)=={"band","id","length","offset","sha256"},"BAD_FIELDS")
        band,site=values["band"],values["id"]
        start,length=int(values["offset"]),int(values["length"])
        require(band in BANDS and site.startswith("site-"),"INVALID_BAND_OR_SITE")
        require(0<=start and 0<length and start+length<=len(bank),"BAD_BYTE_OFFSET")
        payload=bank[start:start+length]
        require(sha(payload)==values["sha256"],"ROW_SHA_UNPINNED")
        raw_obj=json.loads(payload)
        require(raw_obj["id"]==site and raw_obj["band"]==band and
                raw_obj["record"]==records[int(site[5:])],"SOURCE_LINK_UNTRUSTED")
        require((site,band) not in used,"DUPLICATE_BAND_OR_SITE")
        used.add((site,band))
        rows.append((site,band,payload))
        roots[(site,band)]=sha(payload)
    require(len(rows)==567 and len(used)==567,"WRONG_BANK_ROWS")
    path=evidence/"py-coupling/coupling.hbp"
    data=path.read_bytes()
    require(data.endswith(b"\n"),"NON_CANONICAL_EVIDENCE")
    lines=data.splitlines()
    require(len(lines)==567*12,"MISSING_6804_FRAMES")
    manifest=json.loads((evidence/"py-coupling/results.json").read_bytes())
    require(manifest["schema"]=="ASOLARIA-SEAT1-PHOTON-PHONON-ELECTRON-MEMORY-MODEL-V1",
            "INVALID_MODEL_ID")
    require(manifest["frames"]==6804 and manifest["bank_rows"]==567
            and manifest["source_sha256"]==PIN_SOURCE and
            manifest["bank_sha256"]==PIN_BANK and
            manifest["index_sha256"]==PIN_INDEX and
            manifest["scenario_count"]==12,"MANIFEST_TRUST_PIN_FAIL")
    for name in ("actual_photon_phonon_coupling_measured",
                 "optical_storage_medium_measured","real_photoelectron_current_measured",
                 "biological_neuron_measured","real_mcp_server_operational"):
        require(manifest[name] is False,"IMPROPER_PHYSICAL_PROMOTION:"+name)
    require(manifest["hbp_sha256"]==sha(data),"TRACE_SHA_MISMATCH")
    require(len(manifest["negative_controls"])==14 and
            all(e["held"] for e in manifest["negative_controls"]),"NEGATIVE_INJECTIONS_MISSING")
    summaries={s["arm"]:s for s in manifest["scenario_results"]}
    require(set(summaries)==set(ARMS),"ARM_SET_MISSING")
    mean={}
    for arm_ix,arm in enumerate(ARMS):
        count=0
        errors=0
        electron_count=0
        photon_count=0
        exact=0
        false_green=0
        for i,(site,band,payload) in enumerate(rows):
            f=json.loads(lines[arm_ix*567+i])
            recovered=bytes.fromhex(f["readback_hex"])
            require(f["schema"]==manifest["schema"] and f["arm"]==arm and
                    f["ordinal"]==i and f["site"]==site and f["band"]==band,
                    "CAPTURE_IDENTITY_DRIFT")
            require(f["wavelength_nm_assumed"]==
                    {"red":650,"orange":610,"yellow":580,"green":530,
                     "blue":470,"indigo":440,"violet":405}[band],
                    "SYMBOLIC_BAND_SPOOF")
            require(len(recovered)==len(payload),"BYTE_LENGTH_CHANGED")
            errors_here=sum((a^b).bit_count() for a,b in zip(payload,recovered))
            miss=sum(((a^b)&a).bit_count() for a,b in zip(payload,recovered))
            false=sum(((a^b)&b).bit_count() for a,b in zip(payload,recovered))
            require(f["bit_errors"]==errors_here and
                    f["missed_one_bits"]==miss and
                    f["false_zero_bits"]==false,"ACTUAL_BYTE_ERRORS_NOT_COUNTED")
            require(f["readback_sha256"]==sha(recovered) and
                    f["reference_sha256"]==roots[(site,band)],"SOURCE_DIGEST_DRIFT")
            original_fp=LIF(payload)
            result_fp=LIF(recovered)
            neural=(original_fp==result_fp)
            authorized=(recovered==payload and neural)
            require(f["source_byte_exact"]==(recovered==payload) and
                    f["neural_only_match"]==neural and
                    f["strict_authorized"]==authorized,"AUTHORIZATION_FALSE_GREEN")
            require(f["mcp_capture"]["params"]["name"]=="electron.capture" and
                    f["mcp_neural_gate"]["params"]["name"]=="neuron.gate",
                    "MCP_NAME_SPOOF")
            require(f["mcp_capture"]["params"]["arguments"]["reference_sha256"]==sha(payload)
                    and f["mcp_capture"]["params"]["arguments"]["readback_sha256"]==sha(recovered),
                    "SELF_REPORTED_SOURCE_ROOT")
            require(f["mcp_neural_gate"]["params"]["arguments"]["authorized"]==authorized,
                    "FORGED_NEURAL_GATE")
            require(f["mcp_neural_gate"]["params"]["arguments"]["trained_fingerprint_sha256"]==sha(original_fp)
                    and f["mcp_neural_gate"]["params"]["arguments"]["observed_fingerprint_sha256"]==sha(result_fp),
                    "LIF_FINGERPRINT_NOT_SOURCED")
            require(f["photoelectrons_modeled"]<=f["emitted_photons_modeled"],
                    "ELECTRON_COUNT_OUT_OF_BUDGET")
            require(f["sector"]==i%27,"UNBOUND_SECTOR")
            nonce=sha(f"ASOLARIA-COUPLING-NONCE|{PIN_BANK}|{arm}|{i}".encode())[:24]
            require(f["nonce"]==nonce and
                    f["mcp_capture"]["params"]["arguments"]["nonce"]==nonce,
                    "NONCE_REPLAY_OR_REASSIGNMENT")
            if arm in ("optical_dark","acoustic_only","held_t3_erased"):
                require(not any(recovered) and f["photoelectrons_modeled"]==0
                        and f["emitted_photons_modeled"]==0,"DARK_SOURCE_FALSIFIER")
            count+=1
            errors+=errors_here
            exact+=int(authorized)
            false_green+=int(neural and recovered!=payload)
            photon_count+=f["emitted_photons_modeled"]
            electron_count+=f["photoelectrons_modeled"]
        require(count==567,"NOT_ALL_ROWS")
        summary=summaries[arm]
        require((summary["bit_errors"],summary["authorized_rows"],
                 summary["neural_false_greens"],
                 summary["emitted_photons_modeled"],summary["photoelectrons_modeled"])==
                (errors,exact,false_green,photon_count,electron_count),
                "AGGREGATE_NOT_SUPPORTED_BY_PER_BYTE_TEST")
        mean[arm]={"source_rows":count,"bit_errors":errors,
                   "source_exact":exact,"false_neural_only_matches":false_green,
                   "model_photons":photon_count,"model_photoelectrons":electron_count}
    require(mean["baseline_t0"]["bit_errors"]==mean["off_resonance"]["bit_errors"],
            "OFF_RESONANCE_READBACK_DIVERGES")
    require(mean["resonant_phase0"]["bit_errors"]<mean["baseline_t0"]["bit_errors"]<
            mean["resonant_phase180"]["bit_errors"],"ASSUMED_PHASE_ORDER_NOT_SEEN")
    require(mean["thermal_sham"]["bit_errors"]<mean["baseline_t0"]["bit_errors"],
            "THERMAL_NUISANCE_CAN_MIMIC_TARGET")
    require(mean["held_t3"]["bit_errors"]>mean["baseline_t0"]["bit_errors"],
            "MODELED_TIME_HOLD_HAS_NO_LOSS")
    require(manifest["erased_violet_rows"]==81 and
            manifest["missing_logical_27_sector_aliases"]==2187,
            "REAL_INDEX_ERASURE_COUNT")
    receipt={
        "schema":"ASOLARIA-SEAT1-PHOTON-PHONON-ELECTRON-THIRD-SOURCE-AUDIT-V1",
        "audit_status":"DIGITAL_MODEL_PASS_NO_PHYSICAL_OPTICAL_MEASUREMENT",
        "source_original_sha256":PIN_SOURCE,
        "full_byte_memory_bank_sha256":PIN_BANK,
        "bank_index_sha256":PIN_INDEX,
        "real_original_memories":81,
        "true_original_bank_rows":567,
        "distinct_source_bytes":184815,
        "software_trace_rows_fully_audited":6804,
        "trace_sha256":sha(data),
        "independent_readback_summary":mean,
        "negative_controls_from_producer":14,
        "current_photons_measured":False,
        "actual_sound_transducer_measured":False,
        "physical_retention_measured":False,
        "source_digitally_signed":False,
        "software_deterministic_source_nonce_unpredictable":False,
    }
    out=(json.dumps(receipt,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_bytes(out)
    print(json.dumps({"status":"PASS","rows":6804,"bank_sha":PIN_BANK,
                      "trace_sha":sha(data),"auditor_sha":sha(out),
                      "thermal_sham_improves_as_assumed":True,
                      "real_photon_measurement":False},sort_keys=True))
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: audit_coupling.py <evidence_root> <output.json>")
    main(sys.argv[1],sys.argv[2])
