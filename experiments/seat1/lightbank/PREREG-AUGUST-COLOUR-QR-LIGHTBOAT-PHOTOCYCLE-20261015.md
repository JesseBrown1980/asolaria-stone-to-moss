# Seat 1 — PREREGISTERED Phase C: August Light-Bank × Colour QR × Light-Boat × synthetic photocycle

Status: **PREREGISTERED BEFORE IMPLEMENTATION OR NEW CI OUTPUT**; Round 3 independent computational experiment, not an extension of frozen baseline. Parent work order #56, coordinator #55, room draft PR #60. No automatic merge or HF publication.

## Exact August public design roots (GitHub blob pins)
1. `JesseBrown1980/the-colour-qr` README blob `dec43dd370de557f2511e69227b1e234e001ddfc`, https://github.com/JesseBrown1980/the-colour-qr/blob/main/README.md . Colour QR: cut binary source into chunks **up to 2100 bytes**, prepend **little-endian uint32** chunk index; Base64 encode indexed chunk; ordinary black/white QR symbol in each R/G/B plane with chunk IDs 3k,3k+1,3k+2; unused planes are filler. Sort decoded chunks by index and compare original SHA256. **This benchmark implements the binary indexed + Base64 + RGB routing layer only**; no browser QR image generation, optical sensors, finder-pattern/ECC decoding, or mobile camera readback is simulated.
2. `JesseBrown1980/light-boat-engine-ships-with-oils` README blob `ba1c1a36ec1d4201297ccad325f848c6040dc95e`, https://github.com/JesseBrown1980/light-boat-engine-ships-with-oils/blob/main/README.md . Its **optical census** T/A/R is a one-hot partition `T+A+R=1`; a 27-block population with 9 each is a counting identity. Its buoyancy and no-arbitrage equations refer to **different systems** and are not automatically validated by this test. The browser's frame-driven animations are not measurements of optical power.
3. `JesseBrown1980/RAINBOR` August 8 HBP blob `f5e8a5004157229988f8a181e68773c0a2055955`, https://github.com/JesseBrown1980/RAINBOR/blob/master/RAINBOR-HUB-2026-08-08.hbp . It labels the three-wave optical hard-drive memory-stack hardware **CONJECTURE / DESIGN not measured**. `HBI/HBP/SHA` are digital provenance formats, not photonic retention readings.

**This phase is a digital surrogate, not a reproduction of the August physical light-memory stick**. Preserve all frozen Phase A HBP bytes `de2c346a92e626403cc5c59b9ffa688d050163fbb48ab8b1cb6a4cde795b0a8b`. Do not pool original Seat 1, Seat 3, Seat 4 or Phase B results.

## Frozen input space and encoding

- 27 ordered logical addresses: time `(-,0,+)` × colour `(R,G,B)` × space `(X,Y,Z)`, with wave index w=0..26, time=floor(w/9), colour=floor(w/3)%3, space=w%3.
- 81 immutable IDs `site-000` through `site-080`. **2187** independent source memory records.
- Binary memory length is **[436,2536,4636,6736][(w+site)%4]** bytes (tests 1,2,3,4 chunks, and filler). Generate bytes by concatenating `SHA256(ASCII "LIGHTBANK|AUGUST|V1|"+wave+"|"+site+"|"+counter)` until length reached. No hidden random state; seed has no security function.
- Segmentation 2100-byte maximum, packet bytes = LE32 index + payload; Base64 encode and associate packet with image group floor(index/3) and channel in R,G,B by index%3. Physical RGB is **labeling**, not optical encoding or a real QR scanner.
- Read by arbitrary order, Base64 decode, verify frame address, original LE32 index, uniqueness, contiguous indices, length, and SHA-256 of reassembled bytes. A SHA digest is **integrity**, not authenticity. Missing filled lane **must not silently count as filler**.
- Optional out-of-band per-group **XOR parity sidecar** (not a fourth visible QR channel), over the full indexed packet bytes zero-padded to maximum packet length, with stored length per lane. Requires unaltered sidecar; enables repair of **exactly one explicitly flagged absent lane** when other two are present. Plain colour QR **without** parity must reject even one lane erasure. Two erasures within one group must fail even with parity. A tampered lane with data present fails SHA check; coherent memory+manifest forgery cannot be authenticated by self-produced hashes.
- Each wave's T/A/R one-hot category is w%3 => T if 0, A if 1, R if 2: **9 each**, trit sum +1/0/-1 equals zero. This is an independent census control, NOT physical measured photon conservation or 3-state biological occupancy.

## Frozen photocycle and memory-recall coupling

Synthetic C/O/R fractions stored as integer units `S=1,000,000,000`, initial `(C,O,R)=(S,0,0)`, all identities constant. Model uses assumed rates in milli-per-second: `alpha(1000)=800`, `alpha(0)=0`, `beta=450`, `gamma=120`; dt=20 ms, 64 ticks.
For nonnegative milli-rate r, flux probability `p(r)=floor(S*r*20/(1_000_000+r*20))`; compute simultaneously `f_CO=floor(C*p(alpha)/S)`, `f_OR=floor(O*p(beta)/S)`, `f_RC=floor(R*p(gamma)/S)`; update C'=C−f_CO+f_RC, O'=O+f_CO−f_OR, R'=R+f_OR−f_RC. Mass and nonnegativity **at every tick**. Integer current proxy `I_milli_pA=−floor(120000*O/S)`, assumed g=2000 pS, V=-60mV, Erev=0; **not recorded membrane current**.

Commands drive `L=1000` at ticks 8..23 and 40..55 inclusive, otherwise dark; five fixed arms:
- `dark`: no commands
- `open_loop`: all scheduled ticks
- `feedback_now`: command only if latest model O < 100,000,000 when scheduled
- `feedback_delay5`: O from 5 ticks earlier (initial 0 if history not available)
- `feedback_stale25`: O from 25 ticks earlier (initial 0 if history unavailable), intentionally controlled delay not a falsely authenticated observer

The memory is stored independently as binary packets. A valid simulated read request is made after tick 63 **only if** O>=50,000,000; otherwise the memory exists but its optical-gate **proxy** reports HOLD. Dark arm must be HOLD; non-dark commands may pass or HOLD as observed without post-hoc tuning. A read that opens a digital gate is not proof a photon stored memory. Count gated successes by arm and record output SHA.

Sample frozen checkpoints (state after tick): `[0,7,8,23,24,39,40,55,56,63]`; output `27*81*5*10=109350` whole-state FRAME rows plus `27*81*5=10935` MEMORY rows, with deterministic ASCII `MODEL|...` and `END|...` envelope. Python and an independently coded Node BigInt path must be **byte exact**. Emit raw HBP, metadata JSON, SHA sidecars in Linux+Windows GitHub Actions. **No manual prompts per tick**, no external privileges or autonomous writes to remote services.

## B2 fault schedule, executed separately from baseline

At least one mutation test across each of all 27 wave addresses:
1. Plain RGB **single data-lane erasure** -> reject. With optional clean parity and declared lane index -> reconstruct original payload SHA byte-exact. No promise of recovery for >1 erasures.
2. **Two distinct erasures from same 3-lane group** -> reject even with parity.
3. One encoded-lane bit flip -> decode failure or SHA reject (not a falsely reported pass).
4. Swap an otherwise valid packet from a different source address -> external expected-source binding must reject.
5. Change one model occupancy by +1 -> conservation assertion fails.
6. Coherent forgery changing source bytes and updating self-generated SHA => classify **EXTERNAL_TRUST_HELD**, not "detected", until independent signing/witness.
7. Ensure invalid/filler lanes are not accidentally treated as valid chunks.

Record actual exercised flag, stage, expected/observed fail/recovery verdict. No physical or cryptographic proof from this suite.

## Evidence gates and peer handoff
- Pre-registration Git SHA saved before implementation. Stage sources independently; compare 109350+10935 exact rows, counters and HBP SHA under Ubuntu/Windows.
- Must not alter existing benchmark, claim independently controlled hosts, physical LEDs/fibres/photons, neurons, oscilloscope readings, hardware read endurance, biological fit, or optical QR imaging. Old actual August device may be connected **only with a separate device/driver/observation interface and calibrated measurements**.
- Request Seat 3 kinetics & mathematical review, Seat 2 source/QR provenance audit, Seat 4 independent runtime replay. Leave a draft PR pending peer review. Deliver actual receipts to #56 and #55.
