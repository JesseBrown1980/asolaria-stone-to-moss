#!/usr/bin/env python3
"""Independent, integer-only verification of *real NASA released* image decoding.
No generated/AI-filled image pixels, no neural super-resolution, no calibrated
photon-wavelength assertions. Pillow is only the JPEG decoder.
"""
import hashlib, pathlib, time
from PIL import Image

ROOT=pathlib.Path("real_observations/output")
EXPECTED_SOURCE_SHA="481540dc6ddc65ddf0cf8d8bb495bf08d79552e505fba29916d41ed9f35da2a3"
EXPECTED_DECODED_SHA="f3ba34149a5c6f570af95b72211fd98c6952fcd8d10a161fab27d69b89ff472c"
def digest(data):return hashlib.sha256(data).hexdigest()
def main():
    original=(ROOT/"ORIGINAL-SOURCE-MANIFEST.hbp").read_text()
    images=[line for line in original.splitlines() if line.startswith("IMAGE|")]
    assert len(images)==1
    pairs=images[0].split("|")[1:]
    image={}
    for pair in pairs:
        assert "=" in pair
        key,value=pair.split("=",1)
        assert key not in image and value
        image[key]=value
    assert image["available"]=="true"
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
    # Audit original image bytes and all six balanced trits per channel
    # without emitting nested JSON or claiming calibrated wavelength data.
    lines=[
      "HBP1|schema=ASOLARIA-PROXIMA-REAL-HUBBLE-TERNARY-V2|field=GF3|trits=-1,0,+1|json=0",
      "SOURCE|instrument=Hubble_WFC3_UVIS|filter=F555W|exposure_date=2012-10-01|exposure_seconds=175|source=NASA_RENDERED_JPEG_NOT_CALIBRATED_WCS_FITS|json=0",
      f"BYTES|source_jpeg_sha256={digest(source)}|decoded_rgb_sha256={digest(rgb)}|width={width}|height={height}|pixel_count={width*height}|rgb_byte_samples={len(rgb)}|json=0",
      f"TRITS|balanced_trits_per_byte=6|trit_count={len(rgb)*6}|negative={hist[-1]}|zero={hist[0]}|positive={hist[1]}|exact_rgb_roundtrip=PASS|json=0",
      "BOUNDARY|new_3d_particles_detected=0|new_planet_detected=FALSE|physical_photon_wavelength_instrumented=FALSE|raw_calibrated_fits_ingested=FALSE|image_epochs=1|json=0"
    ]
    (ROOT/"REAL-HUBBLE-TERNARY-RECEIPT.hbp").write_bytes(("\\n".join(lines)+"\\n").encode("ascii"))
    print("REAL_HUBBLE_IMAGE_SOURCE_SHA",digest(source))
    print("REAL_HUBBLE_RGB_ROUNDTRIP_SHA",digest(rgb))
    print("REAL_HUBBLE_PIXELS",width*height,"TRITS",len(rgb)*6,"EXACT_RECONSTRUCTION_PASS")
    print("NO_NEW_PLANET_FROM_SINGLE_RENDERED_IMAGE")
if __name__=="__main__":main()
