#!/usr/bin/env node
"use strict";
/* Independently replay every software R8 light×acoustic factorial source row. */
const crypto=require("node:crypto"),fs=require("node:fs"),path=require("node:path"),readline=require("node:readline"),assert=require("node:assert/strict");
const SHA={source:"02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22",
bank:"52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345",
index:"6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee"};
const BANDS=["red","orange","yellow","green","blue","indigo","violet"];
const MODES=["NULL","OPTICAL_ONLY","INTERACTION_TOY","THERMAL_CONFOUND"],TIMES=[1,10,60];
const sha=x=>crypto.createHash("sha256").update(x).digest("hex");
const digestBytes=x=>crypto.createHash("sha256").update(x).digest();
function canon(x){
 if(Array.isArray(x))return "["+x.map(canon).join(",")+"]";
 if(x!==null&&typeof x==="object")return "{"+Object.keys(x).sort().map(k=>JSON.stringify(k)+":"+canon(x[k])).join(",")+"}";
 return JSON.stringify(x);
}
function sourceRows(dir){
 const original=fs.readFileSync(path.join(dir,"base-evidence/lightbank-memories.json"));
 const bank=fs.readFileSync(path.join(dir,"rainbow-evidence/rainbow7-bank.jsonl"));
 const index=fs.readFileSync(path.join(dir,"rainbow-evidence/rainbow7-index.hbi"));
 assert.equal(sha(original),SHA.source);assert.equal(sha(bank),SHA.bank);assert.equal(sha(index),SHA.index);
 const originals=JSON.parse(original).records;
 const rows=new Map();
 for(const line of index.toString("ascii").trimEnd().split("\n")){
  const pieces=line.split("|");assert.equal(pieces[0],"MEM");assert.equal(pieces.length,6);
  const d=Object.fromEntries(pieces.slice(1).map(x=>x.split("=")));
  const site=Number(d.id.substring(5)),start=Number(d.offset),n=Number(d.length);
  const row=bank.subarray(start,start+n);assert.equal(sha(row),d.sha256);
  assert.deepEqual(JSON.parse(row).record,originals[site]);
  rows.set(d.band+"|"+site,d.sha256);
 }
 assert.equal(rows.size,567);return rows;
}
function sourceBit(rowsha){return digestBytes("ASOLARIA-R8-FROZEN-BIT|"+rowsha)[0]&1;}
function noise(band,site,delay,rep){
 const input="ASOLARIA-R8-COMMON-POTENTIAL-NOISE|"+SHA.bank+"|"+band+"|"+site+"|"+delay+"|"+rep;
 return Number(digestBytes(input).readBigUInt64BE(0)%1000n);
}
function p(mode,l,a){
 if(mode==="NULL")return 880;
 if(mode==="OPTICAL_ONLY")return 880-300*l;
 if(mode==="INTERACTION_TOY")return 880-40*(l+a)-340*l*a;
 if(mode==="THERMAL_CONFOUND")return 880-75*(l+a)**2;
 throw Error("MODE_UNKNOWN");
}
async function main(input,out){
 const rows=sourceRows(input);
 const results=JSON.parse(fs.readFileSync(path.join(out,"r8-results.json"),"ascii"));
 const trace=path.join(out,"r8-synthetic-factorial.jsonl");
 const hash=crypto.createHash("sha256"),counter=new Map();let n=0;
 const stream=fs.createReadStream(trace);
 const rl=readline.createInterface({input:stream,crlfDelay:Infinity});
 for await (const line of rl){
  const v=JSON.parse(line);
  assert.equal(line,canon(v),"CANONICAL_JSON_DRIFT");
  const mode=MODES[Math.floor(n/(3*7*81*8*4))],rem=n%(3*7*81*8*4);
  const delay=TIMES[Math.floor(rem/(7*81*8*4))];
  const r1=rem%(7*81*8*4),band=BANDS[Math.floor(r1/(81*8*4))];
  const r2=r1%(81*8*4),site=Math.floor(r2/(8*4));
  const rep=Math.floor(r2%32/4),aidx=r2%4;
  const [l,a]=[[0,0],[1,0],[0,1],[1,1]][aidx];
  assert.equal(v.schema,"ASOLARIA-SEAT4-R8-LIGHT-VIBRATION-SIMULATED-V1");
  assert.equal(v.simulation_only,true);
  assert.equal(v.regime,mode);assert.equal(v.delay_label_s,delay);
  assert.equal(v.band,band);assert.equal(v.site,site);assert.equal(v.rep,rep);
  assert.equal(v.light,l);assert.equal(v.acoustic,a);
  assert.equal(v.source_leaf_sha256,rows.get(band+"|"+site));
  assert.equal(v.source_bit,sourceBit(v.source_leaf_sha256));
  const success=noise(band,site,delay,rep)<p(mode,l,a);
  assert.equal(v.correct,Number(success));
  assert.equal(v.readout_bit,success?v.source_bit:1-v.source_bit);
  assert.equal(v.sim_optical_meter_nw,1000*l);
  assert.equal(v.sim_accelerometer_mg,100*a);
  assert.equal(v.sim_temperature_mK,mode==="THERMAL_CONFOUND"?25000+250*(l+a):25000);
  assert.equal(v.sim_supply_uV,3300000);
  assert.equal(v.actual_photons_measured,false);
  assert.equal(v.actual_phonons_measured,false);
  const group=mode+"|"+delay+"|"+l+a;
  counter.set(group,(counter.get(group)||0)+v.correct);
  hash.update(line+"\n");n++;
 }
 assert.equal(n,217728);
 const fullHash=hash.digest("hex");assert.equal(fullHash,results.trace_sha256);
 for(const mode of MODES)for(const delay of TIMES){
  const p00=counter.get(mode+"|"+delay+"|00")/(7*81*8);
  const p10=counter.get(mode+"|"+delay+"|10")/(7*81*8);
  const p01=counter.get(mode+"|"+delay+"|01")/(7*81*8);
  const p11=counter.get(mode+"|"+delay+"|11")/(7*81*8);
  const x=results.statistical_contrasts_by_regime_and_delay[mode][String(delay)];
  const check=(name,val)=>assert(Math.abs(x[name]-val)<=0.00000101,mode+" "+delay+" "+name);
  check("p_correct_00",p00);check("p_correct_10",p10);
  check("p_correct_01",p01);check("p_correct_11",p11);
  check("D_light",p10-p00);check("D_acoustic",p01-p00);
  check("D_interaction",p11-p10-p01+p00);
 }
 assert.equal(results.photonic_memory_verified,false);
 assert.equal(results.phononic_memory_verified,false);
 assert.equal(results.biological_neural_memory_verified,false);
 assert.equal(results.external_independent_instrument_custody,false);
 assert.equal(results.digital_negative_controls.length,13);
 for(const file of ["r8-synthetic-factorial.jsonl","r8-results.json","r8-results.hbp"]){
  const body=fs.readFileSync(path.join(out,file));
  assert.equal(fs.readFileSync(path.join(out,file+".sha256"),"ascii"),sha(body)+"  "+file+"\n");
 }
 const body=Buffer.from(canon({
  schema:"ASOLARIA-SEAT4-R8-INDEPENDENT-NODE-REFEREE-V1",
  full_trace_sha256:fullHash,independently_verified_rows:n,
  independently_verified_factorial_cells:counter.size,
  mechanism_confound_identifiable_from_synthetic_fixture:false,
  actual_photon_measurements:0,actual_phonon_measurements:0,
  classical_cpu_replay_pass:true})+"\n");
 fs.writeFileSync(path.join(out,"r8-independent-node.json"),body);
 fs.writeFileSync(path.join(out,"r8-independent-node.json.sha256"),sha(body)+"  r8-independent-node.json\n");
 process.stdout.write(JSON.stringify({status:"NODE_R8_SOURCE_REPLAY_PASS",rows:n,cells:counter.size,
  sha256:fullHash,independent_sha256:sha(body),physical:"HOLD"})+"\n");
}
if(process.argv.length!==4)throw Error("usage: node verify_factorial.js ORIGINAL_ARCHIVE OUT");
main(process.argv[2],process.argv[3]).catch(err=>{console.error(err);process.exitCode=1;});
