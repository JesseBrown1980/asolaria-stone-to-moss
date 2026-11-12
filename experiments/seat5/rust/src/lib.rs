//! Balanced ternary (-1,0,+1), integer-only, no floating point.
//! Historical note: Setun (1958, USSR) was a ternary computer; this is a
//! software balanced-ternary representation, not an emulation of Setun hardware.
pub type Trit = i8;
pub fn encode(mut n: i64) -> Vec<Trit> {
    if n == 0 { return vec![0]; }
    let mut out = Vec::new();
    while n != 0 {
        let mut rem = n.rem_euclid(3);
        n = n.div_euclid(3);
        if rem == 2 { rem = -1; n += 1; }
        out.push(rem as Trit);
    }
    out
}
pub fn decode(trits: &[Trit]) -> Option<i64> {
    let mut acc=0i64;
    for &t in trits.iter().rev() {
        if !(-1..=1).contains(&t) { return None; }
        acc=acc.checked_mul(3)?.checked_add(i64::from(t))?;
    }
    Some(acc)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn signed_range_roundtrip() {
        for n in -59049..=59049 { assert_eq!(decode(&encode(n)),Some(n)); }
    }
    #[test] fn invalid_trit_rejected(){ assert_eq!(decode(&[2]),None); }
    #[test] fn overflow_rejected(){ assert_eq!(decode(&[1; 100]),None); }
    #[test] fn balanced_27() {
        let mut unique=std::collections::HashSet::new();
        for a in -1..=1 {for b in -1..=1 {for c in -1..=1 {
            let value=a+3*b+9*c;
            assert!(unique.insert(value));
            assert_eq!(decode(&encode(value)),Some(value));
        }}}
        assert_eq!(unique.len(),27);
    }
}
