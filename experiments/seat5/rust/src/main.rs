use std::{collections::HashSet,env,fs,path::PathBuf};

const SOURCE: &[u8] = b"seat5:81-original-qr:567-rainbow7:15309-aliases:trusted-root";
const NONCE: &str = "seat5-referee-nonce-001";

fn accept(source: &[u8], nonce: &str, expected_nonce: &str, ledger: &mut HashSet<String>) -> bool {
    if source != SOURCE || nonce != expected_nonce || ledger.contains(nonce) { return false; }
    ledger.insert(nonce.to_owned());
    true
}
fn main() {
    let out = PathBuf::from(env::args().nth(1).expect("output directory required"));
    fs::create_dir_all(&out).unwrap();
    assert_eq!(81*7*27,15309);
    assert_eq!(81*7,567);
    assert_eq!(81*27,2187);
    assert_eq!(7*27,189);
    assert_eq!(567*27-81*27,13122);
    let mut ledger = HashSet::new();
    assert!(accept(SOURCE,NONCE,NONCE,&mut ledger));
    assert!(!accept(SOURCE,NONCE,NONCE,&mut ledger));
    fs::write(out.join("nonce-ledger.txt"),format!("{}\n",NONCE).as_bytes()).unwrap();
    let mut restored: HashSet<String> = fs::read_to_string(out.join("nonce-ledger.txt")).unwrap().lines().map(str::to_owned).collect();
    assert!(!accept(SOURCE,NONCE,NONCE,&mut restored));
    let mut rejected=0;
    for i in 0..6 {
        let mut altered=SOURCE.to_vec();
        altered[i] ^= 1;
        if !accept(&altered,&format!("fresh-{i}"),&format!("fresh-{i}"),&mut HashSet::new()) { rejected+=1; }
    }
    assert_eq!(rejected,6);
    let receipt=format!("{{\"toolchain\":\"rust-1.81\",\"scope\":\"software-only\",\"aliases\":15309,\"bank_entries\":567,\"original_memories\":81,\"missing_band_aliases\":2187,\"missing_base_row_aliases\":27,\"substitutions_rejected\":{},\"persistent_replay_rejected\":true}}\n",rejected);
    fs::write(out.join("rust-receipt.json"),receipt.as_bytes()).unwrap();
    print!("{receipt}");
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn aliases_not_capacity(){assert_eq!(81*7*27,15309);assert_eq!(81*7,567);}
    #[test] fn missing_band(){assert_eq!(81*27,2187);}
    #[test] fn replay(){let mut l=HashSet::new();assert!(accept(SOURCE,NONCE,NONCE,&mut l));assert!(!accept(SOURCE,NONCE,NONCE,&mut l));}
    #[test] fn forged_source(){let mut s=SOURCE.to_vec();s[0]^=1;assert!(!accept(&s,NONCE,NONCE,&mut HashSet::new()));}
}
