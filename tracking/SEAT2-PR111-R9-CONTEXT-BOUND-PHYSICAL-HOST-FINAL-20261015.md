# Seat 2 — PR #111 correction, physical-host evidence and unsigned counter custody

**October 15, 2026. Owner/author seat: Seat 2.** This is an **author remediation report and independent source-file spot-check**, not an independent cross-seat approval. Final approval belongs to external Seats 1/3/4/5 coordinated by [Issue #117](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/117). No merges, branch deletions, forced rebases or changes to original hardware/optical historical records.

## Frozen scientific source and completed experiment

- PR: [#111](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/111); **revised source head** `43f2dbbefd406c6f74262bff79cc3862ca0d487b`.
- Corrected 5/5 GitHub Actions run: [38782415687](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38782415687) (Linux Python3.11/3.13, Windows Python3.11/3.13, fifth artifact referee: all SUCCESS). Actual `pull_request` synthetic producing merge commit `3aa2ba5deb49095276badb4f0cf650217f54bbe0`; distinguish from source head.
- Prior successful original [run 38777263894](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38777263894) at head `8e597ae4c8d5d1ff76a2d25ad394ec49e601afc4` is preserved. Its resource values differ from this new run naturally.
- Actual input: **701-byte** original Seat4 source HBP from frozen main `5d3e3a1147ad7af84c1b5b1ba482dfddd9832c86` SHA256 `077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400`. HBP references **earlier** bank SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345` but this benchmark does **not** replay all 184,815 older bank source bytes.
- Each new hosted job generated original-source-derived 2 MiB payload, 256 SHA256 indexed passes and actual page-touched 24 MiB memory. The identical new/source-original deterministic digest across hosts is `ae3474a94a03e024ad41bd6d0c508a18cbb3ed43c551da0ed3c6ec701e5b61cf`. Not 512 MiB unique original information, not physical optical readback.

## Four real operating-system measurements (new run only)

All numbers are **direct OS-reported physical process CPU/RSS observations** on hosted powered machines (not synthetic simulation of CPU or resident RAM). GitHub-hosted jobs may share underlying virtualized hardware; unique physical chassis custody not established.

| Actual hosted job | CPU time ns | Monotonic elapsed ns | RSS increase bytes | SHA256 of original per-host raw `host-activity.json` |
|---|---:|---:|---:|---|
| Ubuntu Python3.11 | 340,000,000 | 342,010,773 | 25,169,920 | `843c4d3649a71ee9171862b9b82708e3ee7d095e536d08f631776a366f8ebbf9` |
| Ubuntu Python3.13 | 300,000,000 | 299,818,346 | 25,169,920 | `2bc9836aa3c6704979b0d9b4685c3c7d54762ae01233dd074bec9493d4598331` |
| Windows Python3.11 | 343,750,000 | 345,345,300 | 25,186,304 | `74cb9f70c376f343f368e616cbb8f2eaf109f2b2eee47c977a4bdd455127bd6e` |
| Windows Python3.13 | 343,750,000 | 345,829,000 | 25,178,112 | `92961f1b791c2fe07dac36d78b33edf67bbd8aaa7299cf93d6c3fdba45cc0279` |

All four raw original uploaded artifact ZIP archives were independently downloaded and checked in the local review environment. GitHub Actions artifact IDs: Ubuntu3.11 `11995972679`, Ubuntu3.13 `11996836172`, Windows3.11 `11996052587`, Windows3.13 `11995159261`. Every ZIP archive contained 10 actual files: four original canonical JSON results with SHA sidecars plus independent `attack-review.json` and its sidecar. The following **full evidence files were byte-identical across four hosts**:
- `digital.json` 938 bytes SHA256 `7b47c0270c5818c9d134fe81abcf767e2bacfb10ca72c4b1cae8afec0a17b73b`.
- `node-review.json` 1054 bytes SHA256 `0d2260d3ce712b0bcbe61312d3f8dc1edf47cd3b33261bd909ebaf1cf1ae3023`.
- `instrument-status.json` 1123 bytes SHA256 `762bea2272ec6fabcc20e80c0ef540151e90db931ccb37413dff5d727f33591f`.
- **NEW** `attack-review.json` 2005 bytes SHA256 `3bbd406aae04d1157c9e6a0e2a24fe1531ea11c5c68d85bc251c9efc5a67924d`.
- Each original per-host host-activity JSON was correctly SHA-hashed **individually**, not incorrectly expected to match other OS resource measures.

## Append-only correction chronology, including failed attempt

1. Original PR111 source and 5/5 hosted run at `8e597ae4c8d5d1ff76a2d25ad394ec49e601afc4` and Actions 38777263894 remain unchanged.
2. **Before** modifications, Seat2 committed [context-binding preregistration](https://github.com/JesseBrown1980/asolaria-stone-to-moss/blob/agent/seat-2/round9-host-activity-evidence-bridge-20261015/experiments/seat2/round9/CORRECTION-CI-CONTEXT-AND-COUNTER-FORGERY-20261015.md) commit `2f814204e47cf8d4736839bda78f0b207574d5b1`.
3. Producer host record validation now strictly binds to `GITHUB_RUN_ID`, `GITHUB_SHA` (pull request synthetic merge SHA), `RUNNER_OS`, `GITHUB_JOB`, actual OS platform; independent Node replay tests the same external job context. Cross-host fifth job binds reported data against current run/merge identity and exact artifact OS+Python3.11/3.13 matrix.
4. Added **actual seven malicious file-copy attempts** to the original Node reviewer; each deliberately reserializes an altered field and recomputes a matching SHA256 sidecar. Not just seven asserted conditions.
5. [First hostile CI run 38782110065](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38782110065) **FAILED** with `('FORGED_UNSIGNED_HOST_REPORT_ACCEPTED','counter_cpu_positive')`. This is a valuable negative observation: with reporter and unsigned sidecar controlled, a plausible positive CPU counter remains accepted by pure source/context/format verification. The historical failed workflow and its traceback are preserved.
6. **Before** changing test acceptance, added [second append-only correction](https://github.com/JesseBrown1980/asolaria-stone-to-moss/blob/agent/seat-2/round9-host-activity-evidence-bridge-20261015/experiments/seat2/round9/CORRECTION-UNSIGNED-CPU-TAMPER-20261015.md) commit `6c9f955817a255c3ec5f016446ab36d3d05180d1`; explicit new falsifiers correctly classify the unavoidable **unsigned positive CPU counter gap** rather than silently claiming secure counter attestation.
7. Final corrected source head `43f2dbbefd406c6f74262bff79cc3862ca0d487b` and CI 38782415687 **5/5 PASS**, all four original artifacts independently downloaded.

## Exactly seven independently exercised malicious file-input outcomes

- `run_id_numeric_wrong` → **Node REJECT** when run value is numeric but not the current GitHub run.
- `producer_sha_valid_40_wrong` → **REJECT** 40-character alternate producing SHA.
- `runner_os_and_platform_consistent_but_wrong` → **REJECT** internally consistent but wrong Linux/Windows host OS.
- `github_job_valid_looking_wrong` → **REJECT** valid-looking wrong CI job identity.
- `fake_device_current_with_forged_sidecar` → **REJECT** uninstrumented current falsely marked measured.
- `combined_counter_and_run_and_sha` → **REJECT** mixed counter and job identity substitution.
- `counter_cpu_positive` → **EXPECTED ACCEPTED** plausible, unsigned CPU-value substitution with recomputed local SHA; `UNSIGNED_CPU_COUNTER_PROVENANCE_NOT_ATTESTED`.

Thus **six actually rejected, one actually accepted and preserved as an explicit trust-boundary limitation**. Existing original nine negative controls remain intact. Do not report 7/7 forged reports rejected, and do not interpret this acceptance as evidence the real platform-measured CPU values were forged.

## Physical evidence / reported historical experiments

Host execution and memory allocations are physically real. AC→regulated DC power is the physical enabling substrate; local OS runtime counters are legitimate observations of physical resource use. This workflow **does not attach an external calibrated voltmeter, ammeter, ground-potential logger, spectrometer, photon detector, acoustic displacement sensor, or physical optical memory shutter/readout trace**. Their missing measurement in this particular October workflow does not show optical mechanisms are absent elsewhere.

The **operator reports completed physical photon-memory measurements** in the historical August Asolaria experiments; retain as operator-reported completed history. The separate public [LIRIS SH Pre-Light Quantum Receipt](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT) reports repeated local frozen-stage observations; numeric event timing, uncertainty, trial count and external laboratory validation remain `UNSEALED/PENDING` *in that publication*. Neither October host dataset substitutes for those original historical experiments.

## Cleanup board / disposition

- Coordinate [Issue #117](https://github.com/JesseBrown1980/asolaria-stone-to-moss/issues/117); this is **Seat2 author remediation, not an independent Seat2 approval of self**.
- Reviewer condition: `SEAT2_CORRECTED_DIGITAL_AND_PHYSICAL_HOST_PROCESS_EVIDENCE=PASS`. Counter sensor custody and hardware instrumentation `HELD`. PR111 stays **DRAFT**, no merge, no branch deletion. Seat1/3/4/5 independently cross-review, compare PR110/112/113 overlap, and decide eventual merge.
