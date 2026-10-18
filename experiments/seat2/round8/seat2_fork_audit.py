#!/usr/bin/env python3
"""Seat2 R8: test-only signed source/detector histories and anti-rollback anchors.

No calibrated sensors, independent key custody or physical photon measurements.
"""
import base64, copy, hashlib, json, sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

BANDS=("red","orange","yellow","green","blue","indigo","violet")
PORTS=(2,5,0,6,1,4,3)
SOURCE="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
SESSION="SEAT2-R8-DIGITAL-FIXTURE-SESSION-20261015"
NONCE="SEAT2-R8-PUBLIC-NONCE-NOT-EXTERNAL-FRESHNESS"
DOMAINS={"SOURCE":"ASOLARIA-SEAT2-R8-SOURCE-V1\n",
 "DETECTOR":"ASOLARIA-SEAT2-R8-OBS-V1\n",
 "CHECKPOINT":"ASOLARIA-SEAT2-R8-CHECKPOINT-V1\n"}
GENESIS=b"ASOLARIA-SEAT2-R8-GENESIS-V1\n"
LINK=b"ASOLARIA-SEAT2-R8-LINK-V1\n"
BASIC=("schema","session","nonce","source_manifest_sha256","sequence",
       "previous_hash","band","port","sector","site","trial_id",
       "detector_count","clock_label")

def sha(x):return hashlib.sha256(x).hexdigest()
def enc(x):return (json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
def signer(role):
    seed=hashlib.sha256(("ASOLARIA-R8-"+role+"-PUBLIC-TEST-FIXTURE-20261015").encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)
def pub(k):
    return k.public_key().public_bytes(encoding=serialization.Encoding.Raw,
                        format=serialization.PublicFormat.Raw).hex()
def sign(role,key,payload):
    body=(DOMAINS[role]).encode()+enc(payload)
    return {"payload":payload,"signature":base64.b64encode(key.sign(body)).decode("ascii")}
def valid(role,pubkey,packet):
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(pubkey)).verify(
            base64.b64decode(packet["signature"],validate=True),
            DOMAINS[role].encode()+enc(packet["payload"]))
        return True
    except (InvalidSignature,ValueError,KeyError,TypeError):return False
def check(ok,reason):
    if not ok:raise ValueError(reason)
def trial(index):return sha(("R8-OPAQUE-TRIAL-ID|"+SESSION+"|"+str(index)).encode())[:24]
def digest(packet):return sha(enc(packet))
def link(packet):return sha(LINK+enc(packet))
def init():
    keys={role:signer(role) for role in DOMAINS}
    pubkeys={role:pub(key) for role,key in keys.items()}
    manifest={"schema":"ASOLARIA-R8-SIGNED-SOURCE-V1","session":SESSION,
        "nonce":NONCE,"source_root":SOURCE,"bank_root":BANK,
        "bands":list(BANDS),"ports":list(PORTS),"sectors":27}
    source=sign("SOURCE",keys["SOURCE"],manifest)
    return keys,pubkeys,source
def make_chain(keys,source,altered=False):
    previous=sha(GENESIS+enc(source))
    packets=[]
    for index in range(4):
        sector=(0,6,18,26)[index]
        band=BANDS[index]
        p={"schema":"ASOLARIA-R8-SIGNED-OBS-V1","session":SESSION,
           "nonce":NONCE,"source_manifest_sha256":digest(source),
           "sequence":index+1,"previous_hash":previous,"band":band,
           "port":PORTS[index],"sector":sector,"site":index,
           "trial_id":trial(index),"detector_count":20+index*7+(9 if altered and index==2 else 0),
           "clock_label":"SYNTHETIC-TIME-NOT-ELAPSED-SEC"}
        signed=sign("DETECTOR",keys["DETECTOR"],p)
        packets.append(signed);previous=link(signed)
    return packets
def chain_verify(source,frames,public,expected_tip=None,external_last_seq=0,expected_nonce=NONCE):
    check(valid("SOURCE",public["SOURCE"],source),"INVALID_SOURCE_SIGNATURE")
    m=source["payload"]
    check(set(m)=={"schema","session","nonce","source_root","bank_root","bands","ports","sectors"},
          "SOURCE_FIELDS")
    check((m["schema"],m["session"],m["nonce"],m["source_root"],m["bank_root"],m["sectors"])==
          ("ASOLARIA-R8-SIGNED-SOURCE-V1",SESSION,expected_nonce,SOURCE,BANK,27),
          "INDEPENDENT_SOURCE_ROOT_OR_CONTEXT")
    check(m["bands"]==list(BANDS) and m["ports"]==list(PORTS),"INDEPENDENT_CHANNEL_ORDER")
    check(len(frames)==4,"INCOMPLETE_SIGNED_CHAIN")
    previous=sha(GENESIS+enc(source))
    for index,packet in enumerate(frames):
        check(valid("DETECTOR",public["DETECTOR"],packet),"INVALID_DETECTOR_SIGNATURE")
        p=packet["payload"]
        check(set(p)==set(BASIC),"DETECTOR_FIELDS_FORBID_SOURCE_LEAK")
        check((p["schema"],p["session"],p["nonce"],p["source_manifest_sha256"])==
              ("ASOLARIA-R8-SIGNED-OBS-V1",SESSION,expected_nonce,digest(source)),
              "INVALID_SOURCE_CONTEXT")
        check(p["sequence"]==index+1,"SEQUENCE_REPLAY_OR_REORDER")
        check(p["previous_hash"]==previous,"BROKEN_PREVIOUS_LINK")
        check((p["band"],p["port"])==(BANDS[index],PORTS[index]) and
              (p["sector"],p["site"])==((0,6,18,26)[index],index),
              "BAD_ORDERED_CHANNEL_OR_SITE")
        check(p["trial_id"]==trial(index),"BLINDED_TRIAL_ID_MISMATCH")
        check(type(p["detector_count"]) is int and 0<=p["detector_count"]<=4096 and
              p["clock_label"]=="SYNTHETIC-TIME-NOT-ELAPSED-SEC",
              "BAD_SENSOR_MOCK_PAYLOAD")
        previous=link(packet)
    check(frames[-1]["payload"]["sequence"]>external_last_seq,"EXTERNAL_CHECKPOINT_REPLAY")
    if expected_tip is not None:check(previous==expected_tip,"EXTERNAL_PINNED_HEAD_MISMATCH")
    return previous

def checkpoint(keys,source,frames):
    tip=link(frames[-1])
    obj={"schema":"ASOLARIA-R8-SIGNED-CHECKPOINT-V1","session":SESSION,
         "nonce":NONCE,"source_manifest_sha256":digest(source),
         "last_sequence":4,"tip_sha256":tip}
    return sign("CHECKPOINT",keys["CHECKPOINT"],obj)
def checkpoint_verify(cp,source,public,externally_pinned_digest):
    check(valid("CHECKPOINT",public["CHECKPOINT"],cp),"INVALID_CHECKPOINT_SIGNATURE")
    p=cp["payload"]
    check(set(p)=={"schema","session","nonce","source_manifest_sha256","last_sequence","tip_sha256"},
          "CHECKPOINT_FIELDS")
    check((p["schema"],p["session"],p["nonce"],p["source_manifest_sha256"],p["last_sequence"])==
          ("ASOLARIA-R8-SIGNED-CHECKPOINT-V1",SESSION,NONCE,digest(source),4),
          "INVALID_CHECKPOINT_SOURCE")
    check(digest(cp)==externally_pinned_digest,"EXTERNAL_CHECKPOINT_PIN_MISMATCH")
    return True

def attacks(keys,public,source,good,fork,cp):
    expected_tip=link(good[-1])
    expected_checkpoint=digest(cp)
    success=[]
    def reject(name,fn,why):
        try:fn()
        except ValueError as err:
            check(str(err)==why,name+"_WRONG_FAIL_STAGE_"+str(err))
            success.append(name)
        else:raise AssertionError("FAIL_OPEN_"+name)
    assert chain_verify(source,good,public)==expected_tip
    assert chain_verify(source,fork,public)!=expected_tip
    # Both conflicting histories have genuine test-fixture signatures.
    assert all(valid("DETECTOR",public["DETECTOR"],p) for p in good+fork)
    assert good[0]==fork[0] and good[1]==fork[1] and good[2]!=fork[2]
    reject("signed_history_fork_vs_external_tip",
           lambda:chain_verify(source,fork,public,expected_tip),
           "EXTERNAL_PINNED_HEAD_MISMATCH")
    # Independent source sees same (session,sequence) with distinct valid payloads.
    conflict=[i+1 for i,(a,b) in enumerate(zip(good,fork)) if digest(a)!=digest(b)]
    check(conflict==[3,4],"FORK_NOT_DETECTED")
    success.append("joint_signed_fork_detected")
    # Reset state accepts a signed old chain; durable external checkpoint rejects.
    assert chain_verify(source,good,public,external_last_seq=0)==expected_tip
    success.append("reset_ledger_replay_possible_demonstrated")
    reject("durable_checkpoint_replay_held",
           lambda:chain_verify(source,good,public,external_last_seq=4),
           "EXTERNAL_CHECKPOINT_REPLAY")
    reject("previous_nonce_reuse_held",
           lambda:chain_verify(source,good,public,expected_nonce="EXTERNALLY-NEW-NONCE"),
           "INDEPENDENT_SOURCE_ROOT_OR_CONTEXT")
    forged_source=copy.deepcopy(source["payload"])
    forged_source["source_root"]="f"*64
    signed_forgery=sign("SOURCE",keys["SOURCE"],forged_source)
    reject("coherent_signed_source_forgery_held",
           lambda:chain_verify(signed_forgery,make_chain(keys,signed_forgery),public),
           "INDEPENDENT_SOURCE_ROOT_OR_CONTEXT")
    swap=copy.deepcopy(source["payload"]);swap["ports"][0]=PORTS[1]
    swapped=sign("SOURCE",keys["SOURCE"],swap)
    reject("signed_channel_owner_swap_held",
           lambda:chain_verify(swapped,make_chain(keys,swapped),public),
           "INDEPENDENT_CHANNEL_ORDER")
    def mutate(name,index,updates,why,resign=True):
        altered=copy.deepcopy(good)
        p=copy.deepcopy(altered[index]["payload"])
        p.update(updates)
        altered[index]=sign("DETECTOR",keys["DETECTOR"],p) if resign else {
            "payload":p,"signature":altered[index]["signature"]}
        reject(name,lambda:chain_verify(source,altered,public),why)
    mutate("unsigned_detector_count_tampering",2,{"detector_count":777},
           "INVALID_DETECTOR_SIGNATURE",False)
    reject("missing_detector_observation",
           lambda:chain_verify(source,good[:-1],public),
           "INCOMPLETE_SIGNED_CHAIN")
    reject("reordered_signed_observations",
           lambda:chain_verify(source,[good[1],good[0],good[2],good[3]],public),
           "SEQUENCE_REPLAY_OR_REORDER")
    mutate("signed_broken_parent_link",2,{"previous_hash":"0"*64},
           "BROKEN_PREVIOUS_LINK")
    mutate("signed_trial_identity_swap",0,{"trial_id":"a"*24},
           "BLINDED_TRIAL_ID_MISMATCH")
    mutate("signed_invalid_band",0,{"band":"infrared"},
           "BAD_ORDERED_CHANNEL_OR_SITE")
    mutate("signed_invalid_sector",0,{"sector":27},
           "BAD_ORDERED_CHANNEL_OR_SITE")
    mutate("duplicate_sequence",1,{"sequence":1},
           "SEQUENCE_REPLAY_OR_REORDER")
    mutate("source_bit_visible_to_detector",0,{"precommitted_bit":1},
           "DETECTOR_FIELDS_FORBID_SOURCE_LEAK")
    mutate("public_predictable_seed_visible_to_detector",0,{"public_bit_seed":"R8-leak"},
           "DETECTOR_FIELDS_FORBID_SOURCE_LEAK")
    fake=copy.deepcopy(cp["payload"]);fake["tip_sha256"]=link(fork[-1])
    signed_fake=sign("CHECKPOINT",keys["CHECKPOINT"],fake)
    assert valid("CHECKPOINT",public["CHECKPOINT"],signed_fake)
    reject("signed_checkpoint_forgery_vs_external_digest",
           lambda:checkpoint_verify(signed_fake,source,public,expected_checkpoint),
           "EXTERNAL_CHECKPOINT_PIN_MISMATCH")
    check(checkpoint_verify(cp,source,public,expected_checkpoint),"ORIGINAL_CHECKPOINT_FAIL")
    success.append("externally_pinned_checkpoint_accepts_original")
    check(len(success)==19,"NEGATIVE_COVERAGE_DRIFT_"+str(len(success)))
    return success

def run(folder):
    keys,public,source=init()
    good=make_chain(keys,source);fork=make_chain(keys,source,True)
    cp=checkpoint(keys,source,good)
    expected_head=chain_verify(source,good,public)
    assert cp["payload"]["tip_sha256"]==expected_head
    cases=attacks(keys,public,source,good,fork,cp)
    fixture={"schema":"ASOLARIA-R8-ALL-TEST-SIGNED-HISTORIES-V1",
             "public_fixture_keys":public,"signed_source":source,
             "signed_good_frames":good,"signed_competing_fork":fork,
             "signed_checkpoint":cp,
             "externally_pinned_checkpoint_sha256":digest(cp),
             "external_expected_tip":expected_head,
             "source_anchor_from_caller":SOURCE,"bank_anchor_from_caller":BANK,
             "fixture_only":True}
    result={"schema":"ASOLARIA-SEAT2-R8-CUSTODY-FORK-ROLLBACK-V1",
            "verdict":"DIGITAL_TEST_PASS_PHYSICAL_AND_EXTERNAL_CUSTODY_HELD",
            "signed_fixture_roles":3,"competing_signed_histories":2,
            "signed_detector_frames":8,"source_records":81,"logical_bands":7,
            "original_bank_records":567,
            "cases_executed":len(cases),"case_labels":cases,
            "same_session_signed_fork_accepted_without_external_tip":True,
            "fork_rejected_with_fixed_external_tip":True,
            "reset_local_replay_possible":True,
            "persisted_external_checkpoint_rejects_replay":True,
            "public_fixture_key_custody_not_independent":True,
            "external_source_authenticated":False,
            "real_optical_retention_measured":False,
            "real_photon_phonon_coupling_measured":False,
            "biological_neural_memory_measured":False,
            "signed_fixture_sha256":sha(enc(fixture))}
    folder.mkdir(parents=True,exist_ok=True)
    for name,bytes_ in (("fixture.json",enc(fixture)),("results.json",enc(result))):
        (folder/name).write_bytes(bytes_)
        (folder/(name+".sha256")).write_bytes((sha(bytes_)+"  "+name+"\n").encode("ascii"))
    print("SEAT2_R8_LOCAL_DIGITAL_PASS",len(cases),result["signed_fixture_sha256"],sha(enc(result)))
    return result
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python seat2_fork_audit.py OUTPUT_DIR")
    run(Path(sys.argv[1]))
