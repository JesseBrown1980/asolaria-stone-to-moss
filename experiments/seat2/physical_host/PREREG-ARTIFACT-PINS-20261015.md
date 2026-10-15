# Seat 2 — immutable artifact pins before independent verifier

2026-10-15. Appended to [Seat2 prereg](PREREG-20261015.md) **before** new verifier code.

Original audited GitHub Actions run `38776274441` at Seat1 source commit `231863250cb1482fabffb53d9a04635e76fb45dd`.

| Kind | Ubuntu SHA256 | Windows SHA256 |
|---|---|---|
| `host-metrics/python-host.json` | `7861d79eb1e786ceb1e811b5d9b9666d787419825d9ef01756040a74bd570c9c` | `35febc753a8df4fabc13fb4b14f30c0c8cfc3fbf3c102723da5bd50b768ad20e` |
| `host-metrics/node-host.json` | `c48408738530acc2c013ac37d552198243c3c61fbaf46c49b97e6311e599d06d` | `29c37e378d72c5a6a81d255a399f64af5b5d423786180d11c5e0d738a3fdc40f` |
| `host-metrics/python-model.log` | `32ad04b0a158aab782a01239aafab095b21a1b84b36dc50cb12db642a3e39210` | `189b87dece211994ae49aea8341dc3da46d7116b45a80c3fbaf2cb76da5485c3` |
| `host-metrics/node-model.log` | `2a5d70fce15c879e32f0887a6afd397a1c3e5ab485bfe25e90c6f9d430bd7406` | SAME as Ubuntu |
| Model canonical HBP 18,217,055B | `42f3b61117a2e771f4f21958e12771b92b7a5d7251d023dc9ab78b34c65f6058` | SAME |
| Model canonical results JSON 7,339B | `4debac19eb1238bb8495018f115aa53494705934ff304129f2f4807920c99804` | SAME |
| Third auditor canonical 2,760B | `5d3cabce44810b08c8e898b0b64fd08eaaf5e160f79d8871af94a62508ac816e` | SAME |

Original parity receipt 1,387B SHA256 `05bc6b01e3906e8083f44047d821b55111356ccf0634c7bf6bd6302f768d57a4`. **This is a Seat1-authored parity statement**, not an independent signed physical sensor. These pins were read from GitHub-hosted artifact downloads and compute external-to-Seat2 review commitments; they are not self-authentication of hardware-chassis identity. Artifact IDs: Ubuntu `11994500478`, Windows `11993108836`, parity `11994345910`.

Published LIRIS provenance and historical correction are separately recorded in [CORRECTION-HISTORICAL-OPTICAL-EVIDENCE-20261015.md](CORRECTION-HISTORICAL-OPTICAL-EVIDENCE-20261015.md). Seat2 does not substitute the LIRIS local repeated frozen-stage shadow-key observation for a calibrated photon-memory retention trace; preserves completed operator report distinctly.
