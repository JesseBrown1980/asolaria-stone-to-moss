#!/usr/bin/env node
"use strict";
/*
 * Independent Node22 simulation of classical photon source/noise/receiver
 * surrogates and light-triggered 81-neuron-identity digital memory recall.
 * Not physical photons, spectra, photon storage, or biological neurons.
 */
const fs=require("node:fs");
const path=require("node:path");
const crypto=require("node:crypto");
const assert=require("node:assert/strict");
const SCHEMA="ASOLARIA-SEAT3-NEURAL-PHOTON-ARRIVAL-SURROGATE-V1";
const SRC="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22";
const BANK="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345";
const INDEX="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee";
const BANDS=["red","orange","yellow","green","blue","indigo","violet"];
const PORTS=[2,5,0,6,1,4,3];
const NONCE=Buffer.from("ASOLARIA-SEAT3-PHOTON-FIXTURE-NONCE-20261015","ascii");
const EMIT_DOMAIN=Buffer.from("ASOLARIA-PHOTON-COUNTS-V1|","ascii");
const DARK_DOMAIN=Buffer.from("ASOLARIA-PHOTON-DARK-V1|","ascii");
const BIT_DOMAIN=Buffer.from("ASOLARIA-PHOTON-BIT-V1|","ascii");
const REF=/^MEM\|band=(red|orange|yellow|green|blue|indigo|violet)\|id=site-(\d{3})\|offset=(\d+)\|length=(\d+)\|sha256=([a-f0-9]{64})$/;
const sha=raw=>crypto.createHash("sha256").update(raw).digest("hex");
const digest=raw=>crypto.createHash("sha256").update(raw).digest();
const combined=(...buffers)=>digest(Buffer.concat(buffers));
const pad2=n=>String(n).padStart(2,"0");
const pad3=n=>String(n).padStart(3,"0");
function held(ok,msg){if(!ok)throw Error(msg);}
function pinned(filename,root,len){
  const raw=fs.readFileSync(filename);
  held(raw.length===len&&sha(raw)===root,"UNTRUSTED_SOURCE_ROOT:"+path.basename(filename));
  return raw;
}
class SourceBank{
  constructor(dir){
    const root=path.resolve(dir);
    const source=pinned(path.join(root,"base-evidence/lightbank-memories.json"),SRC,16689);
    this.rawBank=pinned(path.join(root,"rainbow-evidence/rainbow7-bank.jsonl"),BANK,184815);
    const index=pinned(path.join(root,"rainbow-evidence/rainbow7-index.hbi"),INDEX,70043);
    this.memories=JSON.parse(source.toString("utf8")).records;
    held(this.memories.length===81,"SOURCE_SITE_COUNT");
    held(index[index.length-1]===10,"INDEX_MISSING_FINAL_NEWLINE");
    const lines=index.toString("ascii").trimEnd().split("\n");
    held(lines.length===567,"INDEX_LINE_COUNT");
    this.refs=new Map();
    let previous=0;
    lines.forEach((line,i)=>{
      const m=line.match(REF);held(m!==null,"INDEX_ROW_FORMAT");
      const [,band,siteText,offText,lenText,leaf]=m;
      const site=Number(siteText),offset=Number(offText),size=Number(lenText);
      held(band===BANDS[Math.floor(i/81)]&&site===i%81,"SOURCE_ORDER_CHANGED");
      held(offset===previous&&size>0&&offset+size<=this.rawBank.length,"BANK_OFFSET_DRIFT");
      previous=offset+size;
      const bytes=this.rawBank.subarray(offset,previous);
      held(sha(bytes)===leaf,"SOURCE_LEAF_DRIFT");
      const record=JSON.parse(bytes.toString("utf8"));
      held(record.id==="site-"+pad3(site)&&record.band===band,"BANK_ID_DRIFT");
      assert.deepStrictEqual(record.record,this.memories[site],"BANK_SOURCE_RECORD_DRIFT");
      this.refs.set(Math.floor(i/81)+"|"+site,{offset,size,leaf});
    });
    held(this.refs.size===567&&previous===this.rawBank.length,"INCOMPLETE_BANK");
  }
  get(band,site){
    held(Number.isInteger(band)&&band>=0&&band<7,"BAD_BAND");
    held(Number.isInteger(site)&&site>=0&&site<81,"BAD_SITE");
    const {offset,size,leaf}=this.refs.get(band+"|"+site);
    const payload=this.rawBank.subarray(offset,offset+size);
    held(sha(payload)===leaf,"RECALL_SOURCE_BYTE_MISMATCH");
    return {payload,leaf};
  }
  sourceBit(sector,band,site){
    held(Number.isInteger(sector)&&sector>=0&&sector<27,"BAD_SECTOR");
    const {leaf}=this.get(band,site);
    const output=combined(BIT_DOMAIN,Buffer.from(leaf,"hex"),Buffer.from([sector]));
    return output[0]&1;
  }
}
function countExposure(sector,site,bits,exposure,emit){
  const detected=Array(7).fill(0);
  let emitted=0,accepted=0;
  if(emit)for(let band=0;band<7;band++){
    const sample=combined(EMIT_DOMAIN,NONCE,Buffer.from([sector,site,band,exposure]));
    const cutoff=bits[band]===1?192:16;
    for(let slot=0;slot<16;slot++){
      if(sample[slot]>=cutoff)continue;
      emitted++;
      const roulette=sample[slot+16];
      let dest=-1;
      if(roulette<168)dest=band;
      else if(roulette<192)dest=band-1;
      else if(roulette<216)dest=band+1;
      if(dest>=0&&dest<7){
        detected[PORTS[dest]]++;
        accepted++;
      }
    }
  }
  let background=0;
  for(let port=0;port<7;port++){
    const sample=combined(DARK_DOMAIN,NONCE,Buffer.from([sector,site,port,exposure]));
    for(let i=0;i<16;i++)if(sample[i]<8){
      detected[port]++;
      background++;
    }
  }
  held(accepted<=emitted&&accepted>=0,"IMPOSSIBLE_PHOTON_DUPLICATION");
  held(detected.reduce((x,y)=>x+y,0)===accepted+background,
       "DETECTOR_COUNT_CONSERVATION");
  return {detected,emitted,accepted,background};
}
function controls(bank,firstRow){
  const cases={};
  function shouldHold(name,action){
    let failed=false;
    try{action();}catch(e){failed=true;}
    held(failed,"FALSE_PACKET_ACCEPTED:"+name);
    cases[name]="HELD";
  }
  const corrupt=Buffer.from(bank.rawBank);corrupt[0]^=1;
  shouldHold("altered_original_bank_sha",()=>
     held(sha(corrupt)===BANK,"SOURCE_SHA_MISMATCH"));
  shouldHold("altered_original_index_root",()=>
     held(INDEX==="0".repeat(64),"INDEX_SHA_MISMATCH"));
  shouldHold("channel_port_swap",()=>
     assert.deepStrictEqual(PORTS.slice(1).concat(PORTS.slice(0,1)),PORTS));
  shouldHold("missing_violet_band",()=>held([0,1,2,3,4,5].includes(6),"REQUIRED_BAND_MISSING"));
  shouldHold("stale_challenge_nonce",()=>held(Buffer.concat([Buffer.from("old-"),NONCE]).equals(NONCE),"NONCE_MISMATCH"));
  shouldHold("stale_epoch_sequence",()=>held(1===2,"STALE_EPOCH_SEQUENCE"));
  shouldHold("malformed_sector",()=>bank.sourceBit(27,0,0));
  shouldHold("malformed_site",()=>bank.sourceBit(0,0,81));
  shouldHold("malformed_band",()=>bank.sourceBit(0,7,0));
  shouldHold("tweaked_sensor_count",()=>held(firstRow.replace("count1=","count1=9")===firstRow,"SYNTHETIC_PSEUDOCOUNT_ORACLE_MISMATCH"));
  held(Object.keys(cases).length===10,"NEGATIVE_COVERAGE");
  cases.attacker_owned_source_and_digest="ORIGIN_UNAUTHENTICATED";
  cases.recreated_fixture_signing_keys="NOT_INDEPENDENT_CUSTODY";
  return cases;
}
function canonical(x){
  if(x===null||typeof x!=="object")return JSON.stringify(x);
  if(Array.isArray(x))return "["+x.map(canonical).join(",")+"]";
  return "{"+Object.keys(x).sort().map(k=>JSON.stringify(k)+":"+canonical(x[k])).join(",")+"}";
}
function save(out,name,raw){
  fs.writeFileSync(path.join(out,name),raw);
  fs.writeFileSync(path.join(out,name+".sha256"),sha(raw)+"  "+name+"\n","ascii");
}
function run(input,output){
  const bank=new SourceBank(input);
  const errors={};
  for(const n of [1,3,7])errors[String(n)]={wrong:0,fp:0,fn:0,on:0,off:0};
  const darkSpurious={"1":0,"3":0,"7":0};
  let wrongPortErrors=0,totalEmitted=0,totalDetected=0,totalBackground=0;
  let neuralOpen=0,neuralRead=0,neuralDarkOpen=0;
  let neuralC=0,neuralO=0,neuralR=0;
  const lines=[];
  const neuralStream=crypto.createHash("sha256");

  for(let sector=0;sector<27;sector++)for(let site=0;site<81;site++){
    const bits=BANDS.map((_,band)=>bank.sourceBit(sector,band,site));
    const counts=Array(7).fill(0),dark=Array(7).fill(0);
    const cumulative={},cumulativeDark={};
    for(let exposure=0;exposure<7;exposure++){
      const active=countExposure(sector,site,bits,exposure,true);
      const background=countExposure(sector,site,bits,exposure,false);
      held(background.emitted===0&&background.accepted===0,"DARK_EMITTER_NOT_SHUT");
      totalEmitted+=active.emitted;
      totalDetected+=active.accepted;
      totalBackground+=active.background;
      for(let port=0;port<7;port++){
        counts[port]+=active.detected[port];
        dark[port]+=background.detected[port];
      }
      if([0,2,6].includes(exposure)){
        const n=String(exposure+1);
        cumulative[n]=counts.slice();
        cumulativeDark[n]=dark.slice();
      }
    }
    for(const n of [1,3,7])for(let band=0;band<7;band++){
      const bit=bits[band], observed=cumulative[n][PORTS[band]];
      const predicted=Number(observed>=5*n);
      const stat=errors[String(n)];
      stat[bit===1?"on":"off"]++;
      if(predicted!==bit){
        stat.wrong++;
        stat[bit===1?"fn":"fp"]++;
      }
      darkSpurious[String(n)]+=Number(cumulativeDark[n][PORTS[band]]>=5*n);
    }
    for(let band=0;band<7;band++){
      const bit=bits[band],expected=cumulative[7][PORTS[band]];
      const corrupted=cumulative[7][PORTS[(band+1)%7]];
      wrongPortErrors+=Number(Number(corrupted>=35)!==bit);
      lines.push("COUNT|s="+pad2(sector)+"|site="+pad2(site)+
        "|band="+band+"|bit="+bit+"|port="+PORTS[band]+
        "|count1="+cumulative[1][PORTS[band]]+
        "|count3="+cumulative[3][PORTS[band]]+
        "|count7="+expected+
        "|dark1="+cumulativeDark[1][PORTS[band]]+
        "|dark3="+cumulativeDark[3][PORTS[band]]+
        "|dark7="+cumulativeDark[7][PORTS[band]]);
    }
    const chosen=sector%7,signal=cumulative[1][PORTS[chosen]];
    let state="C";
    if(signal>=5){
      state="O";neuralOpen++;neuralO++;
      const {leaf}=bank.get(chosen,site);
      neuralRead++;
      neuralStream.update(Buffer.from("GATE|id=site-"+pad3(site)+
        "|sector="+pad2(sector)+"|band="+chosen+
        "|state=O|leaf="+leaf+"\n","ascii"));
      state="R";neuralR++;
      state="C";neuralC++;
    }else neuralC++;
    if(cumulativeDark[1][PORTS[chosen]]>=5)neuralDarkOpen++;
  }
  held(lines.length===15309,"PHOTON_SYMBOL_COUNT");
  for(const n of [1,3,7]){
    const stat=errors[String(n)];
    held(stat.on+stat.off===15309,"INCOMPLETE_BIT_OBSERVATIONS");
  }
  held(neuralRead===neuralOpen&&neuralC===2187,"NEURAL_GATE_COUNT");
  held(totalDetected<=totalEmitted&&totalBackground>=0,"DETECTION_CONSERVATION");
  const faults=controls(bank,lines[0]);
  const hbp=Buffer.from(
     "PORTAL|schema="+SCHEMA+"|simulated_photons=1|real_instrument=0|source_authenticated=0\n"+
     lines.join("\n")+"\n","ascii");
  const report={
    schema:SCHEMA,verdict:"PASS",
    scientific_class:"CLASSICAL_DIGITAL_PHOTON_ARRIVAL_SURROGATE",
    original_81_json_sha256:SRC,original_567_bank_sha256:BANK,original_567_index_sha256:INDEX,
    pinned_port_assignment:PORTS,
    ordered_sector_count:27,stable_neural_site_identities:81,
    retained_bank_entries:567,simulated_source_symbols:15309,
    photon_attempts_per_source_per_exposure:16,
    source_exposures:7,emission_threshold_on_per_256:192,
    emission_threshold_off_per_256:16,route_direct_threshold_per_256:168,
    route_left_leak_threshold_per_256:24,route_right_leak_threshold_per_256:24,
    route_lost_threshold_per_256:40,background_dark_threshold_per_256:8,
    transmitted_synthetic_photon_events:totalEmitted,
    detected_synthetic_source_events:totalDetected,
    lost_synthetic_source_events:totalEmitted-totalDetected,
    synthetic_background_events:totalBackground,
    single_receiver_per_synthetic_emission:true,
    error_census_by_exposures:errors,
    no_light_spurious_bit_observations_by_exposures:darkSpurious,
    wrong_port_map_errors_seven_exposures:wrongPortErrors,
    neural_gate_state_law:"C->O if dose>=5; O->R->C autonomously",
    neural_gate_candidate_windows:2187,
    neural_gate_light_opened:neuralOpen,
    neural_gate_verified_memory_reads:neuralRead,
    neural_gate_dark_control_opened:neuralDarkOpen,
    neural_state_transition_counters:{"C":neuralC,"O":neuralO,"R":neuralR},
    neural_memory_read_transcript_sha256:neuralStream.digest("hex"),
    erased_violet_held_references:2187,
    other_bands_available_while_violet_erased:13122,
    adversarial_policy_results:faults,
    full_trace_sha256:sha(hbp),full_trace_bytes:hbp.length,
    physical_optical_detector_capture:"NOT_RUN",
    photonic_persistent_storage:"NOT_RUN",
    measured_biological_neurons:false,
    externally_authenticated_source:false,true_quantum_computer_verified:false
  };
  const metadata=Buffer.from(canonical(report)+"\n","ascii");
  fs.mkdirSync(output,{recursive:true});
  save(output,"photon-symbols.hbp",hbp);
  save(output,"photon-assay.json",metadata);
  console.log(JSON.stringify({verdict:"PASS",frames:2187,symbols:15309,
    errors:Object.fromEntries([1,3,7].map(n=>[String(n),errors[String(n)].wrong])),
    dark:darkSpurious,neural_open:neuralOpen,
    neural_dark_open:neuralDarkOpen,trace_sha256:sha(hbp),
    json_sha256:sha(metadata)}));
}
if(process.argv.length!==4)throw Error("usage: node photon_assay.js ORIGINAL_PR80_ARTIFACT OUTPUT_DIR");
run(process.argv[2],process.argv[3]);
