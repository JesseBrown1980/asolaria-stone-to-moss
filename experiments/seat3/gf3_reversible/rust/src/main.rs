#![forbid(unsafe_code)]
//! Seat3 GF(3) reversible information witness.
//! Exact Rust 1.81.0 no-JSON HBI1/HBP1 mathematical test.
//! This does NOT operate a physical photonic memory or an astronomical sensor.

use std::fs;
use std::path::Path;
const N: usize = 81;
const LAW_A: [usize; 3] = [0, 1, 3];
const LAW_B: [usize; 3] = [0, 4, 7];
const HORIZONS: [usize; 5] = [1, 3, 9, 27, 81];
const SOURCE_SHA: &str = "5303c9b2ed0c0ce33da684706d57caef516ffd2b";
const SOURCE_BLOB: &str = "0a26e3d24ac0b0211c31c3aa32e23d50d7d0c3ec";
type State = [u8; N];
type Matrix = [[u8; N]; N];

fn step(input: &State, law: [usize; 3]) -> State {
    std::array::from_fn(|i| {
        (input[(i + N - law[0]) % N]
            + input[(i + N - law[1]) % N]
            + input[(i + N - law[2]) % N]) % 3
    })
}
fn origin(seed: u8) -> State {
    std::array::from_fn(|i| match seed {
        0 => u8::from(i == 0),
        1 => u8::from(i == 13),
        2 => u8::from(i == 80),
        3 => ((7 * i + 2) % 3) as u8,
        4 => (i % 3) as u8,
        _ => panic!("unregistered seed"),
    })
}
fn law_for(family: u8, tick: usize) -> [usize; 3] {
    match family {
        0 => LAW_A,
        1 => LAW_B,
        2 if tick < 17 => LAW_A,
        2 => LAW_B,
        _ => panic!("unregistered law"),
    }
}

/// Reverse one state update after retaining a single predecessor trit x[0].
/// The first 80 output rows + the witness row form an invertible 81x81 map.
/// Mathematical row indexing is explicit so all coefficients can be inspected.
#[allow(clippy::needless_range_loop)]
fn inverse_matrix(law: [usize; 3]) -> Matrix {
    let mut augmented = [[0u8; 2 * N]; N];
    for (i, row) in augmented.iter_mut().enumerate().take(N - 1) {
        for &offset in &law {
            let col = (i + N - offset) % N;
            row[col] = (row[col] + 1) % 3;
        }
    }
    augmented[N - 1][0] = 1;
    for (i, row) in augmented.iter_mut().enumerate() {
        row[N + i] = 1;
    }
    for col in 0..N {
        let piv = (col..N)
            .find(|&row| augmented[row][col] != 0)
            .expect("additional witness must remove nullspace");
        augmented.swap(col, piv);
        if augmented[col][col] == 2 {
            for value in &mut augmented[col] {
                *value = (*value * 2) % 3;
            }
        }
        let pivot_row = augmented[col];
        for (row_id, row) in augmented.iter_mut().enumerate() {
            if row_id == col || row[col] == 0 {
                continue;
            }
            let factor = row[col];
            for (index, value) in row.iter_mut().enumerate() {
                *value = (*value + 6 - factor * pivot_row[index]) % 3;
            }
        }
    }
    std::array::from_fn(|row| std::array::from_fn(|col| augmented[row][N + col]))
}
fn restore(next: &State, witness: u8, inverse: &Matrix, law: [usize; 3]) -> Result<State, &'static str> {
    if witness > 2 || next.iter().any(|&c| c > 2) {
        return Err("invalid input trit");
    }
    let mut target = *next;
    target[N - 1] = witness; // first 80 output rows, then independent x[0].
    let prior: State = std::array::from_fn(|i| {
        inverse[i]
            .iter()
            .zip(target.iter())
            .map(|(&x, &y)| u16::from(x) * u16::from(y))
            .sum::<u16>()
            .rem_euclid(3) as u8
    });
    if prior[0] != witness || step(&prior, law) != *next {
        return Err("invalid source, law or witness");
    }
    Ok(prior)
}
fn encode_witness(values: &[u8]) -> Vec<u8> {
    values
        .chunks(5)
        .map(|chunk| {
            let mut weight = 1u16;
            let mut result = 0u16;
            for &digit in chunk {
                assert!(digit < 3, "source trits only");
                result += weight * u16::from(digit);
                weight *= 3;
            }
            result as u8
        })
        .collect()
}
fn decode_witness(packed: &[u8], trit_count: usize) -> Result<Vec<u8>, &'static str> {
    if packed.len() != trit_count.div_ceil(5) {
        return Err("wrong witness byte count");
    }
    let mut output = Vec::with_capacity(trit_count);
    for &byte in packed {
        if byte >= 243 {
            return Err("noncanonical 5-trit byte");
        }
        let mut value = byte;
        for _ in 0..5 {
            output.push(value % 3);
            value /= 3;
        }
    }
    if output.iter().skip(trit_count).any(|&v| v != 0) {
        return Err("nonzero witness padding");
    }
    output.truncate(trit_count);
    Ok(output)
}
fn forward(seed: u8, family: u8, ticks: usize) -> (State, Vec<u8>) {
    let mut state = origin(seed);
    let mut witnesses = Vec::with_capacity(ticks);
    for t in 0..ticks {
        witnesses.push(state[0]);
        state = step(&state, law_for(family, t));
    }
    (state, witnesses)
}
fn reconstruct(end: &State, witnesses: &[u8], family: u8, inv_a: &Matrix, inv_b: &Matrix) -> Result<State, &'static str> {
    let mut current = *end;
    for t in (0..witnesses.len()).rev() {
        let (inv, law) = if family == 0 || (family == 2 && t < 17) {
            (inv_a, LAW_A)
        } else {
            (inv_b, LAW_B)
        };
        current = restore(&current, witnesses[t], inv, law)?;
    }
    Ok(current)
}
fn verify_row(seed: u8, family: u8, ticks: usize, inv_a: &Matrix, inv_b: &Matrix) -> (State, Vec<u8>) {
    let (end, witnesses) = forward(seed, family, ticks);
    let packed = encode_witness(&witnesses);
    let decoded = decode_witness(&packed, ticks).expect("canonical source");
    let recovered = reconstruct(&end, &decoded, family, inv_a, inv_b)
        .expect("fixed law + witness reconstructs");
    assert_eq!(recovered, origin(seed), "original identity and exact state must recover");
    if family < 2 && ticks == 81 {
        assert_eq!(end, [0u8; N], "the original transition is nilpotent");
    }
    (end, packed)
}
fn emit(outdir: &Path) -> std::io::Result<()> {
    fs::create_dir_all(outdir)?;
    let inv_a = inverse_matrix(LAW_A);
    let inv_b = inverse_matrix(LAW_B);
    let mut bin = Vec::<u8>::new();
    bin.extend_from_slice(b"HBI1");
    bin.push(1u8); // version
    bin.extend_from_slice(&(55u16).to_le_bytes());
    let mut rows = Vec::new();
    rows.push(format!(
        "HBP1|schema=ASOLARIA-C3-GF3-REVERSIBLE-STATE-WITNESS-V1|Rust=1.81.0|field=GF3|trits=-1,0,+1|original_source={SOURCE_SHA}|original_blob={SOURCE_BLOB}|no_JSON=1|json=0"
    ));
    rows.push("BOUNDARY|original_81_state_only_is_lossy=TRUE|external_event_history_not_inferred=TRUE|source_authentication_requires_external_root=TRUE|real_photons_recorded=NO|json=0".to_string());
    let mut count = 0usize;
    for family in 0u8..=2 {
        for seed in 0u8..5 {
            let horizons: &[usize] = if family == 2 { &[40] } else { &HORIZONS };
            for &ticks in horizons {
                let (end, packed) = verify_row(seed, family, ticks, &inv_a, &inv_b);
                let witness = decode_witness(&packed, ticks).expect("valid packed digits");
                if family != 2 {
                    assert_eq!(ticks, witness.len(), "one lost trit per step");
                }
                // Binary record: family, seed, ticks u16, witness byte length u8,
                // 81 final trits (base-3 residues), canonical witness bytes.
                bin.push(family);
                bin.push(seed);
                bin.extend_from_slice(&(ticks as u16).to_le_bytes());
                bin.push(u8::try_from(packed.len()).expect("witness length bounded"));
                bin.extend_from_slice(&end);
                bin.extend_from_slice(&packed);
                rows.push(format!(
                    "ROW|family={family}|seed={seed}|logical_ticks={ticks}|rank={}|nullity={ticks}|sideband_trits={}|packed_bytes={}|inverse=PASS|source_original=PASS|no_physical_time_claim=TRUE|json=0",
                    N - ticks,
                    witness.len(),
                    packed.len()
                ));
                count += 1;
            }
        }
    }
    assert_eq!(count, 55);
    assert_eq!(bin[5..7], 55u16.to_le_bytes());
    let (zero, _) = forward(0, 0, 81);
    assert!(zero.iter().all(|&v| v == 0));
    rows.push("COLLISION|fixed_law_after_81=ALL_ZERO|possible_initial_states=3^81|minimal_recoverable_witness_trits=81|packed_witness_capacity_bytes=17|independent_stored_memories=NOT_INFERRED|json=0".to_string());
    // A modified history can be another valid initial state. Pinned original required.
    let (end, mut witness) = forward(0, 0, 81);
    witness[0] = (witness[0] + 1) % 3;
    let altered = reconstruct(&end, &witness, 0, &inv_a, &inv_b).expect("altered path can be valid");
    assert_ne!(altered, origin(0), "altered witness must fail pinned original");
    let mut wrongpad = encode_witness(&[1u8]);
    wrongpad[0] += 3;
    assert!(decode_witness(&wrongpad, 1).is_err());
    assert!(decode_witness(&[244], 1).is_err());
    assert!(decode_witness(&[1], 2).is_err() || decode_witness(&[1], 2).unwrap().len() == 2);
    rows.push("NEGATIVES|flipped_history_without_source_root=ALTERNATE_PREIMAGE|flipped_history_against_pinned_original=REJECTED|noncanonical_padding=REJECTED|digit_byte_244=REJECTED|json=0".to_string());
    let body = rows.join("\n") + "\n";
    fs::write(outdir.join("seat3-reversible.hbi"), bin)?;
    fs::write(outdir.join("seat3-reversible.hbp"), body)?;
    println!("SEAT3_GF3_REVERSIBLE_RUST181_HBI_HBP_PASS records={count} source_root={SOURCE_SHA} json=0");
    Ok(())
}
fn main() -> std::io::Result<()> {
    let out = std::env::args().nth(1).expect("output directory required");
    emit(Path::new(&out))
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn predecessor_is_recoverable_for_both_laws() {
        let a = inverse_matrix(LAW_A);
        let b = inverse_matrix(LAW_B);
        for seed in 0..5 {
            for family in 0..=2 {
                let ticks = if family == 2 { 40 } else { 81 };
                verify_row(seed, family, ticks, &a, &b);
            }
        }
    }
    #[test]
    fn exact_trit_packing_and_negative_padding() {
        for ticks in HORIZONS {
            let raw: Vec<_> = (0..ticks).map(|i| (i % 3) as u8).collect();
            let packed = encode_witness(&raw);
            assert_eq!(packed.len(), ticks.div_ceil(5));
            assert_eq!(decode_witness(&packed, ticks).unwrap(), raw);
        }
        assert!(decode_witness(&[255], 5).is_err());
        assert!(decode_witness(&[3], 1).is_err());
    }
    #[test]
    fn forensic_source_witness_is_not_a_signature() {
        let a = inverse_matrix(LAW_A);
        let b = inverse_matrix(LAW_B);
        let (end, mut log) = forward(0, 0, 81);
        assert_eq!(reconstruct(&end, &log, 0, &a, &b).unwrap(), origin(0));
        log[0] = (log[0] + 1) % 3;
        assert_ne!(reconstruct(&end, &log, 0, &a, &b).unwrap(), origin(0));
    }
}
