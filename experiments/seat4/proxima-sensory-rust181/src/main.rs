#![forbid(unsafe_code)]
//! Proxima source-bound sensory witness: balanced trinary, seven address lanes.
//! Source is catalog RV rows, NOT measured rainbow spectra or 3 image epochs.
//! Clippy is a linter. Stack arrays avoid *per-frame heap allocation* in the
//! trit/pack functions; source I/O, SHA and receipts still allocate host RAM.
use asolaria_proxima_ternary::sha256::{digest,hex};
use std::{env,fs,path::Path};
const SOURCE_SHA:&str="027cff5c10b541608b727abada2af531037223edec3bb9112fcbb45fc333e474";
const RAW:usize=120;
const LANES:usize=7;
const SITES:usize=27;
const TRITS:usize=LANES*SITES;
const PACKED:usize=38;
const FRAME_SIZE:usize=8+RAW+PACKED+32+32;
const BINARY_SIZE:usize=8+3*FRAME_SIZE;
#[derive(Clone,Debug,PartialEq,Eq)]
struct Frame {
    tick:u64,
    source:[u8;RAW],
    packed:[u8;PACKED],
    source_sha:[u8;32],
    shadow_sha:[u8;32]
}
fn parse_timestamp(row:&[u8;RAW])->Result<u64,String>{
    let text=std::str::from_utf8(&row[1..10]).map_err(|e|e.to_string())?.trim();
    let (whole,fraction)=text.split_once('.').ok_or("MISSING_DAY_DECIMAL")?;
    if fraction.is_empty()||fraction.len()>8||!fraction.bytes().all(|b|b.is_ascii_digit()){
        return Err("INVALID_MILLIDAY_PRECISION".into());
    }
    let days=whole.parse::<u64>().map_err(|_|"INVALID_DAY")?;
    let numerator=fraction.parse::<u64>().map_err(|_|"INVALID_FRACTION")?;
    let denominator=10u64.pow(fraction.len()as u32);
    let millis=numerator*1000/denominator;
    let remainder=numerator*1000%denominator;
    let rounded=millis+u64::from(remainder*2>denominator ||
        (remainder*2==denominator && millis%2!=0));
    days.checked_mul(1000).and_then(|x|x.checked_add(rounded))
        .ok_or_else(||"TIME_OVERFLOW".to_string())
}
fn pick(source:&[u8])->Result<[[u8;RAW];3],String>{
    if hex(&digest(source))!=SOURCE_SHA{return Err("SOURCE_ROOT_SHA_MISMATCH".into());}
    let mut rows:Vec<(u64,[u8;RAW])>=Vec::new();
    for part in source.split(|&b|b==b'\n').filter(|x|!x.is_empty()){
        if part.len()!=RAW{return Err("SOURCE_BAD_ROW_WIDTH".into());}
        if part[119]!=b'0'{continue;}
        let row:[u8;RAW]=part.try_into().map_err(|_|"INVALID_ROW_ARRAY")?;
        rows.push((parse_timestamp(&row)?,row));
    }
    rows.sort_by_key(|(time,row)|(*time,*row));
    let mut selected=[[0u8;RAW];3];let mut count=0;
    let mut previous=None;
    for (time,row) in rows{
        if previous==Some(time){continue;}
        if count>=3{break;}
        selected[count]=row;count+=1;previous=Some(time);
    }
    if count!=3{return Err("FEWER_THAN_THREE_EPOCHS".into());}
    Ok(selected)
}
/// Pure stack-only per-record balanced-trinary encoder. Seven lanes are
/// symbolic *address indices*, NOT seven calibrated optical wavelength bands.
fn trits(row:&[u8;RAW])->[i8;TRITS]{
    std::array::from_fn(|index|((row[index%RAW]%3)as i8)-1)
}
fn pack(values:&[i8;TRITS])->[u8;PACKED]{
    std::array::from_fn(|group|{
        let mut pow=1u16;let mut value=0u16;
        for j in 0..5{
            let index=group*5+j;
            let digit=if index<TRITS{(values[index]+1)as u16}else{1};
            assert!(digit<=2);
            value+=digit*pow;pow*=3;
        }
        u8::try_from(value).expect("5 ternary digits fit into u8")
    })
}
fn unpack(bytes:&[u8;PACKED])->Result<[i8;TRITS],String>{
    let mut out=[0i8;TRITS];
    for (group,&byte) in bytes.iter().enumerate(){
        let mut n=byte;
        for j in 0..5{
            let digit=n%3;n/=3;
            let index=group*5+j;
            if index<TRITS{out[index]=digit as i8-1;}
            else if digit!=1{return Err("NONCANONICAL_TERNARY_PADDING".into());}
        }
        if n!=0{return Err("NONCANONICAL_PACKED_TRITS".into());}
    }
    Ok(out)
}
fn shadow(source_sha:[u8;32],packed:[u8;PACKED])->[u8;32]{
    let mut bytes=[0u8;4+32+PACKED];
    bytes[..4].copy_from_slice(b"SHV1");
    bytes[4..36].copy_from_slice(&source_sha);
    bytes[36..].copy_from_slice(&packed);
    digest(&bytes)
}
fn frame(row:[u8;RAW])->Result<Frame,String>{
    let packed=pack(&trits(&row));
    let source_sha=digest(&row);
    Ok(Frame{tick:parse_timestamp(&row)?,source:row,
        packed,source_sha,shadow_sha:shadow(source_sha,packed)})
}
fn serialize(frames:&[Frame;3])->Vec<u8>{
    let mut out=Vec::with_capacity(BINARY_SIZE);
    out.extend_from_slice(b"HBI1");
    out.extend_from_slice(&[1,3,LANES as u8,SITES as u8]);
    for f in frames{
        out.extend_from_slice(&f.tick.to_le_bytes());
        out.extend_from_slice(&f.source);
        out.extend_from_slice(&f.packed);
        out.extend_from_slice(&f.source_sha);
        out.extend_from_slice(&f.shadow_sha);
    }
    assert_eq!(out.len(),BINARY_SIZE);
    out
}
fn audit(binary:&[u8],expected:&[[u8;RAW];3])->Result<[Frame;3],String>{
    if binary.len()!=BINARY_SIZE{return Err("HBI_WRONG_LENGTH".into());}
    if &binary[..8]!=b"HBI1\x01\x03\x07\x1b"{return Err("HBI_INVALID_MAGIC_OR_LANES".into());}
    let mut out=Vec::new();
    let mut last=None;
    for (index,row) in expected.iter().enumerate(){
        let offset=8+index*FRAME_SIZE;
        let at=&binary[offset..offset+FRAME_SIZE];
        let tick=u64::from_le_bytes(at[..8].try_into().map_err(|_|"TIME_SLICE")?);
        let bytes:[u8;RAW]=at[8..8+RAW].try_into().map_err(|_|"SOURCE_SLICE")?;
        if bytes!=*row{return Err("SOURCE_ROW_MISMATCH".into());}
        if tick!=parse_timestamp(&bytes)?{return Err("SENSOR_TIMESTAMP_FORGED".into());}
        if last.is_some_and(|prev|tick<=prev){return Err("REPLAY_OR_NON_MONOTONIC_TIME".into());}
        let start=8+RAW;
        let packed:[u8;PACKED]=at[start..start+PACKED]
            .try_into().map_err(|_|"PACKED_SLICE")?;
        let source_sha:[u8;32]=at[start+PACKED..start+PACKED+32]
            .try_into().map_err(|_|"SHA_SLICE")?;
        let shadow_sha:[u8;32]=at[start+PACKED+32..].try_into().map_err(|_|"SH_SLICE")?;
        if source_sha!=digest(&bytes){return Err("SOURCE_FRAME_SHA_FORGED".into());}
        if shadow_sha!=shadow(source_sha,packed){return Err("SHADOW_SHA_FORGED".into());}
        if unpack(&packed)?!=trits(&bytes){return Err("TERNARY_SOURCE_MISMATCH".into());}
        out.push(Frame{tick,source:bytes,packed,source_sha,shadow_sha});
        last=Some(tick);
    }
    out.try_into().map_err(|_|"FRAME_COUNT".into())
}
fn attacks(binary:&[u8],rows:&[[u8;RAW];3])->usize{
    let changes=[
        ("packed-trit",8+8+RAW),
        ("source",8+8+9),
        ("SH-shadow",8+8+RAW+PACKED+32),
        ("timestamp",8),
        ("replay-timestamp",8+FRAME_SIZE),
        ("truncation",BINARY_SIZE-1),
        ("padding",8+8+RAW+PACKED-1)
    ];
    for (label,offset) in changes{
        let mut attack=binary.to_vec();
        match label{
            "replay-timestamp"=>attack[offset..offset+8].copy_from_slice(&binary[8..16]),
            "truncation"=>{attack.pop();},
            "padding"=>attack[offset]=attack[offset].wrapping_add(81),
            _=>attack[offset]^=1
        }
        assert!(audit(&attack,rows).is_err(),"ATTACK_WAS_ACCEPTED:{label}");
    }
    changes.len()
}
fn main()->Result<(),Box<dyn std::error::Error>>{
    let args:Vec<String>=env::args().collect();
    if args.len()!=3{return Err("usage: seat4-proxima-sensory ORIGINAL_SPEC.DAT OUT_DIR".into());}
    let input=fs::read(&args[1])?;
    let rows=pick(&input)?;
    let frames=[frame(rows[0])?,frame(rows[1])?,frame(rows[2])?];
    if !(frames[0].tick<frames[1].tick&&frames[1].tick<frames[2].tick){
        return Err("DUPLICATE_SOURCE_EPOCHS".into());
    }
    let binary=serialize(&frames);
    let replay=audit(&binary,&rows)?;
    assert_eq!(replay,frames);
    let rejected=attacks(&binary,&rows);
    let mut changed=[0usize;2];
    for index in 0..2{
        let left=unpack(&frames[index].packed)?;
        let right=unpack(&frames[index+1].packed)?;
        changed[index]=left.iter().zip(right.iter()).filter(|(a,b)|a!=b).count();
        assert!((1..=TRITS).contains(&changed[index]));
    }
    let out=Path::new(&args[2]);fs::create_dir_all(out)?;
    let hbi_name="sensory-three-epochs.hbi";
    let hbp_name="sensory-three-epochs.hbp";
    fs::write(out.join(hbi_name),&binary)?;
    let mut lines=vec![
        "HBP1|schema=ASOLARIA-SEAT4-PROXIMA-SENSORY-R13|format=HBP|field=GF3|trits=-1,0,+1|rust=1.81.0|json=0".to_string(),
        format!("SOURCE|catalog=CDS_JA+A700A11_spec.dat|original_722_rows_sha256={SOURCE_SHA}|source_kind=PUBLISHED_RV|real_photon_detector=FALSE|json=0"),
        format!("HBI|magic=HBI1|size_bytes={}|frames=3|rainbow_lanes=7|sites_per_lane=27|trits_per_frame=189|packing=5_BALANCED_TRITS_PER_BYTE|sha256={}|json=0",binary.len(),hex(&digest(&binary))),
        "SH|meaning=SHADOW_SHA256_WITNESS_NOT_PHYSICAL_PHOTON_MEMORY|domain=SHV1|source_bound=TRUE|json=0".to_string()
    ];
    for (index,f) in frames.iter().enumerate(){
        lines.push(format!("FRAME|index={index}|time_BJD_minus2450000_milliday={}|source_sha256={}|SH_shadow_sha256={}|trits=189|original_source_bytes=120|seven_lanes=SYMBOLIC_ADDRESS_NOT_SPECTROMETER|json=0",
           f.tick,hex(&f.source_sha),hex(&f.shadow_sha)));
    }
    for (index,&count) in changed.iter().enumerate(){
        lines.push(format!("MOTION|from={index}|to={}|changed_trits={count}|sites=189|delta_milliday={}|motion_claim=SOURCE_RECORD_DIFFERENCE_NOT_PHYSICAL_PROPER_MOTION|json=0",index+1,frames[index+1].tick-frames[index].tick));
    }
    lines.push(format!("FALSIFY|applied_attacks={rejected}|rejected={rejected}|invalid_photonic_claims=HELD|json=0"));
    lines.push("BOUNDARY|physical_CPU_execution=HOSTED|Clippy=STATIC_LINTER|stack_only_hot_path=SOURCE_TRANSFORM|RAM_FREE_CLAIM=FALSE|FITS_IMAGE_EPOCHS=NOT_PRESENT|novel_exoplanet=NOT_DETECTED|json=0".to_string());
    let report=lines.join("\n")+"\n";
    fs::write(out.join(hbp_name),report.as_bytes())?;
    for (name,bytes) in [(hbi_name,binary.as_slice()),(hbp_name,report.as_bytes())]{
        fs::write(out.join(format!("{name}.sha256")),
          format!("{}  {name}\n",hex(&digest(bytes))))?;
    }
    println!("SEAT4_R13_PROXIMA_SENSORY_PASS three_real_RV_epochs=3 balanced_trits=567 attacks_rejected={rejected}");
    Ok(())
}
#[cfg(test)]
mod tests{
 use super::*;
 fn test_rows()->[[u8;RAW];3]{
  std::array::from_fn(|i|{
    let mut row=[b'0';RAW];
    let times:[&[u8;9];3]=[b"8595.123 ",b"8595.124 ",b"8595.125 "];
    row[1..10].copy_from_slice(times[i]);
    row[119]=b'0';
    row[20]=(i as u8)+b'1';
    row
  })
 }
 #[test]
 fn all_three_trit_values_and_pack_unpack_round_trip(){
  let mut row=[0u8;RAW];
  for (i,byte) in row.iter_mut().enumerate(){*byte=(i%3)as u8;}
  let data=trits(&row);
  assert!(data.contains(&-1)&&data.contains(&0)&&data.contains(&1));
  assert_eq!(unpack(&pack(&data)),Ok(data));
 }
 #[test]
 fn shadow_digest_is_domain_separated(){
  let row=[b'X';RAW];
  let f=frame(row);
  assert!(f.is_err()); // source timestamp must be a real date
  let data=pack(&trits(&row));
  let h=digest(&row);
  assert_ne!(shadow(h,data),h);
 }
 #[test]
 fn original_three_epoch_hbi_replay_and_attacks(){
  let rows=test_rows();
  let frames=[frame(rows[0]).unwrap(),frame(rows[1]).unwrap(),frame(rows[2]).unwrap()];
  let wire=serialize(&frames);
  assert_eq!(wire.len(),BINARY_SIZE);
  assert_eq!(audit(&wire,&rows),Ok(frames));
  assert_eq!(attacks(&wire,&rows),7);
 }
}
