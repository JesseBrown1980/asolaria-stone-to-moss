#!/usr/bin/env python3
"""Independent original-byte and nine-checkpoint review, integer-only.
Does not validate the Rust fitted model coefficients; this separately checks
original source integrity, chronology, observations, and reviewer controls.
"""
import hashlib, json, pathlib
from collections import Counter
from itertools import product
from decimal import Decimal

HERE=pathlib.Path("real_observations/output")
RV_SHA="027cff5c10b541608b727abada2af531037223edec3bb9112fcbb45fc333e474"
PH_SHA="d42dad64fcbf80159bfc1edf20c35db82d01ce2aa7830248d7198aad05bc6dd5"
def sha(x):return hashlib.sha256(x).hexdigest()
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
    train=[];test=[];inst_counts={}
    for inst in range(6):
        subset=sorted((x for x in data if x[0]==inst),key=lambda r:r[1])
        cutoff=(len(subset)*7//10) if len(subset)>=10 else len(subset)
        train+=subset[:cutoff];test+=subset[cutoff:]
        inst_counts[str(inst)]={"train":cutoff,"test":len(subset)-cutoff}
    result=json.loads((HERE/"NINE-REAL-OBSERVATION-WINDOWS.json").read_text())
    assert result["source_measurements"]==722
    assert result["source_photo_rows"]==2212
    assert result["train_rows"]==len(train)
    assert result["heldout_rows"]==len(test)
    assert result["per_instrument"]==inst_counts
    instrument_scores=result["heldout_instrument_scores"]
    assert set(instrument_scores)==set(str(i) for i in range(6))
    for inst,values in instrument_scores.items():
        assert values["n"]==inst_counts[inst]["test"]
        for key in ("baseline_wrmse_mm_s","known_wrmse_mm_s","extra_wrmse_mm_s"):
            assert 0<=values[key]<100000

    assert result["first_bjd_minus_2450000_milliday"]==min(r[1] for r in data)
    assert result["last_bjd_minus_2450000_milliday"]==max(r[1] for r in data)
    assert result["exploratory_trials"]==6
    assert result["brown_edens_i"].startswith("UNDETECTED")
    assert result["source_hubble_status"] in ("HUBBLE_BINARY_SOURCE_HELD","HUBBLE_PUBLIC_RENDERED_IMAGE_AVAILABLE")
    assert 0<=result["extra_wrmse_mm_s"]<100000
    assert 0<=result["known_bd_wrmse_mm_s"]<100000
    assert 0<=result["null_wrmse_mm_s"]<100000
    periods=[900_000,2_700_000,8_100_000,24_300_000,72_900_000,190_000_000]
    assert result["train_selected_extra_period_1e5_days"] in periods
    alltest=sorted(test,key=lambda r:r[1])
    checkpoints=result["heldout_windows"]
    assert len(checkpoints)==9
    nearby=[]
    for i,row in enumerate(checkpoints):
        subset=alltest[len(alltest)*i//9:len(alltest)*(i+1)//9]
        assert row["index"]==i+1
        assert row["count"]==len(subset)
        assert row["median_bjd_minus_2450000_milliday"]==subset[len(subset)//2][1]
        assert all(row[k]>=0 for k in ["baseline_wrmse_mm_s","known_bd_wrmse_mm_s","exploratory_wrmse_mm_s"])
        median=row["median_bjd_minus_2450000_milliday"]
        count1=sum(abs(x[1]-median)<=1000 for x in subset)
        count2=sum(abs(x[1]-median)<=2000 for x in subset)
        nearby.append({"index":i+1,"observation_date_bjd_minus2450000_milli":median,
            "within_1_day_count":count1,"within_2_days_count":count2})
    # A nine-window robustness check, distinct from the RV fit itself:
    # Do not confuse an extra fitted period with a newly detected planet.
    differences=[
        w["known_bd_wrmse_mm_s"]-w["exploratory_wrmse_mm_s"]
        for w in checkpoints
    ]
    gains=[
        w["known_bd_wrmse_mm_s"]**2-w["exploratory_wrmse_mm_s"]**2
        for w in checkpoints
    ]
    observed=sum(gains)
    extreme=sum(sum(g*s for g,s in zip(gains,signs))>=observed
                for signs in product((-1,1),repeat=9))
    assert len(checkpoints)==9
    assert extreme>=1
    better=sum(d>0 for d in differences)
    worse=sum(d<0 for d in differences)
    source=HERE/"ORIGINAL-SOURCE-MANIFEST.json"
    manifest=json.loads(source.read_text())
    assert manifest["files"][0]["sha256"]==RV_SHA
    assert manifest["files"][1]["sha256"]==PH_SHA
    assert manifest["image"]["available"] is False or (HERE/manifest["image"]["file"]).exists()
    doc={
      "schema":"ASOLARIA-INDEPENDENT-REAL-PROXIMA-SOURCE-WINDOWS-V1",
      "source_rv_sha256":RV_SHA,"source_photometry_sha256":PH_SHA,
      "rv_instruments_seen":dict(Counter(str(x[0]) for x in data)),
      "real_rv_rows":722,"real_photometry_rows":2212,
      "train_rows":len(train),"heldout_rows":len(test),
      "actual_observation_date_range_milliday":
        [min(x[1] for x in data),max(x[1] for x in data)],
      "nine_checkpoints":nearby,
      "extra_period_windows_better":better,
      "extra_period_windows_worse":worse,
      "extra_period_signflip_extreme_sums":extreme,
      "extra_period_signflip_total_assignments":512,
      "signflip_statistic":"nine aggregated windows, post-selection diagnostic, NOT multiple-trial-adjusted planet-detection p-value",

      "independently_recalculated_source_chronology":True,
      "independent_fit_coefficients_reimplementation":False,
      "new_planet_from_this_data":False,
      "raw_telescope_fits_images_loaded":False,
      "model_significance_or_external_validation":False
    }
    (HERE/"INDEPENDENT-OBSERVATION-REVIEW.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print("REAL_RV_SOURCE_722_PHOTO_2212_SHA_MATCH_PASS")
    print("REAL_NINE_WINDOWS_CHRONOLOGY_INDEPENDENT_PASS",len(train),len(test))
    print("SOURCE_INSTRUMENT_COUNTS",doc["rv_instruments_seen"])
    print("OBSERVATION_EPOCHS_MILLIDAY",doc["actual_observation_date_range_milliday"])
    print("EXTRA_PERIOD_9_WINDOWS",better,"better",worse,"worse","signflip",extreme,"/ 512; descriptive only")
    print("NO_CLAIM_OF_NEW_PLANET")
if __name__=="__main__":main()
