#![forbid(unsafe_code)]
//! Seat5 independently constructs OUTPUT rows of 81-bit GF(2) transition.
//! This is not Seat4's polynomial convolution or Node output-column matrix.
//! Only integer arithmetic. No external crates, no optical measurement claims.

use std::{env, fs, path::PathBuf};

const N: usize = 81;
const MASK: u128 = (1_u128 << N) - 1;
const LAWS: [&[usize]; 5] = [
    &[0, 1], &[0, 2], &[0, 1, 3], &[0, 4, 7], &[0, 1, 5, 9],
];
const SEEDS: [[u128; 3]; 5] = [
    [0x1eb0ff28ceb27955b56ba, 0x042c7cd7ad1a5ef4145ab, 0x0d47a912d257a104f3bc6],
    [0x19ea616fecd2bfa631536, 0x1bc349d6be43ea650c164, 0x0e81c398f7db8f1fa1c61],
    [0x086653ba75f346546f585, 0x13175b65caa852a51275a, 0x0101cbdd66f425847dde5],
    [0x0a57d11ad6fd0d216cb16, 0x01edd07fa8fb8ff5f47a5, 0x0778a793a153367b4add5],
    [0x1725cfdbffe633141ebdb, 0x1163905feac81216b2f04, 0x0415d11fd7fa46b961e61],
];
const SOURCE_BLOB: &str = "2b0ed7e52776cd8a9b48086d83ba31c8486629fb";
const LARGE_HORIZON: u64 = 10_000_000_000_000;
type Rows = [u128; N];

fn rows_for(taps: &[usize]) -> Rows {
    let mut rows = [0_u128; N];
    for (i, row) in rows.iter_mut().enumerate() {
        for &tap in taps {
            // Row i identifies input bit (i-tap) modulo 81.
            *row ^= 1_u128 << ((i + N - tap) % N);
        }
    }
    rows
}

fn apply(rows: &Rows, x: u128) -> u128 {
    let mut result = 0_u128;
    for (i, &row) in rows.iter().enumerate() {
        result |= (u128::from((row & x).count_ones() & 1)) << i;
    }
    result
}

fn compose(a: &Rows, b: &Rows) -> Rows {
    // Composition output-row i = XOR of rows of b selected by row a_i.
    let mut rows = [0_u128; N];
    for (i, &source_row) in a.iter().enumerate() {
        let mut select = source_row;
        while select != 0 {
            let j = select.trailing_zeros() as usize;
            rows[i] ^= b[j];
            select &= select - 1;
        }
    }
    rows
}

fn powers(taps: &[usize]) -> Vec<Rows> {
    let mut out = vec![rows_for(taps)];
    for _ in 0..45 {
        let next = compose(out.last().expect("initial matrix"), out.last().expect("initial matrix"));
        out.push(next);
    }
    out
}

fn jump(mut state: u128, mut steps: u64, ladder: &[Rows]) -> u128 {
    let mut i = 0;
    while steps != 0 {
        if steps & 1 != 0 {
            state = apply(&ladder[i], state);
        }
        steps >>= 1;
        i += 1;
    }
    state
}

fn rank(rows: &Rows) -> usize {
    let mut pivot = [0_u128; N];
    let mut count = 0;
    for &r in rows {
        let mut value = r;
        while value != 0 {
            let col = 127 - value.leading_zeros() as usize;
            if pivot[col] == 0 {
                pivot[col] = value;
                count += 1;
                break;
            }
            value ^= pivot[col];
        }
    }
    count
}

fn hex81(x: u128) -> String {
    format!("{x:021x}")
}

fn field<'a>(line: &'a str, name: &str) -> Result<&'a str, String> {
    let needle = format!("\"{name}\":");
    let data = line.split_once(&needle).ok_or(format!("MISSING_{name}"))?.1;
    if let Some(quoted) = data.strip_prefix('"') {
        quoted.split('"').next().ok_or(format!("BAD_{name}"))
    } else {
        data.split([',', '}']).next().ok_or(format!("BAD_{name}"))
    }
}

fn number(line: &str, name: &str) -> Result<u64, String> {
    field(line, name)?.parse::<u64>().map_err(|_|format!("INVALID_{name}"))
}

fn hex_number(line: &str, name: &str) -> Result<u128, String> {
    u128::from_str_radix(field(line, name)?, 16).map_err(|_|format!("INVALID_HEX_{name}"))
}

fn checked_case(line: &str, powers_per_law: &[Vec<Rows>]) -> Result<String, String> {
    let law = number(line, "law_index")? as usize;
    let trial = number(line, "trial")? as usize;
    if law >= LAWS.len() || trial >= 3 {return Err("UNSUPPORTED_LAW_OR_TRIAL".to_owned());}
    let taps_string = LAWS[law].iter().map(usize::to_string).collect::<Vec<_>>().join(",");
    if !line.contains(&format!("\"taps\":[{taps_string}]")) {return Err("TAP_LAW_SUBSTITUTED".to_owned());}
    if field(line, "source_original_git_blob")? != SOURCE_BLOB {return Err("SOURCE_ROOT_SUBSTITUTED".to_owned());}
    if field(line, "real_optical_photon_measurement")? != "false" {return Err("FALSE_OPTICAL_PROMOTION".to_owned());}
    let seed = SEEDS[law][trial];
    if hex_number(line, "seed_81_hex")? != seed {return Err("WRONG_FROZEN_SEED".to_owned());}
    let a = number(line,"a")?;
    let b = number(line,"b")?;
    let kind = field(line,"kind")?;
    let ladder=&powers_per_law[law];
    let (step, final_state, witness) = match kind {
        "split" => {
            let step=a.checked_add(b).ok_or("STEP_OVERFLOW")?;
            (step, jump(seed,step,ladder),jump(jump(seed,a,ladder),b,ladder))
        },
        "short" => {
            if a > 81 || b != 0 {return Err("SHORT_BOUND".to_owned());}
            let mut slow=seed;
            for _ in 0..a {slow=apply(&ladder[0],slow);}
            (a,jump(seed,a,ladder),slow)
        },
        "bitflip" => {
            let bit=number(line,"bit")? as usize;
            if a!=LARGE_HORIZON || b!=0 || ![0,40,80].contains(&bit) {return Err("BITFLIP_BOUND".to_owned());}
            let final_state=jump(seed,a,ladder);
            let delta=jump(seed^(1_u128<<bit),a,ladder)^final_state;
            if delta!=jump(1_u128<<bit,a,ladder){return Err("SUPERPOSITION_FAILED".to_owned());}
            (a,final_state,delta)
        },
        _=>return Err("UNKNOWN_KIND".to_owned()),
    };
    if step != number(line,"simulated_logical_steps")? {return Err("STEP_COUNT_CORRUPTED".to_owned());}
    if final_state != hex_number(line,"final_state_hex")? {return Err("STATE_CHANGED".to_owned());}
    if witness != hex_number(line,"witness_hex")? {return Err("WITNESS_CHANGED".to_owned());}
    if final_state > MASK || witness > MASK {return Err("OUTSIDE_81BIT_STATE".to_owned());}
    if kind=="split" && final_state!=witness {return Err("SEMIGROUP_FAILED".to_owned());}
    Ok(format!("{law}|{trial}|{kind}|{a}|{b}|{}|{}|{}\n",
        if kind=="bitflip" {field(line,"bit")?.to_owned()} else {"-".to_owned()},
        hex81(final_state),hex81(witness)))
}

fn check_switched_law(ladders:&[Vec<Rows>])->(String,String) {
    let seed=SEEDS[0][0];
    let mut reference=seed;
    for (&law,&iterations) in [0_usize,1].iter().zip([17_usize,23].iter()){
        let rows=rows_for(LAWS[law]);
        for _ in 0..iterations {reference=apply(&rows,reference);}
    }
    let composed=jump(jump(seed,17,&ladders[0]),23,&ladders[1]);
    let wrong=jump(seed,40,&ladders[0]);
    assert_eq!(reference,composed,"correctly scheduled law must match direct reference");
    assert_ne!(wrong,reference,"stale law must fail");
    assert_eq!(hex81(wrong),"1284fb06a20fdbc73537c");
    assert_eq!(hex81(reference),"1949302f90e20a0478bf2");
    (hex81(reference),hex81(wrong))
}

fn execute(case_file:&str,out_dir:&str) {
    let original=fs::read_to_string(case_file).expect("Seat4 195-case trace required");
    let lines:Vec<&str>=original.lines().collect();
    assert_eq!(lines.len(),195,"expected all 195 frozen records");
    let ladders:Vec<Vec<Rows>>=LAWS.iter().map(|taps| powers(taps)).collect();
    let ranks:Vec<usize>=ladders.iter().map(|ladder|rank(&ladder[0])).collect();
    assert_eq!(ranks,[80,80,81,81,80],"invertibility discovery drift");
    for (i,&r) in ranks.iter().enumerate(){
        if r < N {
            assert_eq!(apply(&ladders[i][0],MASK),0,"nonzero all-ones kernel");
            assert_eq!(apply(&ladders[i][0],MASK),apply(&ladders[i][0],0));
        } else {
            assert_eq!(apply(&ladders[i][0],MASK),MASK,"odd law preserves ones");
        }
    }
    let mut witness=String::new();
    let mut cases=0_usize;
    for line in lines {
        match checked_case(line,&ladders) {
            Ok(s)=>{witness.push_str(&s);cases+=1;},
            Err(err)=>panic!("81BIT_CASE_{cases}_REJECTED:{err}"),
        }
    }
    assert_eq!(cases,195);
    let (correct,stale)=check_switched_law(&ladders);
    let a=1_u128;let b=2_u128;
    let linear=|x|apply(&ladders[0][0],x);
    let nonlinear=|x|linear(x)^(((x&1)&((x>>1)&1))<<40);
    let carry=|x|(linear(x)+x)&MASK;
    assert_ne!(nonlinear(a^b)^nonlinear(a)^nonlinear(b),0);
    assert_ne!(carry(a^b)^carry(a)^carry(b),0);
    fs::create_dir_all(out_dir).expect("create output directory");
    fs::write(PathBuf::from(out_dir).join("r11-cases.tsv"),witness.as_bytes()).expect("write case witness");
    let receipt=format!(
      "{{\"schema\":\"ASOLARIA-SEAT5-R11-RUST181-ROW-GF2-V1\",\"rows_verified\":{cases},\"law_ranks\":[80,80,81,81,80],\"law_nullities\":[1,1,0,0,1],\"noninvertible_all_ones_kernel\":true,\"valid_switched_state\":\"{correct}\",\"stale_invalid_state\":\"{stale}\",\"nonlinear_and_carry_rejected\":true,\"arbitrary_hashchain_jump_claimed\":false,\"direct_optical_detector_measured\":false}}\n"
    );
    fs::write(PathBuf::from(out_dir).join("r11-receipt.json"),receipt.as_bytes()).expect("write receipt");
    print!("{receipt}");
}

fn main(){
    let args:Vec<String>=env::args().collect();
    assert_eq!(args.len(),3,"usage: binary REFERENCE_CASES_JSONL OUT_DIR");
    execute(&args[1],&args[2]);
}

#[cfg(test)]
mod tests{
    use super::*;
    #[test] fn rank_and_kernel(){
        assert_eq!(LAWS.iter().map(|law|rank(&rows_for(law))).collect::<Vec<_>>(),[80,80,81,81,80]);
        assert_eq!(apply(&rows_for(LAWS[0]),MASK),0);
        assert_ne!(MASK,0);
    }
    #[test] fn identity_and_direct(){
        let ladder=powers(LAWS[2]);let state=SEEDS[2][0];
        assert_eq!(jump(state,0,&ladder),state);
        assert_eq!(jump(state,1,&ladder),apply(&ladder[0],state));
        assert_eq!(jump(state,2,&ladder),apply(&ladder[0],apply(&ladder[0],state)));
    }
    #[test] fn large_horizon_and_continuation(){
        let ladder=powers(LAWS[3]);let seed=SEEDS[3][1];
        let final_state=jump(seed,LARGE_HORIZON,&ladder);
        assert_eq!(jump(seed,LARGE_HORIZON+1,&ladder),apply(&ladder[0],final_state));
        assert_eq!(jump(seed,2*LARGE_HORIZON+1,&ladder),
                   jump(jump(seed,LARGE_HORIZON,&ladder),LARGE_HORIZON+1,&ladder));
    }
    #[test] fn switched_schedule_correct(){
        let ladders=LAWS.iter().map(|tap|powers(tap)).collect::<Vec<_>>();
        let (a,b)=check_switched_law(&ladders);
        assert_ne!(a,b);
    }
    #[test] fn altered_metadata_rejected(){
        let ladders=LAWS.iter().map(|tap|powers(tap)).collect::<Vec<_>>();
        let sample=format!("{{\"law_index\":0,\"trial\":0,\"kind\":\"short\",\"a\":0,\"b\":0,\"taps\":[0,1],\"source_original_git_blob\":\"{SOURCE_BLOB}\",\"real_optical_photon_measurement\":false,\"seed_81_hex\":\"{}\",\"simulated_logical_steps\":0,\"final_state_hex\":\"{}\",\"witness_hex\":\"{}\"}}",hex81(SEEDS[0][0]),hex81(SEEDS[0][0]),hex81(SEEDS[0][0]));
        assert!(checked_case(&sample,&ladders).is_ok());
        for altered in [
           sample.replace("\"a\":0","\"a\":1"),
           sample.replace("\"taps\":[0,1]","\"taps\":[0,2]"),
           sample.replace("\"real_optical_photon_measurement\":false","\"real_optical_photon_measurement\":true"),
           sample.replace(SOURCE_BLOB,&"0".repeat(40)),
           sample.replace("\"final_state_hex\":","\"final_state_hex\":\"000000000000000000000\",\"extra\":"),
        ] {assert!(checked_case(&altered,&ladders).is_err());}
    }
}
