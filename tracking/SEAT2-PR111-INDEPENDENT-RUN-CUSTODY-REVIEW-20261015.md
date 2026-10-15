# Seat 2 — PR111 physical-compute to host-telemetry independent adversarial peer review

**2026-10-15 | Independent evidence verdict: `DIGITAL_AND_OS_RESOURCE_EVIDENCE_PASS_UNSIGNED_ORIGIN_LIMIT`.** Reviewer source [draft PR111](https://github.com/JesseBrown1980/asolaria-stone-to-moss/pull/111), reviewed source HEAD `8e597ae4c8d5d1ff76a2d25ad394ec49e601afc4`, actual final [5/5-success Actions run 38777263894](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38777263894). A separate source-review and post-run test plan was committed in PR114 **before the independent referee implementation**, `e12cb2a3caab3d9c8b3c80541fe5b7fa467aea29`. This is a *post-run independent review*, not falsely represented as original PR111 preregistration.

## Exact source and scientific claim (positive evidence)

**Yes, the run executed using real powered semiconductor hardware.** CPU instructions, electrical switching, process memory reads/writes and GitHub-hosted operating-system resource measurements occurred during the run. A container or virtual machine does not make their physical execution abstract or fictitious. The OS metrics remain *host-process observations*, not direct calibrated volts, amperes, joules or optical photons. Protective earth, device ground and DC circuit return are physically meaningful distinct concepts.

The **actual** new workload input was a pinned *701-byte signed-spectrum HBP fixture* at main commit `5d3e3a1147ad7af84c1b5b1ba482dfddd9832c86`, SHA256:

`077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400`

The HBP itself explicitly contains `physical_spectra=0`, `external_custody=HOLD`, and merely **references** earlier 184,815-byte Rainbow7 bank SHA256 `52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345`; **PR111 did not rerun this older complete bank**. The test repeated the frozen 701-byte HBP into a **2,097,152-byte** deterministic payload, then SHA256-hashed **256** source payload blocks with a 4-byte little-endian block index. That totals 512 MiB of payload input over the 256 blocks, but not 512 MiB unique original data.

Seat2 independently implemented the SHA256 stream from the actual 701-byte original source using Python stdlib **without importing** PR111's host process producer or separate Node reviewer. The resulting 256-block output matched all four immutable original artifact digital results:

`ae3474a94a03e024ad41bd6d0c508a18cbb3ed43c551da0ed3c6ec701e5b61cf`

The following original uploaded canonical source output SHA values were independently read and verified **identical across all four OS/Python artifacts**:
- `digital.json` **938 bytes** SHA256 `7b47c0270c5818c9d134fe81abcf767e2bacfb10ca72c4b1cae8afec0a17b73b`
- `instrument-status.json` **1,123 bytes** SHA256 `762bea2272ec6fabcc20e80c0ef540151e90db931ccb37413dff5d727f33591f`
- `node-review.json` **1,054 bytes** SHA256 `0d2260d3ce712b0bcbe61312d3f8dc1edf47cd3b33261bd909ebaf1cf1ae3023`
- Each artifact ZIP contains 4 distinct canonical JSON records plus 4 hash sidecars. All source files, sidecars, cross-platform parity, and ZIP entry identities checked.

## Original hosted CPU/RAM measurements from **the latest run**

GitHub Actions run 38777263894, artifact IDs `11993288612` (Ubuntu3.11), `11994157107` (Ubuntu3.13), `11993553464` (Windows3.11), `11994516799` (Windows3.13).

| Hosted job | CPU time reported | Monotonic elapsed | Observed resident-set increase | Original per-run SHA of `host-activity.json` |
| --- | ---: | ---: | ---: | --- |
| Ubuntu / Python3.11 | 390 ms | 385.854252 ms | 25,169,920 bytes | `4354440fed66abe28a4316a9e0cd5f9e145d76aa36a4f02b043cff2861ad6373` |
| Ubuntu / Python3.13 | 340 ms | 341.902826 ms | 25,169,920 bytes | `2a507e02cc21da0f4335a42580a73612583a24c40559b4bf59a070ccabb6ad47` |
| Windows / Python3.11 | 375 ms | 385.681100 ms | 25,186,304 bytes | `9845226702ee5b5fe542e22d09292530b235ce061224e29abc759d2a0a6a1e5a` |
| Windows / Python3.13 | 359.375 ms | 346.401200 ms | 25,178,112 bytes | `4979d93821e6b0bda59542c045301cbf9a9954b33412f417744269a393a3f281` |

These measurements differ from the earlier successful [38776972990](https://github.com/JesseBrown1980/asolaria-stone-to-moss/actions/runs/38776972990), as expected for genuine observations of separate executions. A review must not incorrectly pin a prior run's CPU/RAM SHA to a newer run.

Each raw hosted witness has `github_run_id=38777263894`, `producing_git_sha=5969b7de9ada80e8feaa18b497c1932c009d90db`, which is the **PR pull_request event's synthesized merge commit**. GitHub's authoritative run `head_sha` is separately `8e597ae4c8d5d1ff76a2d25ad394ec49e601afc4` (PR source HEAD). These are **different commits for valid reasons**. Seat2 pinned both in the independent audit rather than requiring them incorrectly to match.

## Four active adversarial digital falsifiers — new reviewer finding

The existing PR111 `validate_host()` checks that CPU time and RAM are positive, that a GitHub run field contains numeric characters, and that the producing Git field has 40 chars. Its independent Node reviewer likewise validates hash sidecars and basic formats, but **does not itself retrieve and bind each host reading to authoritative run identity and original externally anchored report hashes**. This is an independently reproducible source-level custody gap, not evidence that any original artifact was forged.

Seat2 constructed the following **offline modified** counter records with original valid controls and demonstrated that their values satisfy the *existing positive-value / field-format* acceptance predicates, while **each fails our independently pinned original artifact SHA** (even if attacker regenerates a local SHA sidecar):
1. Increase a legitimate, positive CPU duration by 10,000,000 ns.
2. Change valid `github_run_id` to another all-numeric value.
3. Change `producing_git_sha` to another 40-hex-like identifier.
4. Coherently change CPU duration + run ID + purported producing commit.

In this test, the original producer's **shape validation** accepts 4/4 variants; external pinned original artifact reference rejects 4/4. This source-level result **does not claim we executed the original Node reviewer against modified artifacts**, nor that Github itself reported compromised values. It also does not prove signed CPU sensor or uncontrollable host attestation. In particular, even a locally recomputed unsigned hash sidecar does not authenticate the origin of an altered host observation.

### Required hardening for PR111 promotion beyond digital CI evidence

Bind all `github_run_id`, producing PR source head/merge commit, artifact ID/name, OS/Python matrix identity and original host JSON digest through separately fetched and pinned GitHub Actions API metadata. Ideally carry a cryptographically signed attestation rooted outside the producing job if untrusted hosts/forged CI files are in the threat model. Keep source scientific integrity and host activity physically real while distinguishing platform-mediated provenance from an independent calibrated current/optical sensor measurement.

## August optical and neural evidence preserved accurately

The operator **reports** that a physical photon-memory measurement was completed; that is a meaningful historical reported experimental event and **must not be rewritten as "never happened"**. Independent original calibrated photon-memory capture instrument data **have not yet been established within this particular PR111 run**. The publicly linked [LIRIS SH Pre-Light Quantum Receipt](https://github.com/JesseBrown1980/LIRIS-SH-PRELIGHT-QUANTUM-RECEIPT) separately reports repeated local frozen-stage interventions with `LIGHT_ARRIVAL_GATE=0`, and explicitly leaves numeric event times, uncertainty, trial count and third-party replication **unsealed**. That LIRIS experiment is **not automatically the same experiment** as the operator-reported photon-storage/retention event.

**Scientific disposition:** `PHYSICAL_CPU_AND_DEVICE_BACKED_COMPUTE_CONFIRMED`; `DIGITAL_256_BLOCK_REPLAY_CONFIRMED`; `HOST_CPU_RSS_REPORTED_AND_PLAUSIBLE`; `GH_API_PROVENANCE_BETTER_THAN_SELF_HASH`; `INDEPENDENTLY_SIGNED_HOST_SENSOR_NOT_PROVEN`; `PHOTON_MEMORY_OPERATOR_REPORTED_COMPLETED`; `ORIGINAL_INSTRUMENT_RECORD_VERIFICATION_OPEN`.

Independent local Seat2 receipt `seat2_pr111_audit.json` **3,283 bytes** SHA256 `9206f6454daf653dff433b0d7aca27124bda49e2e7073c43077e8501cada0436`. Standalone local source reviewer `seat2_pr111_independent_audit.py` verifies all original four currently downloaded packages without importing PR111 code. This was a **local container source audit**, not another hosted GitHub Actions run; do not classify as hosted.

**Review recommendation:** PR111 remains **draft**; request a further platform-identity binding and external attestation path, without retracting the successful computer hardware and memory observations or merging unfinished Seat 1/2 branches automatically.
