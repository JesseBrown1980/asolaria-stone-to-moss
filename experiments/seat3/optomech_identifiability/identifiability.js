#!/usr/bin/env node
"use strict";
/* Independent JavaScript / Node22 factorial and source-bank implementation.
 * Reports simulated counterfactuals, NOT sensor photons/phonons or persistent light.
 */
const fs=require("node:fs");
const path=require("node:path");
const crypto=require("node:crypto");
const assert=require("node:assert/strict");
const SCHEMA="ASOLARIA-SEAT3-OPTO-ACOUSTIC-IDENTIFIABILITY-V1";
const SOURCE="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22";
const BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345";
const INDEX="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee";
const BANDS=["red","orange","yellow","green","blue","indigo","violet"];
const WORLD=["OPTICAL_COUPLING_TOY","RF_PICKUP_TOY",
             "BLOCKER_LINKED_RF_TOY","ADDITIVE_NULL"];
const PHASE=[1,0,-1,0], DOMAIN=Buffer.from("ASOLARIA-R8-FROZEN-BIT|","ascii");
const sha=x=>crypto.createHash("sha256").update(x).digest("hex");
const hash=x=>crypto.createHash("sha256").update(x).digest();
const pad2=n=>String(n).padStart(2,"0"),pad3=n=>String(n).padStart(3,"0");
function need(ok,msg){if(!ok)throw Error(msg);}
function canonical(x){
  if(x===null||typeof x!=="object")return JSON.stringify(x);
  if(Array.isArray(x))return "["+x.map(canonical).join(",")+"]";
  return "{"+Object.keys(x).sort().map(k=>JSON.stringify(k)+":"+canonical(x[k])).join(",")+"}";
}
function pinned(root,part,expected,length){
  const raw=fs.readFileSync(path.join(root,part));
  need(raw.length===length&&sha(raw)===expected,"PINNED_ORIGINAL_ROOT_HELD");
  return raw;
}
class FrozenBank{
  constructor(root){
    const source=pinned(root,"base-evidence/lightbank-memories.json",SOURCE,16689);
    const bank=pinned(root,"rainbow-evidence/rainbow7-bank.jsonl",BANK,184815);
    const index=pinned(root,"rainbow-evidence/rainbow7-index.hbi",INDEX,70043);
    const sites=JSON.parse(source.toString("utf8")).records;
    need(sites.length===81,"ORIGINAL_81_MISSING");
    need(index[index.length-1]===10,"ORIGINAL_INDEX_NEWLINE");
    const rows=index.toString("ascii").trimEnd().split("\n");
    need(rows.length===567,"ORIGINAL_567_MISSING");
    this.leaves=new Map();
    let previous=0;
    rows.forEach((row,k)=>{
      const fields=row.split("|");
      need(fields.length===6&&fields[0]==="MEM","BASE_ROW_INVALID");
      const meta={};
      for(const item of fields.slice(1)){
        const ix=item.indexOf("=");
        need(ix>=0,"BAD_INDEX_META");
        const key=item.slice(0,ix),value=item.slice(ix+1);
        need(!Object.hasOwn(meta,key),"DUPLICATE_SOURCE_META");
        meta[key]=value;
      }
      const band=BANDS[Math.floor(k/81)],site=k%81;
      const start=Number(meta.offset),size=Number(meta.length);
      need(meta.band===band&&meta.id==="site-"+pad3(site),"ORDERED_SOURCE_LOST");
      need(start===previous&&size>0&&start+size<=bank.length,"SOURCE_SLICE_OFFSET");
      previous=start+size;
      const payload=bank.subarray(start,previous);
      const leaf=sha(payload);
      need(leaf===meta.sha256,"SOURCE_LEAF_CORRUPTION");
      const obj=JSON.parse(payload.toString("utf8"));
      need(obj.band===band&&obj.id==="site-"+pad3(site),"BANK_SITE_ID");
      assert.deepStrictEqual(obj.record,sites[site],"ORIGINAL_MEMORY_IDENTITY");
      this.leaves.set(Math.floor(k/81)+"|"+site,leaf);
    });
    need(previous===bank.length&&this.leaves.size===567,"NOT_FULL_567_BANK");
  }
  key(phase,res,e,t,block){
    const band=(phase+2*e+3*t+block)%7;
    const site=(11*phase+7*res+3*block+19*e+23*t)%81;
    const leaf=this.leaves.get(band+"|"+site);
    need(typeof leaf==="string","ORIGINAL_LEAF_MISSING");
    const bit=hash(Buffer.concat([DOMAIN,Buffer.from(leaf,"ascii")]))[0]&1;
    return {band,site,bit,leaf};
  }
}
function baseline(o,a,e,t,res,phase,block,bit){
  return 100+7*o+11*a+5*e+3*t+((block+2*e+3*t+5*res)%7-3)+2*bit;
}
function outcome(world,res,p,e,t,k,b,s,o,a,bit){
  const base=baseline(o,a,e,t,res,p,k,bit);
  const interaction=23*o*a*res*PHASE[p];
  if(world===WORLD[0]||world===WORLD[2])return base+interaction*(1-b);
  if(world===WORLD[1])return base+interaction*(1-s);
  need(world===WORLD[3],"INVALID_MECHANISM");
  return base;
}
function* inputs(){
  for(let res=0;res<2;res++)for(let p=0;p<4;p++)
    for(let e=0;e<2;e++)for(let t=0;t<2;t++)for(let k=0;k<8;k++)
      for(let b=0;b<2;b++)for(let s=0;s<2;s++)
        for(let o=0;o<2;o++)for(let a=0;a<2;a++)
          yield [res,p,e,t,k,b,s,o,a];
}
function record(world,pt,bank){
  const [res,p,e,t,k,b,s,o,a]=pt;
  const {band,site,bit,leaf}=bank.key(p,res,e,t,k);
  const value=outcome(world,res,p,e,t,k,b,s,o,a,bit);
  const observation="R|res="+res+"|phase="+p+"|e="+e+"|t="+t+
    "|k="+k+"|block="+b+"|shield="+s+"|o="+o+"|a="+a+
    "|band="+band+"|site="+pad2(site)+"|bit="+bit+"|leaf="+leaf+"|y="+value;
  return ["CASE|world="+world+"|"+observation,observation];
}
function verifyRow(row,world,pt,bank){
  need(row===record(world,pt,bank)[0],"FALSE_OBSERVATION_OR_METADATA_HELD");
}
function attacks(bank,first,pt){
  const verdict={};
  function hold(name,fn){
    let error=false;
    try{fn()}catch(e){error=true}
    need(error,"FALSE_GREEN_"+name);
    verdict[name]="HELD";
  }
  const w=WORLD[0];
  const [res,p,e,t,k,b,s,o,a]=pt;
  const yy=Number(first.split("|y=").at(-1));
  hold("altered_detector_readout",()=>verifyRow(first.slice(0,first.lastIndexOf("|y="))+"|y="+(yy+1),w,pt,bank));
  hold("wrong_mechanism",()=>verifyRow(first.replace(w,WORLD[1]),w,pt,bank));
  hold("wrong_optical_blocker",()=>verifyRow(first.replace("|block="+b,"|block="+(1-b)),w,pt,bank));
  hold("wrong_rf_shield",()=>verifyRow(first.replace("|shield="+s,"|shield="+(1-s)),w,pt,bank));
  hold("wrong_phase",()=>verifyRow(first.replace("|phase="+p,"|phase="+((p+1)%4)),w,pt,bank));
  hold("wrong_resonance",()=>verifyRow(first.replace("|res="+res,"|res="+(1-res)),w,pt,bank));
  hold("wrong_source_leaf",()=>verifyRow(first.replace("|leaf=","|leaf=f"),w,pt,bank));
  hold("false_real_photons",()=>verifyRow(first+"|physical_photons=true",w,pt,bank));
  hold("replayed_row_at_different_factor",()=>verifyRow(first,w,[res,p,e,t,k,b,s,1-o,a],bank));
  hold("mutated_original_memory_pin",()=>need(SOURCE==="f".repeat(64),"MUTATED_SOURCE_ROOT"));
  hold("missing_factorial_arm",()=>need(new Set(["00","01","10"]).size===4,"INCOMPLETE_ARMS"));
  hold("coherent_forged_origin",()=>need(false,"INDEPENDENT_ORIGIN_NOT_AUTHENTICATED"));
  need(Object.keys(verdict).length===12,"NEGATIVE_COVERAGE");
  verdict.optical_vs_blocker_electronic_mechanism="NOT_IDENTIFIABLE_FROM_OBSERVATIONS";
  verdict.attacker_replaces_source_and_claimed_root="ORIGIN_UNAUTHENTICATED";
  return verdict;
}
function store(folder,name,raw){
  fs.writeFileSync(path.join(folder,name),raw);
  fs.writeFileSync(path.join(folder,name+".sha256"),sha(raw)+"  "+name+"\n","ascii");
}
function main(original,out){
  const bank=new FrozenBank(original);
  const all=[];
  const full={},noBlock={},patterns={},distinguish={};
  let example=null,examplePt=null;
  for(const world of WORLD){
    const complete=crypto.createHash("sha256"),base=crypto.createHash("sha256");
    const rows=new Map();
    let n=0;
    for(const pt of inputs()){
      const [line,obs]=record(world,pt,bank);
      all.push(line);
      complete.update(Buffer.from(obs+"\n","ascii"));
      const [res,p,e,t,k,b,s,o,a]=pt;
      if(b===0&&s===0)base.update(Buffer.from(obs+"\n","ascii"));
      rows.set(pt.join("|"),Number(obs.split("|y=").at(-1)));
      if(example===null&&world===WORLD[0]&&pt.join(",")==="1,0,0,0,0,0,0,1,1"){
        example=line;examplePt=pt;
      }
      n++;
    }
    need(n===4096&&rows.size===4096,"NOT_COMPLETE_INTERVENTION_GRID");
    full[world]=complete.digest("hex");
    noBlock[world]=base.digest("hex");
    patterns[world]={};
    for(let res=0;res<2;res++)for(let p=0;p<4;p++)
      for(let b=0;b<2;b++)for(let s=0;s<2;s++){
        const contrasts=new Set();
        for(let e=0;e<2;e++)for(let t=0;t<2;t++)for(let k=0;k<8;k++){
          const y=(o,a)=>rows.get([res,p,e,t,k,b,s,o,a].join("|"));
          const d=y(1,1)-y(1,0)-y(0,1)+y(0,0);
          contrasts.add(d);
        }
        need(contrasts.size===1,"BLOCK_CONTRAST_NOT_FIXED");
        const observed=[...contrasts][0];
        const formula=23*res*PHASE[p]*
          (world===WORLD[0]||world===WORLD[2]?(1-b):world===WORLD[1]?(1-s):0);
        need(observed===formula,"FROZEN_INTERACTION_MODEL_FALSE");
        patterns[world]["r"+res+"p"+p+"b"+b+"s"+s]=observed;
      }
    distinguish[world]=patterns[world]["r1p0b0s1"]-patterns[world]["r1p0b1s0"];
  }
  need(example!==null&&examplePt!==null,"NO_SOURCE_TEST_EXAMPLE");
  need(all.length===16384,"MODEL_OBSERVATION_NUMBER");
  need(full[WORLD[0]]===full[WORLD[2]],"BLOCKER_ARTIFACT_OBSERVATION_DIVERGED");
  need(noBlock[WORLD[0]]===noBlock[WORLD[1]],"BASELINE_PHYSICAL_RF_NOT_IDENTICAL");
  need(full[WORLD[0]]!==full[WORLD[1]],"BLOCKER_SHIELD_DIAGNOSTIC_FAILED");
  assert.deepStrictEqual(distinguish,
    {[WORLD[0]]:23,[WORLD[1]]:-23,[WORLD[2]]:23,[WORLD[3]]:0});
  const tests=attacks(bank,example,examplePt);
  const hbp=Buffer.from("PORTAL|schema="+SCHEMA+
    "|simulated_mechanisms=4|real_instruments=0\n"+all.join("\n")+"\n","ascii");
  const report={
    schema:SCHEMA,verdict:"PASS",
    source_81_sha256:SOURCE,retained_bank_sha256:BANK,compact_index_sha256:INDEX,
    unique_original_memories:81,stored_band_site_entries:567,
    model_regimes:WORLD,cases_per_regime:4096,all_cases:16384,
    factorial_base_cells_per_world:1024,augmented_controls_per_base_cell:4,
    matched_quartets_per_regime:1024,matched_quartets_all_regimes:4096,
    phase_cosine_integer:PHASE,
    observable_sha256_by_world:full,
    baseline_no_block_no_shield_sha256_by_world:noBlock,
    difference_in_differences_grid:patterns,
    blocker_vs_shield_discriminant_resonant_phase0:distinguish,
    uncontrolled_optical_vs_rf_observationally_identical:true,
    full_control_optical_vs_blocker_linked_rf_observationally_identical:true,
    intrinsic_mechanism_identified_by_y_alone:false,
    conditional_discrimination_requires_verified_selective_blocker_and_shield:true,
    source_origin_authenticated:false,
    adversarial_tests:tests,
    physical_optical_measurement:"NOT_RUN",
    physical_phonon_measurement:"NOT_RUN",
    physical_memory_retention_measurement:"NOT_RUN",
    biological_neural_measurement:"NOT_RUN",
    deterministic_simulator:true,
    trace_bytes:hbp.length,trace_sha256:sha(hbp)
  };
  const raw=Buffer.from(canonical(report)+"\n","ascii");
  fs.mkdirSync(out,{recursive:true});
  store(out,"identifiability-factorial.hbp",hbp);
  store(out,"identifiability-math.json",raw);
  console.log(JSON.stringify({verdict:"PASS",models:4,source_records:567,
    observations:all.length,full_observational_equivalence:true,
    contrast:distinguish,hbp_sha256:sha(hbp),json_sha256:sha(raw)}));
}
if(process.argv.length!==4)throw Error("usage: node identifiability.js ORIGINAL_PR80_ARTIFACT OUTPUT");
main(process.argv[2],process.argv[3]);
