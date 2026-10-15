#!/usr/bin/env node
"use strict";
/* Independent Node22 photon–phonon–electron model. All optical/acoustic
 * quantities are software values, not physically measured photons/phonons.
 */
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
const BANK_ROOT="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345";
const INDEX_ROOT="6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee";
const SOURCE_ROOT="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22";
const BANDS=["red","orange","yellow","green","blue","indigo","violet"];
const WAVELENGTHS=[650,610,580,530,470,440,405];
const SCHEMA="ASOLARIA-SEAT1-PHOTON-PHONON-ELECTRON-MEMORY-MODEL-V1";
const ARMS=[
 ["reference_bright",24,64,100,0,"OFF","NONE",0],
 ["baseline_t0",8,32,100,0,"OFF","NONE",0],
 ["resonant_phase0",8,44,100,0,"RESONANT","0",0],
 ["resonant_phase180",8,20,100,0,"RESONANT","180",0],
 ["off_resonance",8,32,100,0,"OFF_RESONANCE","0",0],
 ["thermal_sham",8,36,100,0,"THERMAL_SHAM","NONE",0],
 ["detector_dark_noise",8,32,100,1,"OFF","NONE",0],
 ["optical_dark",0,0,100,0,"OFF","NONE",0],
 ["acoustic_only",0,0,100,0,"RESONANT","0",0],
 ["held_t3",8,16,100,0,"OFF","NONE",3],
 ["held_t3_resonant",8,22,100,0,"RESONANT","0",3],
 ["held_t3_erased",0,0,100,0,"OFF","NONE",3]
];
const sha=b=>crypto.createHash("sha256").update(b).digest("hex");
function check(x,e){if(!x)throw Error(e)}
function ordered(x){if(Array.isArray(x))return x.map(ordered);if(x&&typeof x==="object"&&!Buffer.isBuffer(x)){const o={};for(const k of Object.keys(x).sort())o[k]=ordered(x[k]);return o}return x}
const canon=x=>Buffer.from(JSON.stringify(ordered(x))+"\n","ascii");
class RNG{
 constructor(ordinal,lane){const h=crypto.createHash("sha256").update("ASOLARIA-COUPLING-A|"+BANK_ROOT+"|"+ordinal+"|"+lane).digest();this.s=h.readUInt32LE(0)||0x6d2b79f5}
 draw(){let x=this.s>>>0;x^=(x<<13)>>>0;x^=x>>>17;x^=(x<<5)>>>0;this.s=x>>>0;return this.s}
}
function comb(n,k){let value=1n;for(let z=1;z<=k;z++)value=value*BigInt(n-z+1)/BigInt(z);return value}
function cdf(n,num,den){if(n===0)return [4294967296];const N=BigInt(n),p=BigInt(num),d=BigInt(den);let total=d**N,acc=0n,out=[];
 for(let k=0;k<=n;k++){acc+=comb(n,k)*p**BigInt(k)*(d-p)**BigInt(n-k);out.push(Number(acc*(1n<<32n)/total))}
 check(out.at(-1)===4294967296,"CDF_MASS");return out}
function sample(table,u){let lo=0,hi=table.length;while(lo<hi){const mid=(lo+hi)>>>1;if(table[mid]<=u)lo=mid+1;else hi=mid}return lo}
function lif(data){let m=0,spikes=0;const out=[];for(let i=0;i<data.length;i++){let b=data[i];for(let shift=7;shift>=0;shift--){let bit=(b>>>shift)&1;m=Math.max(0,m-1)+4*bit;if(m>=7){spikes++;m-=7}if((i*8+7-shift)%32===31){out.push(spikes);spikes=0}}}if(data.length*8%32)out.push(spikes);return Buffer.from(out)}
function load(original,bankFile,indexFile){
 const source=fs.readFileSync(original),bank=fs.readFileSync(bankFile),index=fs.readFileSync(indexFile);
 check(sha(source)===SOURCE_ROOT,"ORIGINAL_QR_SHA");
 check(bank.length===184815&&sha(bank)===BANK_ROOT,"BANK_ROOT");
 check(index.length===70043&&sha(index)===INDEX_ROOT,"INDEX_ROOT");
 const sources=JSON.parse(source.toString("utf8"));check(sources.records.length===81,"ORIGINAL_MEMORIES");
 const result=[],seen=new Set(),lines=index.toString("ascii").split("\n");
 check(lines.at(-1)==="","INDEX_TERMINATOR");lines.pop();
 for(let ordinal=0;ordinal<lines.length;ordinal++){
   const parts=lines[ordinal].split("|");check(parts.length===6&&parts[0]==="MEM","INDEX_ROW");
   const f={};for(const part of parts.slice(1)){const at=part.indexOf("=");check(at>0,"INDEX_FIELDS");f[part.slice(0,at)]=part.slice(at+1)}
   check(Object.keys(f).sort().join(",")==="band,id,length,offset,sha256","INDEX_FIELDS");
   const band=f.band,site=f.id,start=Number(f.offset),length=Number(f.length);
   check(BANDS.includes(band)&&site.length===8&&site.startsWith("site-"),"SOURCE_LABEL");
   const key=site+"|"+band;check(!seen.has(key),"REPEATED_SOURCE");seen.add(key);
   check(start>=0&&length>0&&start+length<=bank.length,"INDEX_BOUNDS");
   const data=bank.subarray(start,start+length);check(sha(data)===f.sha256,"INDEX_ROW_HASH");
   const obj=JSON.parse(data.toString("utf8"));
   check(JSON.stringify(ordered(obj.record))===JSON.stringify(ordered(sources.records[Number(site.slice(5))]))
      &&obj.band===band&&obj.id===site,"SOURCE_ANCESTRY");
   result.push([ordinal,site,band,data,sha(data),lif(data)]);
 }
 check(result.length===567&&seen.size===567,"MISSING_MEMORY");return {rows:result,bank};
}
function frame(row,arm,signal,dark,table){
 const [ordinal,site,band,data,trusted,trained]=row;
 const [name,n,pnum,pden,noise,acoustic,phase,hold]=arm;
 const recovered=Buffer.alloc(data.length);
 let emitted=0,electrons=0,dark_e=0,bit_errors=0,ones_miss=0,zeros_false=0;
 let position=0;
 for(let i=0;i<data.length;i++){
   let observed=0;
   for(let shift=7;shift>=0;shift--){
     const bit=(data[i]>>>shift)&1,u=signal[position],v=dark[position];position++;
     const photo=bit&&n?sample(table,u):0;
     if(bit)emitted+=n;
     electrons+=photo;
     const de=Number(noise>0&&v<Math.floor(4294967296*noise/1000));
     dark_e+=de;
     const result=Number(photo+de>0);
     observed=(observed<<1)|result;
     bit_errors+=Number(bit!==result);
     ones_miss+=Number(bit===1&&result===0);
     zeros_false+=Number(bit===0&&result===1);
   }recovered[i]=observed;
 }
 check(position===data.length*8&&electrons<=emitted,"PHOTON_ELECTRON_BUDGET");
 const fp=lif(recovered),neural_match=fp.equals(trained),byte_match=sha(recovered)===trusted,authorized=neural_match&&byte_match;
 const nonce=sha(Buffer.from("ASOLARIA-COUPLING-NONCE|"+BANK_ROOT+"|"+name+"|"+ordinal)).slice(0,24);
 const wave=WAVELENGTHS[BANDS.indexOf(band)],observedSha=sha(recovered);
 const args={bank_sha256:BANK_ROOT,source_sha256:SOURCE_ROOT,index_sha256:INDEX_ROOT,
   site,band,sector:ordinal%27,wavelength_nm_assumed:wave,
   phonon_drive:acoustic,phase_deg:phase,hold_ticks_assumed:hold,
   signal_photons_modeled:emitted,photoelectrons_modeled:electrons,
   dark_electrons_modeled:dark_e,readback_sha256:observedSha,
   reference_sha256:trusted,nonce};
 const gate={trained_fingerprint_sha256:sha(trained),observed_fingerprint_sha256:sha(fp),
   fingerprint_match:neural_match,source_hash_match:byte_match,authorized};
 return {schema:SCHEMA,arm:name,ordinal,site,band,sector:ordinal%27,
   wavelength_nm_assumed:wave,phonon_drive:acoustic,phase_deg:phase,
   hold_ticks_assumed:hold,photons_per_source_one:n,
   detection_probability_numerator:pnum,detection_probability_denominator:pden,
   dark_per_1000:noise,emitted_photons_modeled:emitted,
   photoelectrons_modeled:electrons,dark_electrons_modeled:dark_e,
   reference_sha256:trusted,readback_sha256:observedSha,
   readback_hex:recovered.toString("hex"),bit_errors,
   missed_one_bits:ones_miss,false_zero_bits:zeros_false,
   neural_only_match:neural_match,source_byte_exact:byte_match,
   strict_authorized:authorized,nonce,
   mcp_capture:{jsonrpc:"2.0",id:"electron:"+name+":"+ordinal,method:"tools/call",
     params:{name:"electron.capture",arguments:args}},
   mcp_neural_gate:{jsonrpc:"2.0",id:"neuron:"+name+":"+ordinal,method:"tools/call",
     params:{name:"neuron.gate",arguments:gate}}};
}
function validate(candidate,row,arm,signal,dark,table){
 check(canon(candidate).equals(canon(frame(row,arm,signal,dark,table))),"INDEPENDENT_SOURCE_REPLAY_FAIL_CLOSED");
 check(candidate.mcp_capture.params.name==="electron.capture"&&
   candidate.mcp_neural_gate.params.name==="neuron.gate","INVALID_MCP_TOOL");
 check(candidate.strict_authorized===
  (candidate.source_byte_exact&&candidate.neural_only_match),"FALSE_AUTHORIZATION");
}
function negatives(row,arm,signal,dark,table,original){
 const mutants=[
 ["changed_row_payload",x=>x.readback_hex="00"+x.readback_hex.slice(2)],
 ["coherent_local_readback_forgery",x=>{x.readback_sha256="f".repeat(64);x.mcp_capture.params.arguments.readback_sha256="f".repeat(64)}],
 ["swapped_band",x=>x.band="violet"],
 ["swapped_wavelength",x=>x.wavelength_nm_assumed=405],
 ["swapped_site",x=>x.site="site-080"],
 ["bad_sector",x=>x.sector=(x.sector+1)%27],
 ["phase_spoof",x=>x.phase_deg="180"],
 ["phonon_spoof",x=>x.phonon_drive="RESONANT"],
 ["impossible_electrons",x=>x.photoelectrons_modeled=x.emitted_photons_modeled+1],
 ["replayed_nonce",x=>x.nonce="stale"],
 ["forged_bank_root",x=>x.mcp_capture.params.arguments.bank_sha256="0".repeat(64)],
 ["forged_capture_tool",x=>x.mcp_capture.params.name="electron.bypass"],
 ["forged_neural_gate",x=>x.mcp_neural_gate.params.arguments.authorized=false],
 ["missing_frame",x=>{for(const k of Object.keys(x))delete x[k]}]
 ];
 const rejected=[];
 for(const [name,mutation] of mutants){
   const test=JSON.parse(JSON.stringify(original));mutation(test);
   try{validate(test,row,arm,signal,dark,table)}
   catch(e){rejected.push({attack:name,held:true,why:e.message});continue}
   throw Error("ATTACK_ACCEPTED:"+name)
 }
 check(rejected.length===14,"MUTATION_COVERAGE");return rejected;
}
function run(original,bankFile,indexFile,dest){
 const {rows,bank}=load(original,bankFile,indexFile),ones=[...bank].reduce((s,x)=>s+popcount(x),0),zeros=bank.length*8-ones;
 check(ones===662443&&zeros===816077,"BANK_BIT_DISTRIBUTION");
 const tables=Object.fromEntries(ARMS.map(a=>[a[0],cdf(a[1],a[2],a[3])]));
 const summaries=ARMS.map(a=>({
   arm:a[0],photons_per_one:a[1],p_num:a[2],p_den:a[3],dark_per_1000:a[4],
   phonon_drive:a[5],phase_deg:a[6],hold_ticks:a[7],
   rows:0,source_bytes:0,bit_errors:0,missed_one_bits:0,false_zero_bits:0,exact_rows:0,
   neural_only_matches:0,neural_false_greens:0,authorized_rows:0,
   emitted_photons_modeled:0,photoelectrons_modeled:0,dark_electrons_modeled:0
 }));
 const chunks=ARMS.map(()=>[]);let recorded_negatives=null,erasure_rows=0;
 for(const row of rows){
   const [ordinal,site,band,data]=row;
   const signal=new RNG(ordinal,"signal"),dark=new RNG(ordinal,"dark");
   const us=new Array(data.length*8),vs=new Array(data.length*8);
   for(let i=0;i<us.length;i++)us[i]=signal.draw();
   for(let i=0;i<vs.length;i++)vs[i]=dark.draw();
   for(let j=0;j<ARMS.length;j++){
      const arm=ARMS[j],out=frame(row,arm,us,vs,tables[arm[0]]);
      validate(out,row,arm,us,vs,tables[arm[0]]);
      if(recorded_negatives===null)recorded_negatives=negatives(row,arm,us,vs,tables[arm[0]],out);
      chunks[j].push(canon(out));
      const s=summaries[j];
      s.rows++;s.source_bytes+=data.length;s.bit_errors+=out.bit_errors;
      s.missed_one_bits+=out.missed_one_bits;s.false_zero_bits+=out.false_zero_bits;
      s.exact_rows+=Number(out.source_byte_exact);
      s.neural_only_matches+=Number(out.neural_only_match);
      s.neural_false_greens+=Number(out.neural_only_match&&!out.source_byte_exact);
      s.authorized_rows+=Number(out.strict_authorized);
      for(const k of ["emitted_photons_modeled","photoelectrons_modeled","dark_electrons_modeled"])s[k]+=out[k];
   }
   if(band==="violet")erasure_rows++;
 }
 check(erasure_rows===81&&567-erasure_rows===486,"ERASURE_COUNT");
 for(const s of summaries)check(s.rows===567&&s.source_bytes===184815,"MISSING_SOURCE_BYTES");
 const byName=Object.fromEntries(summaries.map(x=>[x.arm,x]));
 const get=name=>byName[name].bit_errors;
 check(get("reference_bright")<get("baseline_t0")&&get("resonant_phase0")<get("baseline_t0")&&
       get("resonant_phase180")>get("baseline_t0")&&get("held_t3")>get("baseline_t0")&&
       get("held_t3_resonant")<get("held_t3")&&get("thermal_sham")<get("baseline_t0")&&
       get("detector_dark_noise")>get("baseline_t0"),"COUPLING_ORDER_FALSIFIED");
 check(!Buffer.concat(chunks[1]).equals(Buffer.concat(chunks[4])),"SCENARIO_METADATA_MUST_CHANGE");
 for(let i=0;i<567;i++){
    const a=JSON.parse(chunks[1][i]),b=JSON.parse(chunks[4][i]);
    check(a.readback_hex===b.readback_hex,"OFF_RESONANCE_CONFOUNDER");
    const x=JSON.parse(chunks[7][i]),y=JSON.parse(chunks[8][i]),z=JSON.parse(chunks[11][i]);
    check(x.readback_hex===y.readback_hex&&x.readback_hex===z.readback_hex,"NO_OPTICAL_INPUT_SHOULD_NOT_TRANSDUCE");
    check(x.photoelectrons_modeled===0&&y.photoelectrons_modeled===0&&z.photoelectrons_modeled===0,"PHOTONLESS_ELECTRON_FALSE_POSITIVE");
 }
 const retained=chunks[1].filter((_,i)=>rows[i][2]!=="violet");
 check(retained.length===486&&retained.length!==567,"VIOLET_ERASURE_NOT_HELD");
 const flat=Buffer.concat(chunks.flat());
 check(flat.toString("ascii").split("\n").length===567*ARMS.length+1,"MISSING_EXPERIMENT_FRAMES");
 let analytic_count=0;
 for(const s of summaries){
   const p=s.p_num/s.p_den,d=s.dark_per_1000/1000,q1=(1-p)**s.photons_per_one*(1-d),q0=d;
   const exp=ones*q1+zeros*q0,variance=ones*q1*(1-q1)+zeros*q0*(1-q0);
   const limit=6*Math.sqrt(Math.max(1,variance))+2;
   check(Math.abs(s.bit_errors-exp)<limit,"MODEL_ANALYTIC_EXPECTATION_FAIL:"+s.arm);analytic_count++;
 }
 const manifest={schema:SCHEMA,source_sha256:SOURCE_ROOT,bank_sha256:BANK_ROOT,index_sha256:INDEX_ROOT,
   original_source_memories:81,bank_rows:567,bank_bytes:184815,source_ones:ones,source_zeros:zeros,
   scenario_count:ARMS.length,frames:567*ARMS.length,wavelengths_nm_assumed:Object.fromEntries(BANDS.map((x,i)=>[x,WAVELENGTHS[i]])),
   computational_execution_on_physical_hardware:true,actual_photon_phonon_coupling_measured:false,
   optical_storage_medium_measured:false,real_photoelectron_current_measured:false,
   biological_neuron_measured:false,real_mcp_server_operational:false,
   model_type:"DECLARED_CLASSICAL_BINOMIAL_PROBABILITY_WITH_SYNTHETIC_PHONON_DRIVE",
   negative_controls:recorded_negatives,erased_violet_rows:erasure_rows,
   missing_logical_27_sector_aliases:erasure_rows*27,
   scenario_results:summaries,analytic_checked_arms:analytic_count,
   hbp_sha256:sha(flat),hbp_bytes:flat.length};
 fs.mkdirSync(dest,{recursive:true});
 for(const [name,data] of Object.entries({"coupling.hbp":flat,"results.json":canon(manifest)})){
   fs.writeFileSync(path.join(dest,name),data);
   fs.writeFileSync(path.join(dest,name+".sha256"),sha(data)+"  "+name+"\n","ascii");
 }
 console.log(JSON.stringify({status:"PASS",hbp_sha256:sha(flat),hbp_bytes:flat.length,
   frames:567*ARMS.length,attack_controls_held:recorded_negatives.length,
   scenario_error_counts:Object.fromEntries(summaries.map(s=>[s.arm,s.bit_errors])),
   measured_photons:false}));
 return manifest;
}
function popcount(n){let x=n,s=0;while(x){s+=x&1;x>>>=1}return s}
if(process.argv.length!==6)throw Error("usage: node coupling.js original81.json retained567.jsonl base.hbi result_dir");
run(...process.argv.slice(2));
