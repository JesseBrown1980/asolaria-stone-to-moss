#!/usr/bin/env node
"use strict";
/* Independent Node BigInt implementation. Digital indexed RGB packets only. */
const fs=require("node:fs"),crypto=require("node:crypto");
const SCHEMA="ASOLARIA-SEAT1-AUGUST-LIGHTBANK-PHOTOCYCLE-V1";
const S=1000000000n,LENGTHS=[436,2536,4636,6736],COLORS=["R","G","B"];
const ARMS=["dark","open_loop","feedback_now","feedback_delay5","feedback_stale25"];
const CHECKS=new Set([0,7,8,23,24,39,40,55,56,63]);
const sha=x=>crypto.createHash("sha256").update(x).digest("hex");
function ok(c,m){if(!c)throw Error(m);}
function source(w,i){
  let n=LENGTHS[(w+i)%4],blocks=[],size=0,k=0;
  while(size<n){let b=crypto.createHash("sha256").update("LIGHTBANK|AUGUST|V1|"+w+"|"+i+"|"+k,"ascii").digest();
    blocks.push(b);size+=b.length;k++;}
  return Buffer.concat(blocks).subarray(0,n);
}
function packetize(data,w,i){
  let chunks=[];
  for(let off=0;off<data.length;off+=2100)chunks.push(data.subarray(off,off+2100));
  const packets=chunks.map((chunk,j)=>{
    const header=Buffer.alloc(4);header.writeUInt32LE(j);
    return {index:j,wave:w,site:i,group:Math.floor(j/3),channel:COLORS[j%3],
            b64:Buffer.concat([header,chunk]).toString("base64")};});
  const parity=[];
  for(let group=0;group<Math.ceil(chunks.length/3);group++){
    const members=[];
    for(let d=0;d<3;d++){
      const j=group*3+d;
      if(j>=chunks.length){members.push(Buffer.alloc(0));continue;}
      const header=Buffer.alloc(4);header.writeUInt32LE(j);
      members.push(Buffer.concat([header,chunks[j]]));
    }
    const x=Buffer.alloc(Math.max(...members.map(z=>z.length)));
    for(const lane of members)for(let n=0;n<lane.length;n++)x[n]^=lane[n];
    parity.push({group,lengths:members.map(z=>z.length),xor_b64:x.toString("base64")});
  }
  return {packets,parity,manifest:{wave:w,site:i,count:chunks.length,size:data.length,sha:sha(data)}};
}
function strictBase64(encoded){
  ok(typeof encoded==="string"&&encoded.length%4===0&&/^[A-Za-z0-9+/]*={0,2}$/.test(encoded),"INVALID_BASE64");
  const b=Buffer.from(encoded,"base64");
  ok(b.toString("base64")===encoded,"INVALID_BASE64");
  return b;
}
function read(packets,parity,manifest,w,i,repair=false){
  if(manifest.wave!==w||manifest.site!==i)throw Error("WRONG_SOURCE");
  const seen=new Map();
  for(const pkt of packets){
    const idx=pkt.index;
    if(pkt.wave!==w||pkt.site!==i)throw Error("WRONG_SOURCE");
    if(!Number.isInteger(idx)||idx<0||idx>=manifest.count||seen.has(idx))throw Error("INVALID_OR_DUPLICATE_INDEX");
    if(pkt.channel!==COLORS[idx%3]||pkt.group!==Math.floor(idx/3))throw Error("WRONG_RGB_LANE");
    const raw=strictBase64(pkt.b64);
    if(raw.length<4||raw.readUInt32LE(0)!==idx)throw Error("HEADER_BAD");
    seen.set(idx,raw);
  }
  const missing=[];
  for(let idx=0;idx<manifest.count;idx++)if(!seen.has(idx))missing.push(idx);
  if(missing.length){
    if(missing.length!==1||!repair)throw Error("ERASURE");
    const idx=missing[0],group=Math.floor(idx/3);
    const p=parity[group];
    if(p.group!==group)throw Error("WRONG_PARITY");
    const row=strictBase64(p.xor_b64);
    for(let k=group*3;k<group*3+3;k++){
      if(k===idx||k>=manifest.count)continue;
      if(!seen.has(k))throw Error("DOUBLE_ERASURE");
      const b=seen.get(k);
      for(let n=0;n<b.length;n++)row[n]^=b[n];
    }
    const recovered=row.subarray(0,p.lengths[idx%3]);
    if(recovered.length<4||recovered.readUInt32LE(0)!==idx)throw Error("BAD_PARITY");
    seen.set(idx,recovered);
  }
  if(seen.size!==manifest.count)throw Error("MISSING_CHUNK");
  const blocks=[];
  for(let j=0;j<manifest.count;j++)blocks.push(seen.get(j).subarray(4));
  const result=Buffer.concat(blocks);
  if(result.length!==manifest.size||sha(result)!==manifest.sha)throw Error("SHA_BAD");
  return result;
}
function mm(x){const sum=x.reduce((a,b)=>a+b,0);return x.map(a=>3*a-sum);}
function projector(){
  const rows=[];
  for(let w=0;w<27;w++){
    const x=[w%3,Math.floor(w/3)%3,Math.floor(w/9)%3],y=mm(x),ground=x.reduce((a,b)=>a+b,0);
    ok(y.reduce((a,b)=>a+b,0)===0,"projector sum");
    ok(mm(y).every((t,j)=>t===3*y[j]),"projector idempotence");
    ok(y.every((v,j)=>(v+ground)%3===0&&(v+ground)/3===x[j]),"ground missing");
    ok(mm(x.map(z=>z+5)).every((v,j)=>v===y[j]),"common mode lost");
    rows.push("PROJECTOR|w="+w+"|x="+x.join(",")+"|y="+y.join(",")+"|ground="+ground+"|noninvertible_without_ground=1");
  }
  return rows;
}
function prob(r){r=BigInt(r);return S*r*20n/(1000000n+r*20n)}
const PA=prob(800),PB=prob(450),PG=prob(120);
function step(state,light){
  const [c,o,r]=state;
  if(c<0n||o<0n||r<0n||c+o+r!==S)throw Error("NONCONSERVATIVE_STATE");
  const co=c*(light?PA:0n)/S,orr=o*PB/S,rc=r*PG/S;
  const next=[c-co+rc,o+co-orr,r+orr-rc];
  if(next.some(x=>x<0n)||next.reduce((a,b)=>a+b,0n)!==S)throw Error("NONCONSERVATIVE_STEP");
  return next;
}
function simulate(){
  const rows=["MODEL|schema="+SCHEMA+"|waves=27|sites=81|arms=5|ticks=64|chunk=2100|qr_image_pixels=0|photons_measured=0",...projector()];
  const stats=Object.fromEntries(ARMS.map(a=>[a,{lit:0,switches:0,gate_pass:0,gate_hold:0,error:0}]));
  const root=crypto.createHash("sha256");
  let frames=0,memory=0;const census={T:0,A:0,R:0};
  for(let w=0;w<27;w++){
    census[["T","A","R"][w%3]]++;
    for(let i=0;i<81;i++){
      const payload=source(w,i),{packets,parity,manifest}=packetize(payload,w,i);
      ok(read([...packets].reverse(),parity,manifest,w,i).equals(payload),"clean decode");
      root.update(Buffer.from(manifest.sha,"hex"));
      const ident="site-"+String(i).padStart(3,"0");
      for(const arm of ARMS){
        let state=[S,0n,0n],history=[],last=0;
        for(let tick=0;tick<64;tick++){
          const [c,o,r]=state;
          const enabled=(tick>=8&&tick<24)||(tick>=40&&tick<56);
          let light=0;
          if(arm==="dark")light=0;
          else if(arm==="open_loop")light=Number(enabled);
          else if(arm==="feedback_now")light=Number(enabled&&o<100000000n);
          else{
            const lag=arm==="feedback_delay5"?5:25;
            const obs=tick>=lag?history[tick-lag]:0n;
            light=Number(enabled&&obs<100000000n);
          }
          history.push(o);
          stats[arm].lit+=light;
          stats[arm].switches+=Number(light!==last);
          last=light;state=step(state,light);
          stats[arm].error+=Number((state[1]-(enabled?100000000n:0n))<0n?
            -(state[1]-(enabled?100000000n:0n)):(state[1]-(enabled?100000000n:0n)));
          if(CHECKS.has(tick)){
            const [newc,newo,newr]=state;
            const current=-(120000n*newo/S);
            rows.push("FRAME|w="+w+"|id="+ident+"|arm="+arm+"|tick="+tick+
              "|C="+newc+"|O="+newo+"|R="+newr+"|I_millipA="+current);
            frames++;
          }
        }
        const gate=state[1]>=50000000n?"PASS":"HOLD";
        stats[arm][gate==="PASS"?"gate_pass":"gate_hold"]++;
        rows.push("MEMORY|w="+w+"|id="+ident+"|arm="+arm+"|chunks="+manifest.count+
          "|bytes="+manifest.size+"|sha="+manifest.sha+"|gate="+gate);
        memory++;
      }
    }
  }
  ok(JSON.stringify(census)===JSON.stringify({T:9,A:9,R:9}),"census");
  ok(frames===109350&&memory===10935,"row count");
  rows.push("CENSUS|T=9|A=9|R=9|tritsum=0|digitally_classified=1");
  rows.push("END|frames=109350|memory=10935|projector=27|hardware_readbacks=0");
  const raw=Buffer.from(rows.join("\n")+"\n","ascii");
  const report={schema:SCHEMA,status:"PASS",trace_sha256:sha(raw),trace_bytes:raw.length,
    source_sha256_root:root.digest("hex"),frames,memory_rows:memory,
    projector_cases:27,optical_hardware:false,qr_pixel_codec:false,
    biology_measured:false,metrics:stats};
  return {raw,report};
}
function main(){
  if(process.argv.length!==4)throw Error("usage: node lightbank_node.js output.hbp output.json");
  const {raw,report}=simulate();
  fs.writeFileSync(process.argv[2],raw);
  fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+"\n");
  console.log(JSON.stringify({status:"PASS",sha256:report.trace_sha256,
       frames:report.frames,memory:report.memory_rows,projector:report.projector_cases}));
}
if(require.main===module)main();
module.exports={source,packetize,read,step,projector,simulate};
