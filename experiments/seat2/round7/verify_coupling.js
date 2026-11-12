#!/usr/bin/env node
"use strict";
/* Independent Seat 2 Node readback. All observations are synthetic numbers. */
const fs=require("node:fs"), crypto=require("node:crypto"), assert=require("node:assert/strict");
const path=require("node:path");
const M=["COHERENT_TOY","ADDITIVE_NULL","HEAT_ELECTRONIC_CONFOUND","PHASE_INSENSITIVE_ARTIFACT"];
const R="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345";
const STONE="077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400";
const SCHEMA="ASOLARIA-SEAT2-R7-PHONON-ELECTRON-OPTICAL-FACTORS-V1";
const SHA=x=>crypto.createHash("sha256").update(x).digest("hex");
function canonical(x){
 if(Array.isArray(x)) return "["+x.map(canonical).join(",")+"]";
 if(x!==null && typeof x==="object")return "{"+Object.keys(x).sort().map(k=>JSON.stringify(k)+":"+canonical(x[k])).join(",")+"}";
 return JSON.stringify(x);
}
function value(m,o,a,e,t,p,res,b){
 const noise=((b+2*e+3*t+5*res)%7)-3;
 const baseline=100+7*o+11*a+5*e+3*t+noise;
 if(m==="COHERENT_TOY")return baseline+23*o*a*res*[1,0,-1,0][p];
 if(m==="ADDITIVE_NULL")return baseline;
 if(m==="HEAT_ELECTRONIC_CONFOUND")return baseline+23*o*t+17*a*e;
 if(m==="PHASE_INSENSITIVE_ARTIFACT")return baseline+23*o*a;
 throw Error("UNKNOWN_MODEL");
}
function main(out,repo){
 const historical=fs.readFileSync(path.join(repo,"stones/2026-10-15-rainbow81/seat4-round5-signed-spectrum-mapping-20261015.hbp"));
 assert.equal(SHA(historical),STONE);
 const rows=fs.readFileSync(path.join(out,"factorial.jsonl"));
 const result=fs.readFileSync(path.join(out,"results.json"));
 const report=JSON.parse(result.toString("ascii"));
 assert.equal(report.trace_sha256,SHA(rows));
 assert.equal(report.physical_optomechanical_coupling_measured,false);
 assert.equal(report.independent_optical_memory_measured,false);
 assert.equal(report.biological_neural_memory_measured,false);
 const unique=new Map(), grouped=new Map();
 for(const line of rows.toString("ascii").trimEnd().split("\n")){
  const d=JSON.parse(line);assert.equal(canonical(d),line);
  assert.equal(d.schema,SCHEMA);assert.equal(d.source_bank_sha256,R);
  assert.equal(d.simulation_only,true);assert.equal(d.physical_optomechanical_coupling_measured,false);
  const [m,o,a,e,t,p,res,b]=[d.model,d.optical,d.acoustic,d.electronic,d.thermal,d.phase_idx,d.resonance,d.block];
  assert(M.includes(m)&&[o,a,e,t,res].every(x=>Number.isInteger(x)&&(x===0||x===1)));
  assert(Number.isInteger(p)&&p>=0&&p<4&&Number.isInteger(b)&&b>=0&&b<8);
  assert.equal(d.detector_mock_units,value(m,o,a,e,t,p,res,b));
  const k=[m,res,p,e,t,b,o,a].join("|");
  assert(!unique.has(k));unique.set(k,1);
  const group=[m,res,p,e,t,b].join("|");
  if(!grouped.has(group))grouped.set(group,{});
  grouped.get(group)[o+""+a]=d.detector_mock_units;
 }
 assert.equal(unique.size,4096);assert.equal(grouped.size,1024);
 const contrasts=new Map();
 for(const [group,four] of grouped){
  assert.equal(Object.keys(four).length,4);
  const delta=four["11"]-four["10"]-four["01"]+four["00"];
  const key=group.split("|").slice(0,3).join("|");
  if(!contrasts.has(key))contrasts.set(key,[]);
  contrasts.get(key).push(delta);
 }
 assert.equal(contrasts.size,32);
 const patterns={
 "COHERENT_TOY":{"0":[0,0,0,0],"1":[23,0,-23,0]},
 "ADDITIVE_NULL":{"0":[0,0,0,0],"1":[0,0,0,0]},
 "HEAT_ELECTRONIC_CONFOUND":{"0":[0,0,0,0],"1":[0,0,0,0]},
 "PHASE_INSENSITIVE_ARTIFACT":{"0":[23,23,23,23],"1":[23,23,23,23]}
 };
 for(const m of M)for(const res of [0,1])for(const p of [0,1,2,3]){
   const cases=contrasts.get([m,res,p].join("|"));
   assert.equal(cases.length,32);
   assert(cases.every(n=>n===patterns[m][String(res)][p]));
   assert.deepEqual(report.interaction_difference_in_differences[m][String(res)][p],
     patterns[m][String(res)][p]);
 }
 const mutated=Buffer.from(rows);
 mutated[17]^=1;
 assert.notEqual(SHA(mutated),report.trace_sha256);
 for(const name of ["factorial.jsonl","results.json","result.hbp"]){
  const x=fs.readFileSync(path.join(out,name));
  assert.equal(fs.readFileSync(path.join(out,name+".sha256"),"ascii"),SHA(x)+"  "+name+"\n");
 }
 const summary={schema:"ASOLARIA-SEAT2-R7-INDEPENDENT-NODE-CHECK-V1",
 classification:"SYNTHETIC_PHOTON_PHONON_ELECTRONIC_ONLY",
 original_source_sha256:R,original_stone_sha256:STONE,
 actual_observations:0,validated_simulated_rows:unique.size,
 exact_matched_difference_in_differences:grouped.size,
 computed_interaction_cells:contrasts.size,
 physically_measured_coupling:false,independent_optical_memory_measured:false,
 real_biological_neural_memory_measured:false,corruption_detected:true,
 trace_sha256:SHA(rows)};
 const buf=Buffer.from(canonical(summary)+"\n","ascii");
 fs.writeFileSync(path.join(out,"independent-node.json"),buf);
 fs.writeFileSync(path.join(out,"independent-node.json.sha256"),SHA(buf)+"  independent-node.json\n");
 process.stdout.write("NODE_INDEPENDENT_R7_PASS "+SHA(buf)+"\n");
}
if(process.argv.length!==4)throw Error("usage: node verify_coupling.js OUTPUT FROZEN_MAIN");
main(process.argv[2],process.argv[3]);
