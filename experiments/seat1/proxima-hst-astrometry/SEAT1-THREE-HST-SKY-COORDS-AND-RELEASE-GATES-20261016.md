# Seat 1 — Proxima HST sky-coordinate, source-custody and physical-memory review

**Scientific status: PRELIMINARY ASTROMETRY / EXTERNAL INSTITUTIONAL IMAGE PROVENANCE PASS / PLANETARY ORBIT HOLD / PHOTON-MEMORY HOLD.** 2026-10-16. Stacked on Seat 4 [draft PR #136](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/136), frozen original-source artifact 12052940550, acquisition [run 38916527331](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38916527331), and exact-head software [run 38917725213](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38917725213). **No original image files, frozen 2.062 m/s RV benchmark, code, or historical stones changed.**

## 1. Three genuine external original observation files

The three public, calibrated HST/WFC3 UVIS **F555W** 0.48-second science FITS observations are **from separate nights**, not synthetic frames or separate spectral bands. Their bytes were extracted from the independently downloaded original GitHub-hosted acquisition artifact and SHA-256 checked:

| UTC start | MAST root / proposal | Original bytes | Original FITS SHA-256 |
|---|---|---:|---|
| 2012-10-01 01:08:35 | ic3j01a8q / 12985 | 42,526,080 | `cc8d0afe69943b5aec7e678a75ac84341138d6343e092a7ab99b276006ab541c` |
| 2014-04-01 12:16:11 | icdc03lzq / 13466 | 42,341,760 | `fd8563aaabf0530f3dc5a1ee837c1759493f3015335f85cc36a11d4005217ad0` |
| 2015-04-16 07:06:42 | icpc01xwq / 13847 | 42,393,600 | `68a2633f54141cb0d55f1d8a35bbcca20654163a97c75ad408a3169e8e50fc67` |

Original NASA/STScI source identity: `mast:HST/product/<root>_flc.fits`; primary FITS header ROOTNAME, PROPOSID, DATE-OBS/TIME-OBS, TARGNAME=PROXIMA-CEN-SOURCE, INSTRUME=WFC3, DETECTOR=UVIS, FILTER=F555W, SCI BITPIX=-32, verified on all three. STScI/MAST is an **institutional external telescope/archive custodian**, independently of Asolaria. This is archival source provenance, **not a detector-private-key signed original photon waveform**.

## 2. Exact WCS sky reference coordinates from the SCI headers

Each SCI header uses ICRS `RA---TAN-SIP`/`DEC--TAN-SIP`, `CRPIX=(762,815)` in FITS 1-based coordinates, and fourth-order SIP polynomials. The `CRVAL` values are **sky positions at this reference detector pixel, not the star's centroid**.

| Date | Active WCSNAME | CRVAL1 RA (deg) | CRVAL2 Dec (deg) | Pixel scale |
|---|---|---:|---:|---:|
| 2012-10-01 | IDC_2731450pi-FIT_REL_GAIAeDR3 | 217.3974541472 | -62.680096607433 | ~39.618 mas/pixel |
| 2014-04-01 | IDC_2731450pi-HSC30 | 217.38801431002 | -62.673367378376 | ~39.628 mas/pixel |
| 2015-04-16 | IDC_2731450pi-HSC30 | 217.39014104165 | -62.672860513892 | ~39.627 mas/pixel |

**Never subtract CRVAL1/2 between different orientations and call the difference planet motion.** Different pointing/roll/WCS calibrations require true registration.

## 3. Provisional bright-source / Proxima sky positions from actual SCI pixels

An independent read-only Python source referee selected the dominant source within 40 detector pixels of the SIMBAD/Gaia-propagated Proxima J2000 position (`RA=217.428942221606 deg, Dec=-62.679490189076 deg`; `mu_RA*cosDec=-3781.741 mas/yr, mu_Dec=769.465 mas/yr`). It made a 9x9 background-subtracted center-of-light and computed the forward TAN+SIP celestial projection. The Gaia selection prior omitted annual spacecraft parallax; no D2IM/NPOL distortion lookup corrections, ePSF fitting, reference-star registration or published uncertainty fit were applied.

| UTC date | Preliminary centroid detector x,y, zero-based | Preliminary star RA (deg) | Preliminary star Dec (deg) |
|---|---|---:|---:|
| 2012-10-01 | (734.35811,1142.04998) | 217.39952697678 | -62.67661326322 |
| 2014-04-01 | (1158.68404,1012.47502) | 217.39636285465 | -62.67661318673 |
| 2015-04-16 | (1048.04672,1007.29561) | 217.39386730733 | -62.67639509785 |

Apparent **2012 to 2015** difference is approximately `delta_RA*cosDec = -9.3523 arcsec`, `delta_Dec = +0.7854 arcsec`, net `9.385 arcsec` in 2.54 years: consistent in scale with **known Proxima stellar proper motion plus seasonal parallax**, not a planetary reflex measurement. All quoted numerical precision is computational output precision, **NOT instrument astrometric accuracy**. The source selection uses a Gaia prior and is not blind source identification. The WFC3 full distortion/covariance reference solution remains mandatory. For calibrated WFC3 use [STScI WFC3 astrometry](https://hst-docs.stsci.edu/wfc3dhb/chapter-9-wfc3-data-analysis/9-2-astrometry) and [geometric distortion corrections](https://hst-docs.stsci.edu/wfc3dhb/chapter-4-wfc3-images-distortion-correction-and-astrodrizzle/4-2-distortion-corrections-and-image-combination).

## 4. Planet hypothesis: exact acceptance gate

- **REQUIRED**: complete calibrated WFC3 distortion + D2IM/NPOL + headerlet choice; ePSF/ERR/DQ source centroids; independent Gaia field-star reference positions with proper motion/parallax, HST spacecraft observation epoch and observer barycentric correction, camera roll, and covariance.
- **REQUIRED**: source-blinded registered positions over more independent observing epochs (not merely three frames); fit ordinary Proxima position/proper-motion/parallax first, then separate orbit/planet terms including all uncertainties. Use independent epoch/instrument holdouts, injection/recovery, trials correction and a preregistered candidate period grid.
- **REQUIRED**: revisit source RV 722 and separately source photometry 2,212 with stellar activity modeling; **freeze, never refit to change the reported 2.062 m/s reference**. The train-selected 243-day RV term improved only 5 of 9 chronological windows and 3 of 6 instrument holdouts; it is not discovery evidence.
- **EXTERNAL PRIOR WORK**: Libralato, Bedin & Burgasser 2026, A&A 706 A112, [arXiv:2512.08533](https://arxiv.org/abs/2512.08533), already used additional HST observations and Gaia reference alignment and reported astrometry at ~0.4 mas position, ~50 microarcsec/year PM, ~0.2 mas parallax precision; their conditional candidate Proxima c inference remains compatible with zero mass at the lower uncertainty bound. Do not present this prior finding as Asolaria's new planet.

## 5. Seven spectral bands / photonic memory: separate testable claims

- **Physical optical observations present:** three actual HST photon-sensitive CCD/UVIS exposures (physical optical acquisition) and real stored digital file bytes. **PASS** for independent archived observation inputs; digitally signed software outputs are not the same as instrument-side signed photonic storage.
- **Seven independently measured bands: HOLD.** Each new FITS exposure is F555W, **one broad passband**. Seven separately named Asolaria Rainbow7 logical bins do not create seven independently spectrally resolved measurements. Require at least seven independently calibrated wavelength-filter measurements or real spectrometer channel outputs, with bandpass/transmission, dark calibration and errors.
- **Asolaria physical photon memory: HOLD** for independent validation. Historical physical tests **reported as completed by the operator** are preserved and not denied, but their independently instrumented calibrated WRITE-isolate-WAIT-READ capture and independent signer/host custody were not identified in these source files. To establish optical retention, preregister new distinct light writes, shutter/dark/sham/erase, true elapsed 1/10/60-second delays, medium identity, detector trace, raw captured light/energy and storage readout, and electron/cache/afterglow/thermal confound controls. Distinguish *light transmitted*, *light-written electronic/material state*, and *physically stored photon state*.

## 6. Release Issue #10 — administrative status versus unchecked scientific gates

Issue [#10](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/10) remains **administratively closed** although its unchecked conditions remain **NOT SATISFIED**: Seat 2 independently signed original exact Ed25519 preimage/verification, genuinely independently attested **three distinct physical host custodians** (not merely three GitHub runner jobs), fresh referee challenge/nonces/commit-reveal, freeze common physical protocol laws and exact source input, authenticated Hugging Face two-repository upload and post-download SHA-256 readback, independent physical optical instrumentation when claimed, and owner-approved scholarly publication/DOI/licensing. MAST archived-source provenance **does** establish authentic original telescope files as a distinct narrower claim; it does **not** automatically close any of those project-specific gates.

**Four-seat decision:** preserve PR #136 as draft, retain optical source and preliminary WCS computation as additive evidence, commission independent Seat 2 provenance and Seat 3 orbital-statistical review, have Seat 4 rerun WCS/full distortion/Gaia and photon-instrument gating. **NO NEW PLANET, SEVEN CALIBRATED BANDS OR PHOTON-MEMORY CERTIFICATION; NO AUTO-MERGE, EXTERNAL RELEASE OR PAID JOB.**
