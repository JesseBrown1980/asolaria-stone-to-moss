#!/usr/bin/env node
"use strict";
/* Independently check simulated detector data and source/witness mathematics. */
const fs=require("node:fs"),crypto=require("node:crypto"),assert=require("node:assert/strict"),path=require("node:path");
const bands=["red","orange","yellow","green","blue","indigo","violet"];
const ports=[2,5,0,6,1,4,3],scenarios=["MEMORY_TOY","NO_MEMORY_NULL","FAST_AFTERGLOW"];
const arms=["WRITE","SHAM","ERASE"],delays=[1,10,60];
const root="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345";
const stoneSha="077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400";
const nonce="R6-TEST-ONLY-FIXED-NOT-PHYSICAL-FRESHNESS";
const sha=x=>crypto.createHash("sha256").update(x).digest("hex");
function ordered(sector){assert(Number.isInteger(sector)&&sector>=0&&sector<27);return [Math.floor(sector/9),Math.floor(sector/3)%3,sector%3];}
function witness(k){const [r,g,b]=ordered(k);return (r+4*g+3*b+4*r*g)%8;}
function primitive(k){
 const [r,g,b]=ordered(k),sum=r+g+b,q=r*r+g*g+b*b-r*g-r*b-g*b;
 const parts=[sum*sum,q,q],gcd=(x,y)=>y?gcd(y,x%y):x,common=parts.reduce((g,v)=>gcd(g,v),0);
 return common?parts.map(x=>x/common).join(","):"DARK";
}
function bit(band,site){return crypto.createHash("sha256").update("R6|FROZEN-SEED|"+band+"|"+site).digest()[0]&1;}
function numeric(scenario,arm,delay,band,site,value){
 let signal=0;
 if(arm==="WRITE"&&scenario==="MEMORY_TOY")signal=70*value;
 if(arm==="WRITE"&&scenario==="FAST_AFTERGLOW"&&delay<60)signal=(delay===1?70:42)*value;
 const n=crypto.createHash("sha256").update("R6|NOISE|"+scenario+"|"+arm+"|"+delay+"|"+band+"|"+site).digest()[0]%11-5;
 return 22+signal+n;
}
function canon(x){
 if(Array.isArray(x))return "["+x.map(canon).join(",")+"]";
 if(x!==null&&typeof x==="object")return "{"+Object.keys(x).sort().map(k=>JSON.stringify(k)+":"+canon(x[k])).join(",")+"}";
 return JSON.stringify(x);
}
function main(folder,mainroot){
 const merged=fs.readFileSync(path.join(mainroot,"stones/2026-10-15-rainbow81/seat4-round5-signed-spectrum-mapping-20261015.hbp"));
 assert.equal(sha(merged),stoneSha);
 const inverse=new Set([...Array(27).keys()].map(i=>primitive(i)+"|"+witness(i)));
 assert.equal(inverse.size,27);
 const trace=fs.readFileSync(path.join(folder,"r6-raw-synthetic-detector.jsonl"));
 const receipt=JSON.parse(fs.readFileSync(path.join(folder,"r6-results.json"),"ascii"));
 assert.equal(receipt.digital_preflight_pass,true);
 assert.equal(receipt.physical_spectrum_verified,false);
 assert.equal(receipt.actual_photonic_persistence_measured,false);
 assert.equal(receipt.real_neural_electrophysiology_measured,false);
 assert.equal(receipt.trace_sha256,sha(trace));
 let total=0;const group=new Map();
 for(const line of trace.toString("ascii").trimEnd().split("\n")){
  const p=JSON.parse(line);assert.equal(line,canon(p));
  assert.equal(p.schema,"ASOLARIA-SEAT4-R6-RAW-SIMULATED-OPTICAL-COUNT-V1");
  assert.equal(p.simulation_only,true);
  assert.equal(p.nonce,nonce);assert.equal(p.source_bank_sha256,root);
  assert.equal(p.sector,p.site%27);assert.equal(p.witness,witness(p.sector));
  assert.equal(p.port,ports[bands.indexOf(p.band)]);
  assert.equal(p.precommitted_bit,bit(p.band,p.site));
  assert.equal(p.detector_count,numeric(p.scenario,p.arm,p.delay_s,p.band,p.site,p.precommitted_bit));
  const sequence=1+delays.indexOf(p.delay_s)*(3*81*7)+arms.indexOf(p.arm)*81*7+p.site*7+bands.indexOf(p.band);
  assert.equal(p.sequence,sequence);
  const id=p.scenario+"|"+p.arm+"|"+p.delay_s+"|"+p.band;
  if(!group.has(id))group.set(id,[]);
  group.get(id).push([p.detector_count>=50?1:0,p.precommitted_bit]);total++;
 }
 assert.equal(total,15309);
 assert.equal(group.size,3*3*3*7);
 for(const scenario of scenarios)for(const arm of arms)for(const delay of delays)for(const band of bands){
  const id=scenario+"|"+arm+"|"+delay+"|"+band,pairs=group.get(id);
  assert.equal(pairs.length,81);
  const pos=pairs.filter(p=>p[1]===1),neg=pairs.filter(p=>p[1]===0);
  const ba=(pos.reduce((s,p)=>s+p[0],0)/pos.length+
            neg.reduce((s,p)=>s+1-p[0],0)/neg.length)/2;
  assert(Math.abs(ba-receipt.balanced_accuracy_by_scenario_arm_delay_band[scenario][arm][String(delay)][band])<0.000001);
 }
 for(const name of ["r6-results.hbp","r6-results.json","r6-raw-synthetic-detector.jsonl"]){
  const val=fs.readFileSync(path.join(folder,name));
  assert.equal(fs.readFileSync(path.join(folder,name+".sha256"),"ascii"),
     sha(val)+"  "+name+"\n");
 }
 const changed=Buffer.from(trace);
 changed[changed.length-50]^=1;
 assert.notEqual(sha(changed),receipt.trace_sha256);
 assert.equal(receipt.negative_controls.length,12);
 const result={schema:"ASOLARIA-SEAT4-R6-INDEPENDENT-NODE-REVIEW-V1",
  classification:"ALL_TESTED_NUMERIC_TRACES_SIMULATION_ONLY",
  source_sha256:root,raw_trace_sha256:sha(trace),cases_independently_verified:total,
  ternary_order_classes_exact:inverse.size,independently_checked_statistical_cells:group.size,
  actual_photon_measurements:0,actual_neural_recordings:0,
  corrupted_full_trace_detected:true};
 const file=Buffer.from(canon(result)+"\n");
 fs.writeFileSync(path.join(folder,"r6-independent-node.json"),file);
 fs.writeFileSync(path.join(folder,"r6-independent-node.json.sha256"),sha(file)+"  r6-independent-node.json\n");
 console.log(JSON.stringify({status:"INDEPENDENT_NODE_PASS",traces:total,cells:group.size,
 source_trace_sha:sha(trace),node_sha:sha(file),physical:"HOLD"}));
}
if(process.argv.length!==4)throw Error("usage: node verify_photon_neural.js GENERATED_OUT FROZEN_MAIN");
main(process.argv[2],process.argv[3]);
