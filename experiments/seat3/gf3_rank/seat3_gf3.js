#!/usr/bin/env node
"use strict";
/* Independently authored Node22 GF3 81-basis matrix/rank and law switching.
 * No Rust or Python source imports, HBP only, no JSON science files.
 */
const fs=require("node:fs"), path=require("node:path"), crypto=require("node:crypto");
const N=81,LAWS=[[0,1,3],[0,4,7]],HS=[0,1,3,9,27,81,82];
const COMMIT="5303c9b2ed0c0ce33da684706d57caef516ffd2b";
const BLOB="0a26e3d24ac0b0211c31c3aa32e23d50d7d0c3ec";
const digest=data=>crypto.createHash("sha256").update(data).digest("hex");
function gate(ok,msg){if(!ok)throw new Error(msg);}
function singleton(j){return Array.from({length:N},(_,i)=>Number(i===j));}
function basis(){return Array.from({length:N},(_,j)=>singleton(j));}
function advanceOne(input,taps){
  const out=Array(N).fill(0);
  for(let i=0;i<N;i++){
    let sum=0;for(const tap of taps)sum+=input[(i+N-tap)%N];
    out[i]=sum%3;
  }
  return out;
}
function advance(input,taps,n){
  let x=input.slice();for(let i=0;i<n;i++)x=advanceOne(x,taps);
  return x;
}
function rank(columns){
 const rows=Array.from({length:N},(_,i)=>columns.map(c=>c[i]));
 let piv=0;
 for(let col=0;col<N;col++){
   let row=-1;for(let i=piv;i<N;i++)if(rows[i][col]!==0){row=i;break;}
   if(row<0)continue;
   [rows[piv],rows[row]]=[rows[row],rows[piv]];
   if(rows[piv][col]===2)for(let k=0;k<N;k++)rows[piv][k]=(2*rows[piv][k])%3;
   for(let j=0;j<N;j++)if(j!==piv&&rows[j][col]!==0){
      const factor=rows[j][col];
      for(let k=0;k<N;k++)rows[j][k]=((rows[j][k]-factor*rows[piv][k])%3+3)%3;
   }
   piv++;
   if(piv===N)break;
 }
 return piv;
}
function apply(cols,input){
 const out=Array(N).fill(0);
 for(let j=0;j<N;j++)if(input[j]!==0)
   for(let i=0;i<N;i++)out[i]=(out[i]+input[j]*cols[j][i])%3;
 return out;
}
function mul(a,b){return b.map(col=>apply(a,col));}
function skip(input,taps,logicalTicks){
 let power=basis().map(b=>advanceOne(b,taps)),x=input.slice(),n=logicalTicks;
 let sq=0,selected=0;
 while(n!==0){
   if((n%2)===1){x=apply(power,x);selected++;}
   n=Math.floor(n/2);
   if(n>0){power=mul(power,power);sq++;}
 }
 return {state:x,sq,selected};
}
function valuation(taps){
 let coeff=Array(Math.max(...taps)+1).fill(0);
 for(const tap of taps)coeff[tap]=(coeff[tap]+1)%3;
 let value=0;
 while(coeff.length>1){
   const q=Array(coeff.length-1).fill(0);
   q[q.length-1]=coeff[coeff.length-1];
   for(let i=q.length-2;i>=0;i--)q[i]=(coeff[i+1]+q[i+1])%3;
   const remainder=(coeff[0]+q[0])%3;
   if(remainder!==0)break;
   coeff=q;value++;
 }
 return value;
}
function stateHash(x,h,taps){
 const n=Buffer.alloc(8);n.writeBigUInt64LE(BigInt(h));
 return digest(Buffer.concat([
   Buffer.from("ASOLARIA-C3-ORIGINAL-RUST181-GF3|","ascii"),
   Buffer.from(taps),n,Buffer.from(x)
 ]));
}
function run(outdir){
 const rows=[
  "HBP1|schema=ASOLARIA-C3-GF3-ORIGINAL81-MATRIX-RANK-V1|field=GF3|trits=-1,0,+1|Rust_source_commit="+COMMIT+"|Rust_lib_blob="+BLOB+"|json=0",
  "BOUNDARY|logical_time_not_host_clock=TRUE|original_trained_GNN_weights=NOT_LOADED|quantum_photonic_neural_memory=NOT_PROVEN|existing_reported_physical_experiment=PRESERVED|json=0"
 ];
 const origins=basis();
 const trials=[origins[0],origins[13],origins[80],
                Array.from({length:N},(_,i)=>(i*7+2)%3),
                Array.from({length:N},(_,i)=>i%3)];
 for(const taps of LAWS){
   const multiplicity=valuation(taps);
   gate(multiplicity===1,"POLYNOMIAL_VALUATION");
   let history=basis(),last=0;
   for(const h of HS){
     for(let n=last;n<h;n++)history=history.map(c=>advanceOne(c,taps));
     last=h;
     const found=rank(history),expected=N-Math.min(h*multiplicity,N);
     gate(found===expected,"RANK_EXPECTATION_DID_NOT_MATCH");
     for(const seed of trials){
       const expectedState=advance(seed,taps,h);
       const fast=skip(seed,taps,h).state;
       gate(fast.every((value,i)=>value===expectedState[i]),"MATRIX_STEPWISE_DISAGREE");
       const projected=apply(history,seed);
       gate(fast.every((value,i)=>value===projected[i]),"POWER_BASIS_DISAGREE");
     }
     if(h>=81)gate(history.every(c=>c.every(v=>v===0)),"NILPOTENT_81_NOT_ZERO");
     const final=advance(trials[0],taps,h);
     rows.push("RANK|taps="+taps.join("")+"|logical_ticks="+h+
       "|rank="+found+"|nullity="+(N-found)+"|theoretical_rank="+expected+
       "|poly_valuation="+multiplicity+"|81_basis_reconstructed=PASS"+
       "|matrix_vs_stepwise=PASS|sha256="+stateHash(final,h,taps)+"|json=0");
   }
   gate(advanceOne(Array(N).fill(1),taps).every(x=>x===0),"CONSTANT_KERNEL");
   gate(advanceOne(Array(N).fill(0),taps).every(x=>x===0),"ZERO_KERNEL");
   gate(trials.every(x=>advance(x,taps,81).every(y=>y===0)),"NILPOTENCE_TEST");
   rows.push("COLLISION|taps="+taps.join("")+
       "|zero_vs_all_ones_after_tick1=SAME_ZERO|kernel_after_27=3^27|kernel_after_81=3^81"+
       "|underlying_source_history_reconstructible_from_surface_only=FALSE|separate_history_required=TRUE|json=0");
 }
 const first=LAWS[0],second=LAWS[1];
 let mismatch=0;
 for(const x of origins){
   const correct=advance(advance(x,first,17),second,23);
   const fast=skip(skip(x,first,17).state,second,23).state;
   const wrong=skip(x,first,40).state;
   gate(fast.every((v,j)=>v===correct[j]),"COMPOSED_LAW_SWITCH_FAILED");
   mismatch+=Number(wrong.some((v,j)=>v!==correct[j]));
 }
 gate(mismatch>0,"STALE_SWITCH_NEVER_FAILED");
 rows.push("LAW_SWITCH|early_law=013|early_ticks=17|late_law=047|late_ticks=23"+
      "|basis_checked=81|stale_same_law_fail_count="+mismatch+
      "|law_aware_composition=PASS|json=0");
 const genuine=skip(origins[0],[0,1,3],27).state;
 const fake=skip(origins[0],[0,1,4],27).state;
 gate(genuine.some((v,j)=>v!==fake[j]),"FAKE_TAP_NOT_DISTINGUISHED");
 gate(stateHash(genuine,27,[0,1,3])!==stateHash(fake,27,[0,1,4]),"FAKE_DIGEST_NOT_DISTINGUISHED");
 rows.push("NEGATIVES|forged_taps_014=REJECTED|forged_final_hash=REJECTED|deleted_original_history_cannot_be_rebuilt=TRUE|json=0");
 const buffer=Buffer.from(rows.join("\n")+"\n","ascii");
 const name="seat3-gf3-rank-certificate.hbp";
 fs.mkdirSync(outdir,{recursive:true});
 fs.writeFileSync(path.join(outdir,name),buffer);
 fs.writeFileSync(path.join(outdir,name+".sha256"),digest(buffer)+"  "+name+"\n");
 console.log("SEAT3_C3_GF3_81_RANK_PROOF_PASS",rows.length,"records",digest(buffer),"stale",mismatch);
}
if(process.argv.length!==3)throw Error("usage: node seat3_gf3.js OUT");
run(process.argv[2]);
