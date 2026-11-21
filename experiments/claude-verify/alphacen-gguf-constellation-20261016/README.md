# Alpha Centauri GGUF constellation — independent verification (2026-10-16)

`CAPTURE|at=2026-10-16T20:05Z|github=JesseBrown1980|hf=Jessedbrown|rust=1.81.0|float_used=0|json=0`

This folder checks ChatGPT's Alpha Centauri GGUF constellation report against bytes on GitHub. The full receipt is [`VERIFY-ALPHACEN-GGUF-CONSTELLATION-20261016.hbp`](VERIFY-ALPHACEN-GGUF-CONSTELLATION-20261016.hbp). Every file has a `.sha256` sidecar.

Claim classes: **MEASURED_GATE** means re-run or re-hashed here. **MEASURED_GIT** means read from git or GitHub API bytes. **CLAIMED** means stated but not checked. **BOUNDARY** means not measured.

## Chain

```text
@seat1 → alpha-cen-jwst-zoom@675288d → run 38949542459 → artifact 12066934619
       → webb_miri_esa_large.jpg [5475f875…] → explorer HTML embedded image [+1]
@chatgpt → AlphaCentauri_Constellation_PixelTiles_GGUFv3.gguf [3084cd8b…] → published [0] → verified [0]
```

## Verdicts (+1 holds · 0 unknown · -1 fails)

| Claim | Verdict | Evidence |
|---|---|---|
| Explorer's Webb image is the ESA original | +1 | Embedded JPEG SHA-256 `5475f875…` matches Seat1 artifact 12066934619 (`weic2515c.jpg`). The artifact zip digest matches GitHub. |
| 27.20 MB decoded, 6.56 MB zlib, 5.09 MB predictive (22.5%) | +1 | 27,199,800 B; 6,561,651 B; 5,086,283 B (left-neighbour predictor) |
| 12,772 addressable 27×27 leaves | +1 | 187×67 = 12,529 Webb + 243 HST |
| 542 identical Webb tiles | +1 | 542 duplicate copies, edge tiles included; the largest group has 347 tiles |
| S1: 3.5 mJy at 15.5 µm, 1.5″, Aug 2024; not recovered Feb/Apr 2025 | +1 | Beichman, Sanghi et al. 2025, ApJ 989 L22; MAST rows for 6797 (MJD 60726) and 9252 (MJD 60790) |
| Issue #84 open; PR #87 and #90 merged | +1 | GitHub API |
| PR #90 mathematics | +1 | Re-derived in [`rainbow27-check`](rainbow27-check) (Rust 1.81, integers only) |
| GGUF `3084cd8b…`: 411/411 tensors, browser PASS | 0 | The file is not on any GitHub branch or PR ref, nor on Hugging Face or in Seat1's artifact. It is held by the operator. |

## Better result found

| Reversible predictor + zlib-9 | Bytes | Reduction |
|---|---|---|
| left (used in ChatGPT's report) | 5,086,283 | 22.5% |
| paeth | 4,783,500 | 27.1% |
| up | 4,702,577 | 28.3% |
| **MED / LOCO-I** | **4,615,523** | **29.7%** |

## Rule audit

- `no_float` **-1**: the GGUF stores HST tiles as F32, and the explorer's contrast stretch uses float math.
- `no_node`, `no_json` **-1**: PR #87 and PR #90 (both merged to `main`) run Python and Node22 and emit JSON.
- `rust_kernel` **-1**: ChatGPT's package ships Python reconstruction tools.
- This folder: both crates are Rust 1.81, std-only, pass clippy `-D warnings`, and use no `f32`/`f64`. The receipts are HBP. The one Python file is a labelled measurement referee and is not part of the kernel.

## Tools

- [`gguf-verify-hbp`](gguf-verify-hbp) is a GGUF v2/v3 verifier.
  - It reads float tensors as raw bit patterns.
  - It checks per-tensor SHA-256, layout, overlaps and trailing bytes.
  - It supports `--expect-sha256` and `--expect-meta key=value`.
  - Its SHA-256 passes the FIPS 180-2 test vectors.
  - Tested on 4 real FOLLOW GGUFs (+1) and 5 attacks (all -1).
- [`rainbow27-check`](rainbow27-check) re-derives Issue #84 / PR #90. Its output must equal [`EXPECTED-OUTPUT.hbp`](rainbow27-check/EXPECTED-OUTPUT.hbp).
- CI is [`claude-verify-alphacen-gguf.yml`](../../../.github/workflows/claude-verify-alphacen-gguf.yml). It uses no JavaScript actions: plain `git` fetch, `rustup` 1.81.0, Ubuntu and Windows.

To verify the GGUF once it is published:

```text
cargo +1.81.0 run --release --locked --manifest-path gguf-verify-hbp/Cargo.toml -- \
  AlphaCentauri_Constellation_PixelTiles_GGUFv3.gguf \
  --expect-sha256 3084cd8ba7eaafb75b8d2a7e2c42425b34c69113dca6930f1d28ce44345e3a00 \
  --expect-meta general.architecture=asolariaimg \
  --expect-meta asolaria.webb.original_file_sha256=5475f875fc7e5ea2c375fe97f59fb0576856f2b767b7d19508bc6a6c46803bb7 \
  --tensors
```

## Boundary

- The GGUF's contents are not verified here.
- The explorer's three HST preview PNGs are not yet traced to Seat4's original FITS (run 38916527331).
- No Webb detector-level FITS was ingested.
- No planet detection is claimed. Zooming adds no resolution.
- Hugging Face was not updated because this session has no Hugging Face write credential.

The Webb image inside the explorer is ESA/Webb release `weic2515c` (CC BY 4.0; full credit is on the ESA/Webb release page). The explorer HTML is the operator's ChatGPT-produced file, published unchanged.
