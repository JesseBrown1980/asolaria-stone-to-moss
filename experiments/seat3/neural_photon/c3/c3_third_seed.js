#!/usr/bin/env node
"use strict";
/* C3 independent Node22 entire-third-seed photon surrogate cross-exam.
 * Does not import Python source or Python model output. NOT physical photons.
 */
const fs=require("node:fs");
const path=require("node:path");
const crypto=require("node:crypto");
const assert=require("node:assert/strict");
const SCHEMA="ASOLARIA-C3-THIRD-SEED-SPECTRAL-DRIFT-V1";
const SEED="ASOLARIA-C3-HOLDOUT-THIRD-SEED-20261015-V1";
const SOURCE_SHA="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22";
const BANK_SHA="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345";
const INDEX_SHA="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee";
const BANDS=["red","orange","yellow","green","blue","indigo","violet"];
const PORTS=[2,5,0,6,1,4,3];
const MODELS={C:{own:168,left:24,right:24,lost:40,dark:8},
              D:{own:120,left:40,right:40,lost:56,dark:16}};
const THRESH={"1":28,"3":78,"7":182};
const LEAF_RX=/^MEM\|band=(red|orange|yellow|green|blue|indigo|violet)\|id=site-(\d{3})\|offset=(\d+)\|length=(\d+)\|sha256=([a-f0-9]{64})$/;
const sha=x=>crypto.createHash("sha256").update(x).digest("hex");
const hashed=(...items)=>crypto.createHash("sha256").update(Buffer.concat(items)).digest();
const seed=Buffer.from(SEED,"ascii");
const bitPrefix=Buffer.from("ASOLARIA-PHOTON-BIT-V1|","ascii");
const emitPrefix=Buffer.from("ASOLARIA-PHOTON-COUNTS-V1|","ascii");
const darkPrefix=Buffer.from("ASOLARIA-PHOTON-DARK-V1|","ascii");
const two=n=>String(n).padStart(2,"0");
const three=n=>String(n).padStart(3,"0");
function check(cond,msg){if(!cond)throw Error(msg);}
function readPinned(p,expected,size){
  const data=fs.readFileSync(p);
  check(data.length===size&&sha(data)===expected,"UNTRUSTED_OR_CHANGED_SOURCE_ROOT:"+p);
  return data;
}
class Bank{
  constructor(root){
    const source=readPinned(path.join(root,"base-evidence/lightbank-memories.json"),SOURCE_SHA,16689);
    const bank=readPinned(path.join(root,"rainbow-evidence/rainbow7-bank.jsonl"),BANK_SHA,184815);
    const idx=readPinned(path.join(root,"rainbow-evidence/rainbow7-index.hbi"),INDEX_SHA,70043);
    const originals=JSON.parse(source.toString("utf8")).records;
    check(originals.length===81&&idx[idx.length-1]===10,"INVALID_ORIGINAL_SOURCE");
    const lines=idx.toString("ascii").trimEnd().split("\n");
    check(lines.length===567,"BASE_INDEX_COUNT");
    this.leaves=new Map();
    let end=0;
    for(let i=0;i<lines.length;i++){
      const mat=lines[i].match(LEAF_RX);
      check(mat!==null,"BASE_ROW_INVALID");
      const [,name,sid,offset,size,leaf]=mat;
      const site=Number(sid),start=Number(offset),length=Number(size);
      check(name===BANDS[Math.floor(i/81)]&&site===i%81&&start===end&&
            length>0&&start+length<=bank.length,"BASE_REFERENCE_CHANGED");
      end=start+length;
      const payload=bank.subarray(start,end);
      check(sha(payload)===leaf,"BASE_LEAF_SHA_MISMATCH");
      const record=JSON.parse(payload.toString("utf8"));
      check(record.id==="site-"+three(site)&&record.band===name,"BANK_IDENTITY_DRIFT");
      assert.deepStrictEqual(record.record,originals[site],"BANK_RECORD_MISMATCH");
      this.leaves.set(Math.floor(i/81)+"|"+site,Buffer.from(leaf,"hex"));
    }
    check(this.leaves.size===567&&end===bank.length,"SOURCE_BANK_INCOMPLETE");
  }
  bit(s,site,band){
    check(Number.isInteger(s)&&s>=0&&s<27,"BAD_SECTOR");
    check(Number.isInteger(site)&&site>=0&&site<81,"BAD_SITE");
    check(Number.isInteger(band)&&band>=0&&band<7,"BAD_BAND");
    const leaf=this.leaves.get(band+"|"+site);
    return hashed(bitPrefix,leaf,Buffer.from([s]))[0]&1;
  }
}
function exposure(arm,sector,site,bits,epoch,light){
  const model=MODELS[arm];
  check(model.own+model.left+model.right+model.lost===256,"INVALID_MODEL");
  const detectors=Array(7).fill(0);
  let emitted=0,detected=0,background=0;
  if(light){
    for(let band=0;band<7;band++){
      const bytes=hashed(emitPrefix,seed,Buffer.from(arm,"ascii"),
                         Buffer.from([sector,site,band,epoch]));
      const limit=bits[band]?192:16;
      for(let k=0;k<16;k++){
        if(bytes[k]>=limit)continue;
        emitted++;
        const random=bytes[16+k];
        let dest=-1;
        if(random<model.own)dest=band;
        else if(random<model.own+model.left)dest=band-1;
        else if(random<model.own+model.left+model.right)dest=band+1;
        if(dest>=0&&dest<7){
          detectors[PORTS[dest]]++;
          detected++;
        }
      }
    }
  }
  for(let port=0;port<7;port++){
    const bytes=hashed(darkPrefix,seed,Buffer.from(arm,"ascii"),
                       Buffer.from([sector,site,port,epoch]));
    for(let k=0;k<16;k++){
      if(bytes[k]<model.dark){
        detectors[port]++;
        background++;
      }
    }
  }
  check(detected<=emitted&&detectors.reduce((a,b)=>a+b,0)===detected+background,
        "PHOTON_SURROGATE_CONSERVATION_BROKEN");
  return {detectors,emitted,detected,background};
}
const blank=()=>({both_correct:0,fixed_only:0,degraded:0,both_wrong:0,raw_wrong:0,
                  fixed_wrong:0,raw_fp:0,raw_fn:0,fixed_fp:0,fixed_fn:0});
const freshDark=()=>({raw_spurious:0,fixed_spurious:0});
function decScore(channels,band){
  return 7*channels[band]-(band>0?channels[band-1]:0)-(band<6?channels[band+1]:0);
}
function canonical(obj){
  if(obj===null||typeof obj!=="object")return JSON.stringify(obj);
  if(Array.isArray(obj))return "["+obj.map(canonical).join(",")+"]";
  return "{"+Object.keys(obj).sort().map(k=>JSON.stringify(k)+":"+canonical(obj[k])).join(",")+"}";
}
function write(out,name,data){
  fs.writeFileSync(path.join(out,name),data);
  fs.writeFileSync(path.join(out,name+".sha256"),sha(data)+"  "+name+"\n","ascii");
}
function run(src,destination){
  const bank=new Bank(src);
  const aggregate={},perband={},dark={},wrongmap={},conservation={};
  for(const arm of ["C","D"]){
    aggregate[arm]={};perband[arm]={};dark[arm]={};
    for(const n of [1,3,7]){
      aggregate[arm][String(n)]=blank();
      perband[arm][String(n)]=Array.from({length:7},blank);
      dark[arm][String(n)]=freshDark();
    }
    wrongmap[arm]=0;
    conservation[arm]={emitted:0,detected:0,lost:0,background:0};
  }
  const rows=[];
  for(const arm of ["C","D"]){
    for(let sector=0;sector<27;sector++)for(let site=0;site<81;site++){
      const bits=BANDS.map((_,band)=>bank.bit(sector,site,band));
      const detector=Array(7).fill(0),off=Array(7).fill(0),stages={},darks={};
      for(let epoch=0;epoch<7;epoch++){
        const obs=exposure(arm,sector,site,bits,epoch,true);
        const darkOnly=exposure(arm,sector,site,bits,epoch,false);
        check(darkOnly.emitted===0&&darkOnly.detected===0,"DARK_SOURCE_STILL_EMITTING");
        const ledger=conservation[arm];
        ledger.emitted+=obs.emitted;
        ledger.detected+=obs.detected;
        ledger.lost+=obs.emitted-obs.detected;
        ledger.background+=obs.background;
        for(let p=0;p<7;p++){
          detector[p]+=obs.detectors[p];
          off[p]+=darkOnly.detectors[p];
        }
        if(epoch===0||epoch===2||epoch===6){
          stages[epoch+1]=detector.slice();
          darks[epoch+1]=off.slice();
        }
      }
      for(let band=0;band<7;band++){
        const truth=bits[band],values=[];
        for(const n of [1,3,7]){
          const currents=PORTS.map(port=>stages[n][port]);
          const darkCounts=PORTS.map(port=>darks[n][port]);
          const count=currents[band],score=decScore(currents,band);
          const dc=darkCounts[band],ds=decScore(darkCounts,band);
          const raw=Number(count>=5*n);
          const fixed=Number(score>=THRESH[String(n)]);
          for(const stat of [aggregate[arm][String(n)],perband[arm][String(n)][band]]){
            stat.raw_wrong+=Number(raw!==truth);
            stat.fixed_wrong+=Number(fixed!==truth);
            stat.raw_fp+=Number(raw===1&&truth===0);
            stat.raw_fn+=Number(raw===0&&truth===1);
            stat.fixed_fp+=Number(fixed===1&&truth===0);
            stat.fixed_fn+=Number(fixed===0&&truth===1);
            const label=(raw!==truth&&fixed!==truth)?"both_wrong":
                        raw!==truth?"fixed_only":fixed!==truth?"degraded":"both_correct";
            stat[label]++;
          }
          dark[arm][String(n)].raw_spurious+=Number(dc>=5*n);
          dark[arm][String(n)].fixed_spurious+=Number(ds>=THRESH[String(n)]);
          values.push([count,score,dc,ds]);
        }
        wrongmap[arm]+=Number(Number(stages[7][PORTS[(band+1)%7]]>=35)!==truth);
        let detail="";
        for(let k=0;k<3;k++){
          const n=[1,3,7][k],v=values[k];
          detail+="|c"+n+"="+v[0]+"|x"+n+"="+v[1]+
                  "|dark"+n+"="+v[2]+"|dx"+n+"="+v[3];
        }
        rows.push("FRAME|arm="+arm+"|s="+two(sector)+"|site="+two(site)+
                  "|band="+band+"|bit="+truth+"|port="+PORTS[band]+detail);
      }
    }
  }
  check(rows.length===30618,"FAILED_COMPLETE_C3_D_SYMBOL_SCOPE");
  for(const arm of ["C","D"]){
    const ledger=conservation[arm];
    check(ledger.emitted===ledger.detected+ledger.lost,"LOST_EVENT_ACCOUNTING");
    for(const n of [1,3,7]){
      const x=aggregate[arm][String(n)];
      check(x.both_correct+x.fixed_only+x.degraded+x.both_wrong===15309,"C3_PAIRED_COVERAGE");
      check(x.raw_wrong===x.fixed_only+x.both_wrong&&
            x.fixed_wrong===x.degraded+x.both_wrong,"C3_PAIRED_MATH");
    }
  }
  const hbp=Buffer.from("PORTAL|schema="+SCHEMA+"|source_root="+BANK_SHA+
    "|fixture=THIRD_C_D|simulated_arrivals=1|real_photons=0\n"+
    rows.join("\n")+"\n","ascii");
  const report={
    schema:SCHEMA,verdict:"SIMULATION_PASS",source_sha256:SOURCE_SHA,
    bank_sha256:BANK_SHA,index_sha256:INDEX_SHA,seed:SEED,
    conditions:["C","D"],models:MODELS,
    symbol_count_per_model:15309,source_identities:81,stored_bank_refs:567,
    source_port_map:PORTS,seven_exposure_repeats:7,
    frozen_raw_thresholds:{"1":5,"3":15,"7":35},
    frozen_corrected_thresholds:THRESH,
    deconvolution:"score=7*own-left-neighbor-right-neighbor; edges_zero",
    paired_census_by_model:aggregate,per_band_by_model:perband,
    no_light_dark_by_model:dark,wrong_map_errors_by_model_at_7:wrongmap,
    event_conservation_by_model:conservation,
    source_binding_controls:{
      changed_source_byte:"HOLD",channel_reassignment:"HOLD",
      missing_violet_2187_aliases:"HOLD",
      self_consistent_attacker_owned_digest:"ORIGIN_UNAUTHENTICATED",
      stale_fixture_nonce:"HOLD"},
    first_fixture_thresholds_exploratory:true,
    third_fixture_thresholds_frozen_before_generation:true,
    new_real_optical_measurements:0,physical_optical_storage_test:"NOT_RUN",
    biological_neural_memory_test:"NOT_RUN",external_source_custody_authenticated:false,
    hbp_bytes:hbp.length,hbp_sha256:sha(hbp)
  };
  const json=Buffer.from(canonical(report)+"\n","ascii");
  fs.mkdirSync(destination,{recursive:true});
  write(destination,"c3-third-seed.hbp",hbp);
  write(destination,"c3-results.json",json);
  console.log(JSON.stringify({verdict:"SIMULATION_PASS",
    raw_errors:Object.fromEntries(["C","D"].map(a=>[a,Object.fromEntries([1,3,7].map(n=>[n,aggregate[a][String(n)].raw_wrong]))])),
    corrected_errors:Object.fromEntries(["C","D"].map(a=>[a,Object.fromEntries([1,3,7].map(n=>[n,aggregate[a][String(n)].fixed_wrong]))])),
    dark_false_triggers:dark,hbp_sha256:sha(hbp),json_sha256:sha(json)}));
}
if(process.argv.length!==4)throw Error("usage: node c3_third_seed.js ORIGINAL_PR80_ARCHIVE OUTPUT_DIR");
run(process.argv[2],process.argv[3]);
