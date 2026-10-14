#!/usr/bin/env node
"use strict";
/* Independent Node.js + Windows implementation of cross-host 81-body SHA portal. */
const crypto = require("node:crypto");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const TAG = "ASOLARIA-81-CROSS-HOST-PORTAL-V1";
const fields = ["HBI", "HBP", "SHA", "SH", "HASH"];
function H(...items) {
  const hash = crypto.createHash("sha256");
  for (const v of items) {
    const bytes=Buffer.from(String(v),"utf8");
    const frame=Buffer.alloc(8);
    frame.writeBigUInt64BE(BigInt(bytes.length));
    hash.update(frame);
    hash.update(bytes);
  }
  return hash.digest("hex");
}
function assert(condition, message) {
  if (!condition) throw Error(message || "assertion failed");
}
function build(challenge) {
  const nonce = challenge.nonce;
  assert(challenge.protocol===TAG, "protocol mismatch");
  assert(/^[0-9a-f]{32}$/.test(nonce), "bad challenge nonce");
  assert(JSON.stringify(challenge.targets)===JSON.stringify([0,1,2,3,9,13,17,25,26]), "targets");
  assert(JSON.stringify(challenge.scales)===JSON.stringify([1,1000000,1000000000]), "scales");
  const ids=Array.from({length:27}, (_,i)=>H("ASOLARIA|ID|HOST-CROSS-V1",i,Math.floor(i/3),i%3));
  const state=ids.map(id=>H("ASOLARIA|BODY|STATE0",id));
  assert(new Set(ids).size===27, "identity duplicate");
  function derived(states) {
    const root=H("ASOLARIA|SOURCE-ROOT", ...states);
    const cells=[];
    for (const id of ids) {
      for (const direction of [-1,0,1]) {
        cells.push(fields.map(label=>H("ASOLARIA|CELL|"+label,root,id,direction)));
      }
    }
    return {root,cells,final:H("ASOLARIA|81-CELL-ROOT",...cells.flat())};
  }
  const base=derived(state);
  let rows=["PORTAL|schema="+TAG+"|challenge="+nonce+"|json=0",
    "BASE|source="+base.root+"|cells_root="+base.final+"|count=81|json=0"];
  challenge.targets.forEach((target,idx)=>{
    const changed=state.slice();
    changed[target]=H("ASOLARIA|MUTATION",state[target],nonce,target);
    const post=derived(changed);
    let fieldDiff=0,cellDiff=0;
    for (let c=0;c<81;c++){
      let cellChanged=false;
      for(let j=0;j<5;j++){
        if(base.cells[c][j]!==post.cells[c][j]){
          fieldDiff++;cellChanged=true;
        }
      }
      if(cellChanged)cellDiff++;
    }
    assert(cellDiff===81&&fieldDiff===405,"fanout mismatch");
    assert(post.root!==base.root&&post.final!==base.final,"no global change");
    challenge.scales.forEach((scale,index)=>{
      rows.push("WAVE|id="+(idx*3+index)+"|leaf="+target+"|scale="+scale+
                "|source="+post.root+"|root="+post.final+"|cell_changes="+cellDiff+
                "|register_changes="+fieldDiff+"|local_change=1|json=0");
    });
  });
  rows.push("END|waves=27|bodies=81|changes_per_wave=405|json=0");
  return rows.join("\n")+"\n";
}
function main() {
  const challengePath=process.argv[2];
  const outputDir=process.argv[3];
  assert(challengePath&&outputDir,"usage: node script.js challenge.json out_dir");
  fs.mkdirSync(outputDir,{recursive:true});
  const challengeBytes=fs.readFileSync(challengePath);
  const challenge=JSON.parse(challengeBytes.toString("utf8"));
  const start=new Date().toISOString();
  const result=Buffer.from(build(challenge),"utf8");
  fs.writeFileSync(path.join(outputDir,"results.hbp"),result);
  const fingerprint=crypto.createHash("sha256").update(result).digest("hex");
  const meta={
    schema:TAG,source_implementation:"independent_Node_crypto",
    lang:"node",runtime:process.version,
    os:process.env.RUNNER_OS||process.platform,
    runner_name:process.env.RUNNER_NAME||os.hostname(),
    hostname:os.hostname(),architecture:os.arch(),
    started_utc:start,ended_utc:new Date().toISOString(),
    run_id:process.env.GITHUB_RUN_ID||"local",
    git_sha:process.env.GITHUB_SHA||"",
    challenge_sha256:crypto.createHash("sha256").update(challengeBytes).digest("hex"),
    result_sha256:fingerprint,body_count:81,wave_count:27,
    evidence_class:"public GitHub hosted runner or explicitly described local host; software hashes only"
  };
  fs.writeFileSync(path.join(outputDir,"host.json"),JSON.stringify(meta,null,2)+"\n");
  console.log(JSON.stringify({result_sha256:fingerprint,waves:27,runner:meta.runner_name,os:meta.os}));
}
main();
