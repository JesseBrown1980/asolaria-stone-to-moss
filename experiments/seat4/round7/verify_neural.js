#!/usr/bin/env node
"use strict";
/* Independently written Node22 archived source+LIF crosscheck. No python imports. */
const fs=require("node:fs"),crypto=require("node:crypto"),assert=require("node:assert/strict"),path=require("node:path");
const digest=x=>crypto.createHash("sha256").update(x).digest("hex");
const MODES=["bright_t0","dim_t0","bright_t3","dark_t0","protected_t3"];
const SHA={bank:"52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345",idx:"6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee",hbp:"332e1eeb2d4de748c2e1da07729944fefe5b63589e9533b4c93b74d7cf3f5527"};
function lif(raw){
 let charge=0,window=0;const spikes=[];
 for(let k=0;k<raw.length*8;k++){
  const bit=(raw[k>>3]>>(7-k%8))&1;
  charge=Math.max(0,charge-1)+4*bit;
  if(charge>=7){charge-=7;window++;}
  if(k%32===31){spikes.push(window);window=0;}
 }
 if(raw.length*8%32)spikes.push(window);
 return Buffer.from(spikes);
}
function main(upstream,out){
 const bank=fs.readFileSync(path.join(upstream,"rainbow-evidence/rainbow7-bank.jsonl"));
 const idx=fs.readFileSync(path.join(upstream,"rainbow-evidence/rainbow7-index.hbi"));
 const raw=fs.readFileSync(path.join(upstream,"py-photon/photon-electron.hbp"));
 assert.equal(digest(bank),SHA.bank);assert.equal(digest(idx),SHA.idx);
 assert.equal(digest(raw),SHA.hbp);
 const entries=[];
 for(const line of idx.toString("ascii").trimEnd().split("\n")){
  const chunks=line.split("|");assert.equal(chunks[0],"MEM");
  const f=Object.fromEntries(chunks.slice(1).map(x=>x.split("=")));
  const stored=bank.subarray(Number(f.offset),Number(f.offset)+Number(f.length));
  assert.equal(digest(stored),f.sha256);
  entries.push({blob:stored,sha:f.sha256,band:f.band,id:f.id});
 }
 assert.equal(entries.length,567);
 const lines=raw.toString("ascii").trimEnd().split("\n");assert.equal(lines.length,2835);
 const counts=Array.from({length:5},()=>({match:0,exact:0,false_green:0}));
 const hbp=[];
 for(let i=0;i<lines.length;i++){
  const frame=JSON.parse(lines[i]),mode=MODES[Math.floor(i/567)],ordinal=i%567,orig=entries[ordinal];
  const obs=Buffer.from(frame.readback_hex,"hex");
  assert.equal(frame.scenario,mode);assert.equal(frame.ordinal,ordinal);
  assert.equal(frame.site,orig.id);assert.equal(frame.band,orig.band);
  assert.equal(frame.expected_row_sha256,orig.sha);
  assert.equal(digest(obs),frame.observed_row_sha256);
  let errors=0;
  assert.equal(obs.length,orig.blob.length);
  for(let j=0;j<obs.length;j++){
   let value=obs[j]^orig.blob[j];
   while(value){errors++;value&=value-1;}
  }
  assert.equal(frame.bit_errors,errors);
  const a=lif(obs).equals(lif(orig.blob)),b=digest(obs)===orig.sha;
  counts[Math.floor(i/567)].match+=Number(a);
  counts[Math.floor(i/567)].exact+=Number(b);
  counts[Math.floor(i/567)].false_green+=Number(a&&!b);
  hbp.push("REC|mode="+mode+"|id="+String(ordinal).padStart(3,"0")+"|neural="+Number(a)+"|source="+Number(b)+"|errors="+errors+"|source_sha="+orig.sha+"|observed_sha="+digest(obs)+"\n");
 }
 const actual=Buffer.from(hbp.join(""));
 assert(actual.equals(fs.readFileSync(path.join(out,"seat4-r7-trace.hbp"))),"CROSS_PROGRAM_FULL_TRACE_DISAGREEMENT");
 const summary=JSON.parse(fs.readFileSync(path.join(out,"seat4-r7-results.json"),"ascii"));
 assert.deepEqual(counts.map(x=>x.match),summary.neural_matches);
 assert.deepEqual(counts.map(x=>x.exact),summary.byte_exact_reads);
 assert.deepEqual(counts.map(x=>x.false_green),summary.neural_false_green);
 assert.deepEqual(counts.map(x=>x.false_green),[0,0,27,89,0]);
 assert.equal(summary.synthetic_physical_spoof_results.synthetic_plausible_5103_record_claim,"PHYSICAL_HOLD");
 assert.equal(summary.actual_photons_measured,false);
 assert.equal(summary.biological_neurons_measured,false);
 assert.equal(summary.full_trace_sha256,digest(actual));
 console.log(JSON.stringify({status:"NODE_INDEPENDENT_PASS",frames:lines.length,neural:counts.map(x=>x.match),
 false_green:counts.map(x=>x.false_green),strict:counts.map(x=>x.exact),trace_sha256:digest(actual)}));
}
if(process.argv.length!==4)throw Error("usage: node referee.js ARTIFACT OUTPUT");
main(process.argv[2],process.argv[3]);
