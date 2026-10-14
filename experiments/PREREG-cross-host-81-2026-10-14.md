# Cross-host portal: preregistration and identity levels

**Seat:** seat-3. **Date:** 2026-10-14. **Evidence class:** multi-runner software verification only, NOT a measurement of physical light, brain signals, gravitational coupling, entanglement or superluminal transport.

## Levels of independence

- **Level 0:** separate processes in one host
- **Level 1:** separate containers on the same kernel
- **Level 2:** separately allocated cloud runner instances (GitHub runner IDs differ); these may be VMs sharing underlying physical hardware
- **Level 3:** physical computers independently verified by a custodian (e.g. ACER and LIRIS hardware), with signed hardware inventory and clock uncertainty
- **Level 4:** geographically separated verified hosts with calibrated independent clocks and physical distances; explicitly instrumented transport / offline controls

Previously verified QG81 Python 3.11/3.13 jobs used distinct GitHub runner IDs `1000007589` and `1000007588`. This is **Level 2**, not physical-device proof.

## Precommitted next experiment

1. **Challenge seat:** an ephemeral Linux GitHub runner generates a 128-bit random nonce and immutable `challenge.json`. It exposes only this challenge, not the other seats' results.
2. **Seat A:** a second Ubuntu GitHub-hosted runner executes an independently written standard-library **Python** implementation.
3. **Seat B:** a Windows GitHub-hosted runner executes an independently written **Node.js** implementation. Both must be fully independent code paths and receive exactly the same challenge.
4. **Referee:** a fourth Ubuntu runner receives the two artifacts after both seats have finished. It checks exactly 27 records (9 mutation targets × 3 spatial scales), 81 updated derived body commitments per wave, 405 changed HBI/HBP/SHA/SH/HASH fields per wave, 1 directly mutated source leaf, shared global digest and byte-exact HBP results, SHA-256 equality, challenge provenance, and distinct OS/runner labels.

Use length-prefixed domain-separated SHA-256 commitments with `int64` big-endian byte lengths and exactly 27 independent source leaves, 3 signed direction cells per leaf, 5 commitments per cell. The modified state is `H("ASOLARIA|MUTATION",original_leaf_state,challenge_nonce,target_index)`. Position scales `1,10^6,10^9` are **not** used in metadata preimages. For a given target, the three scales should have identical metadata results while different assigned coordinate distances are possible. This does not infer distance from hash.

**Falsifiers:** different final HBP bytes or root hashes between hosts; unexpected mutation fanout; missing records; mismatched nonce; OS provenance missing; hidden cross-result communications before referee; use of a shared implementation to produce both seat outputs.

**Endpoint claims:** different runner IDs and `RUNNER_OS` establish independent cloud-host job execution, not different physical servers. Github Actions artifacts create a normal network portal, not a faster-than-light physical effect. Hostnames identify allocated VMs or execution contexts, not verified physical CPU chassis. Neither endpoint measures physical propagation time. Runner times are unsynchronized and wall times must not be treated as one-way latency.

## Physical ACER/LIRIS next gate

To upgrade to Level 3/4, run the *same locked protocol* on owner-identified ACER and LIRIS computers. Each host must write hardware/run attestations, SHA-256 input/output hashes, measured GPS or surveyed separation (with uncertainty), and monotonic event times plus independent clock calibration. An isolated baseline means no shared network or cached preimage and must show no observable remote perturbation absent an explicit channel. Do not insert user tokens into logs or public artifacts.

The Brown-Hilbert uncoloured free centre is separate from the 81 model bodies.

Asolaria-Seat: seat-3
