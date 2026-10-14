#!/usr/bin/env python3
"""Independent Seat-4 digital check of the published Seat-3 2-horizon bit counts.

Only synthetic GF(2) 81-site ring computation. DOES NOT recheck the complete
9720 records or imply a separate physical machine or issued shared challenge.
No network, credentials, or private key required.
"""
import hashlib
import json

N = 81
MASK = (1 << N) - 1
T = 10**13
TAPS = ((0,1),(0,2),(0,1,3),(0,4,7),(0,1,5,9))
EXPECTED = ((38,44),(38,44),(39,43),(53,47),(36,38))
DOMAIN = "ASOLARIA-SEAT4-2H-INDEPENDENT-DIGITAL-V1"

def circular_mul(left, right):
    out = 0
    while right:
        bit = right & -right
        shift = bit.bit_length()-1
        rotated = ((left << shift) | (left >> (N-shift))) & MASK if shift else left
        out ^= rotated
        right ^= bit
    return out

def fast_forward(rule, horizon):
    result = 1
    while horizon:
        if horizon & 1:
            result = circular_mul(result, rule)
        rule = circular_mul(rule, rule)
        horizon >>= 1
    return result

results = []
impulse_checks = 0
seeded_full_state_checks = 0
for law_index, taps in enumerate(TAPS):
    operator = sum(1 << shift for shift in taps)
    at_t = fast_forward(operator, T)
    at_t_plus_1 = fast_forward(operator, T+1)
    assert (at_t.bit_count(), at_t_plus_1.bit_count()) == EXPECTED[law_index]
    assert circular_mul(at_t,operator) == at_t_plus_1
    for site in range(N):
        start = 1 << site
        future = circular_mul(start,at_t)
        successor = circular_mul(start,at_t_plus_1)
        assert circular_mul(future,operator) == successor
        assert future.bit_count() == EXPECTED[law_index][0]
        assert successor.bit_count() == EXPECTED[law_index][1]
        impulse_checks += 1
    for wave in range(12):
        seed = hashlib.sha256(f"{DOMAIN}|{wave}|{law_index}".encode("ascii")).digest()
        state = int.from_bytes(seed,"little") & MASK
        assert circular_mul(circular_mul(state,at_t),operator) == circular_mul(state,at_t_plus_1)
        seeded_full_state_checks += 1
    results.append({"law_index":law_index,"taps":list(taps),"delta_bits_t":at_t.bit_count(),"delta_bits_tplus1":at_t_plus_1.bit_count(),"impulse_mask_t_hex":format(at_t,"021x"),"impulse_mask_tplus1_hex":format(at_t_plus_1,"021x")})
assert impulse_checks == 405
assert seeded_full_state_checks == 60
output = {
    "schema": "ASOLARIA-SEAT4-INDEPENDENT-SEAT3-TWO-HORIZON-AUDIT-V1",
    "date": "2026-10-14",
    "seat": "seat-4",
    "source_of_claim": "stones/2026-10-14-rainbow81/seat-3-two-horizon-9720-control.json",
    "source_repo": "JesseBrown1980/asolaria-stone-to-moss",
    "evidence_class": "self-contained synthetic GF(2) computation in one unverified host; not a fresh challenge",
    "modeled_horizons": [T,T+1],
    "ring_length": N,
    "law_checks": results,
    "one_step_impulse_recurrences_checked": impulse_checks,
    "seeded_full_state_metamorphic_controls": seeded_full_state_checks,
    "published_changed_bit_counts_reproduced": True,
    "published_full_9720_record_sha256_reproduced": False,
    "separate_physical_host_verified": False,
    "fresh_postcommit_challenge_issued": False,
    "no_secrets_published": True,
    "status": "PASS_LIMITED_DIGITAL_CROSSCHECK",
}
print(json.dumps(output,sort_keys=True,indent=2))
