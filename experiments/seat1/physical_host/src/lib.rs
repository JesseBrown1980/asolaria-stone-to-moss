#![forbid(unsafe_code)]
//! Deterministic integer-only balanced-ternary workload for physical-host measurements.
//! This measures executable work, not optical photons or electrical instrumentation.

pub type Trit = i8;
pub const BASE_MEMORIES: u64 = 81;
pub const BANDS: u64 = 7;
pub const SECTORS: u64 = 27;
pub const ADDRESSES_PER_ROUND: u64 = BASE_MEMORIES * BANDS * SECTORS;
pub const ROUNDS: u32 = 128;
pub const FROZEN_DIGEST: &str = "3b6fe647a64e065f";

pub fn balanced_value(a: Trit, b: Trit, c: Trit) -> Option<i64> {
    if !(-1..=1).contains(&a) || !(-1..=1).contains(&b) || !(-1..=1).contains(&c) {
        return None;
    }
    Some(i64::from(a) + 3 * i64::from(b) + 9 * i64::from(c))
}

/// Deterministic integer work. All state is u64 or signed balanced trits.
/// Wrapping addition is intentional and declared; no float calculations occur.
pub fn workload(rounds: u32) -> (u64, u64) {
    let mut accumulator = 0u64;
    let mut addresses = 0u64;
    for round in 0..rounds {
        for site in 0..81u64 {
            for band in 0..7u64 {
                for a in [-1i8, 0, 1] {
                    for b in [-1i8, 0, 1] {
                        for c in [-1i8, 0, 1] {
                            let sector = balanced_value(a, b, c).expect("valid ternary digits");
                            let word = ((site + 1) * 0x9E37_79B1u64)
                                ^ ((band + 1) * 0x85EB_CA77u64)
                                ^ (((sector + 14) as u64) * 0xC2B2_AE3Du64);
                            accumulator = accumulator.rotate_left(7)
                                .wrapping_add(word ^ u64::from(round));
                            addresses += 1;
                        }
                    }
                }
            }
        }
        accumulator = std::hint::black_box(accumulator);
    }
    (accumulator, addresses)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn every_three_trit_address_is_distinct() {
        let mut values = std::collections::HashSet::new();
        for a in [-1i8, 0, 1] {
            for b in [-1i8, 0, 1] {
                for c in [-1i8, 0, 1] {
                    let sector = balanced_value(a,b,c).unwrap();
                    assert!(values.insert(sector));
                }
            }
        }
        assert_eq!(values.len(), 27);
        assert_eq!(values.iter().min(), Some(&-13));
        assert_eq!(values.iter().max(), Some(&13));
    }
    #[test]
    fn invalid_trit_rejected() {
        assert_eq!(balanced_value(2,0,0),None);
        assert_eq!(balanced_value(-2,0,0),None);
    }
    #[test]
    fn original_bank_cardinality_not_alias_capacity() {
        assert_eq!(BASE_MEMORIES,81);
        assert_eq!(BASE_MEMORIES * BANDS,567);
        assert_eq!(ADDRESSES_PER_ROUND,15_309);
        assert_eq!(BASE_MEMORIES * SECTORS,2_187);
    }
    #[test]
    fn frozen_integer_workload() {
        let (value,addresses) = workload(ROUNDS);
        assert_eq!(format!("{value:016x}"),FROZEN_DIGEST);
        assert_eq!(addresses, ADDRESSES_PER_ROUND * u64::from(ROUNDS));
    }
    #[test]
    fn zero_rounds_do_not_execute() {
        assert_eq!(workload(0),(0,0));
    }
}
