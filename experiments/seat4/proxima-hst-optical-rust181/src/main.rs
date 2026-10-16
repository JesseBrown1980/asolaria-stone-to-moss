#![forbid(unsafe_code)]
//! Three actual MAST/STScI calibrated Hubble Proxima image exposures.
//! Source samples are detector-indexed WFC3 pixels, NOT registered sky motion.
//! Seven symbolic rainbow address lanes and 27 sites; no JSON outputs.
//! Clippy statically checks code; host RAM is still used for reading FITS etc.
use asolaria_proxima_ternary::sha256::{digest,hex};
use std::{collections::BTreeMap,env,fs,path::Path};

const ROOTS:[&str;3]=["ic3j01a8q","icdc03lzq","icpc01xwq"];
const PROGRAMS:[u16;3]=[12985,13466,13847];
const LANES:usize=7;
const SITES:usize=27;
const TRITS:usize=LANES*SITES;
const SOURCE_WORDS:usize=TRITS*4;
const PACKED:usize=38;
const FRAME_BYTES:usize=9+2+4+2+2+32+SOURCE_WORDS+PACKED+32;
const HBI_BYTES:usize=8+3*FRAME_BYTES;

fn fielder<'a>(h:&'a BTreeMap<String,String>,key:&str)->Result<&'a str,String>{
    h.get(key).map(String::as_str).ok_or_else(||format!("FITS_MISSING_{key}"))
}
fn integer(h:&BTreeMap<String,String>,key:&str)->Result<i64,String>{
    fielder(h,key)?.parse::<i64>().map_err(|_|format!("FITS_INTEGER_{key}"))
}
/// FITS header boundary and extension length; reject truncated science bytes.
fn hdu(raw:&[u8],pos:usize)->Result<(BTreeMap<String,String>,usize,usize),String>{
    if pos>=raw.len()||pos%2880!=0{return Err("BAD_FITS_HDU_OFFSET".into());}
    let mut cards=0usize;
    let mut header=BTreeMap::<String,String>::new();
    loop{
        let offset=pos.checked_add(cards*80).ok_or("FITS_CARD_OVERFLOW")?;
        let bytes=raw.get(offset..offset+80).ok_or("FITS_TRUNCATED_HEADER")?;
        if !bytes.is_ascii(){return Err("FITS_HEADER_NOT_ASCII".into());}
        cards+=1;
        let key=std::str::from_utf8(&bytes[..8]).map_err(|e|e.to_string())?.trim();
        if key=="END"{break;}
        if bytes[8..10]==*b"= "&& !key.is_empty(){
            let tail=std::str::from_utf8(&bytes[10..]).map_err(|e|e.to_string())?.trim();
            let value=if let Some(rest)=tail.strip_prefix('\''){
                rest.split('\'').next().unwrap_or("").trim()
            }else{tail.split('/').next().unwrap_or("").trim()};
            if let Some(previous)=header.get(key){
                if ["ROOTNAME","PROPOSID","INSTRUME","DETECTOR","FILTER",
                    "DATE-OBS","EXPTIME","EXPSTART","NAXIS","BITPIX","EXTNAME","EXTVER"].contains(&key)
                    && previous!=value{
                    return Err(format!("CONFLICTING_FITS_PROVENANCE:{key}"));
                }
            }else{header.insert(key.to_owned(),value.to_owned());}
        }
        if cards>8000{return Err("FITS_HEADER_EXCEEDS_LIMIT".into());}
    }
    let header_size=(cards*80+2879)/2880*2880;
    let data=pos.checked_add(header_size).ok_or("FITS_HEADER_OVERFLOW")?;
    let naxis=usize::try_from(integer(&header,"NAXIS")?).map_err(|_|"NEGATIVE_NAXIS")?;
    if naxis>8{return Err("UNSUPPORTED_FITS_RANK".into());}
    let mut count=usize::from(naxis!=0);
    for axis in 1..=naxis {
        let dimension=integer(&header,&format!("NAXIS{axis}"))?;
        let side=usize::try_from(dimension).map_err(|_|"NEGATIVE_FITS_AXIS")?;
        count=count.checked_mul(side).ok_or("FITS_AXIS_OVERFLOW")?;
    }
    let bitpix=integer(&header,"BITPIX")?.unsigned_abs();
    let bpp=usize::try_from(bitpix/8).map_err(|_|"FITS_BITPIX_CONVERSION")?;
    if bpp==0{return Err("EMPTY_FITS_BITPIX".into());}
    let pcount=usize::try_from(integer(&header,"PCOUNT").unwrap_or(0))
        .map_err(|_|"NEGATIVE_PCOUNT")?;
    let gcount=usize::try_from(integer(&header,"GCOUNT").unwrap_or(1))
        .map_err(|_|"NEGATIVE_GCOUNT")?;
    let n=count.checked_mul(bpp).and_then(|v|v.checked_add(pcount))
        .and_then(|v|v.checked_mul(gcount)).ok_or("FITS_DATA_OVERFLOW")?;
    let next=data.checked_add((n+2879)/2880*2880).ok_or("FITS_SKIP_OVERFLOW")?;
    if next>raw.len(){return Err("TRUNCATED_FITS_PAYLOAD".into());}
    Ok((header,data,next))
}
fn date_as_number(date:&str)->Result<u32,String>{
    let digits=date.replace('-',"");
    if digits.len()!=8||!digits.bytes().all(|b|b.is_ascii_digit()){
        return Err("MISSING_OR_INVALID_SOURCE_DATE".into());
    }
    digits.parse::<u32>().map_err(|_|"INVALID_DATE_INTEGER".into())
}
fn trits(wordbytes:&[u8;SOURCE_WORDS])->[i8;TRITS]{
    std::array::from_fn(|i|{
        let word=u32::from_be_bytes(wordbytes[i*4..i*4+4].try_into().expect("four bytes"));
        (word%3)as i8-1
    })
}
fn pack(values:&[i8;TRITS])->[u8;PACKED]{
    std::array::from_fn(|index|{
        let mut n=0u16;
        let mut place=1u16;
        for j in 0..5 {
            let slot=index*5+j;
            let digit=if slot<TRITS{(values[slot]+1)as u16}else{1};
            n+=digit*place;place*=3;
        }
        u8::try_from(n).expect("base3 five-digit byte")
    })
}
fn unpack(bytes:&[u8;PACKED])->Result<[i8;TRITS],String>{
    let mut out=[0i8;TRITS];
    for (index,&word) in bytes.iter().enumerate(){
        let mut value=word;
        for digit in 0..5{
            let trit=(value%3)as i8-1;
            value/=3;
            let offset=index*5+digit;
            if offset<TRITS{out[offset]=trit;}
            else if trit!=0{return Err("NONCANONICAL_TERNARY_PADDING".into());}
        }
        if value!=0{return Err("BAD_PACKED_TERNARY_BYTE".into());}
    }
    Ok(out)
}
fn shadow(file_sha:[u8;32],date:u32,words:[u8;SOURCE_WORDS])->[u8;32]{
    let mut block=Vec::with_capacity(4+32+4+SOURCE_WORDS);
    block.extend_from_slice(b"SHV1");
    block.extend_from_slice(&file_sha);
    block.extend_from_slice(&date.to_le_bytes());
    block.extend_from_slice(&words);
    digest(&block)
}
#[derive(Clone,Debug,PartialEq,Eq)]
struct Exposure {
    root:[u8;9],proposal:u16,date:u32,width:u16,height:u16,
    file_sha:[u8;32],words:[u8;SOURCE_WORDS],packed:[u8;PACKED],sh:[u8;32]
}
fn extract(raw:&[u8],root:&str,program:u16)->Result<Exposure,String>{
    let (primary,_,mut next)=hdu(raw,0)?;
    if fielder(&primary,"ROOTNAME")?.to_ascii_lowercase()!=root
        ||integer(&primary,"PROPOSID")?!=i64::from(program)
        ||fielder(&primary,"INSTRUME")?!="WFC3"
        ||fielder(&primary,"DETECTOR")?!="UVIS"
        ||fielder(&primary,"FILTER")?!="F555W"
        ||!fielder(&primary,"TARGNAME")?.starts_with("PROXIMA"){
        return Err("WRONG_SOURCE_HST_IDENTITY_OR_FILTER".into());
    }
    let date=date_as_number(fielder(&primary,"DATE-OBS")?)?;
    if !primary.contains_key("EXPSTART")||!primary.contains_key("EXPTIME"){
        return Err("MISSING_REAL_OBSERVATION_TIMING".into());
    }
    let file_sha=digest(raw);
    for _ in 0..14{
        let (h,data,skip)=hdu(raw,next)?;
        next=skip;
        if h.get("EXTNAME").map(String::as_str)!=Some("SCI")
            ||h.get("EXTVER").map(String::as_str).unwrap_or("1")!="1"{continue;}
        if integer(&h,"NAXIS")?!=2||integer(&h,"BITPIX")?!=-32{
            return Err("NON_CALIBRATED_32BIT_IMAGE".into());
        }
        let width=usize::try_from(integer(&h,"NAXIS1")?)
            .map_err(|_|"INVALID_IMAGE_WIDTH")?;
        let height=usize::try_from(integer(&h,"NAXIS2")?)
            .map_err(|_|"INVALID_IMAGE_HEIGHT")?;
        if width<27||height<27||width>8191||height>8191{
            return Err("INVALID_IMAGE_SHAPE".into());
        }
        let mut words=[0u8;SOURCE_WORDS];
        for lane in 0..LANES {
            for site in 0..SITES{
                let x=((lane+1)*width)/(LANES+1);
                let y=((site+1)*height)/(SITES+1);
                let address=data.checked_add((y*width+x)*4).ok_or("PIXEL_ADDRESS_OVERFLOW")?;
                let word=raw.get(address..address+4).ok_or("PIXEL_TRUNCATED")?;
                let dest=(lane*SITES+site)*4;
                words[dest..dest+4].copy_from_slice(word);
            }
        }
        let packed=pack(&trits(&words));
        let sh=shadow(file_sha,date,words);
        let rootbytes:[u8;9]=root.as_bytes().try_into().map_err(|_|"ROOTNAME_WIDTH")?;
        return Ok(Exposure{root:rootbytes,proposal:program,date,
            width:u16::try_from(width).map_err(|_|"WIDTH_U16")?,
            height:u16::try_from(height).map_err(|_|"HEIGHT_U16")?,
            file_sha,words,packed,sh});
    }
    Err("NO_CALIBRATED_SCI_EXTENSION".into())
}
fn serialize(data:&[Exposure;3])->Vec<u8>{
    let mut out=Vec::with_capacity(HBI_BYTES);
    out.extend_from_slice(b"HBI1\x01\x03\x07\x1b");
    for e in data{
        out.extend_from_slice(&e.root);
        out.extend_from_slice(&e.proposal.to_le_bytes());
        out.extend_from_slice(&e.date.to_le_bytes());
        out.extend_from_slice(&e.width.to_le_bytes());
        out.extend_from_slice(&e.height.to_le_bytes());
        out.extend_from_slice(&e.file_sha);
        out.extend_from_slice(&e.words);
        out.extend_from_slice(&e.packed);
        out.extend_from_slice(&e.sh);
    }
    assert_eq!(out.len(),HBI_BYTES);
    out
}
fn verify(wire:&[u8],expected:&[Exposure;3])->Result<(),String>{
    if wire.len()!=HBI_BYTES||wire.get(..8)!=Some(&b"HBI1\x01\x03\x07\x1b"[..]){
        return Err("HBI_WRONG_HEADER_OR_LENGTH".into());
    }
    let mut previous=0u32;
    for (index,e) in expected.iter().enumerate(){
        let at=&wire[8+index*FRAME_BYTES..8+(index+1)*FRAME_BYTES];
        let root=&at[..9];
        let proposal=u16::from_le_bytes(at[9..11].try_into().map_err(|_|"PROPOSAL_FIELD")?);
        let date=u32::from_le_bytes(at[11..15].try_into().map_err(|_|"DATE_FIELD")?);
        if root!=e.root||proposal!=e.proposal{return Err("SOURCE_ROOT_OR_PROPOSAL_FORGED".into());}
        if date!=e.date||date<=previous{return Err("REPLAYED_OR_FORGED_OBSERVATION_DATE".into());}
        previous=date;
        let width=u16::from_le_bytes(at[15..17].try_into().map_err(|_|"WIDTH_FIELD")?);
        let height=u16::from_le_bytes(at[17..19].try_into().map_err(|_|"HEIGHT_FIELD")?);
        if width!=e.width||height!=e.height{return Err("SOURCE_IMAGE_GEOMETRY_FORGED".into());}
        let src:&[u8]=&at[19..51];
        if src!=e.file_sha{return Err("SOURCE_FITS_SHA_FORGED".into());}
        let sample=&at[51..51+SOURCE_WORDS];
        if sample!=e.words{return Err("PIXEL_SAMPLE_CHANGED".into());}
        let packed:[u8;PACKED]=at[51+SOURCE_WORDS..51+SOURCE_WORDS+PACKED]
            .try_into().map_err(|_|"PACKED_TERNARY_MISSING")?;
        if unpack(&packed)?!=trits(&e.words)||packed!=e.packed{
            return Err("UNSIGNED_NONCANONICAL_TERNARY_SOURCE".into());
        }
        let sh=&at[51+SOURCE_WORDS+PACKED..];
        if sh!=e.sh||e.sh!=shadow(e.file_sha,e.date,e.words){
            return Err("SH_SHADOW_WITNESS_FORGED".into());
        }
    }
    Ok(())
}
fn attacks(original:&[u8],frames:&[Exposure;3])->usize{
    let changed=[
        ("pixel",8+51),("root",8),("date",8+11),("source-sha",8+19),
        ("packed-trit",8+51+SOURCE_WORDS),("SH-shadow",8+51+SOURCE_WORDS+PACKED),
        ("noncanonical-padding",8+51+SOURCE_WORDS+PACKED-1),
        ("truncated",HBI_BYTES-1),("replayed-date",8+FRAME_BYTES+11)
    ];
    for (name,offset) in changed{
        let mut bad=original.to_vec();
        match name{
            "truncated"=>{bad.pop();},
            "replayed-date"=>{bad[offset..offset+4].copy_from_slice(&original[8+11..8+15]);},
            "noncanonical-padding"=>{bad[offset]=bad[offset].wrapping_add(81);},
            _=>bad[offset]^=1
        }
        assert!(verify(&bad,frames).is_err(),"CORRUPTION_TEST_FALSE_PASS:{name}");
    }
    changed.len()
}
fn output(root:&Path,frames:[Exposure;3])->Result<(),String>{
    fs::create_dir_all(root).map_err(|e|e.to_string())?;
    let hbi_name="three-original-proxima-optical-epochs.hbi";
    let hbp_name="three-original-proxima-optical-epochs.hbp";
    let binary=serialize(&frames);
    verify(&binary,&frames)?;
    let rejected=attacks(&binary,&frames);
    fs::write(root.join(hbi_name),&binary).map_err(|e|e.to_string())?;
    let mut rows=vec![
        "HBP1|schema=SEAT4-HST-PROXIMA-THREE-ACTUAL-OPTICAL-IMAGES-R14|field=GF3|trits=-1,0,+1|rust=1.81.0|json=0".to_string(),
        "SOURCE|archive=STSCI_MAST|instrument=WFC3_UVIS|filter=F555W|product=CALIBRATED_INDIVIDUAL_FLC|optical_observations=ACTUAL_THREE_EPOCHS|json=0".to_string(),
        format!("HBI|file={hbi_name}|bytes={}|sha256={}|lanes=7|sites_per_lane=27|total_ternary_sites=567|json=0",
            binary.len(),hex(&digest(&binary))),
        "SH|meaning=SHV1_DOMAIN_SEPARATED_SHA256_SHADOW|context=FITS_SOURCE_SHA_DATE_AND_PIXEL_WORDS|independent_detector_signed=NOT_AVAILABLE|json=0".to_string(),
    ];
    let values:Vec<_>=frames.iter().map(|f|trits(&f.words)).collect();
    for (i,f) in frames.iter().enumerate(){
        let name=std::str::from_utf8(&f.root).map_err(|e|e.to_string())?;
        rows.push(format!("FRAME|index={i}|rootname={name}|proposal_id={}|date_yyyymmdd={}|science_width={}|science_height={}|bitpix=-32|original_full_fits_sha256={}|sample_words_sha256={}|SH_shadow_sha256={}|trits_per_epoch=189|registered_sky_motion=UNTESTED|json=0",
          f.proposal,f.date,f.width,f.height,hex(&f.file_sha),hex(&digest(&f.words)),hex(&f.sh)));
    }
    for i in 0..2{
        let count=values[i].iter().zip(values[i+1].iter()).filter(|(a,b)|a!=b).count();
        rows.push(format!("DIFFERENCE|from={i}|to={}|changed_ternary_detector_samples={count}|available_source_sites=189|motion_interpretation=NOT_SKY_REGISTERED|json=0",i+1));
    }
    rows.push(format!("FALSIFY|applied_corruptions={rejected}|rejected_corruptions={rejected}|source_authentication=MAST_ARCHIVE_PROVENANCE_NOT_DETECTOR_SIGNATURE|json=0"));
    rows.push("BOUNDARY|three_real_optical_images=TRUE|three_actual_detector_epochs=TRUE|seven_lanes=SYMBOLIC_ADDRESS|FITS_WCS_REGISTRATION=NOT_COMPLETED|recovered_3D_particle_motion=NOT_ESTABLISHED|photon_memory_retention=NOT_MEASURED|Clippy_is_not_zero_RAM=TRUE|json=0".to_string());
    let text=rows.join("\n")+"\n";
    fs::write(root.join(hbp_name),text.as_bytes()).map_err(|e|e.to_string())?;
    for (name,bytes) in [(hbi_name,binary.as_slice()),(hbp_name,text.as_bytes())]{
        fs::write(root.join(format!("{name}.sha256")),
          format!("{}  {name}\n",hex(&digest(bytes)))).map_err(|e|e.to_string())?;
    }
    println!("SEAT4_R14_THREE_REAL_HST_OPTICAL_FRAMES_PASS images=3 trits=567 hostile_corruptions_rejected={rejected}");
    Ok(())
}
fn main()->Result<(),Box<dyn std::error::Error>>{
    let args:Vec<String>=env::args().collect();
    if args.len()!=5{return Err("usage: seat4-proxima-hst-optical IMG1 IMG2 IMG3 OUTPUT_DIR".into());}
    let images:Vec<_>=ROOTS.iter().enumerate().map(|(i,root)|{
        let raw=fs::read(&args[i+1]).map_err(|e|e.to_string())?;
        extract(&raw,root,PROGRAMS[i])
    }).collect::<Result<Vec<_>,String>>()?;
    let frames:[Exposure;3]=images.try_into().map_err(|_|"NEED_THREE_REAL_IMAGES")?;
    if !(frames[0].date<frames[1].date&&frames[1].date<frames[2].date){
        return Err("EXPOSURE_DATES_NOT_STRICTLY_INCREASING".into());
    }
    output(Path::new(&args[4]),frames)?;
    Ok(())
}
#[cfg(test)]
mod tests{
 use super::*;
 #[test] fn every_balanced_value_and_noncanonical_padding(){
    let values:[i8;TRITS]=std::array::from_fn(|i|(i%3)as i8-1);
    let binary=pack(&values);
    assert_eq!(unpack(&binary),Ok(values));
    let mut bad=binary;
    bad[37]=bad[37].wrapping_add(81);
    assert!(unpack(&bad).is_err());
 }
 #[test] fn signed_shadow_is_domain_separated(){
    let words=[42u8;SOURCE_WORDS];
    let src=digest(b"ORIGINAL_HST_BYTES");
    assert_ne!(shadow(src,20121001,words),src);
    assert_ne!(shadow(src,20121001,words),shadow(src,20140301,words));
 }
}
