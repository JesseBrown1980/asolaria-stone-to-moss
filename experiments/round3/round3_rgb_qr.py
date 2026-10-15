#!/usr/bin/env python3
"""Independently decode rendered *digital RGB* QR planes. NO camera/photons."""
import argparse
import base64
import hashlib
import json
import struct
from pathlib import Path
import numpy as np
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

def sha(b):
    return hashlib.sha256(b).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=Path("round3-qr-artifacts"))
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    prefix=b"ASOLARIA-R3-MEMORY-V1|synthetic|"
    payload=b"".join(hashlib.sha256(prefix+struct.pack("<I",i)).digest()
                     for i in range(108))
    assert len(payload)==3456
    block_size=128
    chunks=[payload[i:i+block_size] for i in range(0,len(payload),block_size)]
    assert len(chunks)==27
    recovered={}
    meta=[]
    for image_number in range(9):
        planes=[]
        for channel in range(3):
            index=image_number*3+channel
            message=base64.b64encode(struct.pack("<I",index)+chunks[index]).decode("ascii")
            qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                             border=4,box_size=8)
            qr.add_data(message,optimize=0)
            qr.make(fit=True)
            planes.append(np.asarray(qr.make_image(
                fill_color="black",back_color="white").convert("L"),dtype=np.uint8))
        assert len({p.shape for p in planes})==1
        frame=np.stack(planes,axis=2)
        filename=args.out/("colour-qr-%02d.png"%image_number)
        Image.fromarray(frame,"RGB").save(filename)
        reopened=np.asarray(Image.open(filename).convert("RGB"))
        for channel in range(3):
            symbols=decode(Image.fromarray(reopened[:,:,channel],mode="L"))
            assert len(symbols)==1,("missing QR",image_number,channel)
            record=base64.b64decode(symbols[0].data,validate=True)
            index=struct.unpack("<I",record[:4])[0]
            assert index==3*image_number+channel
            assert index not in recovered
            recovered[index]=record[4:]
        meta.append({"frame":image_number,
                     "png_sha256":sha(filename.read_bytes())})
    assembled=b"".join(recovered[i] for i in range(27))
    assert assembled==payload
    result={"schema":"ASOLARIA-R3-RGB-STANDARD-QR-V1",
            "status":"PASS","frames":9,"decoded_planes":27,
            "source_bytes":len(payload),"chunk_size":block_size,
            "source_sha256":sha(payload),"recovered_sha256":sha(assembled),
            "byte_exact":True,"fischer_le_indices":27,
            "files":meta,"camera_used":False,
            "physical_light_storage":False,
            "classification":"PIXEL_RGB_QR_READBACK_NOT_PHYSICAL_OPTICS"}
    (args.out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","frames":9,"decoded_planes":27,
                      "bytes":3456,"sha256":sha(assembled)},sort_keys=True))

if __name__=="__main__":
    main()
