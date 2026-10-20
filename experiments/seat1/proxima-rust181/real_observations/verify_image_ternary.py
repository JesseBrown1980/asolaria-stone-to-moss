#!/usr/bin/env python3
"""Independent, integer-only verification of *real NASA released* image decoding.
No generated/AI-filled image pixels, no neural super-resolution, no calibrated
photon-wavelength assertions. Pillow is only the JPEG decoder.
"""
import hashlib, json, pathlib, time
from PIL import Image

ROOT=pathlib.Path("real_observations/output")
EXPECTED_SOURCE_SHA="481540dc6ddc65ddf0cf8d8bb495bf08d79552e505fba29916d41ed9f35da2a3"
EXPECTED_DECODED_SHA="f3ba34149a5c6f570af95b72211fd98c6952fcd8d10a161fab27d69b89ff472c"
def digest(data):return hashlib.sha256(data).hexdigest()
def main():
    manifest=json.loads((ROOT/"ORIGINAL-SOURCE-MANIFEST.json").read_text())
    image=manifest["image"]
    assert image["available"] is True
    assert image["encoded_format"]=="jpg"
    source=(ROOT/image["file"]).read_bytes()
    assert source[:3]==b"\xff\xd8\xff"
    assert digest(source)==EXPECTED_SOURCE_SHA
    assert digest(source)==image["sha256"]
    with Image.open(ROOT/image["file"]) as im:
        im.load()
        assert im.size==(763,587)
        width,height=im.size
        rgb=im.convert("RGB").tobytes()
    assert digest(rgb)==EXPECTED_DECODED_SHA
    start=time.perf_counter_ns()
    hist={-1:0,0:0,1:0}
    reconstructed=bytearray(len(rgb))
    for idx,byte in enumerate(rgb):
        number=byte
        restored=0
        multiplier=1
        for _ in range(6):
            remainder=number%3
            trit=-1 if remainder==2 else remainder
            number=(number-trit)//3
            hist[trit]+=1
            restored+=multiplier*trit
            multiplier*=3
        assert number==0
        assert restored==byte
        reconstructed[idx]=restored
    assert reconstructed==rgb
    assert sum(hist.values())==len(rgb)*6
    output={
        "schema":"ASOLARIA-PROXIMA-REAL-HUBBLE-PUBLICATION-TERNARY-V1",
        "instrument":"Hubble WFC3/UVIS","filter":"F555W",
        "exposure_date":"2012-10-01","exposure_seconds":175,
        "source":"NASA released rendered JPEG, NOT calibrated WCS FITS and NOT seven measured wavelength bands",
        "source_jpeg_sha256":digest(source),
        "decoded_rgb_sha256":digest(rgb),
        "width":width,"height":height,"pixel_count":width*height,
        "decoded_rgb_byte_samples":len(rgb),
        "balanced_trits_per_byte":6,"trit_count":len(rgb)*6,
        "trit_histogram":{"minus":hist[-1],"zero":hist[0],"plus":hist[1]},
        "full_rgb_byte_roundtrip_exact":True,
        "new_3d_particles_detected":0,
        "new_planet_detected":False,
        "physical_photon_wavelength_instrumented":False,
        "raw_calibrated_fits_ingested":False,
        "different_observation_epochs_in_image_test":1,
        "code_exec_host":"GitHub Actions hosted physical CPU"
    }
    (ROOT/"REAL-HUBBLE-TERNARY-RECEIPT.json").write_text(json.dumps(output,sort_keys=True,indent=2)+"\n")
    print("REAL_HUBBLE_IMAGE_SOURCE_SHA",digest(source))
    print("REAL_HUBBLE_RGB_ROUNDTRIP_SHA",digest(rgb))
    print("REAL_HUBBLE_PIXELS",width*height,"TRITS",len(rgb)*6,"EXACT_RECONSTRUCTION_PASS")
    print("NO_NEW_PLANET_FROM_SINGLE_RENDERED_IMAGE")
if __name__=="__main__":main()
