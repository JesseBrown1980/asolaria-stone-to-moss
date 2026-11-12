# Asolaria Seat 1 — Real Proxima observations, nine-window cross-seat falsification

**Observation intake and independent computation: 2026-10-16.**  
**Verdict: REAL MEASUREMENT INPUTS VERIFIED; COMPUTATIONAL CROSS-VALIDATION PASS; NEW PLANET NOT DETECTED.**  
**Exact-head verification:** [GitHub Actions #38898409458](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38898409458) and [independent PR #38898417796](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38898417796), both PASS at commit `a40db886cad318248594fdb80c433b744ed38109`. Rust 1.81 strict offline Clippy and tests + independent integer referee + actual hosted CPU run. No auto-merge.

## 1. Original, independently published source bytes

**Scientific source:** [Suárez Mascareño et al., *Astronomy & Astrophysics* 700 A11 (2025)](https://www.aanda.org/articles/aa/pdf/2025/08/aa53728-25.pdf), [CDS catalog J/A+A/700/A11 ReadMe](https://cdsarc.cds.unistra.fr/viz-bin/ReadMe/J/A%2BA/700/A11?format=html&tex=true).

- `spec.dat` — 722 **real** timestamped radial-velocity/spectroscopic observations, six instrument identities (UVES, HARPS before/after, ESPRESSO before/after, NIRPS), plus per-record RV uncertainties and optional FWHM/CRX indicators. **87,362 original bytes**, SHA-256 **`027cff5c10b541608b727abada2af531037223edec3bb9112fcbb45fc333e474`**. Times reported as BJD−2450000 at 0.001-day precision.
- `photo.dat` — 2,212 real photometry measurements from ASAS-3/4, ASAS-SN and LCO. **97,328 original bytes**, SHA-256 **`d42dad64fcbf80159bfc1edf20c35db82d01ce2aa7830248d7198aad05bc6dd5`**. **Acquired and source-audited, NOT included in the current regression fit.**
- [NASA/HST published Proxima image](https://science.nasa.gov/asset/hubble/hubble-image-of-proxima-centauri/) — WFC3/UVIS **F555W**, **2012-10-01**, exposure 175 s. The dynamically served asset is a **763×587 JPEG**, 54,805 B, source SHA-256 **`481540dc6ddc65ddf0cf8d8bb495bf08d79552e505fba29916d41ed9f35da2a3`**. It is **not** calibrated original HST/FITS pixel data, not an observation of the surface of Proxima b/d, and not a nine-epoch image series.

Original source files, downloaded camera image, derived results, source manifests and independent review outputs are retained as an artifact of the exact GitHub Actions run. A source checksum proves integrity against that original; its ownership/collection is grounded in original institutional archive records, not in an owner-created signature.

## 2. Actual 2D camera-frame ternary result

The decoded Hubble publication JPEG is **447,881 RGB pixels** = **1,343,643 individual channel bytes**. Each 8-bit decoded RGB channel sample was converted **exactly** to six balanced trits `-1,0,+1`, totaling **8,061,858 trits**; all samples were recovered **byte-identically** by a second decoding pass.

Decoded RGB bytes SHA-256: **`f3ba34149a5c6f570af95b72211fd98c6952fcd8d10a161fab27d69b89ff472c`**. Hosted Python integer loop + pinned Pillow JPEG decoder: PASS. This is a real observation *rendering* input, and an exact code-domain round-trip; no invented astronomical detail, additional telescope wavelength, second image epoch, or new planet is established.

## 3. Nine held-out checkpoints in **actual measured RV time**

**Predeclared source division:** first 70% of chronological RV samples **within each instrument** (504 train); later 30% (218 held-out). Every measurement carries its published formal RV uncertainty, used as an inverse-variance weight. The 218 held-out measurements were divided into **nine chronological blocks** (24 or 25 observations each). These **real observation dates are not 81×3^k years**. The ternary law is used only to compute per-epoch phase bins efficiently, not to assert real time-skipped gravitational evolution.

The new Rust1.81 analysis uses **integer arithmetic only**, 27-point phase templates, an instrument-offset baseline, optional FWHM/CRX activity indicators, a deliberately simple 83-day rotation proxy, the published b and d periods, and a train-only *exploratory* selection over six candidate periods (9, 27, 81, 243, 729, 1900 days). This is **not** a calibrated multi-instrument Gaussian-process stellar-activity / full Keplerian model, nor a discovery-grade periodogram. Formal uncertainties are used as individual measurement weights; uncertainties in activity models and orbital periods are not fully propagated.

| Model on all 218 held-out measurements | Weighted RMS residual | Change from simpler comparator |
| --- | ---: | ---: |
| Instrument and approximate stellar activity only | **2.508 m/s** | baseline |
| Plus known Proxima b and d | **2.297 m/s** | 0.211 m/s lower (**8.4%**) |
| Plus train-selected exploratory **243-day** term | **2.062 m/s** | 0.235 m/s lower (**10.2%** from b+d) |

**Nine actual chronological held-out windows** (all errors m/s):

| Window | Obs. | Baseline | b+d | Plus 243d | Added period improves? |
|---:|---:|---:|---:|---:|---|
|1|24|2.887|2.575|2.462|Yes|
|2|24|6.375|5.906|5.138|Yes|
|3|24|1.730|1.563|1.138|Yes|
|4|24|1.483|1.381|1.826|No|
|5|25|3.943|3.776|3.757|Yes|
|6|24|2.572|2.384|2.573|No|
|7|24|2.377|2.102|1.861|Yes|
|8|24|2.337|1.940|2.191|No|
|9|25|1.941|1.628|1.646|No|

The global weighted RMS is not a simple average of these nine block metrics; weights and source instrument distributions differ. **The additional period improves only 5/9 blocks, worsening 4/9**. A separate independent exact integer sign-flip diagnostic using their nine squared-error differences gives **149/512 (0.291)** one-sided assignments at least as extreme. This number is a **descriptive post-selection diagnostic**, **NOT** a corrected astronomical false-alarm probability: trial selection, instrumental systematics and non-independent windows are not controlled.

### Instrument-independent challenge

| Published RV instrument ID | Held-out n | Known b+d RMS | Added 243d RMS | Improvement? |
|---:|---:|---:|---:|---|
|0, UVES|24|2.575|2.462|Yes|
|1, HARPS pre-upgrade|28|5.727|4.953|Yes|
|2, HARPS post-upgrade|90|3.387|3.454|No|
|3, ESPRESSO pre-upgrade|13|0.909|0.924|No|
|4, ESPRESSO post-upgrade|18|1.692|1.502|Yes|
|5, NIRPS|45|1.550|1.555|No|

**The exploratory signal is not consistently beneficial across instruments** (3/6 improved). In particular, it does not improve the **post-upgrade HARPS** or **NIRPS** holdout sets. A 243-day residual in this crude model can be caused by stellar activity, seasonal sampling aliases, imperfect noise/offset modeling or unaccounted planets; no cause has been established. It is **not evidence of Brown–Edens I**.

## 4. Freeze/play and nine-jump comparison interpretation

- **Real camera:** one genuine Hubble released frame converted to balanced trits without losing *decoded JPEG pixels*; no fake multi-epoch image track.
- **Real timed instruments:** 722 original RV and 2212 photometry records source-hashed. Nine time windows of RV observations examined with real uncertainty weights.
- **Matrix jump:** constant-period modular phase is evaluated exactly at each historical measurement time; skipping intermediate arithmetic is valid for this declared toy phase law. It does **not** solve or certify arbitrary time-evolving, interacting particle orbits.
- **Individual memory:** each source sample/time can map to a separate particle-memory event. Here the observational record remains intact; earlier synthetic 81×27 particle histories stay a distinct experiment.
- **Three leaves:** source provenance PASS; known b+d out-of-sample fit improvement PASS; extra-planet independent identification/replication FAIL. This branch of the **new-planet claim is HELD**, regardless of software pass rate.

## 5. Required next falsification before any new-world report

1. Incorporate the **2,212 photometric** measurements directly, with stellar-activity uncertainties and instrument-specific offsets/jitter; compare multiple activity kernels against fixed 83-day template.
2. Fit true Keplerian b and d signals with literature uncertainties; allow eccentricity and stellar rotation to vary, with careful seasonal cadence/aliases.
3. Freeze candidate period grid *before* a new dataset; run independent source/instrument holdouts or blinded injection–recovery and multiple-trial-corrected false alarms.
4. Acquire **at least nine calibrated, dated, source-authenticated image epochs** if claiming physical motion from pictures. This test contains one dated NASA publication image only.
5. Authenticate original sensor/electrical/photonic source when claimed; never mistake signed software outputs for astrophysical hardware readings.

**Decision: no newly discovered planet, no independent mass for Brown–Edens I, and no evidence of actual galactic 10-billion-year evolution from these source files.** Brown–Edens I remains a provisional internal research name. Preserve the negative controls and old receipts. **Do not merge, issue a press release, trigger paid physical imaging, or elevate the claim without operator review.**
