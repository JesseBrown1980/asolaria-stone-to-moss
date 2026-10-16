#!/usr/bin/env python3
"""Four distinct logical digital audit lanes; NOT physical host independence."""
import argparse,hashlib,pathlib,re
def sha(b):return hashlib.sha256(b).hexdigest()
def check(ok,err):
    if not ok:raise RuntimeError(err)
def scan(in_dir):
    data=(in_dir/"MAST-THREE-EPOCH-INVENTORY.hbp").read_bytes()
    source=(in_dir/"MAST-THREE-EPOCH-INVENTORY.hbp.sha256").read_text().split()[0]
    check(sha(data)==source,"SOURCE_SHA_MISMATCH")
    lines=data.decode().splitlines()
    check(lines[0].startswith("HBP1|schema=ASOLARIA-MIRI-S1-THREE-EPOCH"),"SCHEMA_FAIL")
    ep={p:[] for p in ("1618","6797","9252")}
    for line in lines:
        if line.startswith("EPOCH|"):
            m=re.search(r"\bproposal=(\d+)",line)
            if m and m.group(1) in ep:ep[m.group(1)].append(line)
    check(all(len(v)==1 for v in ep.values()),"EXACT_THREE_EPOCHS_REQUIRED")
    return data,source,lines,ep
def audit(seat,input_dir,out):
    data,source,lines,ep=scan(input_dir)
    linesout=[f"HBP1|schema=ASOLARIA-MIRI-FOUR-SEAT-AUDIT-V1|seat={seat}|source_sha256={source}|json=0",
      "BOUNDARY|source=MAST_PUBLIC|calibrated_FITS_processed=NO|S1_detection=NOT_ESTABLISHED|physical_host_attestation=ABSENT|json=0"]
    if seat==1:
        for p in ep:
            e=ep[p][0]
            coron=re.search(r"coronagraph_obs=(\d+)",e)
            cal=re.search(r"calibrated_candidates=(\d+)",e)
            check(coron is not None and cal is not None,"BAD_EPOCH_COUNTS")
            linesout.append(f"SEAT1|proposal={p}|coronagraph_obs={coron.group(1)}|calibrated_candidates={cal.group(1)}|next=PIN_CALIBRATED_SOURCE_PSF_ROLL|json=0")
    elif seat==2:
        check(not any(token in data for token in (b"Authorization: Bearer",b"HF_TOKEN=",b"github_pat_",b"hf_W")),"CREDENTIAL_IN_PUBLIC_MANIFEST")
        linesout.append("SEAT2|MAST_catalog_digest=PASS|original_FITS_sha=NOT_DOWNLOADED|independent_original_signer=UNKNOWN|HuggingFace_uploaded_and_readback=NOT_PROVEN|json=0")
    elif seat==3:
        for p in ep:
            ct=sum(1 for ln in lines if ln.startswith("OBS|") and "|proposal="+p+"|" in ln and "F1550C" in ln)
            linesout.append(f"SEAT3|proposal={p}|F1550C_obs={ct}|spectral_band_count=ONE_FILTER_NOT_SEVEN|json=0")
        linesout.append("SEAT3|PSF_null_and_false_alarm_rate=HOLD_UNTIL_SCIENCE_FITS|orbit_new_planet=NOT_CLAIMED|json=0")
    elif seat==4:
        mutant=data.replace(b"S1_UNCONFIRMED=TRUE",b"S1_UNCONFIRMED=FALSE",1)
        check(mutant!=data and sha(mutant)!=source,"ALTERED_VERDICT_ACCEPTED")
        missing=b"\n".join(s.encode() for s in lines if not s.startswith("EPOCH|proposal=6797"))+b"\n"
        check(sha(missing)!=source,"MISSING_EPOCH_ACCEPTED")
        linesout.append("SEAT4|altered_science_verdict=REJECTED|removed_epoch=REJECTED|negative_controls=2|json=0")
    else:raise RuntimeError("INVALID_SEAT")
    out.mkdir(parents=True,exist_ok=True)
    result="\n".join(linesout)+"\n"
    f=out/f"SEAT{seat}-MIRI-CATCHUP.hbp"
    f.write_text(result)
    (out/(f.name+".sha256")).write_text(sha(result.encode())+"  "+f.name+"\n")
    print(f"SEAT{seat}_DIGITAL_AUDIT_PASS|scientific_fits_reduction=HOLD|source_sha256={source}|json=0")
def final(indir,out):
    _,root,_,_=scan(indir)
    lines=[f"HBP1|schema=ASOLARIA-MIRI-FOUR-SEAT-COORDINATOR-V1|source_sha256={root}|json=0"]
    for n in (1,2,3,4):
        f=indir/f"SEAT{n}-MIRI-CATCHUP.hbp"
        data=f.read_bytes()
        expected=(indir/(f.name+".sha256")).read_text().split()[0]
        check(sha(data)==expected,"SEAT_RECEIPT_DIGEST_FAILED")
        first=data.decode().splitlines()[0]
        check("|seat="+str(n)+"|" in first and "|source_sha256="+root+"|" in first,"CROSS_SEAT_ROOT_MISMATCH")
        lines.append(f"SEAT|number={n}|HBP_sha256={expected}|source_match=PASS|physical_host_independent=NOT_ATTESTED|json=0")
    lines.append("VERDICT|four_logical_roles=PASS|FITS_S1_three_epoch_reconstruction=PENDING|no_new_planet=CLAIMED_NONE|HF_external_write_and_readback=UNVERIFIED|json=0")
    out.mkdir(parents=True,exist_ok=True)
    (out/"FOUR-SEAT-MIRI-COORDINATOR.hbp").write_text("\n".join(lines)+"\n")
    print("CROSS_SEAT_SHA=PASS|science=HOLD")
def test():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p=pathlib.Path(d)
        lines=["HBP1|schema=ASOLARIA-MIRI-S1-THREE-EPOCH-FAKE|json=0","BOUNDARY|S1_UNCONFIRMED=TRUE|json=0"]
        for n in (1618,6797,9252):
            lines += [f"EPOCH|proposal={n}|coronagraph_obs=1|calibrated_candidates=1|json=0",f"OBS|proposal={n}|filters=F1550C|json=0"]
        data=("\n".join(lines)+"\n").encode()
        (p/"MAST-THREE-EPOCH-INVENTORY.hbp").write_bytes(data)
        (p/"MAST-THREE-EPOCH-INVENTORY.hbp.sha256").write_text(sha(data)+"  MAST-THREE-EPOCH-INVENTORY.hbp\n")
        for n in (1,2,3,4):audit(n,p,p)
        final(p,p)
        (p/"MAST-THREE-EPOCH-INVENTORY.hbp").write_bytes(data+b"FORGERY")
        try:scan(p)
        except RuntimeError: print("NEGATIVE_SOURCE_TAMPER=REJECT")
        else:raise RuntimeError("FORGERY_UNDETECTED")
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--in-dir");ap.add_argument("--out-dir");ap.add_argument("--seat",type=int);ap.add_argument("--final",action="store_true");ap.add_argument("--self-test",action="store_true");a=ap.parse_args()
    if a.self_test:test()
    elif a.final:final(pathlib.Path(a.in_dir),pathlib.Path(a.out_dir))
    else:audit(a.seat,pathlib.Path(a.in_dir),pathlib.Path(a.out_dir))
