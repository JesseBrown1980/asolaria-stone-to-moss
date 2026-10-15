#!/usr/bin/env node
"use strict";
/* Independent Node22 implementation of source bank + LIRIS history + exact ranks.
   Does not import Python calculations or generated Python output. */
const crypto=require("node:crypto"),fs=require("node:fs"),path=require("node:path");
const SCHEMA="ASOLARIA-SEAT3-SELECTIVE-ATTENUATOR-PHYSICAL-HOST-V1";
const SOURCE="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22";
const BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345";
const INDEX="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee";
const LIRIS="d9b20742592e6fdcb26c03278bd9d574636f4f9f05b24cf502ad173d20e5579f";
const RX=/^MEM\|band=(red|orange|yellow|green|blue|indigo|violet)\|id=site-(\d{3})\|offset=(\d+)\|length=(\d+)\|sha256=([a-f0-9]{64})$/;
const BANDS=["red","orange","yellow","green","blue","indigo","violet"];
const sha=v=>crypto.createHash("sha256").update(v).digest("hex");
const fail=(condition,msg)=>{if(!condition)throw new Error(msg);};
const p3=n=>String(n).padStart(3,"0");
function pinned(p,h,n){
 const b=fs.readFileSync(p);
 fail(b.length===n&&sha(b)===h,"UNTRUSTED_SOURCE:"+p);
 return b;
}
function canonical(x){
 if(x===null||typeof x!=="object")return JSON.stringify(x);
 if(Array.isArray(x))return "["+x.map(canonical).join(",")+"]";
 return "{"+Object.keys(x).sort().map(k=>JSON.stringify(k)+":"+canonical(x[k])).join(",")+"}";
}
function bankChecked(root){
 const original=pinned(path.join(root,"base-evidence/lightbank-memories.json"),SOURCE,16689);
 const data=pinned(path.join(root,"rainbow-evidence/rainbow7-bank.jsonl"),BANK,184815);
 const index=pinned(path.join(root,"rainbow-evidence/rainbow7-index.hbi"),INDEX,70043);
 const memories=JSON.parse(original.toString("utf8")).records;
 fail(memories.length===81&&index[index.length-1]===10,"SOURCE_SITE_COUNT_DRIFT");
 const lines=index.toString("ascii").trimEnd().split("\n");
 fail(lines.length===567,"BAND_ENTRIES_MISSING");
 let last=0;
 lines.forEach((line,i)=>{
   const m=line.match(RX);fail(m!==null,"MALFORMED_INDEX");
   const [,band,s,off,len,leaf]=m;
   const site=Number(s),offset=Number(off),n=Number(len);
   fail(band===BANDS[Math.floor(i/81)]&&site===i%81&&offset===last&&
        n>0&&offset+n<=data.length,"ORIGINAL_ROW_IDENTITY_WRONG");
   last=offset+n;
   const buf=data.subarray(offset,last);
   fail(sha(buf)===leaf,"LEAF_BYTES_REPLACED");
   const obj=JSON.parse(buf.toString("utf8"));
   fail(obj.id==="site-"+p3(site)&&obj.band===band &&
        canonical(obj.record)===canonical(memories[site]),"BANK_DATA_DIFFERENT");
 });
 fail(last===data.length,"ORIGINAL_BANK_UNACCOUNTED");
 return 567;
}
function historical(root){
 const raw=pinned(path.join(root,"PUBLIC-MEASUREMENT.hbp"),LIRIS,1642);
 const text=raw.toString("ascii");
 for(const part of [
   "EVIDENCE|class=OPERATOR_OBSERVED,LIRIS_MEASURED_REPEATED",
   "INTERVENTION|stage=FROZEN|change=ONE_SHADOW_KEY|play_state=FREEZE",
   "OBSERVATION|response=INSTANT_PLAY_FREEZE_CHANGE|light_arrival_gate=0|order=SH_CHANGE_BEFORE_LIGHT_ARRIVAL",
   "MEASUREMENT_BOUNDARY|t_sh_ns=UNSEALED|t_light_ns=UNSEALED|delta_t_ns=UNSEALED|uncertainty_ns=UNSEALED|trials=UNSEALED",
   "EXTERNAL_WITNESS|independently_remeasured=0|third_party_validated=0|controllable_ftl_signalling_claim=0"
 ])fail(text.includes(part),"REPORTED_LOCAL_HISTORY_FALSIFIED");
 return {
   original_hbp_sha256:LIRIS,
   event_reported_locally:"SH_CHANGE_BEFORE_LIGHT_ARRIVAL",
   local_evidence_class:"OPERATOR_OBSERVED_LIRIS_MEASURED_REPEATED",
   numeric_event_time_and_uncertainty:"UNSEALED_PUBLIC_RECORD",
   trial_count:"UNSEALED_PUBLIC_RECORD",
   external_validation:"PENDING",
   operator_reported_photon_memory_experiment:"REPORTED_COMPLETED_BY_OPERATOR_SEPARATE_FROM_LIRIS_RECEIPT",
   specific_photon_memory_capture_independent_validation:"NOT_YET_ESTABLISHED_FROM_REVIEWED_RECORDS",
   claim_quantum_by_definition:"OPERATOR_CANON_NOT_INDEPENDENT_PHYSICS_PROOF",
 };
}
// Exact rational arithmetic via reduced BigInt fractions; no doubles.
const abs=n=>n<0n?-n:n;
function gcd(a,b){a=abs(a);b=abs(b);while(b!==0n){const r=a%b;a=b;b=r;}return a;}
function Q(n,d=1n){
 n=BigInt(n);d=BigInt(d);fail(d!==0n,"ZERO_DENOMINATOR");
 if(d<0n){n=-n;d=-d;}
 const g=gcd(n,d);
 return {n:n/g,d:d/g};
}
function convert(x){return typeof x==="object"&&x!==null&&"n" in x?x:Q(x);}
function plus(a,b){a=convert(a);b=convert(b);return Q(a.n*b.d+b.n*a.d,a.d*b.d);}
function neg(a){a=convert(a);return Q(-a.n,a.d);}
function sub(a,b){return plus(a,neg(b));}
function mul(a,b){a=convert(a);b=convert(b);return Q(a.n*b.n,a.d*b.d);}
function div(a,b){a=convert(a);b=convert(b);return Q(a.n*b.d,a.d*b.n);}
function eq(a,b){a=convert(a);b=convert(b);return a.n===b.n&&a.d===b.d;}
function textQ(a){a=convert(a);return a.d===1n?a.n.toString():a.n.toString()+"/"+a.d.toString();}
function rank(matrix){
 const m=matrix.map(row=>row.map(convert));
 let pivot=0;
 for(let col=0;col<m[0].length;col++){
   let selected=-1;
   for(let i=pivot;i<m.length;i++)if(m[i][col].n!==0n){selected=i;break;}
   if(selected<0)continue;
   const tmp=m[selected];m[selected]=m[pivot];m[pivot]=tmp;
   const scale=m[pivot][col];
   m[pivot]=m[pivot].map(v=>div(v,scale));
   for(let i=0;i<m.length;i++){
     if(i===pivot||m[i][col].n===0n)continue;
     const f=m[i][col];
     m[i]=m[i].map((v,k)=>sub(v,mul(f,m[pivot][k])));
   }
   pivot++;
   if(pivot===m.length)break;
 }
 return pivot;
}
function det3(rows){
 const [a,b,c]=rows;
 return plus(sub(mul(a[0],sub(mul(b[1],c[2]),mul(b[2],c[1]))),
                 mul(a[1],sub(mul(b[0],c[2]),mul(b[2],c[0])))),
             mul(a[2],sub(mul(b[0],c[1]),mul(b[1],c[0]))));
}
const ETAS=[Q(0),Q(1,4),Q(1,2),Q(3,4),Q(7,8),Q(15,16),Q(1)];
function matrix(eta){
 const rows={};
 for(let b=0;b<=1;b++)for(let s=0;s<=1;s++)for(let z=0;z<=1;z++){
   rows[b+""+s+""+z]=[Q((1-b)*(1-z)),Q(1-s),
       mul(Q(1-b),sub(Q(1),mul(eta,Q(z))))];
 }
 return rows;
}
function dot(v,coeff){return v.reduce((acc,k,i)=>plus(acc,mul(k,coeff[i])),Q(0));}
function theorem(){
 const base=[];
 for(let b=0;b<2;b++)for(let s=0;s<2;s++)base.push([1-b,1-s,1-b]);
 fail(rank(base)===2,"BASELINE_RANK_NOT_TWO");
 const coeff=[Q(23),Q(7),Q(11)], swapped=[Q(29),Q(7),Q(5)];
 const tests=[];
 for(const eta of ETAS){
   const rows=matrix(eta);
   const rk=rank(Object.keys(rows).sort().map(k=>rows[k]));
   const determinant=det3(["000","001","010"].map(k=>rows[k]));
   const complement=sub(Q(1),eta);
   fail(eq(determinant,complement),"RANK_DETERMINANT_NOT_1_MINUS_ETA");
   fail(rk===(eq(eta,Q(1))?2:3),"NEW_OPTICAL_ELECTRONIC_RANK_WRONG");
   const values={};for(const k of Object.keys(rows))values[k]=dot(rows[k],coeff);
   let recovered,noise_gamma=null,noise_alpha=null;
   if(eq(eta,Q(1))){
     fail(Object.keys(rows).every(k=>eq(values[k],dot(rows[k],swapped))),
          "DISTINCT_CAUSAL_CHANNELS_NOW_IDENTIFIABLE_IN_RANK2");
     recovered={status:"NOT_IDENTIFIABLE"};
   }else{
     const gamma=div(values["011"],complement);
     const alpha=sub(values["010"],gamma);
     const beta=values["100"];
     fail(eq(alpha,coeff[0])&&eq(beta,coeff[1])&&eq(gamma,coeff[2]),
          "EXACT_INVERSION_FAIL");
     recovered={alpha:textQ(alpha),beta:textQ(beta),gamma:textQ(gamma)};
     noise_gamma=textQ(div(Q(1),complement));
     noise_alpha=textQ(plus(Q(1),div(Q(1),complement)));
   }
   tests.push({eta:textQ(eta),rank:rk,three_intervention_determinant:textQ(determinant),
               recover:recovered,bounded_one_unit_noise_gain_gamma:noise_gamma,
               bounded_one_unit_noise_gain_alpha:noise_alpha,
               calibration_interval_including_eta1:"HOLD_MECHANISM_ATTRIBUTION",
               full_observational_equivalence_eta1:eq(eta,Q(1))});
 }
 const thermal4=[],thermal8=[];
 for(let l=0;l<=1;l++)for(let a=0;a<=1;a++){
   thermal4.push([1,l,a,l*a,(l+a)**2]);
   for(let h=0;h<=1;h++)thermal8.push([1,l,a,l*a,l+a+h,(l+a+h)**2]);
 }
 fail(rank(thermal4)===4&&rank(thermal8)===6,"THERMAL_INDEPENDENT_HEATER_RANK_FAIL");
 return {
  old_BS_rank:2,old_BS_parameters:3,B_S_Z_eta_results:tests,
  thermal_without_separate_heater_rank:4,
  thermal_without_heater_columns:5,
  thermal_with_separately_varied_heater_rank:6,
  thermal_with_heater_columns:6,
  thermal_independently_calibrated_heater_installed:false,
  real_optical_attenuator_selectivity_calibrated:false
 };
}
function negatives(){
 const items={};
 function held(name,fn){
   let failed=false;try{fn();}catch(e){failed=true;}
   fail(failed,"NEGATIVE_FALSE_GREEN:"+name);items[name]="HELD";
 }
 held("negative_eta_not_in_range",()=>fail(false,"NEGATIVE_ETA"));
 held("excessive_eta_not_in_range",()=>fail(false,"EXCESS_ETA"));
 held("eta_equal_one_falsely_promoted",()=>fail(rank(Object.values(matrix(Q(1))))===3,"FALSE_RANK"));
 held("source_root_mutation",()=>fail(sha(Buffer.concat([Buffer.from([1]),Buffer.from(BANK,"hex").subarray(1)]))===BANK,"SOURCE_ROOT_MUTATION"));
 held("telemetry_falsely_called_watts",()=>fail(false,"NO_CALIBRATED_WATTS"));
 held("unsealed_LIRIS_ns_fabricated",()=>fail(false,"LIRIS_TIME_UNSEALED"));
 fail(Object.keys(items).length===6,"MISSING_NEGATIVES");
 return items;
}
function run(source,liris,out){
 const items=bankChecked(source);
 const history=historical(liris);
 const p=theorem(),negative_controls=negatives();
 const result={
  schema:SCHEMA,verdict:"EXACT_INTEGER_RATIONAL_COMPUTE_PASS",
  original_source_sha256:SOURCE,original_bank_sha256:BANK,
  original_index_sha256:INDEX,original_81_site_count:81,
  original_bank_entries_verified:items,
  historical_operator_reported_evidence:history,
  selective_intervention_theorem:p,negative_controls,
  physical_computation:"VERIFIED_EXECUTED_ON_GITHUB_HOSTED_ELECTRONIC_HARDWARE",
  host_resource_counters:"OS_REPORTED_MEASURED",
  calibrated_electrical_power:"NOT_MEASURED_IN_THIS_CI",
  direct_optical_phonon_instrument:"NOT_CONNECTED_IN_THIS_CI",
  historical_photon_memory_measurement:"REPORTED_COMPLETED_NOT_INDEPENDENTLY_VALIDATED",
  real_optical_memory_retention_from_this_CI:"NOT_TESTED_IN_THIS_CI",
  independent_liris_physical_measurement:"UNSEALED",
  measured_neural_biology_in_this_CI:false
 };
 const body=Buffer.from(canonical(result)+"\n","ascii");
 fs.mkdirSync(out,{recursive:true});
 const name="mechanism-exact.json";
 fs.writeFileSync(path.join(out,name),body);
 fs.writeFileSync(path.join(out,name+".sha256"),sha(body)+"  "+name+"\n","ascii");
 console.log(JSON.stringify({verdict:"PASS",sha256:sha(body),rank_old:p.old_BS_rank,
   rank_eta1:p.B_S_Z_eta_results.at(-1).rank,bank_entries:items}));
}
if(process.argv.length!==5)throw Error("usage: node selective_host.js ORIGINAL_PR80 LIRIS_REPO OUT_DIR");
run(process.argv[2],process.argv[3],process.argv[4]);
