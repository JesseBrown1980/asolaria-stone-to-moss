#!/usr/bin/env node
"use strict";
/* Seat2 confirmatory post-hoc pin challenge. This Git-pinned fixture reference
   is NOT an independent external source signer or a physical measurement. */
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),assert=require("node:assert/strict");
const BANDS=["red","orange","yellow","green","blue","indigo","violet"],PORTS=[2,5,0,6,1,4,3];
const DOMAIN={SOURCE:"ASOLARIA-SEAT2-R8-SOURCE-V1\n",DETECTOR:"ASOLARIA-SEAT2-R8-OBS-V1\n",
 CHECKPOINT:"ASOLARIA-SEAT2-R8-CHECKPOINT-V1\n"};
const EXPECT_OBS=["schema","session","nonce","source_manifest_sha256","sequence","previous_hash","band",
 "port","sector","site","trial_id","detector_count","clock_label"];
const sha=x=>crypto.createHash("sha256").update(x).digest("hex");
function canon(x){
 if(Array.isArray(x))return "["+x.map(canon).join(",")+"]";
 if(x!==null&&typeof x==="object")return "{"+Object.keys(x).sort().map(k=>JSON.stringify(k)+":"+canon(x[k])).join(",")+"}";
 return JSON.stringify(x);
}
const enc=o=>Buffer.from(canon(o)+"\n","ascii"),digest=o=>sha(enc(o));
function testKey(role){
 const seed=crypto.createHash("sha256").update("ASOLARIA-R8-"+role+"-PUBLIC-TEST-FIXTURE-20261015").digest();
 const der=Buffer.concat([Buffer.from("302e020100300506032b657004220420","hex"),seed]);
 const key=crypto.createPrivateKey({key:der,format:"der",type:"pkcs8"});
 return key;
}
function publicHex(pri){
 return crypto.createPublicKey(pri).export({format:"der",type:"spki"}).subarray(-32).toString("hex");
}
function signature(role,key,payload){return {payload,signature:crypto.sign(null,Buffer.concat([
 Buffer.from(DOMAIN[role],"ascii"),enc(payload)]),key).toString("base64")};}
function genuine(role,pubHex,signed){
 try{
  const pk=crypto.createPublicKey({key:Buffer.concat([Buffer.from("302a300506032b6570032100","hex"),Buffer.from(pubHex,"hex")]),format:"der",type:"spki"});
  return crypto.verify(null,Buffer.concat([Buffer.from(DOMAIN[role],"ascii"),enc(signed.payload)]),
   pk,Buffer.from(signed.signature,"base64"));
 }catch{return false;}
}
function need(ok,why){if(!ok)throw new Error(why);}
const link=packet=>sha(Buffer.concat([Buffer.from("ASOLARIA-SEAT2-R8-LINK-V1\n","ascii"),enc(packet)]));
const genesis=source=>sha(Buffer.concat([Buffer.from("ASOLARIA-SEAT2-R8-GENESIS-V1\n","ascii"),enc(source)]));
const trial=(session,i)=>sha(Buffer.from("R8-OPAQUE-TRIAL-ID|"+session+"|"+i,"ascii")).slice(0,24);
function replay(source,frames,pub,pin,opts={}){
 need(genuine("SOURCE",pub.SOURCE,source),"SOURCE_SIGNATURE");
 const s=source.payload;
 need(s.session===pin.expected_session&&s.nonce===(opts.override_nonce??pin.expected_nonce)&&
 s.source_root===pin.expected_source_root&&s.bank_root===pin.expected_bank_root,
 "PINNED_SOURCE_NONCE");
 need(canon(s.bands)===canon(BANDS)&&canon(s.ports)===canon(PORTS)&&s.sectors===27,
 "PINNED_PORT_MAP");
 need(frames.length===4,"INCOMPLETE_HISTORY");
 let prev=genesis(source);
 for(let i=0;i<4;i++){
  const signed=frames[i],p=signed.payload;
  need(genuine("DETECTOR",pub.DETECTOR,signed),"DETECTOR_SIGNATURE");
  need(canon(Object.keys(p).sort())===canon([...EXPECT_OBS].sort()),"DETECTOR_SCHEMA_LEAK");
  need(p.schema==="ASOLARIA-R8-SIGNED-OBS-V1"&&p.session===s.session&&p.nonce===s.nonce&&
       p.source_manifest_sha256===digest(source),"DETECTOR_SOURCE_CONTEXT");
  need(p.sequence===i+1,"SEQUENCE_REPLAY");
  need(p.previous_hash===prev,"CHAIN_PREDECESSOR");
  need(p.band===BANDS[i]&&p.port===PORTS[i]&&p.site===i&&p.sector===[0,6,18,26][i]&&
       p.trial_id===trial(pin.expected_session,i),"CHANNEL_ORDER_TRIAL");
  need(Number.isInteger(p.detector_count)&&p.detector_count>=0&&p.detector_count<=4096&&
       p.clock_label==="SYNTHETIC-TIME-NOT-ELAPSED-SEC","NOT_CALIBRATED_SENSOR");
  prev=link(signed);
 }
 need(frames[3].payload.sequence>(opts.watermark??0),"DURABLE_REPLAY_CHECKPOINT");
 if(opts.use_tip!==false)need(prev===pin.expected_chain_tip,"PINNED_CHAIN_HEAD");
 return prev;
}
function doAudit(dir,pinPath){
 const pin=JSON.parse(fs.readFileSync(pinPath)),fixtureRaw=fs.readFileSync(path.join(dir,"fixture.json"));
 const fixture=JSON.parse(fixtureRaw);
 need(pin.provenance==="POSTHOC_FROZEN_FROM_FIRST_GREEN_CI_NOT_INDEPENDENT_CUSTODY",
     "PIN_PROVENANCE_IS_NOT_EXTERNAL_CUSTODY");
 need(sha(fixtureRaw)===pin.expected_fixture_sha256,"FROZEN_FIXTURE_BYTES");
 const pub=fixture.public_fixture_keys;
 const keys={};
 for(const role of Object.keys(DOMAIN)){keys[role]=testKey(role);need(publicHex(keys[role])===pub[role],"WRONG_FIXTURE_KEY");}
 const good=fixture.signed_good_frames,fork=fixture.signed_competing_fork,source=fixture.signed_source;
 const originalTip=replay(source,good,pub,pin);
 const forkTip=replay(source,fork,pub,pin,{use_tip:false});
 need(originalTip===pin.expected_chain_tip && originalTip!==forkTip,"EXPECTED_TWO_HISTORIES");
 const fails=[];
 const held=(label,act,cause)=>{
  try{act();}catch(e){need(e.message===cause,label+"_WRONG_FAILURE_STAGE_"+e.message);fails.push(label);return;}
  throw new Error("FAIL_OPEN_"+label);
 };
 held("signed_fork_against_pinned_head",()=>replay(source,fork,pub,pin),"PINNED_CHAIN_HEAD");
 held("old_session_against_durable_checkpoint",()=>replay(source,good,pub,pin,{watermark:pin.durable_external_last_sequence_for_replay_test}),"DURABLE_REPLAY_CHECKPOINT");
 held("new_verifier_challenge_rejects_old_session",()=>replay(source,good,pub,pin,{override_nonce:"UNPREDICTABLE_EXTERNAL_HYPOTHESIS"}),"PINNED_SOURCE_NONCE");
 need(replay(source,good,pub,pin,{watermark:0})===originalTip,"TEST_BASELINE");
 fails.push("restored_local_ledger_accepts_old_signed_session");
 const changedManifest=JSON.parse(JSON.stringify(source.payload));
 changedManifest.source_root="f".repeat(64);
 const signedChanged=signature("SOURCE",keys.SOURCE,changedManifest);
 held("signed_alternate_source_root",()=>replay(signedChanged,good,pub,pin),"PINNED_SOURCE_NONCE");
 const swapped=JSON.parse(JSON.stringify(source.payload));
 swapped.ports=[...PORTS].reverse();
 const signedSwap=signature("SOURCE",keys.SOURCE,swapped);
 held("signed_alternate_port_map",()=>replay(signedSwap,good,pub,pin),"PINNED_PORT_MAP");
 function mutate(label,index,change,why,resign=true){
  const alt=JSON.parse(JSON.stringify(good)),p=alt[index].payload;
  change(p);
  if(resign)alt[index]=signature("DETECTOR",keys.DETECTOR,p);
  held(label,()=>replay(source,alt,pub,pin),why);
 }
 mutate("re_signed_source_answer_leak",0,p=>{p.precommitted_bit=1;},"DETECTOR_SCHEMA_LEAK");
 mutate("re_signed_public_source_seed_leak",0,p=>{p.public_bit_seed="known";},"DETECTOR_SCHEMA_LEAK");
 mutate("re_signed_trial_id",0,p=>{p.trial_id="f".repeat(24);},"CHANNEL_ORDER_TRIAL");
 mutate("re_signed_wrong_channel",0,p=>{p.port=1;},"CHANNEL_ORDER_TRIAL");
 mutate("unsigned_detector_value_change",0,p=>{p.detector_count=100;},
        "DETECTOR_SIGNATURE",false);
 mutate("signed_wrong_source_digest",0,p=>{p.source_manifest_sha256="0".repeat(64);},
        "DETECTOR_SOURCE_CONTEXT");
 mutate("signed_broken_chain",1,p=>{p.previous_hash="0".repeat(64);},
        "CHAIN_PREDECESSOR");
 held("missing_signed_frame",()=>replay(source,good.slice(0,3),pub,pin),"INCOMPLETE_HISTORY");
 held("reordered_signed_frames",()=>replay(source,[good[1],good[0],good[2],good[3]],pub,pin),"SEQUENCE_REPLAY");
 // Key fixture compromise: forged signed checkpoint verifies cryptographically but
 // is inconsistent with separately pinned ORIGINAL head.
 const cp=fixture.signed_checkpoint,wrong=JSON.parse(JSON.stringify(cp.payload));
 wrong.tip_sha256=forkTip;
 const forgedCp=signature("CHECKPOINT",keys.CHECKPOINT,wrong);
 need(genuine("CHECKPOINT",pub.CHECKPOINT,forgedCp),"COMPROMISED_FIXTURE_SIGNATURE_EXPECTED");
 held("signed_checkpoint_replacing_original",()=>need(
   forgedCp.payload.tip_sha256===pin.expected_chain_tip,"PINNED_CHAIN_HEAD"),"PINNED_CHAIN_HEAD");
 need(fails.length===16,"NEGATIVE_COVERAGE="+fails.length);
 const result={schema:"ASOLARIA-SEAT2-R8-POSTHOC-EXTERNAL-PINS-NODE-V1",
     output_type:"DETERMINISTIC_DIGITAL_PROTOCOL_FALSIFICATION",
     first_hosted_producer_run:pin.producing_run_id,
     pin_provenance:pin.provenance,original_signed_chain_head:originalTip,
     competing_valid_signed_chain_head:forkTip,case_count:fails.length,
     cases:fails,conditionally_held_from_versioned_pin:true,
     remote_independent_custody_measured:false,
     real_sensor_source_authenticated:false,physical_photon_retention_measured:false};
 const data=enc(result);
 fs.writeFileSync(path.join(dir,"external-referee.json"),data);
 fs.writeFileSync(path.join(dir,"external-referee.json.sha256"),sha(data)+"  external-referee.json\n");
 console.log("SEAT2_R8_EXTERNAL_PIN_CONFIRMATORY_PASS",fails.length,sha(data));
}
if(process.argv.length!==4)throw Error("usage: node verify_external_checkpoint.js FIXTURE_OUTPUT PINNED_BASELINE");
doAudit(process.argv[2],process.argv[3]);
