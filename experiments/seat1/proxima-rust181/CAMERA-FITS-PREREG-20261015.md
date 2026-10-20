# Seat 1 — Original camera observations → exact balanced ternary memories

**2026-10-15 · preregistration, before implementation.** Keep this separate from synthetic lightbank receipt and simulated Brown–Edens I.

## Source cameras and original data

The source photons come from real astronomical instruments, but there is no camera operating at Proxima b or within the Proxima system. Sources for a real-camera comparison:

1. [STScI/MAST Digitized Sky Survey cutout service](https://outerspace.stsci.edu/spaces/MASTDATA/pages/176435492/Photographic%2BSky%2BSurveys): publicly documented FITS/GIF cutouts with source plates `poss2ukstu_red`, `poss2ukstu_blue`, `poss2ukstu_ir`. These are **photographic survey exposures**, not simultaneous seven-band spectroscopy.
2. [NASA SkyView FITS API](https://skyview.gsfc.nasa.gov/current/docs/batchpage.html): structured source pixels, WCS and FITS headers, distinct from rendered RGB JPEG quicklooks.
3. [ESO ESO1629i](https://www.hq.eso.org/public/images/eso1629i/): 11086×11256 published visual mosaic from DSS2 B+R / R / I plates, composite processing includes artefacts. Not a raw spectral cube or directly resolved exoplanets.
4. [NASA Hubble observation of Proxima Centauri](https://science.nasa.gov/asset/hubble/hubble-image-of-proxima-centauri/): another genuine camera recording from a different instrument, not a direct image of Proxima b's surface.

## Predeclared codec and gate

- Rust **1.81**, standard library, `clippy --offline --locked --all-targets -- -D warnings`, integer trits only.
- Decode **uncompressed** FITS primary two-dimensional raster. FITS card widths 80 bytes, padding 2880, BITPIX `8/16/32` signed/big-endian, NAXIS=2, finite exact axis bounds. Preserve original FITS header bytes and pixel values. Reject any `BSCALE` other than unity and `BZERO` other than zero in the strict raw-int path; do not silently treat scaled pixels as calibrated counts.
- Map pixel bit patterns, **without information loss**, to fixed-width balanced-ternary codes (8-bit→6 trits, 16-bit→11 trits, 32-bit→21 trits). Reconstruct original bytes byte-for-byte and prove exact inverse on adversarial boundary cases.
- ID each pixel by **immutable exposure/source record + band/filter + (x,y)**. When a second distinct exposure arrives, append an event to that specific particle's memory. Never say there is a history of independent events before the actual images are available. Never fabricate wavelengths or map R/G/B computer display channels to a seven-band calibrated spectrometer.
- Demonstration fixture: programmatically generated 7×9 signed FITS frame (63 simulated pixels) with correct header padding. This is *synthetic* and must never be reported as an actual Proxima photograph. Externally acquired FITS sources remain unclaimed until original bytes downloaded, independently SHA-256 sealed and decoded.
- Independent Python full-pixel redecoder must compare original source pixel bytes to Rust's output, verify every sample and reject corrupt header, padding, truncated data, and altered pixel without origin-source provenance.
- Each 2D pixel is an **instrument sample**, not an independently identified star-system atom or proof of a unique 3D realization. Astrophysical claims require additional observational analysis against null models and source custody.

**Release gate:** The matrix jump applies only to a precisely declared state transition. It does not create missing camera photons or higher optical resolution. Brown–Edens I remains model-only until independent observations support a new planet.
