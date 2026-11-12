#!/usr/bin/env node
'use strict';
/* Independent pure-Node readout model for preregistered photon -> photoelectron
 * -> JSON-RPC tools/call electronic signal flow. Classical synthetic optics;
 * photons/electrons are model values, NOT measured hardware photon states.
 */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const SOURCE_SHA='02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22';
const BANK_SHA='52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345';
const INDEX_SHA='6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee';
const BANDS=['red','orange','yellow','green','blue','indigo','violet'];
const WAVELENGTHS=[650,610,580,530,470,440,405];
const SCHEMA='ASOLARIA-PHOTON-ELECTRON-MCP-CLASSICAL-V1';
const SCENARIOS=[['bright_t0',24,0,0,1],['dim_t0',1,0,0,1],['bright_t3',24,3,0,1],['dark_t0',24,0,1,1],['protected_t3',24,3,1,5]];
function sha(b){return crypto.createHash('sha256').update(b).digest('hex')}
function ck(ok,reason){if(!ok)throw Error(reason)}
function sorted(value){if(Array.isArray(value))return value.map(sorted);
  if(value&&typeof value==='object'&&!Buffer.isBuffer(value)){
    let dest={};for(let key of Object.keys(value).sort())dest[key]=sorted(value[key]);return dest;
  }return value;}
function canon(o){return Buffer.from(JSON.stringify(sorted(o))+'\n','ascii')}
function same(a,b){return canon(a).equals(canon(b))}
class XorShift32{
  constructor(scenario,ordinal){let seed=crypto.createHash('sha256').update('ASOLARIA-PHOTON-ELECTRON-V1|'+BANK_SHA+'|'+scenario+'|'+ordinal).digest();
    this.x=seed.readUInt32LE(0)||0x6d2b79f5;}
  take(){let x=this.x>>>0;x^=(x<<13)>>>0;x^=x>>>17;x^=(x<<5)>>>0;this.x=x>>>0;return this.x;}
}
function binom(n,k){let b=1n;for(let j=1;j<=k;j++)b=b*BigInt(n-j+1)/BigInt(j);return b}
function cdfThresholds(n,ticks){let nu=16n*4n**BigInt(ticks),den=25n*5n**BigInt(ticks),total=den**BigInt(n);
  let acc=0n,out=[];for(let k=0;k<=n;k++){
    acc+=binom(n,k)*nu**BigInt(k)*(den-nu)**BigInt(n-k);
    out.push(Number(acc*(1n<<32n)/total));
  }ck(out.at(-1)===4294967296,'BINOMIAL_CDF_MASS');return out;}
function sample(rng,table){const val=rng.take();for(let k=0;k<table.length;k++)if(val<table[k])return k;throw Error('BAD_DETECTOR_CDF')}
function energyYjPerPhoton(nm){const nu=662607015n*299792458n,den=1000000000n*BigInt(nm);return Number((nu+den/2n)/den)}
function getRows(sourcePath,bankPath,indexPath){const src=fs.readFileSync(sourcePath),bank=fs.readFileSync(bankPath),index=fs.readFileSync(indexPath);
  ck(sha(src)===SOURCE_SHA,'SOURCE_ROOT_MISMATCH');
  ck(sha(bank)===BANK_SHA&&bank.length===184815,'BANK_ROOT_MISMATCH');
  ck(sha(index)===INDEX_SHA&&index.length===70043,'INDEX_ROOT_MISMATCH');
  const obj=JSON.parse(src.toString('utf8'));
  ck(obj.schema==='ASOLARIA-SEAT1-81-RGB-LIGHTBANK-V1'&&obj.records.length===81,'ORIGINAL_81_INVALID');
  const lines=index.toString('ascii').split('\n');ck(lines.at(-1)===''&&lines.length===568,'BANK_ROWS_INVALID');
  lines.pop();const rows=[],seen=new Set();
  for(let ordinal=0;ordinal<lines.length;ordinal++){
    const fields=lines[ordinal].split('|');ck(fields.length===6&&fields[0]==='MEM','ROW_FORMAT');
    const kv={};for(const f of fields.slice(1)){let at=f.indexOf('=');ck(at>0,'ROW_FIELD');kv[f.slice(0,at)]=f.slice(at+1)}
    ck(Object.keys(kv).sort().join(',')==='band,id,length,offset,sha256','INDEX_FIELDS');
    const band=kv.band,site=kv.id,siteN=Number(site?.slice(5));
    ck(BANDS.includes(band)&&/^site-\d{3}$/.test(site)&&siteN>=0&&siteN<81,'BAND_SITE_INVALID');
    const key=band+'|'+site;ck(!seen.has(key),'DUPLICATE_BANK_ROW');seen.add(key);
    const offset=Number(kv.offset),size=Number(kv.length);
    ck(Number.isSafeInteger(offset)&&Number.isSafeInteger(size)&&offset>=0&&size>0&&offset+size<=bank.length,'INDEX_BOUNDS');
    const raw=bank.subarray(offset,offset+size);ck(sha(raw)===kv.sha256,'ROW_HASH_INVALID');
    const rec=JSON.parse(raw.toString('utf8'));
    ck(rec.schema==='ASOLARIA-RAINBOW7-BANK-ENTRY-V1'&&rec.id===site&&rec.band===band&&
       rec.address==='rainbow7/'+band+'/'+site&&same(rec.record,obj.records[siteN]),'RECORD_ANCESTRY');
    rows.push({ordinal,band,site,raw,sha:kv.sha256,sector:ordinal%27,wavelength:WAVELENGTHS[BANDS.indexOf(band)]});
  }
  ck(seen.size===567&&new Set(rows.map(x=>x.site)).size===81,'INCOMPLETE_BANK');return rows;
}
function buildFrame(row,scenario){const [name,pulse,ticks,darkPer1000,copies]=scenario;
  const rng=new XorShift32(name,row.ordinal),cdf=cdfThresholds(pulse,ticks);
  let emitted=0,photoelectrons=0,darkElectrons=0,errors=0;
  const decoded=Buffer.alloc(row.raw.length);
  for(let i=0;i<row.raw.length;i++){
    let rebuilt=0;
    for(let shift=7;shift>=0;shift--){const bit=(row.raw[i]>>>shift)&1;let votes=0;
      for(let c=0;c<copies;c++){
        let photo=0;
        if(bit){emitted+=pulse;photo=sample(rng,cdf);photoelectrons+=photo}
        const dark=darkPer1000&&rng.take()<Math.floor(4294967296/1000)?1:0;
        darkElectrons+=dark;votes+=Number(photo+dark>0);
      }
      const observed=Number(votes>Math.floor(copies/2));errors+=Number(observed!==bit);
      rebuilt=(rebuilt<<1)|observed;
    }
    decoded[i]=rebuilt;
  }
  ck(photoelectrons<=emitted,'ELECTRON_PHOTON_CONSERVATION');
  ck(darkElectrons<=row.raw.length*8*copies,'DARK_ELECTRON_BOUND');
  const observedSha=sha(decoded);
  const nonce=sha(Buffer.from('ASOLARIA-MCP-CAPTURE|'+BANK_SHA+'|'+name+'|'+row.ordinal)).slice(0,24);
  const msgId=name+':'+row.ordinal;
  const request={jsonrpc:'2.0',id:msgId,method:'tools/call',params:{name:'electron.capture',arguments:{
    source_sha256:SOURCE_SHA,bank_sha256:BANK_SHA,site:row.site,band:row.band,sector:row.sector,
    wavelength_nm_assumed:row.wavelength,held_ticks_assumed:ticks,context_nonce:nonce,
    expected_row_sha256:row.sha,observed_row_sha256:observedSha,
    emitted_photons_modeled:emitted,photoelectrons_modeled:photoelectrons,
    dark_electrons_modeled:darkElectrons}}};
  const response={jsonrpc:'2.0',id:msgId,result:{status:errors===0?'EXACT_READBACK':'BIT_ERRORS',
    electron_engine:'SIMULATED',photoelectrons_modeled:photoelectrons,observed_row_sha256:observedSha}};
  return {schema:SCHEMA,scenario:name,ordinal:row.ordinal,site:row.site,band:row.band,
    sector:row.sector,wavelength_nm_assumed:row.wavelength,expected_row_sha256:row.sha,
    observed_row_sha256:observedSha,readback_hex:decoded.toString('hex'),bit_errors:errors,
    emitted_photons_modeled:emitted,photoelectrons_modeled:photoelectrons,
    dark_electrons_modeled:darkElectrons,emitted_energy_yJ_assumed:emitted*energyYjPerPhoton(row.wavelength),
    context_nonce:nonce,mcp_request:request,mcp_response:response};
}
function requireFrame(candidate,reference){ck(same(candidate,reference),'INDEPENDENT_TRUTH_MISMATCH');
  const arg=candidate.mcp_request.params.arguments;
  ck(candidate.mcp_request.method==='tools/call'&&candidate.mcp_request.params.name==='electron.capture'&&
     arg.source_sha256===SOURCE_SHA&&arg.bank_sha256===BANK_SHA,'MCP_AUTHORITY_OR_TOOL');
  ck(candidate.mcp_response.id===candidate.mcp_request.id&&
     candidate.mcp_response.result.photoelectrons_modeled===candidate.photoelectrons_modeled,'MCP_RESPONSE_BINDING');
  ck(sha(Buffer.from(candidate.readback_hex,'hex'))===candidate.observed_row_sha256,'READBACK_DIGEST');
}
function negativeControls(frame){const mods=[
  ['changed_band',o=>o.band='violet'],
  ['swapped_wavelength',o=>o.wavelength_nm_assumed=405],
  ['reassigned_sector',o=>o.sector=(o.sector+1)%27],
  ['forged_source_root',o=>o.mcp_request.params.arguments.source_sha256='0'.repeat(64)],
  ['changed_row_hash',o=>o.expected_row_sha256='a'.repeat(64)],
  ['counterfeit_electron',o=>o.photoelectrons_modeled=o.emitted_photons_modeled+1],
  ['replay_context_nonce',o=>o.context_nonce='stale-nonce'],
  ['wrong_tool_name',o=>o.mcp_request.params.name='photon.fake'],
  ['modified_readback',o=>o.readback_hex='00'+o.readback_hex.slice(2)],
  ['response_mismatch',o=>o.mcp_response.result.photoelectrons_modeled=-1],
  ['missing_frame',o=>{for(let key of Object.keys(o))delete o[key]}],
  ['coherent_local_hash_spoof',o=>{o.observed_row_sha256='f'.repeat(64);
    o.mcp_request.params.arguments.observed_row_sha256='f'.repeat(64);
    o.mcp_response.result.observed_row_sha256='f'.repeat(64)}]
];const reject=[];
  for(const [name,fn] of mods){let mutant=JSON.parse(JSON.stringify(frame));fn(mutant);
    try{requireFrame(mutant,frame)}catch(e){reject.push(name+':'+e.message);continue}throw Error('ATTACK_ACCEPTED:'+name);
  }ck(reject.length===12,'NEGATIVE_TEST_COVERAGE');return reject;
}
function run(sourcePath,bankPath,indexPath,outDir){const rows=getRows(sourcePath,bankPath,indexPath);fs.mkdirSync(outDir,{recursive:true});
  let lines=[],cases=[],negatives=null;
  for(const scenario of SCENARIOS){const [name,pulse,ticks,dark,copies]=scenario;
    const stat={scenario:name,photons_per_one:pulse,hold_ticks:ticks,dark_per_1000:dark,
      replicas:copies,rows:0,source_bytes:0,bit_windows:0,bit_errors:0,exact_rows:0,
      emitted_photons_modeled:0,photoelectrons_modeled:0,dark_electrons_modeled:0,
      emitted_energy_yJ_assumed:0};
    for(const row of rows){let frame=buildFrame(row,scenario);
      if(negatives===null)negatives=negativeControls(frame);
      requireFrame(frame,frame);lines.push(canon(frame));stat.rows++;
      stat.source_bytes+=row.raw.length;stat.bit_windows+=row.raw.length*8*copies;
      stat.bit_errors+=frame.bit_errors;stat.exact_rows+=Number(frame.bit_errors===0);
      for(const key of ['emitted_photons_modeled','photoelectrons_modeled','dark_electrons_modeled',
                        'emitted_energy_yJ_assumed'])stat[key]+=frame[key];
    }
    ck(stat.rows===567&&stat.source_bytes===184815,'INCOMPLETE_FULL_BANK');cases.push(stat);
  }
  ck(lines.length===2835,'MISSING_SIMULATED_FRAMES');const hbp=Buffer.concat(lines);
  const results={schema:SCHEMA,source_sha256:SOURCE_SHA,bank_sha256:BANK_SHA,index_sha256:INDEX_SHA,
    original_memory_records:81,stored_bank_rows:567,retained_bank_bytes:184815,
    modeled_wavelengths_nm:Object.fromEntries(BANDS.map((b,i)=>[b,WAVELENGTHS[i]])),
    physical_computation_executed:true,physical_photon_detection_measured:false,
    optical_storage_measured:false,electron_charge_physically_measured:false,
    external_origin_authenticated:false,mcp_transport_real_server:false,
    software_electron_mcp_tool_name:'electron.capture',quantum_effect_verified:false,
    model_name:'CLASSICAL_ON_OFF_KEYING_WITH_BINOMIAL_PHOTODETECTION_AND_REPETITION',
    photon_hbp_sha256:sha(hbp),photon_hbp_bytes:hbp.length,
    negative_controls_rejected:negatives.length,negative_control_reasons:negatives,scenarios:cases};
  const files={'photon-electron.hbp':hbp,'results.json':canon(results)};
  for(const [name,bytes] of Object.entries(files)){
    fs.writeFileSync(path.join(outDir,name),bytes);
    fs.writeFileSync(path.join(outDir,name+'.sha256'),sha(bytes)+'  '+name+'\n','ascii');
  }
  console.log(JSON.stringify({status:'PASS',hbp_sha256:sha(hbp),hbp_bytes:hbp.length,
    negative_controls:negatives.length,
    scenarios:cases.map(x=>[x.scenario,x.bit_errors,x.exact_rows])}));
}
if(process.argv.length!==6)throw Error('usage: node electron_verifier.js source-json bank-jsonl index-hbi output_dir');
run(...process.argv.slice(2));
