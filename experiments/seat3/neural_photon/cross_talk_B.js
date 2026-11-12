#!/usr/bin/env node
"use strict";
/* Independent Node22 cross-talk B validation, separate new deterministic seed.
 * Seven symbolic detectors, event conservation, frozen thresholds selected on
 * earlier original fixture; NO independently captured photons or persistence.
 */
const fs=require("node:fs");
const path=require("node:path");
const crypto=require("node:crypto");
const assert=require("node:assert/strict");

const SCHEMA="ASOLARIA-SEAT3-SPECTRAL-CROSSTALK-SECOND-NONCE-V1";
const NONCE="ASOLARIA-SEAT3-PHOTON-UNSEEN-COUNTS-VALIDATION-B-20261015";
const SOURCE_SHA="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22";
const BANK_SHA="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345";
const INDEX_SHA="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee";
const PORTS=[2,5,0,6,1,4,3];
const NAMES=["red","orange","yellow","green","blue","indigo","violet"];
const T={"1":28,"3":78,"7":182};
const BIT=Buffer.from("ASOLARIA-PHOTON-BIT-V1|","ascii");
const EMIT=Buffer.from("ASOLARIA-PHOTON-COUNTS-V1|","ascii");
const DARK=Buffer.from("ASOLARIA-PHOTON-DARK-V1|","ascii");
const NONCE_BUF=Buffer.from(NONCE,"ascii");
const indexRe=/^MEM\|band=(red|orange|yellow|green|blue|indigo|violet)\|id=site-(\d{3})\|offset=(\d+)\|length=(\d+)\|sha256=([0-9a-f]{64})$/;
const hash=b=>crypto.createHash("sha256").update(b).digest("hex");
const combined=(...items)=>crypto.createHash("sha256").update(Buffer.concat(items)).digest();
const two=n=>String(n).padStart(2,"0");
const three=n=>String(n).padStart(3,"0");
function hold(ok,why){if(!ok)throw Error(why);}
function verified(file,expected,n){
  const bytes=fs.readFileSync(file);
  hold(bytes.length===n&&hash(bytes)===expected,"HISTORICAL_ROOT_UNTRUSTED:"+file);
  return bytes;
}
function bankFromSource(src){
  const original=verified(path.join(src,"base-evidence/lightbank-memories.json"),SOURCE_SHA,16689);
  const bank=verified(path.join(src,"rainbow-evidence/rainbow7-bank.jsonl"),BANK_SHA,184815);
  const index=verified(path.join(src,"rainbow-evidence/rainbow7-index.hbi"),INDEX_SHA,70043);
  const mem=JSON.parse(original.toString("utf8")).records;
  hold(mem.length===81,"ORIGINAL_MEMORY_COUNT");
  hold(index[index.length-1]===10,"INDEX_MISSING_NEWLINE");
  const lines=index.toString("ascii").trimEnd().split("\n");
  hold(lines.length===567,"INDEX_ENTRY_COUNT");
  const leaves=new Map();
  let oldEnd=0;
  for(let i=0;i<lines.length;i++){
    const m=lines[i].match(indexRe);
    hold(m!==null,"BAD_BASE_ROW");
    const [,band,id,off,size,sha]=m;
    const site=Number(id),start=Number(off),n=Number(size);
    hold(band===NAMES[Math.floor(i/81)]&&site===i%81,"BANK_LOGICAL_ORDER");
    hold(start===oldEnd&&n>0&&start+n<=bank.length,"INVALID_LEAF_OFFSET");
    oldEnd=start+n;
    const data=bank.subarray(start,oldEnd);
    hold(hash(data)===sha,"BANK_LEAF_HASH");
    const obj=JSON.parse(data.toString("utf8"));
    hold(obj.id==="site-"+three(site)&&obj.band===band,"BANK_ID_MISMATCH");
    assert.deepStrictEqual(obj.record,mem[site],"BANK_SOURCE_IDENTITY");
    leaves.set(Math.floor(i/81)+"|"+site,sha);
  }
  hold(oldEnd===bank.length&&leaves.size===567,"BANK_BYTES_UNACCOUNTED");
  return leaves;
}
function bitFor(leaves,sector,site,band){
  const sha=leaves.get(band+"|"+site);
  hold(typeof sha==="string","MISSING_SOURCE_LEAF");
  return combined(BIT,Buffer.from(sha,"hex"),Buffer.from([sector]))[0]&1;
}
function oneExposure(sector,site,sourceBits,exposure,sourceEnabled){
  const ports=Array(7).fill(0);
  let emitted=0,detection=0,background=0;
  if(sourceEnabled)for(let band=0;band<7;band++){
    const sample=combined(EMIT,NONCE_BUF,Buffer.from([sector,site,band,exposure]));
    const cutoff=sourceBits[band]===1?192:16;
    for(let event=0;event<16;event++){
      if(sample[event]>=cutoff)continue;
      emitted++;
      const destination=sample[event+16];
      let receiver=-1;
      if(destination<168)receiver=band;
      else if(destination<192)receiver=band-1;
      else if(destination<216)receiver=band+1;
      if(receiver>=0&&receiver<7){
        ports[PORTS[receiver]]++;
        detection++;
      }
    }
  }
  for(let port=0;port<7;port++){
    const sample=combined(DARK,NONCE_BUF,Buffer.from([sector,site,port,exposure]));
    for(let event=0;event<16;event++)if(sample[event]<8){
      ports[port]++;
      background++;
    }
  }
  hold(ports.reduce((s,v)=>s+v,0)===detection+background,"DETECTOR_EVENT_DOUBLE_COUNT");
  hold(detection<=emitted,"SOURCE_PHOTON_MULTIPLICATION");
  return [ports,emitted,detection,background];
}
function canonical(x){
  if(x===null||typeof x!=="object")return JSON.stringify(x);
  if(Array.isArray(x))return "["+x.map(canonical).join(",")+"]";
  return "{"+Object.keys(x).sort().map(k=>JSON.stringify(k)+":"+canonical(x[k])).join(",")+"}";
}
function write(out,name,bytes){
  fs.writeFileSync(path.join(out,name),bytes);
  fs.writeFileSync(path.join(out,name+".sha256"),hash(bytes)+"  "+name+"\n","ascii");
}
function run(input,folder){
  const leaves=bankFromSource(input);
  const errors={};
  const darkCensus={};
  for(const n of [1,3,7]){
    errors[String(n)]={raw_wrong:0,corrected_wrong:0,raw_fp:0,raw_fn:0,
                       corrected_fp:0,corrected_fn:0};
    darkCensus[String(n)]={raw_spurious:0,corrected_spurious:0};
  }
  const trace=[];
  let photons=0,detected=0,background=0,wrongMap=0;
  for(let sector=0;sector<27;sector++)for(let site=0;site<81;site++){
    const bits=NAMES.map((_,band)=>bitFor(leaves,sector,site,band));
    const counts=Array(7).fill(0),dark=Array(7).fill(0);
    const censuses={},negative={};
    for(let exposure=0;exposure<7;exposure++){
      const [observed,emitted,accepted,bg]=oneExposure(sector,site,bits,exposure,true);
      const [off,offE,offD]=oneExposure(sector,site,bits,exposure,false);
      hold(offE===0&&offD===0,"NO_LIGHT_SOURCE_EMISSION");
      photons+=emitted;detected+=accepted;background+=bg;
      for(let port=0;port<7;port++){
        counts[port]+=observed[port];
        dark[port]+=off[port];
      }
      if([0,2,6].includes(exposure)){
        const n=String(exposure+1);
        censuses[n]=counts.slice();
        negative[n]=dark.slice();
      }
    }
    for(let band=0;band<7;band++){
      const bit=bits[band],series={};
      for(const n of [1,3,7]){
        const key=String(n),obs=censuses[key],dark=negative[key];
        const port=PORTS[band],own=obs[port];
        const prev=band>0?obs[PORTS[band-1]]:0;
        const next=band<6?obs[PORTS[band+1]]:0;
        const score=7*own-prev-next;
        const d=dark[port],pDark=band>0?dark[PORTS[band-1]]:0;
        const nDark=band<6?dark[PORTS[band+1]]:0;
        const scoreDark=7*d-pDark-nDark;
        const rawBit=Number(own>=5*n);
        const fixedBit=Number(score>=T[key]);
        if(rawBit!==bit){
          errors[key].raw_wrong++;
          errors[key][bit?"raw_fn":"raw_fp"]++;
        }
        if(fixedBit!==bit){
          errors[key].corrected_wrong++;
          errors[key][bit?"corrected_fn":"corrected_fp"]++;
        }
        darkCensus[key].raw_spurious+=Number(d>=5*n);
        darkCensus[key].corrected_spurious+=Number(scoreDark>=T[key]);
        series[key]=[own,score,d,scoreDark];
      }
      wrongMap+=Number(Number(censuses["7"][PORTS[(band+1)%7]]>=35)!==bit);
      const [c1,s1,d1,ds1]=series["1"];
      const [c3,s3,d3,ds3]=series["3"];
      const [c7,s7,d7,ds7]=series["7"];
      trace.push("CROSSTALK|s="+two(sector)+"|site="+two(site)+"|band="+band+
        "|bit="+bit+"|port="+PORTS[band]+
        "|c1="+c1+"|s1="+s1+"|d1="+d1+"|ds1="+ds1+
        "|c3="+c3+"|s3="+s3+"|d3="+d3+"|ds3="+ds3+
        "|c7="+c7+"|s7="+s7+"|d7="+d7+"|ds7="+ds7);
    }
  }
  hold(trace.length===15309&&detected<=photons,"SOURCE_SYMBOL_OR_EVENT_COUNT_DRIFT");
  const hbp=Buffer.from(
    "PORTAL|schema="+SCHEMA+"|validation_B=1|synthetic_arrivals=1|real_sensor=0\n"+
    trace.join("\n")+"\n","ascii");
  const report={
    schema:SCHEMA,verdict:"PASS",fixture_nonce:NONCE,
    original_source_sha256:SOURCE_SHA,original_bank_sha256:BANK_SHA,
    original_base_index_sha256:INDEX_SHA,
    source_symbols:15309,frames:2187,stable_source_identities:81,
    source_port_map:PORTS,source_band_count:7,
    correction_law:"score=7*c_own-c_prev-c_next(no_wrap)",
    frozen_thresholds:T,raw_thresholds:{"1":5,"3":15,"7":35},
    source_counts_by_exposure:errors,
    dark_counts_by_exposure:darkCensus,
    wrong_receiver_map_error_count_at_7:wrongMap,
    source_emission_events:photons,
    one_detector_source_events:detected,
    lost_source_events:photons-detected,
    background_detector_events:background,
    conserved_one_receiver_per_event:true,
    violet_band_erasure_status:"HELD_2187_MISSING",
    six_band_available_symbols:13122,
    source_ownership_authenticated:false,
    real_optical_capture_status:"NOT_RUN",
    physical_photonic_retention_status:"NOT_RUN",
    full_trace_sha256:hash(hbp),full_trace_bytes:hbp.length,
    thresholds_frozen_before_validation_data:true,
    threshold_selection_was_exploratory_original_fixture:true
  };
  const json=Buffer.from(canonical(report)+"\n","ascii");
  fs.mkdirSync(folder,{recursive:true});
  write(folder,"photon-cross-talk-B.hbp",hbp);
  write(folder,"photon-cross-talk-B.json",json);
  console.log(JSON.stringify({status:"PASS",
    fixed_error_counts:Object.fromEntries([1,3,7].map(n=>[String(n),errors[String(n)].corrected_wrong])),
    raw_error_counts:Object.fromEntries([1,3,7].map(n=>[String(n),errors[String(n)].raw_wrong])),
    hbp_sha256:hash(hbp),json_sha256:hash(json)}));
}
if(process.argv.length!==4)throw Error("usage: node cross_talk_B.js ORIGINAL_PR80_ARTIFACT OUT_DIR");
run(process.argv[2],process.argv[3]);
