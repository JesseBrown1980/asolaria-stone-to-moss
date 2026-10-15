#![forbid(unsafe_code)]
//! Reproducible hosted-CPU run. Source physics measurements are not fabricated.
use asolaria_proxima_ternary::{B_PERIOD,D_PERIOD,decimal_pow3,phase_3pow,report};
use std::{env,fs,io,path::Path,time::Instant};
fn main()->io::Result<()>{
    let started=Instant::now();
    let destination=env::args().nth(1).unwrap_or_else(||"out".to_string());
    let dir=Path::new(&destination);
    fs::create_dir_all(dir)?;
    let hbp=report();
    assert_eq!(hbp.lines().filter(|x|x.starts_with("LEVEL|")).count(),7);
    assert!(!hbp.contains("BobbyFischer=FAIL"));
    fs::write(dir.join("ASOLARIA-PROXIMA-RUST181.hbp"),hbp)?;
    let mut csv=String::from("exponent,years_exact,b_phase_numerator,b_phase_denominator,d_phase_numerator,d_phase_denominator,field,method,observed_photons\n");
    for exponent in 1..=200{
        let years=decimal_pow3(exponent);
        let b=phase_3pow(exponent,B_PERIOD);
        let d=phase_3pow(exponent,D_PERIOD);
        use std::fmt::Write as _;
        writeln!(csv,"{exponent},{years},{},{},{},{},GF3,EXACT_MODULAR_FAST_FORWARD,false",b.n,b.d,d.n,d.d).expect("write string");
    }
    fs::write(dir.join("EPOCHS-RUST181.csv"),csv)?;
    fs::write(dir.join("RUNTIME.hbp"),format!(
        "RUNTIME|hosted_os={}|arch={}|elapsed_ns={}|physical_device=HOSTED_CPU|distinct_host_custody=UNATTESTED|instrumented_optics=NONE|json=0\n",
        env::consts::OS,env::consts::ARCH,started.elapsed().as_nanos()))?;
    println!("ASOLARIA_RUST181_TERNARY_PASS levels=7 epochs=200 actual_cpu_instructions=TRUE");
    Ok(())
}
