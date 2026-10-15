//! Finite *classical* route and digital projection falsifiers.
//! These do NOT implement physical quantum cloning, photon detectors, QR
//! decoding, GPU optical readout, or infinite simultaneous agent processes.
//! Full source identities are necessary: residues alone have collisions.

use crate::{GateError, Trit, CELLS};
use std::collections::HashSet;

pub const OPERATOR_PATHS: [u8; 8] = [1, 2, 3, 5, 7, 9, 11, 13];

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct PathAddress {
    pub origin: u64,
    pub route_label: u8,
    pub level: u32,
    pub ordered_trits: Vec<Trit>,
}

pub fn is_prime(n: u64) -> bool {
    if n < 2 { return false; }
    let mut d = 2u64;
    while d <= n / d {
        if n % d == 0 { return false; }
        d += 1;
    }
    true
}

/// Classes coprime to 27: exactly 18 residues, not collision-free identities.
pub fn unit_residue27(n: u64) -> Option<u8> {
    let rem = (n % 27) as u8;
    if rem % 3 == 0 { None } else { Some(rem) }
}

/// Zero depth denotes the center-root *empty path*, not null/missing.
pub fn digits(mut ordinal: u64, depth: u32) -> Result<Vec<Trit>, GateError> {
    let width = 3u64.checked_pow(depth).ok_or(GateError::Overflow)?;
    if ordinal >= width { return Err(GateError::InvalidOrdinal); }
    let mut out = vec![0; depth as usize];
    for trit in out.iter_mut().rev() {
        *trit = (ordinal % 3) as Trit - 1;
        ordinal /= 3;
    }
    Ok(out)
}

pub fn digits_to_ordinal(path: &[Trit]) -> Result<u64, GateError> {
    let mut result = 0u64;
    for &digit in path {
        if !(-1..=1).contains(&digit) { return Err(GateError::InvalidTrit); }
        result = result
            .checked_mul(3)
            .and_then(|x| x.checked_add((digit + 1) as u64))
            .ok_or(GateError::Overflow)?;
    }
    Ok(result)
}

pub fn address(origin: u64, route: u8, level: u32, ordinal: u64) -> Result<PathAddress, GateError> {
    if !OPERATOR_PATHS.contains(&route) { return Err(GateError::InvalidOrdinal); }
    Ok(PathAddress { origin, route_label: route, level, ordered_trits: digits(ordinal, level)? })
}

/// Exact 3×9 *digital* grid of 27 trit symbols, not a sensor-captured image.
pub fn rasterize(colour: &[Trit; CELLS]) -> Result<[[u8; 9]; 3], GateError> {
    let mut raster = [[0u8; 9]; 3];
    for (i, &trit) in colour.iter().enumerate() {
        if !(-1..=1).contains(&trit) { return Err(GateError::InvalidTrit); }
        raster[i / 9][i % 9] = (trit + 1) as u8;
    }
    Ok(raster)
}

pub fn restore_raster(raster: &[[u8; 9]; 3]) -> Result<[Trit; CELLS], GateError> {
    let mut colour = [0i8; CELLS];
    for (i, dest) in colour.iter_mut().enumerate() {
        let val = raster[i / 9][i % 9];
        if val > 2 { return Err(GateError::InvalidTrit); }
        *dest = val as Trit - 1;
    }
    Ok(colour)
}

/// The optional binary threshold loses the distinction between center and +.
pub fn collapsed_binary_shadow(colour: &[Trit; CELLS]) -> [u8; CELLS] {
    colour.map(|t| if t < 0 { 0 } else { 1 })
}

/// Full path witnesses make a finite address set injective by construction.
pub fn unique_keys(origins: u64, level: u32) -> Result<usize, GateError> {
    if origins == 0 { return Err(GateError::NoOrigin); }
    let width = 3u64.checked_pow(level).ok_or(GateError::Overflow)?;
    let mut seen = HashSet::new();
    for origin in 0..origins {
        for route in OPERATOR_PATHS {
            for ordinal in 0..width {
                assert!(seen.insert(address(origin, route, level, ordinal)?));
            }
        }
    }
    Ok(seen.len())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn prime_residue_collisions_and_trime_classes() {
        assert!(is_prime(2) && is_prime(29));
        assert_eq!(unit_residue27(2), Some(2));
        assert_eq!(unit_residue27(29), Some(2));
        assert_eq!(unit_residue27(27), None);
        assert_eq!(unit_residue27(3), None);
        let distinct: HashSet<_> = (0..27).filter_map(unit_residue27).collect();
        assert_eq!(distinct.len(), 18);
        assert!(!is_prime(1) && !is_prime(9));
        assert_eq!(OPERATOR_PATHS.len(), 8);
    }

    #[test]
    fn finite_nested_paths_do_not_collide_when_full_identity_is_kept() {
        for level in 0..=4 {
            assert_eq!(unique_keys(3, level), Ok(3usize * 8 * 3usize.pow(level)));
        }
        assert_eq!(unique_keys(0, 3), Err(GateError::NoOrigin));
        assert_eq!(unique_keys(1, 41), Err(GateError::Overflow));
        assert_ne!(address(0, 3, 3, 13), address(0, 5, 3, 13));
        assert_ne!(address(0, 3, 3, 13), address(1, 3, 3, 13));
        assert_ne!(address(0, 3, 2, 4), address(0, 3, 3, 13));
    }

    #[test]
    fn ordered_trits_recover_center_at_all_tested_levels() {
        for level in 0..=9 {
            let width = 3u64.pow(level);
            for position in 0..width {
                let sequence = digits(position, level).unwrap();
                assert_eq!(digits_to_ordinal(&sequence), Ok(position));
            }
            assert_eq!(digits_to_ordinal(&vec![0; level as usize]), Ok((width - 1) / 2));
        }
        assert_eq!(digits(1, 0), Err(GateError::InvalidOrdinal));
        assert_eq!(digits_to_ordinal(&[2]), Err(GateError::InvalidTrit));
        assert_eq!(digits(0, 41), Err(GateError::Overflow));
    }

    #[test]
    fn nesting_depth_thirteen_is_an_address_count_not_live_agent_population() {
        assert_eq!(3u64.checked_pow(13), Some(1_594_323));
        assert_eq!(3u64.checked_pow(41), None);
        assert_eq!(digits_to_ordinal(&[0; 13]), Ok(797_161));
        assert_eq!(digits(797_161, 13), Ok(vec![0; 13]));
    }

    #[test]
    fn lossless_digital_shadow_3_by_9_roundtrip() {
        let mut source = [0i8; CELLS];
        for (i, trit) in source.iter_mut().enumerate() { *trit = (i % 3) as i8 - 1; }
        let image = rasterize(&source).unwrap();
        assert_eq!(restore_raster(&image), Ok(source));
        let mut damaged = image;
        damaged[0][0] = 3;
        assert_eq!(restore_raster(&damaged), Err(GateError::InvalidTrit));
    }

    #[test]
    fn binary_threshold_collapses_center_and_positive() {
        let mut a = [0i8; CELLS];
        let mut b = a;
        b[13] = 1;
        assert_ne!(a, b);
        assert_eq!(collapsed_binary_shadow(&a), collapsed_binary_shadow(&b));
        a[0] = -1;
        assert_ne!(collapsed_binary_shadow(&a), collapsed_binary_shadow(&b));
    }
}
