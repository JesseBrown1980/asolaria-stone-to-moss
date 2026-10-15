#!/usr/bin/env node
"use strict";
/* Independent host/workload source auditor, not an electrical wattmeter. */
const fs=require("node:fs"),crypto=require("node:crypto"),path=require("node:path"),assert=require("node:assert/strict");
const BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345";
const SOURCE="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22";
const sha=x=>crypto.createHash("sha256").update(x).digest("hex");
function main(src,out){
 const bank=fs.readFileSync(path.join(src,"rainbow-evidence/rainbow7-bank.jsonl"));
 const source=fs.readFileSync(path.join(src,"base-evidence/lightbank-memories.json"));
 assert.equal(bank.length,184815);assert.equal(sha(bank),BANK);
 assert.equal(sha(source),SOURCE);
 const work=crypto.createHash("sha256");
 for(let i=0;i<4096;i++)work.update(bank);
 const digest=work.digest("hex");
 const science=JSON.parse(fs.readFileSync(path.join(out,"r9-science.json"),"ascii"));
 const host=JSON.parse(fs.readFileSync(path.join(out,"r9-host.json"),"ascii"));
 assert.equal(science.source_bank_sha256,BANK);
 assert.equal(science.source_records_sha256,SOURCE);
 assert.equal(science.workload_sha256,digest);
 assert.equal(science.original_bank_bytes_processed,184815*4096);
 assert.equal(science.hash_iterations,4096);
 assert.equal(host.source_bank_sha256,BANK);
 assert.equal(host.workload_sha256,digest);
 for(const prop of ["host_process_cpu_time_ns_OS","monotonic_elapsed_ns_OS",
   "tracemalloc_peak_python_allocation_bytes","scratch_allocation_bytes"]){
   assert(Number.isInteger(host[prop])&&host[prop]>0,"COUNTER_MISSING:"+prop);
 }
 assert(host.tracemalloc_peak_python_allocation_bytes>=4*1024*1024);
 assert(host.wall_end_time_unix_ns_OS>host.wall_start_time_unix_ns_OS);
 assert.equal(host.measured_ac_wall_energy_joules,null);
 assert.equal(host.measured_dc_rail_voltage_volts,null);
 assert.equal(host.measured_dc_current_amperes,null);
 assert.equal(host.measured_optical_photon_counts,null);
 assert.equal(host.measured_acoustic_phonon_counts,null);
 assert.equal(host.spectrometer_raw_sha256,null);
 assert.equal(science.actual_optical_detector_instrumented,false);
 assert.equal(science.actual_electrical_energy_instrumented,false);
 for(const name of ["r9-science.json","r9-host.json"]){
  const bytes=fs.readFileSync(path.join(out,name));
  const sidecar=fs.readFileSync(path.join(out,name+".sha256"),"ascii");
  assert.equal(sidecar,sha(bytes)+"  "+name+"\n");
 }
 const report={schema:"ASOLARIA-SEAT4-R9-INDEPENDENT-NODE-REPLAY-V1",
  source_bank_sha256:BANK,science_workload_sha256:digest,
  iteration_count:4096,verified_bytes:184815*4096,
  source_replacement_rejected:true,
  host_telemetry_present:true,
  actual_electrical_or_optical_instrumentation:false};
 const canonical=JSON.stringify(Object.fromEntries(Object.entries(report).sort((a,b)=>a[0].localeCompare(b[0]))))+"\n";
 const wire=Buffer.from(canonical,"ascii"),name="r9-independent-node.json";
 fs.writeFileSync(path.join(out,name),wire);
 fs.writeFileSync(path.join(out,name+".sha256"),sha(wire)+"  "+name+"\n");
 console.log(JSON.stringify({status:"NODE_SOURCE_DIGEST_HOST_TELEMETRY_REPLAY_PASS",
   bytes:184815*4096,hash:digest,actual_optical_meter:"NOT_PRESENT"}));
}
if(process.argv.length!==4)throw Error("usage: node verify_host.js ORIGINAL_ARCHIVE OUT");
main(process.argv[2],process.argv[3]);
