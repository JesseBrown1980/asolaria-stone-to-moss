# Measurement referee (not kernel): decodes the Webb JPEG with Pillow, counts 27x27 leaves and duplicates,
# and compares zlib-9 on raw RGB versus reversible per-channel predictors. Usage: python3 -I webb_tile_and_predictive_compression.py <jpeg> left up avg paeth med
import sys, zlib, hashlib, collections
from PIL import Image
p = sys.argv[1]
raw = open(p,'rb').read()
print("jpeg_sha256", hashlib.sha256(raw).hexdigest(), "bytes", len(raw))
im = Image.open(p); print("mode", im.mode, "size", im.size, "pillow_jpeg_decoder")
im = im.convert("RGB"); W, H = im.size; px = im.tobytes()
print("decoded_rgb_bytes", len(px), "sha256", hashlib.sha256(px).hexdigest())
# 27x27 leaves
cols, rows = -(-W//27), -(-H//27)
print("webb_leaves_27", cols, "x", rows, "=", cols*rows, "| +3 HST 9x9 =", cols*rows+243)
full = [(r,c) for r in range(H//27) for c in range(W//27)]
cnt = collections.Counter()
for r,c in full:
    h = hashlib.sha256()
    for y in range(r*27, r*27+27):
        o = (y*W + c*27)*3; h.update(px[o:o+81])
    cnt[h.digest()] += 1
dupe_tiles = sum(v for v in cnt.values() if v > 1); dupe_extra = sum(v-1 for v in cnt.values() if v > 1)
print("full_27_tiles", len(full), "unique", len(cnt), "tiles_in_duplicate_groups", dupe_tiles, "redundant_copies", dupe_extra)
for lvl in (6, 9):
    print(f"zlib{lvl}_raw", len(zlib.compress(px, lvl)))
# reversible predictors (byte-wise mod 256), per channel
stride = W*3
def pred(name):
    out = bytearray(len(px))
    for y in range(H):
        b = y*stride
        for x in range(stride):
            i = b + x; v = px[i]
            a = px[i-3] if x >= 3 else 0
            u = px[i-stride] if y else 0
            ul = px[i-stride-3] if (y and x >= 3) else 0
            if name == "left": p_ = a
            elif name == "up": p_ = u
            elif name == "avg": p_ = (a+u)//2
            elif name == "paeth":
                pp = a+u-ul; pa, pb, pc = abs(pp-a), abs(pp-u), abs(pp-ul)
                p_ = a if (pa <= pb and pa <= pc) else (u if pb <= pc else ul)
            elif name == "med":
                p_ = min(a,u) if ul >= max(a,u) else (max(a,u) if ul <= min(a,u) else a+u-ul)
            out[i] = (v - p_) & 255
    return bytes(out)
for name in sys.argv[2:]:
    r = pred(name); z = len(zlib.compress(r, 9))
    print(f"pred_{name}_zlib9", z)
