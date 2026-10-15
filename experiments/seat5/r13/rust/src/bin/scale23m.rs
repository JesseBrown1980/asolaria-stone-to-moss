#![forbid(unsafe_code)]
//! 23 million *classical trit* position stress experiment per deterministic
//! seed profile. It is NOT a 23 million physical qubit experiment.
//! Operator-reported older Relic/Azure qubit results are distinct history.
use asolaria_seat5_r13::{chariot_walk, CENTER};
use std::{env, fs, path::PathBuf};

const POSITIONS: usize = 23_000_000;
const FRAME: usize = 27;
const FULL_FRAMES: usize = POSITIONS / FRAME;
const REMAINDER: usize = POSITIONS % FRAME;
const ROUTES: [u8; 8] = [1, 2, 3, 5, 7, 9, 11, 13];

fn splitmix64(index: u64, salt: u64) -> u64 {
    let mut value = index
        .wrapping_add(salt)
        .wrapping_add(0x9E37_79B9_7F4A_7C15);
    value = (value ^ (value >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    value = (value ^ (value >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    value ^ (value >> 31)
}

/// Deterministic, frozen signed trit generation. No physical quantum system
/// participates; deterministic pseudorandom state is not a quantum state.
fn source_trit(index: usize, salt: u64) -> i8 {
    (splitmix64(index as u64, salt) % 3) as i8 - 1
}

/// Byte-exact whole-data transform. A frame stores center once followed by
/// 26 *signed differences* in [-2,+2] (encoded to 0..4).
/// Importantly it DOES NOT falsely assume mirror symmetry or discard a trit.
fn encode(source: &[i8]) -> Vec<u8> {
    let mut packed = Vec::with_capacity(source.len());
    for chunk in source.chunks(FRAME) {
        if chunk.len() != FRAME {
            packed.extend(chunk.iter().map(|&t| (t + 1) as u8));
            continue;
        }
        let center = chunk[CENTER];
        packed.push((center + 1) as u8);
        for (i, &t) in chunk.iter().enumerate() {
            if i != CENTER {
                packed.push((t - center + 2) as u8);
            }
        }
    }
    assert_eq!(packed.len(), source.len());
    packed
}

fn decode(bytes: &[u8]) -> Option<Vec<i8>> {
    let mut decoded = Vec::with_capacity(bytes.len());
    for chunk in bytes.chunks(FRAME) {
        if chunk.len() != FRAME {
            for &v in chunk {
                if v > 2 { return None; }
                decoded.push(v as i8 - 1);
            }
            continue;
        }
        let center_byte = chunk[0];
        if center_byte > 2 { return None; }
        let center = center_byte as i8 - 1;
        let mut positions = [0i8; FRAME];
        positions[CENTER] = center;
        let mut field = 1;
        for (i, t) in positions.iter_mut().enumerate() {
            if i == CENTER { continue; }
            let b = chunk[field];
            if b > 4 { return None; }
            let restored = center + b as i8 - 2;
            if !(-1..=1).contains(&restored) { return None; }
            *t = restored;
            field += 1;
        }
        decoded.extend_from_slice(&positions);
    }
    Some(decoded)
}

fn audit_chariots(source: &[i8], restored: &[i8]) -> (usize, usize, [u64; 3]) {
    let positive = chariot_walk(true);
    let negative = chariot_walk(false);
    let mut center_count = [0u64; 3];
    let mut outbound_checks = 0usize;
    let mut inbound_checks = 0usize;
    for (a, b) in source.chunks(FRAME).zip(restored.chunks(FRAME)) {
        if a.len() != FRAME {
            for (&original, &readback) in a.iter().zip(b) {
                assert_eq!(original, readback);
                outbound_checks += 1;
                inbound_checks += 1;
            }
            continue;
        }
        let center = a[CENTER];
        center_count[(center + 1) as usize] += 1;
        for &i in &positive {
            assert_eq!(a[i], b[i]);
            outbound_checks += 1;
        }
        for &i in &negative {
            assert_eq!(a[i], b[i]);
            inbound_checks += 1;
        }
    }
    (outbound_checks, inbound_checks, center_count)
}

fn main() {
    let profile = env::args().nth(1).expect("usage: scale23m relic-seed|azure-seed outdir");
    let out = PathBuf::from(env::args().nth(2).expect("output directory"));
    let salt: u64 = match profile.as_str() {
        "relic-seed" => 0x7E11_C0DE_1111_1111,
        "azure-seed" => 0xA2E1_C0DE_2222_2222,
        _ => panic!("unknown profile; only relic-seed or azure-seed"),
    };
    fs::create_dir_all(&out).expect("mkdir");
    assert_eq!(FULL_FRAMES, 851_851);
    assert_eq!(REMAINDER, 23);
    let original: Vec<i8> = (0..POSITIONS).map(|i| source_trit(i, salt)).collect();
    assert!(original.iter().all(|&t| (-1..=1).contains(&t)));
    let packed = encode(&original);
    let decoded = decode(&packed).expect("decoder rejected valid encoded source");
    assert_eq!(decoded, original, "unmodified generated source must roundtrip");
    let (positive, negative, center_count) = audit_chariots(&original, &decoded);
    assert_eq!(positive, POSITIONS);
    assert_eq!(negative, POSITIONS);
    assert_eq!(center_count.iter().sum::<u64>(), FULL_FRAMES as u64);

    // Adversarial checks operate on actual 23M-sized copies and must reject.
    let mut tampered = packed.clone();
    let mut wrong = 0usize;
    for j in 0..tampered.len() {
        if j % FRAME != 0 && tampered[j] < 4 {
            wrong = j;
            break;
        }
    }
    tampered[wrong] += 1;
    let tampered_recovered = decode(&tampered);
    assert!(tampered_recovered.as_ref() != Some(&original));
    tampered[wrong] = 7;
    assert!(decode(&tampered).is_none());

    // Exact path witness: frame index + within-frame coordinate recovers
    // position, even across the partial last frame. Prime residual alone
    // cannot identify arbitrary original indices (2 and 29 collide modulo 27).
    let mut route_counts = [0usize; 8];
    for i in 0..POSITIONS {
        let frame = i / FRAME;
        let trit_path = i % FRAME;
        assert_eq!(frame * FRAME + trit_path, i);
        route_counts[i % ROUTES.len()] += 1;
    }
    assert!(route_counts.iter().all(|&n| n == POSITIONS / ROUTES.len()));
    assert_eq!(2usize % 27, 29usize % 27);

    fs::write(out.join("original-trits.bin"), original.iter().map(|&t| (t + 1) as u8).collect::<Vec<_>>())
        .expect("original raw");
    fs::write(out.join("center-relative.bin"), &packed).expect("packed raw");
    fs::write(out.join("restored-trits.bin"), decoded.iter().map(|&t| (t + 1) as u8).collect::<Vec<_>>())
        .expect("restored raw");

    let receipt = format!(
        "HBP1|seat=5|experiment=R13-SCALE23M|class=REAL_HOST_CLASSICAL_TRIT_RECONSTRUCTION|physical_qubits_tested=0\n\
         PROFILE|name={profile}|label_is_not_physical_host=true|salt={salt:016x}\n\
         COUNT|positions={POSITIONS}|frame=27|frames={FULL_FRAMES}|partial={REMAINDER}|source_bytes={POSITIONS}|encoded_bytes={POSITIONS}|restored_bytes={POSITIONS}\n\
         TRITS|alphabet=-1,0,+1|center_address=13|center_negative={}|center_zero={}|center_positive={}\n\
         ROUTE|ids=1,2,3,5,7,9,11,13|each_count={}|prime_2_and_29_residue27_collision=CONFIRMED|full_position_identity=UNIQUE\n\
         CHARIOT|outward_checked={positive}|inward_checked={negative}|readback=EXACT\n\
         FALSIFIER|tampered_valid_difference=DETECTED|out_of_range_encoded_difference=REJECTED\n\
         SCIENCE|original_relic_azure_23m_qubit_report=OPERATOR_REPORTED|current_result=NOT_A_QUANTUM_CLONING_EXPERIMENT|optical_detector=NOT_CONNECTED\n",
        center_count[0], center_count[1], center_count[2], POSITIONS / ROUTES.len()
    );
    fs::write(out.join("scale23m.hbp"), receipt.as_bytes()).expect("receipt");
    print!("{receipt}");
}
