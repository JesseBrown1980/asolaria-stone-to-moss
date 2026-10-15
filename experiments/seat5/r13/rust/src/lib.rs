#![forbid(unsafe_code)]
//! Seat5 R13: integer-only center-origin ternary addressing.
//! This is a LOSSLESS, GATED address transform, not a physical detector.
//! Roots stay separate; 27 cells are flat 3×3×3 ordered triplets.
//! The separately named Chariots are audit traversals; not new physics.

pub type Trit = i8;
pub mod paths;
pub const CELLS: usize = 27;
pub const CENTER: usize = 13;
pub const PER_ROOT_CHANNELS: usize = 81; // 27 addresses × 3 encircling/shadow channels

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum GateError {
    InvalidTrit,
    InvalidOrdinal,
    NoOrigin,
    Overflow,
    NonIntegralObserver,
}

pub fn ordinal(trits: [Trit; 3]) -> Result<usize, GateError> {
    let mut n = 0usize;
    for t in trits {
        if !(-1..=1).contains(&t) {
            return Err(GateError::InvalidTrit);
        }
        n = n * 3 + usize::try_from(t + 1).map_err(|_| GateError::InvalidTrit)?;
    }
    Ok(n)
}

pub fn path(mut ord: usize) -> Result<[Trit; 3], GateError> {
    if ord >= CELLS {
        return Err(GateError::InvalidOrdinal);
    }
    let mut trits = [0i8; 3];
    for t in trits.iter_mut().rev() {
        *t = (ord % 3) as Trit - 1;
        ord /= 3;
    }
    Ok(trits)
}

pub fn mirror(ord: usize) -> Result<usize, GateError> {
    if ord >= CELLS {
        return Err(GateError::InvalidOrdinal);
    }
    Ok(CELLS - 1 - ord)
}

/// Permutes vantage axes, an order-three action distinct from mirror negation.
/// (a,b,c)->(b,c,a). It leaves zero-center fixed.
pub fn rotate3(trits: [Trit; 3]) -> [Trit; 3] {
    [trits[1], trits[2], trits[0]]
}

/// A depth-d ternary address has 3^d leaves per origin, with checked capacity.
pub fn capacity(origins: u64, depth: u32) -> Result<u64, GateError> {
    if origins == 0 {
        return Err(GateError::NoOrigin);
    }
    let mut size = origins;
    for _ in 0..depth {
        size = size.checked_mul(3).ok_or(GateError::Overflow)?;
    }
    Ok(size)
}

/// Two ordered Chariot traversals start at the observer (free coordinate zero).
/// One takes positive side before negative; the other takes negative first.
/// Both enumerate the SAME 27 addresses and remain mirror images.
pub fn chariot_walk(positive_first: bool) -> [usize; CELLS] {
    let mut order = [CENTER; CELLS];
    for k in 0..13usize {
        let pos = CENTER + 1 + k;
        let neg = CENTER - 1 - k;
        order[1 + 2 * k] = if positive_first { pos } else { neg };
        order[2 + 2 * k] = if positive_first { neg } else { pos };
    }
    order
}

/// Third vantage reconstructible ONLY under explicit 3-centred sum law.
/// Its existence alone does not prove all data can be obtained from two.
pub fn third(center: i64, a: i64, b: i64) -> Result<i64, GateError> {
    center
        .checked_mul(3)
        .and_then(|v| v.checked_sub(a))
        .and_then(|v| v.checked_sub(b))
        .ok_or(GateError::Overflow)
}
pub fn three_way_gate(center: i64, a: i64, b: i64, c: i64) -> bool {
    third(center, a, b).is_ok_and(|value| value == c)
}

/// A tiny two-sided observer arithmetic witness (NOT measured predictor).
/// A nonintegral midpoint is rejected instead of silently truncating.
pub fn bidirectional_observer(left: i64, right: i64) -> Result<i64, GateError> {
    let sum = left.checked_add(right).ok_or(GateError::Overflow)?;
    if sum % 2 != 0 {
        return Err(GateError::NonIntegralObserver);
    }
    Ok(sum / 2)
}

/// Strong gated special case: mirror-symmetric flat 27-jection.
/// The root/observer is paid ONCE; +/- coordinates carry signed differences.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MirrorOrbit {
    pub observer: i64,
    pub offsets_positive: [i64; 13],
}

pub fn encode_orbit(values: &[i64; CELLS]) -> Option<MirrorOrbit> {
    let observer = values[CENTER];
    let double = observer.checked_mul(2)?;
    let mut offsets_positive = [0i64; 13];
    for (i, offset) in offsets_positive.iter_mut().enumerate() {
        let positive_index = CENTER + 1 + i;
        let negative_index = CENTER - 1 - i;
        if values[positive_index].checked_add(values[negative_index])? != double {
            return None;
        }
        *offset = values[positive_index].checked_sub(observer)?;
    }
    Some(MirrorOrbit {
        observer,
        offsets_positive,
    })
}

pub fn decode_orbit(orbit: &MirrorOrbit) -> Result<[i64; CELLS], GateError> {
    let mut values = [orbit.observer; CELLS];
    for (i, &offset) in orbit.offsets_positive.iter().enumerate() {
        values[CENTER + 1 + i] = orbit.observer.checked_add(offset).ok_or(GateError::Overflow)?;
        values[CENTER - 1 - i] = orbit.observer.checked_sub(offset).ok_or(GateError::Overflow)?;
    }
    Ok(values)
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Encoding {
    /// Proven *same* center, proven all mirror pairs. Keep one observer overall.
    Shared {
        observer: i64,
        blocks_positive: Vec<[i64; 13]>,
    },
    /// Independent/unmatched source: its entire 27-cell input is preserved.
    Paid(Vec<[i64; CELLS]>),
}

pub fn encode_flat(blocks: &[[i64; CELLS]]) -> Result<Encoding, GateError> {
    if blocks.is_empty() {
        return Err(GateError::NoOrigin);
    }
    let mut orbits = Vec::with_capacity(blocks.len());
    for b in blocks {
        match encode_orbit(b) {
            Some(o) => orbits.push(o),
            None => return Ok(Encoding::Paid(blocks.to_vec())),
        }
    }
    if orbits.iter().any(|o| o.observer != orbits[0].observer) {
        return Ok(Encoding::Paid(blocks.to_vec()));
    }
    Ok(Encoding::Shared {
        observer: orbits[0].observer,
        blocks_positive: orbits.iter().map(|o| o.offsets_positive).collect(),
    })
}

pub fn decode_flat(encoded: &Encoding) -> Result<Vec<[i64; CELLS]>, GateError> {
    match encoded {
        Encoding::Paid(blocks) => Ok(blocks.clone()),
        Encoding::Shared {
            observer,
            blocks_positive,
        } => blocks_positive
            .iter()
            .map(|offsets| {
                decode_orbit(&MirrorOrbit {
                    observer: *observer,
                    offsets_positive: *offsets,
                })
            })
            .collect(),
    }
}

pub fn synthetic_block(observer: i64, origin: i64) -> [i64; CELLS] {
    let mut out = [observer; CELLS];
    for i in 0..13usize {
        let d = (i as i64 + 1) * (origin + 1);
        out[CENTER + 1 + i] = observer + d;
        out[CENTER - 1 - i] = observer - d;
    }
    out
}

/// Costs in *thirds-units*, never interpreted as state trits.
/// Source preprint: two encircling +1, one shadow -1/3.
pub fn encircling_cost_thirds(units: i64) -> Result<i64, GateError> {
    units.checked_mul(3 + 3 - 1).ok_or(GateError::Overflow)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;

    #[test]
    fn all_27_positions_reversible_from_the_center() {
        let mut distinct = HashSet::new();
        for i in 0..CELLS {
            let p = path(i).unwrap();
            assert!(distinct.insert(p));
            assert_eq!(ordinal(p), Ok(i));
            assert_eq!(ordinal(p.map(|t| -t)), Ok(mirror(i).unwrap()));
            assert_eq!(rotate3(rotate3(rotate3(p))), p);
            let r = rotate3(p);
            assert_eq!(ordinal(rotate3(rotate3(p))), ordinal(rotate3(r)));
        }
        assert_eq!(distinct.len(), 27);
        assert_eq!(path(CENTER), Ok([0, 0, 0]));
        assert_eq!(mirror(CENTER), Ok(CENTER));
        assert_eq!(rotate3([0, 0, 0]), [0, 0, 0]);
        assert_ne!(rotate3([-1, 0, 1]), rotate3(rotate3([-1, 0, 1])));
    }

    #[test]
    fn n_times_three_cubed_and_depth_ladder() {
        for (depth, per_root) in [(0, 1), (1, 3), (2, 9), (3, 27), (4, 81)] {
            assert_eq!(capacity(1, depth), Ok(per_root));
        }
        for n in [1u64, 3, 6, 9, 27, 81] {
            assert_eq!(capacity(n, 3), Ok(n * 27));
        }
        assert_eq!(capacity(0, 3), Err(GateError::NoOrigin));
        assert_eq!(capacity(u64::MAX, 1), Err(GateError::Overflow));
        assert_eq!(ordinal([2, 0, 0]), Err(GateError::InvalidTrit));
        assert_eq!(ordinal([-2, 0, 0]), Err(GateError::InvalidTrit));
        assert_eq!(path(27), Err(GateError::InvalidOrdinal));
    }

    #[test]
    fn paired_chariots_are_complete_and_centered() {
        let pos = chariot_walk(true);
        let neg = chariot_walk(false);
        assert_eq!(pos[0], CENTER);
        assert_eq!(neg[0], CENTER);
        let a: HashSet<_> = pos.iter().copied().collect();
        let b: HashSet<_> = neg.iter().copied().collect();
        assert_eq!(a.len(), 27);
        assert_eq!(a, b);
        for (i, p) in pos.iter().enumerate() {
            assert_eq!(mirror(*p), Ok(neg[i]));
        }
    }

    #[test]
    fn shared_center_required_or_pay_full_input() {
        let mut blocks: Vec<_> = (0..27).map(|i| synthetic_block(1000, i)).collect();
        let shared = encode_flat(&blocks).unwrap();
        match &shared {
            Encoding::Shared { observer, blocks_positive } => {
                assert_eq!(*observer, 1000);
                assert_eq!(blocks_positive.len(), blocks.len());
            }
            Encoding::Paid(_) => panic!("valid shared center unexpectedly declined"),
        }
        assert_eq!(decode_flat(&shared).unwrap(), blocks);
        blocks[10][0] += 1; // single broken mirror: not entitled to "free" third
        let paid = encode_flat(&blocks).unwrap();
        assert!(matches!(paid, Encoding::Paid(_)));
        assert_eq!(decode_flat(&paid).unwrap(), blocks);
        blocks[10][0] -= 1;
        blocks[20][CENTER] += 1; // different roots fail shared-center gate
        assert!(matches!(encode_flat(&blocks).unwrap(), Encoding::Paid(_)));
        assert!(matches!(encode_flat(&[]), Err(GateError::NoOrigin)));
    }

    #[test]
    fn third_is_free_only_under_sum_closure() {
        let (observer, a, b, c) = (10, 7, 13, 10);
        assert!(three_way_gate(observer, a, b, c));
        assert_eq!(third(observer, a, b), Ok(c));
        assert!(!three_way_gate(observer, a, b, c + 1));
        assert_eq!(bidirectional_observer(7, 13), Ok(10));
        assert_eq!(bidirectional_observer(7, 12), Err(GateError::NonIntegralObserver));
        assert_eq!(third(i64::MAX, 1, 2), Err(GateError::Overflow));
    }

    #[test]
    fn distinct_zero_and_shadow_costs_are_not_folded() {
        assert_eq!(path(CENTER), Ok([0, 0, 0]));
        assert_ne!(ordinal([-1, 1, 0]), ordinal([0, 0, 0]));
        assert_eq!((1 + 1 + 1) % 3, 0); // GF3 sum loses direction identity
        assert_eq!(CELLS * 3, PER_ROOT_CHANNELS);
        assert_eq!(encircling_cost_thirds(27), Ok(135));
        assert_eq!(encircling_cost_thirds(81), Ok(405));
        assert_eq!(encircling_cost_thirds(i64::MAX), Err(GateError::Overflow));
        assert_eq!(6 + 1, 7); // separate 2-D geometry with six neighbors + center
    }
}
