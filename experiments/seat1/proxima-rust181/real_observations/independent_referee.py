#!/usr/bin/env python3
"""Seat4 independent source-byte & nine-window observer, HBP text only.

Original CDS bytes and numerical output decisions are unchanged; HBP records
are bounded one-pass text fields, not a JSON serializer or parser.
"""
import hashlib
import pathlib
from collections import Counter
from itertools import product
from decimal import Decimal

HERE=pathlib.Path("real_observations/output")
RV_SHA="027cff5c10b541608b727abada2af531037223edec3bb9112fcbb45fc333e474"
PH_SHA="d42dad64fcbf80159bfc1edf20c35db82d01ce2aa7830248d7198aad05bc6dd5"

def sha(b):return hashlib.sha256(b).hexdigest()

def read_hbp(file, schema):
    rows=[]
    for i,line in enumerate(file.read_text(encoding="utf-8").splitlines(),1):
        columns=line.split("|")
        assert columns[0] and columns[-1]=="json=0",("INVALID_HBP",file,i)
        values={}
        for item in columns[1:]:
            assert "=" in item,("UNKEYED_FIELD",file,i)
            key,value=item.split("=",1)
            assert key not in values and key and value!="",("DUPLICATE_OR_EMPTY",file,i,key)
            values[key]=value
        rows.append((columns[0],values))
    assert rows and rows[0][0]=="HBP1" and rows[0][1]["schema"]==schema
    return rows

def sole(rows,tag):
    matched=[p for t,p in rows if t==tag]
    assert len(matched)==1,(tag,len(matched))
    return matched[0]

def main():
    spec=(HERE/"spec.dat").read_bytes()
    photo=(HERE/"photo.dat").read_bytes()
    assert sha(spec)==RV_SHA,(sha(spec),RV_SHA)
    assert sha(photo)==PH_SHA,(sha(photo),PH_SHA)
    rows=spec.splitlines();phot=photo.splitlines()
    assert len(rows)==722 and all(len(x)==120 for x in rows)
    assert len(phot)==2212 and all(len(x)==43 for x in phot)
    data=[]
    for row in rows:
        tm=round(Decimal(row[1:10].decode().strip())*1000)
        inst=int(row[119:120].decode())
        rv=int(Decimal(row[16:21].decode().strip())*1000)
        er=int(Decimal(row[28:32].decode().strip())*1000)
        assert er>0 and 0<=inst<=5
        data.append((inst,tm,rv,er))
    train=[];test=[];counts={}
    for inst in range(6):
        subset=sorted((x for x in data if x[0]==inst),key=lambda r:r[1])
        cutoff=(len(subset)*7//10) if len(subset)>=10 else len(subset)
        train+=subset[:cutoff];test+=subset[cutoff:]
        counts[str(inst)]=(cutoff,len(subset)-cutoff)
    result=read_hbp(HERE/"NINE-REAL-OBSERVATION-WINDOWS.hbp",
                    "ASOLARIA-ACTUAL-PROXIMA-RV-NINE-WINDOW-V2")
    assert result[0][1]["trits"]=="-1,0,+1"
    summary=sole(result,"SUMMARY");scores=sole(result,"SCORES")
    assert int(summary["source_measurements"])==722
    assert int(summary["source_photo_rows"])==2212
    assert int(summary["train_rows"])==len(train)
    assert int(summary["heldout_rows"])==len(test)
    assert int(summary["first_bjd_minus_2450000_milliday"])==min(r[1] for r in data)
    assert int(summary["last_bjd_minus_2450000_milliday"])==max(r[1] for r in data)
    assert int(summary["exploratory_trials"])==6
    assert int(summary["heldout_window_count"])==9
    assert sole(result,"BOUNDARY")["new_planet_detected"]=="FALSE"
    assert sole(result,"IMAGE")["source_hubble_status"] in (
        "HUBBLE_BINARY_SOURCE_HELD","HUBBLE_PUBLIC_RENDERED_IMAGE_AVAILABLE")
    instruments=[p for t,p in result if t=="INSTRUMENT"]
    assert len(instruments)==6 and set(x["id"] for x in instruments)==set(map(str,range(6)))
    for row in instruments:
        inst=row["id"]
        tr,te=counts[inst]
        assert int(row["train"])==tr and int(row["test"])==te
        assert int(row["n"])==te
        for key in ("baseline_wrmse_mm_s","known_wrmse_mm_s","extra_wrmse_mm_s"):
            assert 0<=int(row[key])<100000

    for key in ("null_wrmse_mm_s","known_bd_wrmse_mm_s","extra_wrmse_mm_s"):
        assert 0<=int(scores[key])<100000
    periods=[900_000,2_700_000,8_100_000,24_300_000,72_900_000,190_000_000]
    assert int(scores["train_selected_extra_period_1e5_days"]) in periods
    alltest=sorted(test,key=lambda r:r[1])
    windows=[p for t,p in result if t=="WINDOW"]
    assert len(windows)==9
    nearby=[]
    for i,row in enumerate(windows):
        subset=alltest[len(alltest)*i//9:len(alltest)*(i+1)//9]
        assert int(row["index"])==i+1
        assert int(row["count"])==len(subset)
        assert int(row["median_bjd_minus_2450000_milliday"])==subset[len(subset)//2][1]
        assert all(int(row[k])>=0 for k in (
            "baseline_wrmse_mm_s","known_bd_wrmse_mm_s","exploratory_wrmse_mm_s"))
        median=int(row["median_bjd_minus_2450000_milliday"])
        nearby.append((i+1,median,
            sum(abs(x[1]-median)<=1000 for x in subset),
            sum(abs(x[1]-median)<=2000 for x in subset)))
    gains=[int(w["known_bd_wrmse_mm_s"])**2-int(w["exploratory_wrmse_mm_s"])**2
           for w in windows]
    observed=sum(gains)
    extreme=sum(sum(g*s for g,s in zip(gains,signs))>=observed
                for signs in product((-1,1),repeat=9))
    better=sum(g>0 for g in gains);worse=sum(g<0 for g in gains)
    assert 1<=extreme<=512

    manifest=read_hbp(HERE/"ORIGINAL-SOURCE-MANIFEST.hbp",
                      "ASOLARIA-REAL-PROXIMA-ORIGINAL-CATALOG-V2")
    src=[p for t,p in manifest if t=="SOURCE"]
    assert len(src)==2
    byname={p["file"]:p for p in src}
    assert set(byname)=={"spec.dat","photo.dat"}
    assert byname["spec.dat"]["sha256"]==RV_SHA
    assert byname["photo.dat"]["sha256"]==PH_SHA
    assert int(byname["spec.dat"]["logical_records"])==722
    assert int(byname["photo.dat"]["logical_records"])==2212
    image=sole(manifest,"IMAGE")
    assert image["available"] in ("true","false")
    if image["available"]=="true":
        assert (HERE/image["file"]).is_file()
        assert sha((HERE/image["file"]).read_bytes())==image["sha256"]

    lines=[
        "HBP1|schema=ASOLARIA-INDEPENDENT-REAL-PROXIMA-SOURCE-WINDOWS-V2|format=HBP|json=0",
        f"SOURCE|source_rv_sha256={RV_SHA}|source_photometry_sha256={PH_SHA}|real_rv_rows=722|real_photometry_rows=2212|json=0",
        f"CHRONOLOGY|train_rows={len(train)}|heldout_rows={len(test)}|start_milliday={min(x[1] for x in data)}|end_milliday={max(x[1] for x in data)}|json=0",
        f"FALSIFY|windows_better={better}|windows_worse={worse}|signflip_extreme={extreme}|signflip_assignments=512|post_selection_diagnostic=TRUE|json=0",
        "BOUNDARY|independent_coefficients_reimplemented=FALSE|new_planet_detected=FALSE|raw_calibrated_telescope_FITS_loaded=FALSE|model_significance_established=FALSE|json=0"
    ]
    for inst in range(6):
        lines.append(f"INSTRUMENT|id={inst}|source_rows={Counter(x[0] for x in data)[inst]}|train_rows={counts[str(inst)][0]}|test_rows={counts[str(inst)][1]}|json=0")
    for index,median,near1,near2 in nearby:
        lines.append(f"WINDOW|index={index}|median_milliday={median}|within_1_day={near1}|within_2_days={near2}|json=0")
    (HERE/"INDEPENDENT-OBSERVATION-REVIEW.hbp").write_bytes(("\n".join(lines)+"\n").encode("ascii"))
    print("REAL_RV_SOURCE_722_PHOTO_2212_SHA_MATCH_PASS")
    print("REAL_NINE_WINDOWS_CHRONOLOGY_INDEPENDENT_PASS",len(train),len(test))
    print("EXTRA_PERIOD_9_WINDOWS",better,"better",worse,"worse","signflip",extreme,"/ 512; descriptive only")
    print("NO_CLAIM_OF_NEW_PLANET")

if __name__=="__main__":main()
