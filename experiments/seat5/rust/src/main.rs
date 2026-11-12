#![forbid(unsafe_code)]
use std::{collections::HashSet,env,fs,path::PathBuf};
use seat5_referee::{decode,encode};

const SOURCE: &[u8] = b"seat5:81-original-qr:567-rainbow7:15309-aliases:trusted-root";
const NONCE: &str = "seat5-referee-nonce-001";

fn accept(source: &[u8], nonce: &str, expected_nonce: &str, ledger: &mut HashSet<String>) -> bool {
    if source != SOURCE || nonce != expected_nonce || ledger.contains(nonce) { return false; }
    ledger.insert(nonce.to_owned());
    true
}
fn enumerate_aliases() -> (usize,usize,usize,usize,usize) {
    let sectors: Vec<i64> = (-13..=13).map(|s| decode(&encode(s)).expect("valid balanced trits")).collect();
    let mut aliases = HashSet::new();
    let mut banks = HashSet::new();
    let mut sites = HashSet::new();
    let mut missing_band_count=0usize;
    let mut missing_row_count=0usize;
    for site in 0..81u16 {
        sites.insert(site);
        for band in 0..7u8 {
            banks.insert((site,band));
            for &sector in &sectors {
                assert!(aliases.insert((site,band,sector)));
                if band==6 { missing_band_count+=1; }
                if site==0 && band==0 { missing_row_count+=1; }
            }
        }
    }
    (aliases.len(),banks.len(),sites.len(),missing_band_count,missing_row_count)
}
fn main() {
    let out = PathBuf::from(env::args().nth(1).expect("output directory required"));
    fs::create_dir_all(&out).unwrap();
    let (aliases, bank_entries, original_memories, missing_band_aliases, missing_base_row_aliases)=enumerate_aliases();
    assert_eq!(aliases,15309);
    assert_eq!(bank_entries,567);
    assert_eq!(original_memories,81);
    assert_eq!(missing_band_aliases,2187);
    assert_eq!(missing_base_row_aliases,27);
    let mut ledger = HashSet::new();
    assert!(accept(SOURCE,NONCE,NONCE,&mut ledger));
    assert!(!accept(SOURCE,NONCE,NONCE,&mut ledger));
    fs::write(out.join("nonce-ledger.txt"),format!("{NONCE}\n").as_bytes()).unwrap();
    let mut restored: HashSet<String> = fs::read_to_string(out.join("nonce-ledger.txt")).unwrap().lines().map(str::to_owned).collect();
    assert!(!accept(SOURCE,NONCE,NONCE,&mut restored));
    let mut rejected=0;
    for i in 0..6 {
        let mut altered=SOURCE.to_vec();
        altered[i] ^= 1;
        if !accept(&altered,&format!("fresh-{i}"),&format!("fresh-{i}"),&mut HashSet::new()) { rejected+=1; }
    }
    assert_eq!(rejected,6);
    let receipt=format!("{{\"toolchain\":\"rust-1.81\",\"scope\":\"software-only\",\"aliases\":{aliases},\"bank_entries\":{bank_entries},\"original_memories\":{original_memories},\"missing_band_aliases\":{missing_band_aliases},\"missing_base_row_aliases\":{missing_base_row_aliases},\"substitutions_rejected\":{rejected},\"persistent_replay_rejected\":true}}\n");
    fs::write(out.join("rust-receipt.json"),receipt.as_bytes()).unwrap();
    print!("{receipt}");
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn aliases_not_capacity(){
        let (aliases,bank,original,missing_band,missing_row)=enumerate_aliases();
        assert_eq!(aliases,15309);
        assert_eq!(bank,567);
        assert_eq!(original,81);
        assert_eq!(missing_band,2187);
        assert_eq!(missing_row,27);
    }
    #[test] fn replay(){
        let mut ledger=HashSet::new();
        assert!(accept(SOURCE,NONCE,NONCE,&mut ledger));
        assert!(!accept(SOURCE,NONCE,NONCE,&mut ledger));
    }
    #[test] fn forged_source(){
        let mut source=SOURCE.to_vec();
        source[0]^=1;
        assert!(!accept(&source,NONCE,NONCE,&mut HashSet::new()));
    }
}
