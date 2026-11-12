#!/usr/bin/env node
"use strict";
/* Independently authored Node22 verification of Seat2 R8 synthetic signed histories. */
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),assert=require("node:assert/strict");
const BANDS=["red","orange","yellow","green","blue","indigo","violet"];
const PORTS=[2,5,0,6,1,4,3];
const ROOT="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22";
const BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345";
const SESSION="SEAT2-R8-DIGITAL-FIXTURE-SESSION-20261015";
const NONCE="SEAT2-R8-PUBLIC-NONCE-NOT-EXTERNAL-FRESHNESS";
const DOMAIN={SOURCE:"ASOLARIA-SEAT2-R8-SOURCE-V1\n",DETECTOR:"ASOLARIA-SEAT2-R8-OBS-V1\n",
              CHECKPOINT:"ASOLARIA-SEAT2-R8-CHECKPOINT-V1\n"};
const OBFIELDS=["schema","session","nonce","source_manifest_sha256","sequence","previous_hash",
                "band","port","sector","site","trial_id","detector_count","clock_label"];
const hash=x=>crypto.createHash("sha256").update(x).digest("hex");
function canonical(v){
 if(Array.isArray(v))return "["+v.map(canonical).join(",")+"]";
 if(v!==null && typeof v==="object")return "{"+Object.keys(v).sort().map(k=>JSON.stringify(k)+":"+canonical(v[k])).join(",")+"}";
 return JSON.stringify(v);
}
const enc=obj=>Buffer.from(canonical(obj)+"\n","ascii");
const digest=obj=>hash(enc(obj));
function key(role){
 const seed=crypto.createHash("sha256").update("ASOLARIA-R8-"+role+"-PUBLIC-TEST-FIXTURE-20261015").digest();
 const pem=Buffer.concat([Buffer.from("302e020100300506032b657004220420","hex"),seed]);
 const pri=crypto.createPrivateKey({key:pem,format:"der",type:"pkcs8"});
 const publicRaw=crypto.createPublicKey(pri).export({format:"der",type:"spki"}).subarray(-32).toString("hex");
 return publicRaw;
}
function verify(role,publicHex,signed){
 try{
  const pk=crypto.createPublicKey({key:Buffer.concat([Buffer.from("302a300506032b6570032100","hex"),Buffer.from(publicHex,"hex")]),format:"der",type:"spki"});
  return crypto.verify(null,Buffer.concat([Buffer.from(DOMAIN[role],"ascii"),enc(signed.payload)]),
         pk,Buffer.from(signed.signature,"base64"));
 }catch{return false;}
}
const link=packet=>hash(Buffer.concat([Buffer.from("ASOLARIA-SEAT2-R8-LINK-V1\n","ascii"),enc(packet)]));
const genesis=source=>hash(Buffer.concat([Buffer.from("ASOLARIA-SEAT2-R8-GENESIS-V1\n","ascii"),enc(source)]));
const trial=i=>hash(Buffer.from("R8-OPAQUE-TRIAL-ID|"+SESSION+"|"+i,"ascii")).slice(0,24);
function verified(source,frames,publicKeys){
 assert(verify("SOURCE",publicKeys.SOURCE,source),"BAD_SOURCE_SIGNATURE");
 const m=source.payload;
 assert.equal(m.schema,"ASOLARIA-R8-SIGNED-SOURCE-V1");assert.equal(m.session,SESSION);
 assert.equal(m.nonce,NONCE);assert.equal(m.source_root,ROOT);assert.equal(m.bank_root,BANK);
 assert.equal(m.sectors,27);assert.deepEqual(m.bands,BANDS);assert.deepEqual(m.ports,PORTS);
 assert.equal(frames.length,4);
 let previous=genesis(source);
 for(let i=0;i<4;i++){
  const x=frames[i];assert(verify("DETECTOR",publicKeys.DETECTOR,x),"BAD_DETECTOR_SIGNATURE");
  const p=x.payload;
  assert.deepEqual(Object.keys(p).sort(),[...OBFIELDS].sort(),"LEAKY_OR_UNEXPECTED_DETECTOR_FIELD");
  assert.equal(p.schema,"ASOLARIA-R8-SIGNED-OBS-V1");
  assert.equal(p.session,SESSION);assert.equal(p.nonce,NONCE);
  assert.equal(p.source_manifest_sha256,digest(source));
  assert.equal(p.sequence,i+1);assert.equal(p.previous_hash,previous);
  assert.equal(p.band,BANDS[i]);assert.equal(p.port,PORTS[i]);
  assert.equal(p.sector,[0,6,18,26][i]);assert.equal(p.site,i);
  assert.equal(p.trial_id,trial(i));
  assert.equal(p.clock_label,"SYNTHETIC-TIME-NOT-ELAPSED-SEC");
  assert(Number.isInteger(p.detector_count)&&p.detector_count>=0&&p.detector_count<=4096);
  previous=link(x);
 }
 return previous;
}
function main(folder){
 const fx=fs.readFileSync(path.join(folder,"fixture.json"));
 const raw=fs.readFileSync(path.join(folder,"results.json"));
 assert.equal(fx.toString("ascii"),canonical(JSON.parse(fx.toString("ascii")))+"\n");
 assert.equal(raw.toString("ascii"),canonical(JSON.parse(raw.toString("ascii")))+"\n");
 const f=JSON.parse(fx),r=JSON.parse(raw),pub=f.public_fixture_keys;
 for(const role of Object.keys(DOMAIN)){
  assert.equal(pub[role],key(role),"PUBLIC_FIXTURE_KEY_DERIVATION_CHANGED_"+role);
 }
 assert.equal(f.source_anchor_from_caller,ROOT);assert.equal(f.bank_anchor_from_caller,BANK);
 const good=verified(f.signed_source,f.signed_good_frames,pub);
 const fork=verified(f.signed_source,f.signed_competing_fork,pub);
 assert.notEqual(good,fork);
 assert.equal(good,f.external_expected_tip);
 assert.equal(f.signed_checkpoint.payload.tip_sha256,good);
 assert.equal(digest(f.signed_checkpoint),f.externally_pinned_checkpoint_sha256);
 assert(verify("CHECKPOINT",pub.CHECKPOINT,f.signed_checkpoint));
 assert.equal(f.signed_checkpoint.payload.last_sequence,4);
 assert.deepEqual(f.signed_good_frames.slice(0,2),f.signed_competing_fork.slice(0,2));
 assert.notDeepEqual(f.signed_good_frames[2],f.signed_competing_fork[2]);
 assert.equal(r.signed_fixture_sha256,hash(fx));
 assert.equal(r.cases_executed,19);
 assert.equal(r.same_session_signed_fork_accepted_without_external_tip,true);
 assert.equal(r.fork_rejected_with_fixed_external_tip,true);
 assert.equal(r.reset_local_replay_possible,true);
 assert.equal(r.persisted_external_checkpoint_rejects_replay,true);
 assert.equal(r.external_source_authenticated,false);
 assert.equal(r.real_optical_retention_measured,false);
 assert.equal(r.biological_neural_memory_measured,false);
 for(const name of ["fixture.json","results.json"]){
  const data=fs.readFileSync(path.join(folder,name));
  assert.equal(fs.readFileSync(path.join(folder,name+".sha256"),"ascii"),hash(data)+"  "+name+"\n");
 }
 const output={schema:"ASOLARIA-SEAT2-R8-INDEPENDENT-NODE-V1",
     status:"DIGITAL_SIGNATURE_CHAIN_VERIFICATION_PASS",
     source_manifest_sha256:digest(f.signed_source),
     original_chain_tip:good,competing_chain_tip:fork,
     published_fixture_public_keys_match:true,
     both_signed_histories_valid:true,
     signed_checkpoint_matches_baseline_fixture:true,
     replay_rejected_without_real_external_log:false,
     real_photon_observations:0,external_custodian_attested:false,
     fixture_sha256:hash(fx)};
 const out=enc(output);
 fs.writeFileSync(path.join(folder,"independent-node.json"),out);
 fs.writeFileSync(path.join(folder,"independent-node.json.sha256"),hash(out)+"  independent-node.json\n");
 console.log("SEAT2_R8_NODE_PASS",good,fork,hash(out));
}
if(process.argv.length!==3)throw Error("usage: node verify_fork.js OUTPUT_DIR");
main(process.argv[2]);
