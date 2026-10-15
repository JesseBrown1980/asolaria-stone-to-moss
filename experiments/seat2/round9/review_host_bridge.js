#!/usr/bin/env node
"use strict";
/* Separate Node22 source/output reviewer. OS metric integrity is only
   self-report consistency; this is NOT trusted power meter attestation. */
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),assert=require("node:assert/strict");
const SOURCE_SHA="077bf98dc7c10e3125ce1147270cc927ce978ab63a19ec30e4655267f1770400";
const BANK_SHA="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345";
const SOURCE_COMMIT="5d3e3a1147ad7af84c1b5b1ba482dfddd9832c86";
const SOURCE_REL="stones/2026-10-15-rainbow81/seat4-round5-signed-spectrum-mapping-20261015.hbp";
const CHANNELS=["mains_ac_voltage_v","dc_supply_voltage_v","device_current_a","device_power_w",
 "ground_potential_v","optical_spectral_counts","acoustic_displacement_m",
 "physical_optical_retention_bits"];
const hash=x=>crypto.createHash("sha256").update(x).digest("hex");
function canon(o){
 if(Array.isArray(o))return "["+o.map(canon).join(",")+"]";
 if(o!==null&&typeof o==="object")return "{"+Object.keys(o).sort().map(k=>JSON.stringify(k)+":"+canon(o[k])).join(",")+"}";
 return JSON.stringify(o);
}
function audit(frozen,out){
 const source=fs.readFileSync(path.join(frozen,SOURCE_REL));
 assert.equal(source.length,701);assert.equal(hash(source),SOURCE_SHA);
 assert(source.toString("ascii").includes(BANK_SHA));
 const files=["digital.json","host-activity.json","instrument-status.json"];
 for(const name of files){
  const raw=fs.readFileSync(path.join(out,name));
  const body=JSON.parse(raw);
  assert.equal(raw.toString("ascii"),canon(body)+"\n","NON_CANONICAL_"+name);
  assert.equal(fs.readFileSync(path.join(out,name+".sha256"),"ascii"),
    hash(raw)+"  "+name+"\n","BAD_SHA_SIDECAR_"+name);
 }
 const digital=JSON.parse(fs.readFileSync(path.join(out,"digital.json")));
 const host=JSON.parse(fs.readFileSync(path.join(out,"host-activity.json")));
 const instr=JSON.parse(fs.readFileSync(path.join(out,"instrument-status.json")));
 assert.equal(digital.source_sha256,SOURCE_SHA);
 assert.equal(digital.source_git_commit,SOURCE_COMMIT);
 assert.equal(digital.original_bank_sha256_as_declared_in_hbp,BANK_SHA);
 assert.equal(digital.input_file_bytes,source.length);
 assert.equal(digital.hash_loops,256);
 assert.equal(digital.deterministic_payload_size_bytes,2*1024*1024);
 const payload=Buffer.alloc(digital.deterministic_payload_size_bytes);
 for(let i=0;i<payload.length;i+=source.length){
  source.copy(payload,i,0,Math.min(source.length,payload.length-i));
 }
 assert.equal(hash(payload),digital.deterministic_payload_sha256);
 const h=crypto.createHash("sha256"),idx=Buffer.alloc(4);
 for(let n=0;n<256;n++){
  idx.writeUInt32LE(n,0);
  h.update(payload);h.update(idx);
 }
 const recomputed=h.digest("hex");
 assert.equal(recomputed,digital.deterministic_workload_sha256);
 assert.equal(digital.physical_optical_storage_measured,false);
 assert.deepEqual(digital.negative_controls,
   ["zero_cpu","backward_wall","source_root_switch","missing_runner_identity",
    "negative_host_rss","untouched_memory","fake_optical_detector",
    "fake_current_meter","false_photon_retention"]);
 assert.equal(host.schema,"ASOLARIA-SEAT2-R9-REAL-OS-PROCESS-METRICS-V1");
 assert.equal(host.source_sha256,SOURCE_SHA);assert.equal(host.source_commit,SOURCE_COMMIT);
 assert(/^[0-9a-f]{40}$/.test(host.producing_git_sha));assert(/^\d+$/.test(host.github_run_id));
 assert(["Linux","Windows"].includes(host.runner_os));
 assert(["Linux","Windows"].includes(host.platform_system));
 assert(Number.isInteger(host.process_pid)&&host.process_pid>0);
 assert(Number.isInteger(host.wall_elapsed_ns)&&host.wall_elapsed_ns>0);
 assert(Number.isInteger(host.cpu_elapsed_ns)&&host.cpu_elapsed_ns>0);
 assert(Number.isInteger(host.rss_before_bytes)&&host.rss_before_bytes>0);
 assert(Number.isInteger(host.rss_during_bytes)&&host.rss_during_bytes-host.rss_before_bytes>=1024*1024);
 assert(Number.isInteger(host.rss_after_work_bytes)&&host.rss_after_work_bytes>0);
 assert(host.rss_during_bytes>=host.rss_after_work_bytes-1024*1024);
 assert.equal(host.memory_allocated_bytes,24*1024*1024);
 assert.equal(host.memory_pages_touched,6144);
 assert(Number.isFinite(Date.parse(host.wall_utc_start)));
 assert(Number.isFinite(Date.parse(host.wall_utc_end)));
 assert(Date.parse(host.wall_utc_end)>=Date.parse(host.wall_utc_start));
 assert.equal(host.measurement_type,"OS_PROCESS_COUNTERS_NOT_INSTRUMENTED_RAIL_POWER");
 assert.equal(instr.schema,"ASOLARIA-SEAT2-R9-INSTRUMENT-MEASUREMENT-STATUS-V1");
 assert.deepEqual(Object.keys(instr.channels).sort(),[...CHANNELS].sort());
 for(const name of CHANNELS){
  assert.deepEqual(instr.channels[name],
   {measured:false,value:null,instrument_id:null,raw_capture_sha256:null});
 }
 assert.equal(instr.externally_attested_instrument_data,false);
 assert.equal(instr.optical_retention_measured,false);
 assert.equal(instr.biological_neural_memory_measured,false);
 const review={
  schema:"ASOLARIA-SEAT2-R9-INDEPENDENT-NODE-SOURCE-AND-HOST-REVIEW-V1",
  classification:"ACTUAL_OS_PROCESS_COUNTERS_PLUS_VERIFIED_DIGITAL_SOURCE_NOT_SENSOR_POWER",
  source_sha256:SOURCE_SHA,original_bank_sha256_reference_only:BANK_SHA,
  digital_sha256:hash(fs.readFileSync(path.join(out,"digital.json"))),
  deterministic_workload_sha256:recomputed,
  raw_source_bytes_sha256:hash(source),reviewed_host_counter_schema:true,
  positive_measured_process_cpu_time:true,positive_measured_elapsed_time:true,
  observed_memory_working_set_increase_over_1MiB:true,
  raw_host_values_are_not_expected_byte_identical_between_OS:true,
  electric_power_watts_measured:false,photons_detected:false,stored_photons_read:false,
  no_independent_host_hardware_attestation:true,physics_claim:"HOST_PROCESS_ACTIVITY_OBSERVED"
 };
 const raw=Buffer.from(canon(review)+"\n","ascii");
 fs.writeFileSync(path.join(out,"node-review.json"),raw);
 fs.writeFileSync(path.join(out,"node-review.json.sha256"),hash(raw)+"  node-review.json\n");
 console.log("R9_INDEPENDENT_DIGITAL_AND_OS_COUNTER_REVIEW_PASS",recomputed,hash(raw));
}
if(process.argv.length!==4)throw Error("usage: node review_host_bridge.js FROZEN_MAIN OUTPUT");
audit(process.argv[2],process.argv[3]);
