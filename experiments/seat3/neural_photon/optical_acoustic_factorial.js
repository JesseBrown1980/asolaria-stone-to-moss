#!/usr/bin/env node
"use strict";
/** Independent numerical 2x2x2 photon–phonon–electronic toy factorial.
 * Every historical bank source root, position, byte leaf and source record
 * checked; no physical optical, phonon or electronic memory experiment.
 */
const fs=require("node:fs"),path=require("node:path");
const crypto=require("node:crypto"),assert=require("node:assert/strict");
const SCHEMA="ASOLARIA-SEAT3-PHOTON-PHONON-ELECTRONIC-FACTORIAL-TOY-V1";
const SRC="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22";
const BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345";
const INDEX="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee";
const BANDS=["red","orange","yellow","green","blue","indigo","violet"];
const PORTS=[2,5,0,6,1,4,3];
const MODELS=["NULL","OPTICAL_MAIN_ONLY","ACOUSTIC_MAIN_ONLY","DIRECT_COUPLING_TOY","THERMAL_ELECTRONIC_MIMIC","FAST_AFTERGLOW"];
const DELAYS=[1,10,60];
const INDEX_RE=/^MEM\|band=(red|orange|yellow|green|blue|indigo|violet)\|id=site-(\d{3})\|offset=(\d+)\|length=(\d+)\|sha256=([a-f0-9]{64})$/;
const sha=b=>crypto.createHash("sha256").update(b).digest("hex");
const pad2=x=>String(x).padStart(2,"0");
const pad3=x=>String(x).padStart(3,"0");
function gate(c,m){if(!c)throw Error(m);}
function rooted(file,h,n){const b=fs.readFileSync(file);gate(b.length===n&&sha(b)===h,"INVALID_SOURCE_ROOT "+file);return b;}
function bankFrom(root){
  const source=rooted(path.join(root,"base-evidence/lightbank-memories.json"),SRC,16689);
  const bank=rooted(path.join(root,"rainbow-evidence/rainbow7-bank.jsonl"),BANK,184815);
  const index=rooted(path.join(root,"rainbow-evidence/rainbow7-index.hbi"),INDEX,70043);
  const originals=JSON.parse(source.toString("utf8")).records;
  gate(originals.length===81,"WRONG_MEMORY_COUNT");
  gate(index[index.length-1]===10,"INDEX_TERMINATOR");
  const lines=index.toString("ascii").trimEnd().split("\n");
  gate(lines.length===567,"INDEX_COUNT");
  const leafs=[];
  let prev=0;
  for(let i=0;i<567;i++){
    const m=lines[i].match(INDEX_RE);
    gate(m!==null,"INVALID_INDEX_ROW");
    const [,band,id,offset,length,leaf]=m;
    const site=Number(id),off=Number(offset),n=Number(length);
    gate(band===BANDS[Math.floor(i/81)]&&site===i%81,"SOURCE_ORDER_MISMATCH");
    gate(off===prev&&n>0&&off+n<=bank.length,"OFFSET_OVERLAP");
    prev=off+n;
    const bytes=bank.subarray(off,prev);
    gate(sha(bytes)===leaf,"UNTRUSTED_LEAF");
    const item=JSON.parse(bytes.toString("utf8"));
    gate(item.id==="site-"+pad3(site)&&item.band===band,"SRC_LEAF_WRONG_ID");
    assert.deepStrictEqual(item.record,originals[site],"WRONG_ROOT_SOURCE_CONTENT");
    leafs.push(leaf);
  }
  gate(leafs.length===567&&prev===bank.length,"INCOMPLETE_SOURCE");
  return leafs;
}
function outcomes(model,site,band,delay,O,A,E){
  const noiseBytes=Buffer.from("ASOLARIA-OAE-NOISE-V1|"+model+"|site="+site+"|band="+band+"|delay="+delay,"ascii");
  const noise=crypto.createHash("sha256").update(noiseBytes).digest()[0]%7-3;
  const mean=100+noise+4*E;
  let temperature=25+2*O+A;
  let base=mean;
  if(model==="OPTICAL_MAIN_ONLY")base=mean+20*O;
  else if(model==="ACOUSTIC_MAIN_ONLY")base=mean+20*A;
  else if(["DIRECT_COUPLING_TOY","THERMAL_ELECTRONIC_MIMIC","FAST_AFTERGLOW"].includes(model)){
    const active=(model==="FAST_AFTERGLOW"&&delay===60)?0:30;
    base=mean+10*O+6*A+active*O*A;
    if(model==="THERMAL_ELECTRONIC_MIMIC")temperature+=5*O*A;
  }else gate(model==="NULL","UNKNOWN_MODEL");
  const independent=model==="THERMAL_ELECTRONIC_MIMIC"?base-30*O*A:base;
  return [base,independent,temperature];
}
function canonical(x){
  if(x===null||typeof x!=="object")return JSON.stringify(x);
  if(Array.isArray(x))return "["+x.map(canonical).join(",")+"]";
  return "{"+Object.keys(x).sort().map(k=>JSON.stringify(k)+":"+canonical(x[k])).join(",")+"}";
}
function save(dest,name,b){
  fs.writeFileSync(path.join(dest,name),b);
  fs.writeFileSync(path.join(dest,name+".sha256"),sha(b)+"  "+name+"\n","ascii");
}
function run(source,dest){
  const leafs=bankFrom(source);
  const result={},lines=[];
  for(const model of MODELS){
    let count=0;
    const perDelay={};
    for(const delay of DELAYS){
      const contrasts={};
      for(const e of [0,1])for(const what of ["electronic","optical","temperature"])
        contrasts["e"+e+"_"+what]=new Set();
      for(let site=0;site<81;site++)for(let band=0;band<7;band++){
        const leaf=leafs[band*81+site];
        const measured=new Map();
        for(const O of [0,1])for(const A of [0,1])for(const E of [0,1]){
          const [electronic,optical,temp]=outcomes(model,site,band,delay,O,A,E);
          measured.set(O+"|"+A+"|"+E,[electronic,optical,temp]);
          lines.push("OAE|model="+model+"|delay="+pad2(delay)+
                     "|site="+pad2(site)+"|band="+band+
                     "|port="+PORTS[band]+"|leaf="+leaf+
                     "|O="+O+"|A="+A+"|E="+E+
                     "|electronic="+electronic+"|optical="+optical+"|temp="+temp);
          count++;
        }
        for(const E of [0,1]){
          const get=(o,a,i)=>measured.get(o+"|"+a+"|"+E)[i];
          for(const [i,label] of ["electronic","optical","temperature"].entries()){
            const delta=get(1,1,i)-get(1,0,i)-get(0,1,i)+get(0,0,i);
            contrasts["e"+E+"_"+label].add(delta);
          }
        }
      }
      const active=(model==="DIRECT_COUPLING_TOY"||
                    model==="THERMAL_ELECTRONIC_MIMIC"||
                    (model==="FAST_AFTERGLOW"&&delay!==60))?30:0;
      const cur={};
      for(const [k,v] of Object.entries(contrasts)){
        gate(v.size===1,"NOISE_FAILED_TO_CANCEL");
        const value=[...v][0];
        const expect=k.endsWith("_electronic")?active:
                     k.endsWith("_optical")?
                       (model==="THERMAL_ELECTRONIC_MIMIC"?0:active):
                       (model==="THERMAL_ELECTRONIC_MIMIC"?5:0);
        gate(value===expect,"FACTORIAL_CONTRAST_INVALID:"+k+":"+model);
        cur[k]=value;
      }
      perDelay[String(delay)]=cur;
    }
    gate(count===13608,"MODEL_CASES_MISSING");
    result[model]={arm_rows:count,contrast_by_delay:perDelay};
  }
  gate(lines.length===6*13608,"MISSING_SIX_HYPOTHESES");
  const hbp=Buffer.from("PORTAL|schema="+SCHEMA+
     "|synthetic_models=6|physical_instrument=NOT_RUN\n"+
     lines.join("\n")+"\n","ascii");
  const report={
    schema:SCHEMA,verdict:"DIGITAL_FACTORIAL_UNIT_TEST_PASS",
    models:MODELS,delays_s_nominal:DELAYS,
    physical_elapsed_time_measured:false,
    source_81_sha256:SRC,bank_567_sha256:BANK,base_index_sha256:INDEX,
    source_stable_site_identities:81,source_symbolic_spectral_bands:7,
    source_bank_stored_entries:567,factorial_arms:8,rows_per_model:13608,
    total_simulated_rows:lines.length,model_results:result,
    reconstructed_source_leafs_sha256_enforced:true,
    real_optical_capture:"NOT_RUN",real_acoustic_capture:"NOT_RUN",
    real_electronic_custody_attested:"NOT_RUN",
    real_photon_phonon_coupling:"NOT_RUN",
    physical_optical_memory_retention:"NOT_RUN",biological_neural_memory:"NOT_RUN",
    model_trace_bytes:hbp.length,model_trace_sha256:sha(hbp)
  };
  const receipt=Buffer.from(canonical(report)+"\n","ascii");
  fs.mkdirSync(dest,{recursive:true});
  save(dest,"photon-phonon-electronic-toy.hbp",hbp);
  save(dest,"photon-phonon-electronic-toy.json",receipt);
  console.log(JSON.stringify({verdict:report.verdict,total:lines.length,
    trace_sha256:sha(hbp),json_sha256:sha(receipt)}));
}
if(process.argv.length!==4)throw Error("usage: node optical_acoustic_factorial.js PR80_ARCHIVE OUT");
run(process.argv[2],process.argv[3]);
