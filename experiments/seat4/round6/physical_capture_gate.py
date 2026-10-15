#!/usr/bin/env python3
"""Real spectrometer/camera acquisition intake (external custody remains mandatory).
NO automatic physical PASS from files, flags, synthetic counts or valid local hashes.
"""
from __future__ import annotations
import csv,hashlib,json,sys
from pathlib import Path
BANDS=("red","orange","yellow","green","blue","indigo","violet")
DELAYS=(1,10,60)
ARMS=("WRITE","SHAM","ERASE")
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return (json.dumps(x,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")
def hold(reason,physical=False):
 return {"schema":"ASOLARIA-SEAT4-PHYSICAL-CAPTURE-INTAKE-V1",
 "decision":"PHYSICAL_HOLD",
 "reason":reason,"independent_external_custody_verified":False,
 "optically_stored_photons_verified":False,"biological_neural_memory_verified":False,
 "actual_external_capture_files_supplied":physical}
def require(v,reason):
 if not v:raise ValueError(reason)
def intake(folder):
 if folder is None:return hold("NO_EXTERNAL_SPECTRAL_INSTRUMENT_CAPTURE_SUPPLIED")
 expected=("challenge.json","calibration.json","detector.csv","custody.json")
 if any(not (folder/x).is_file() for x in expected):return hold("MISSING_MANDATORY_RAW_HARDWARE_OR_CUSTODY_FILES",True)
 try:
  raw={name:(folder/name).read_bytes() for name in expected}
  challenge=json.loads(raw["challenge.json"])
  calibration=json.loads(raw["calibration.json"])
  custody=json.loads(raw["custody.json"])
  require(challenge.get("schema")=="ASOLARIA-R6-PHYSICAL-CHALLENGE-V1","WRONG_CHALLENGE_SCHEMA")
  require(challenge.get("fresh_external_nonce") and challenge.get("source_precommit_sha256"),"MISSING_FRESH_RANDOM_CHALLENGE")
  require(calibration.get("schema")=="ASOLARIA-R6-PHYSICAL-SPECTROMETER-CALIBRATION-V1","NO_PHYSICAL_CALIBRATION")
  wl=calibration.get("seven_wavelengths_nm")
  require(isinstance(wl,list) and len(wl)==7 and all(isinstance(x,(float,int)) for x in wl),"MISSING_MEASURED_WAVELENGTHS")
  require(len(set(wl))==7 and min(wl)>0,"DUPLICATE_OR_IMPOSSIBLE_WAVELENGTH")
  require(calibration.get("spectrometer_model") and calibration.get("detector_calibration_sha256"),
          "NO_CALIBRATED_DETECTOR")
  require(custody.get("source_custodian") and custody.get("detector_custodian") and
          custody.get("external_witness"),"NO_DISTINCT_EXTERNAL_WITNESSES")
  require(challenge.get("raw_capture_sha256")==sha(raw["detector.csv"]),"RAW_FILE_DIGEST_MISMATCH")
  import io
  reader=csv.DictReader(io.StringIO(raw["detector.csv"].decode("utf-8")))
  wanted={"arm","band","site","delay_s","detector_counts","dark_counts",
          "integration_ms","raw_capture_id","source_sequence","spectrometer_channel"}
  require(reader.fieldnames and wanted.issubset(reader.fieldnames),"MISSING_SENSOR_COLUMN")
  rows=list(reader);require(len(rows)>=3*3*81*7,"NOT_ENOUGH_REAL_READS")
  keys=set()
  for p in rows:
   arm=p["arm"];band=p["band"];site=int(p["site"]);delay=int(p["delay_s"])
   require(arm in ARMS and band in BANDS and delay in DELAYS and 0<=site<81,"OUT_OF_RANGE_CAPTURE_ROW")
   require(float(p["detector_counts"])>=0 and float(p["dark_counts"])>=0 and float(p["integration_ms"])>0,
           "BAD_DETECTOR_COUNTS_OR_DURATION")
   require(bool(p["raw_capture_id"]) and bool(p["source_sequence"]) and bool(p["spectrometer_channel"]),
           "MISSING_RAW_SENSOR_ID")
   address=(arm,band,site,delay)
   require(address not in keys,"DUPLICATE_PHYSICAL_SAMPLE")
   keys.add(address)
  require(len(keys)==3*3*81*7,"MISSING_SITE_BAND_DELAY_ARM")
  # Static acceptance of forms or matching checksums DOES NOT prove real instrument
  # operation, independent custody, calibrated spectral content or a blinded claim.
  result=hold("RAW_CAPTURE_FORMAT_VALID_EXTERNAL_SIGNED_PHYSICAL_CUSTODY_AND_BLINDED_REPLAY_STILL_REQUIRED",True)
  result.update(raw_bytes_sha256={name:sha(bytes_) for name,bytes_ in raw.items()},
                detector_records=len(rows),declared_calibrated_bands=7)
  return result
 except (OSError,ValueError,KeyError,TypeError,UnicodeDecodeError) as e:
  return hold("INVALID_PHYSICAL_CAPTURE:"+str(e),True)
def main():
 args=sys.argv[1:]
 if len(args)==2 and args[0]=="--self-test":capture=None;destination=Path(args[1])
 elif len(args)==3 and args[0]=="--capture":capture=Path(args[1]);destination=Path(args[2])
 else:raise SystemExit("usage: physical_capture_gate.py --self-test OUTPUT_DIR | --capture INPUT_DIR OUTPUT_DIR")
 destination.mkdir(parents=True,exist_ok=True)
 status=intake(capture)
 if capture is None:
  assert status["decision"]=="PHYSICAL_HOLD" and status["actual_external_capture_files_supplied"] is False
  assert intake(destination)["decision"]=="PHYSICAL_HOLD"
 data=canonical(status);(destination/"r6-physical-status.json").write_bytes(data)
 (destination/"r6-physical-status.json.sha256").write_text(
  sha(data)+"  r6-physical-status.json\n",encoding="ascii")
 print(json.dumps({"physical":status["decision"],"reason":status["reason"]},sort_keys=True))
if __name__=="__main__":main()
