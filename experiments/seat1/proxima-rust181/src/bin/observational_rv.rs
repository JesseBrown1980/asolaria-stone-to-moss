#![forbid(unsafe_code)]
//! Actual 2025 published Proxima RV readback: integer fixed-point only.
//! Real source data: CDS J/A+A/700/A11/spec.dat and /photo.dat.
//! This program does NOT convert a residual improvement into a planet detection.
use asolaria_proxima_ternary::sha256::{digest,hex};
use std::{collections::BTreeMap, env, fmt::Write as _, fs, path::Path};

const RV_RECORDS:usize=722;
const PHOTO_RECORDS:usize=2212;
const FEATURES:usize=16;
const SIN27:[i64;27]=[
    0,231,449,643,802,918,985,998,958,866,727,550,342,116,
    -116,-342,-550,-727,-866,-958,-998,-985,-918,-802,-643,-449,-231
];
const COS27:[i64;27]=[
    1000,973,894,766,597,396,174,-58,-287,-500,-686,-835,-940,-993,
    -993,-940,-835,-686,-500,-287,-58,174,396,597,766,894,973
];
const KNOWN_B_PERIOD:u64=1_118_465; // 1e-5 day units
const KNOWN_D_PERIOD:u64=512_338;
const STELLAR_PROXY_PERIOD:u64=8_300_000; // 83 days, simplistic fixed stellar activity control
const EXPLORATORY_PERIODS:[u64;6]=[
    900_000,2_700_000,8_100_000,24_300_000,72_900_000,190_000_000
];

#[derive(Clone,Debug)]
struct Rv {
    mjd_milli:i64,
    rv_mm:i64,
    err_mm:i64,
    inst:usize,
    fwhm_mm:Option<i64>,
    crx_cent:Option<i64>,
    train:bool,
}
fn decimal_scaled(raw:&str, decimals:usize)->Result<i64,String>{
    let text=raw.trim();
    if text.is_empty(){return Err("missing decimal".into());}
    let (negative,unsigned)=match text.strip_prefix('-'){Some(s)=>(true,s),None=>(false,text)};
    let (major,minor)=unsigned.split_once('.').unwrap_or((unsigned,""));
    if minor.len()>decimals || !minor.bytes().all(|b|b.is_ascii_digit()){
        return Err(format!("invalid fixed decimal: {raw:?}"));
    }
    let base=10i64.pow(decimals as u32);
    let int:i64=major.trim().parse().map_err(|_|format!("bad integer {raw:?}"))?;
    let fract:i64=if minor.is_empty(){0}else{minor.parse::<i64>().map_err(|_|"bad fractional")?*
        10i64.pow((decimals-minor.len())as u32)};
    let total=int.checked_mul(base).and_then(|v|v.checked_add(fract))
        .ok_or("decimal overflow")?;
    Ok(if negative{-total}else{total})
}
fn col(line:&[u8],start:usize,end:usize)->Result<&str,String>{
    std::str::from_utf8(line.get(start..end).ok_or("short record")?)
        .map_err(|_|"non ASCII".to_string())
}
fn read_source(bytes:&[u8])->Result<Vec<Rv>,String>{
    let lines:Vec<_>=bytes.split(|&v|v==b'\n').filter(|l|!l.is_empty()).collect();
    if lines.len()!=RV_RECORDS{return Err(format!("source rows {}, expected {}",lines.len(),RV_RECORDS));}
    let mut source=Vec::with_capacity(lines.len());
    for (index,line) in lines.into_iter().enumerate(){
        if line.len()!=120{return Err(format!("line {index}: width {}",line.len()));}
        let t=decimal_scaled(col(line,1,10)?,3)?;
        let rv=decimal_scaled(col(line,16,21)?,2)?*10; // centi m/s -> mm/s
        let err=decimal_scaled(col(line,28,32)?,2)?*10;
        if err<=0{return Err(format!("nonpositive source uncertainty at {index}"));}
        let fw=decimal_scaled(col(line,35,43)?,2)?;
        let cr=decimal_scaled(col(line,57,65)?,2)?;
        let inst=col(line,119,120)?.parse::<usize>()
            .map_err(|_|format!("bad instrument in row {index}"))?;
        if inst>5{return Err("instrument outside catalog".into());}
        source.push(Rv{
            mjd_milli:t,rv_mm:rv,err_mm:err,inst,
            fwhm_mm:if fw==-999_900{None}else{Some(fw*10)},
            crx_cent:if cr==-999_900{None}else{Some(cr)},train:false
        });
    }
    source.sort_by_key(|r|(r.inst,r.mjd_milli));
    let mut start=0;
    while start<source.len(){
        let inst=source[start].inst;
        let mut end=start;
        while end<source.len()&&source[end].inst==inst{end+=1;}
        let count=end-start;
        // For sparsely observed instruments, do not pretend a holdout exists.
        let cutoff=if count>=10{start+count*7/10}else{end};
        for record in &mut source[start..cutoff]{record.train=true;}
        start=end;
    }
    Ok(source)
}
fn scaled_feature(value:i64,denom:i64)->i64{
    (value*1000/denom).clamp(-1000,1000)
}
fn harmonic(time_milliday:i64,period_1e5:u64)->(i64,i64){
    let t=(time_milliday as i128*100).rem_euclid(i128::from(period_1e5));
    let slot=(t*27/i128::from(period_1e5))as usize;
    (SIN27[slot],COS27[slot])
}
fn vector(r:&Rv,period:Option<u64>)->[i64;FEATURES]{
    let mut x=[0i64;FEATURES];
    x[r.inst]=1000;
    x[6]=r.fwhm_mm.map(|v|scaled_feature(v,2000)).unwrap_or(0);
    x[7]=r.crx_cent.map(|v|scaled_feature(v,2000)).unwrap_or(0);
    (x[8],x[9])=harmonic(r.mjd_milli,STELLAR_PROXY_PERIOD);
    (x[10],x[11])=harmonic(r.mjd_milli,KNOWN_B_PERIOD);
    (x[12],x[13])=harmonic(r.mjd_milli,KNOWN_D_PERIOD);
    if let Some(p)=period{(x[14],x[15])=harmonic(r.mjd_milli,p);}
    x
}
fn source_weight(r:&Rv)->i128{
    let err=r.err_mm.max(100);
    (100_000_000i128/i128::from(err*err)).max(1)
}
fn predict(coeff:&[i64;FEATURES],x:&[i64;FEATURES],active:usize)->i64{
    let sum=(0..active).map(|i|i128::from(coeff[i])*i128::from(x[i])).sum::<i128>();
    (sum/1000)as i64
}
fn fit(records:&[Rv],active:usize,period:Option<u64>)->[i64;FEATURES]{
    let mut coeff=[0i64;FEATURES];
    let train:Vec<_>=records.iter().filter(|r|r.train)
        .map(|r|(r,vector(r,period),source_weight(r))).collect();
    let weights=train.iter().map(|(_,_,w)|*w).sum::<i128>();
    assert!(weights>0);
    for _ in 0..40{
        let mut max_delta=0i64;
        for i in 0..active{
            let mut n=0i128;
            let mut d=0i128;
            for (r,x,w) in &train{
                let residual=r.rv_mm-predict(&coeff,x,active);
                n+=w*i128::from(x[i])*i128::from(residual);
                d+=w*i128::from(x[i])*i128::from(x[i]);
            }
            if i>=6{d+=weights*1000;} // modest regularization for correlations/activity
            if d==0{continue;}
            let delta=(n*1000/d).clamp(-5000,5000)as i64;
            coeff[i]=(coeff[i]+delta).clamp(-50_000,50_000);
            max_delta=max_delta.max(delta.abs());
        }
        if max_delta<=1{break;}
    }
    coeff
}
fn weighted_error(rows:&[&Rv],c:&[i64;FEATURES],active:usize,p:Option<u64>)->u64{
    let mut sum=0u128;
    let mut weights=0u128;
    for r in rows{
        let w=source_weight(r)as u128;
        let delta=i128::from(r.rv_mm-predict(c,&vector(r,p),active)).unsigned_abs();
        sum+=w*delta*delta;weights+=w;
    }
    if weights==0{return 0;}
    isqrt(sum/weights) as u64
}
fn isqrt(num:u128)->u128{
    let mut lo=0u128;let mut hi=1u128<<64;
    while lo+1<hi{
        let mid=(lo+hi)/2;
        if mid<=num/mid{lo=mid;}else{hi=mid;}
    }lo
}
fn model_hbp(rows:&[Rv],image:&str)->String{
    let train:Vec<_>=rows.iter().filter(|r|r.train).collect();
    let test:Vec<_>=rows.iter().filter(|r|!r.train).collect();
    let c0=fit(rows,10,None);
    let c1=fit(rows,14,None);
    let (choice,choice_train)=EXPLORATORY_PERIODS.iter()
        .map(|&period|{
            let model=fit(rows,16,Some(period));
            (period,weighted_error(&train,&model,16,Some(period)))
        })
        .min_by_key(|(period,score)|(*score,*period)).expect("trial grid");
    let c2=fit(rows,16,Some(choice));
    let (rmse0,rmse1,rmse2)=(
      weighted_error(&test,&c0,10,None),
      weighted_error(&test,&c1,14,None),
      weighted_error(&test,&c2,16,Some(choice))
    );
    let first=rows.iter().map(|r|r.mjd_milli).min().unwrap_or(0);
    let last=rows.iter().map(|r|r.mjd_milli).max().unwrap_or(0);
    let mut lines=vec![
      "HBP1|schema=ASOLARIA-ACTUAL-PROXIMA-RV-NINE-WINDOW-V2|format=HBP|trits=-1,0,+1|json=0".to_string(),
      "SOURCE|catalog=CDS J/A+A/700/A11|file=spec.dat|original_source_data=YES|json=0".to_string(),
      format!("SUMMARY|source_measurements={}|source_photo_rows=2212|train_rows={}|heldout_rows={}|first_bjd_minus_2450000_milliday={}|last_bjd_minus_2450000_milliday={}|exploratory_trials=6|heldout_window_count=9|json=0",
        rows.len(),train.len(),test.len(),first,last),
      format!("SCORES|null_wrmse_mm_s={}|known_bd_wrmse_mm_s={}|extra_wrmse_mm_s={}|train_selected_extra_period_1e5_days={}|train_selected_wrmse_mm_s={}|json=0",
        rmse0,rmse1,rmse2,choice,choice_train),
      format!("IMAGE|source_hubble_status={image}|nine_image_epochs=UNAVAILABLE|json=0"),
      "METHOD|model=integer-only_27-sector_phase|fit=instrument_offset_and_activity_proxies|holdout=70pct_training_per_instrument|json=0".to_string(),
      "BOUNDARY|brown_edens_i=UNDETECTED_SIMULATION_ALIAS|new_planet_detected=FALSE|scan_significance_corrected=FALSE|json=0".to_string()
    ];
    let mut by_instrument=BTreeMap::new();
    for row in rows {
        let entry=by_instrument.entry(row.inst).or_insert((0usize,0usize));
        if row.train{entry.0+=1;}else{entry.1+=1;}
    }
    for (id,(tr,te)) in by_instrument {
        let subset:Vec<_>=test.iter().copied().filter(|row|row.inst==id).collect();
        let a=weighted_error(&subset,&c0,10,None);
        let b=weighted_error(&subset,&c1,14,None);
        let c=weighted_error(&subset,&c2,16,Some(choice));
        lines.push(format!("INSTRUMENT|id={id}|train={tr}|test={te}|n={}|baseline_wrmse_mm_s={a}|known_wrmse_mm_s={b}|extra_wrmse_mm_s={c}|json=0",subset.len()));
    }
    let mut checkpoints=test.clone();
    checkpoints.sort_by_key(|r|r.mjd_milli);
    for i in 0..9 {
        let low=checkpoints.len()*i/9;
        let high=checkpoints.len()*(i+1)/9;
        let group=&checkpoints[low..high];
        assert!(!group.is_empty(),"expected nonempty chronological window");
        let median=group[group.len()/2].mjd_milli;
        let n0=weighted_error(group,&c0,10,None);
        let n1=weighted_error(group,&c1,14,None);
        let n2=weighted_error(group,&c2,16,Some(choice));
        let (sinb,cosb)=harmonic(median,KNOWN_B_PERIOD);
        lines.push(format!("WINDOW|index={}|count={}|median_bjd_minus_2450000_milliday={median}|baseline_wrmse_mm_s={n0}|known_bd_wrmse_mm_s={n1}|exploratory_wrmse_mm_s={n2}|phase_b_sin1000={sinb}|phase_b_cos1000={cosb}|json=0",i+1,group.len()));
    }
    lines.join("\n")+"\n"
}
fn main()->Result<(),String>{
    let dir=env::args().nth(1).unwrap_or_else(||"real_observations/output".to_string());
    let d=Path::new(&dir);
    let spec=fs::read(d.join("spec.dat")).map_err(|e|e.to_string())?;
    let photo=fs::read(d.join("photo.dat")).map_err(|e|e.to_string())?;
    let photo_rows=photo.split(|&b|b==b'\n').filter(|x|!x.is_empty()).count();
    if photo_rows!=PHOTO_RECORDS{return Err(format!("photometry row count: {photo_rows}"));}
    let rows=read_source(&spec)?;
    let image=match fs::read_to_string(d.join("ORIGINAL-SOURCE-MANIFEST.hbp")){
      Ok(manifest)=>if manifest.lines().any(|line|line.starts_with("IMAGE|available=true|")){
        "HUBBLE_PUBLIC_RENDERED_IMAGE_AVAILABLE"
      }else{"HUBBLE_BINARY_SOURCE_HELD"},
      Err(_)=>"HUBBLE_NOT_FETCHED"
    };
    let result=model_hbp(&rows,image);
    fs::write(d.join("NINE-REAL-OBSERVATION-WINDOWS.hbp"),&result)
        .map_err(|e|e.to_string())?;
    println!("REAL_SOURCE_RV_722_SPEC_SHA256 {}",hex(&digest(&spec)));
    println!("REAL_SOURCE_PHOTO_2212_SHA256 {}",hex(&digest(&photo)));
    println!("REAL_SOURCE_RESULTS_SHA256 {}",hex(&digest(result.as_bytes())));
    for line in result.lines().filter(|l|
        l.starts_with("SUMMARY|")||l.starts_with("SCORES|"))
    {println!("{}",line.trim());}
    println!("ACTUAL_PROXIMA_RV_NINE_CHECKPOINTS_ANALYSIS_PASS");
    Ok(())
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test] fn fixed_point_decimal_exact(){
        assert_eq!(decimal_scaled("-0.55",2),Ok(-55));
        assert_eq!(decimal_scaled("8595.123",3),Ok(8_595_123));
        assert_eq!(decimal_scaled("3.1",2),Ok(310));
    }
    #[test] fn period_and_trit_sector_wrap(){
        assert_eq!(harmonic(0,KNOWN_B_PERIOD),(0,1000));
        assert_eq!(harmonic((KNOWN_B_PERIOD/5)as i64,KNOWN_B_PERIOD),(0,1000));
        assert_eq!(EXPLORATORY_PERIODS.len(),6);
    }
    #[test] fn integer_sqrt_reference(){
        for n in 0..10000u128{
            let x=isqrt(n);
            assert!(x*x<=n && (x+1)*(x+1)>n);
        }
    }
}
