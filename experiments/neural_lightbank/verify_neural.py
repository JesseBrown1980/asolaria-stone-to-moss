#!/usr/bin/env python3
"""Independent full-bank byte and LIF-neuron signature audit across Python/Node/OS.

This validator independently computes spike patterns from source/readback bytes,
checks the original immutable bank and modeled photon HBP, and rejects any
spurious neural-only recognition as insufficient without the original row SHA.
No physical photon or biological neuron instrumentation is claimed.
"""
import hashlib,json,sys
from collections import Counter
from pathlib import Path

BANK_SHA='52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345'
INDEX_SHA='6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee'
PHOTON_SHA='332e1eeb2d4de748c2e1da07729944fefe5b63589e9533b4c93b74d7cf3f5527'
NEURAL_SHA='3eadd6827543bfd7234037d494959fb092769d74afe981e5916e32f516d5b497'
JSON_SHA='cf1cfdbe9780637861a0046d041d053e82ac0bf91418ed4256391b4ceb638675'
MODES=['bright_t0','dim_t0','bright_t3','dark_t0','protected_t3']
NEURAL=[567,0,541,231,567]
FALSE_GREEN=[0,0,27,89,0]
STRICT=[567,0,514,142,567]
FILES=['neural-gate.hbp','neural-gate.json','neural-gate.hbp.sha256','neural-gate.json.sha256']
def sha(b):return hashlib.sha256(b).hexdigest()
def require(cond,message):
    if not cond:raise AssertionError(message)

def independent_spikes(data):
    v=0;count=0;windows=[]
    bit_length=len(data)*8
    for position in range(bit_length):
        b=(data[position//8] >> (7-position%8))&1
        v=(v-1 if v>0 else 0) + (4 if b else 0)
        if v>=7:
            count+=1
            v-=7
        if position%32==31:
            windows.append(count)
            count=0
    if bit_length%32:
        windows.append(count)
    return bytes(windows)

def reference_rows(bank,index):
    b=Path(bank).read_bytes();i=Path(index).read_bytes()
    require(len(b)==184815 and sha(b)==BANK_SHA,'BANK_SHA')
    require(len(i)==70043 and sha(i)==INDEX_SHA,'INDEX_SHA')
    rows=[]
    for line in i.decode('ascii').splitlines():
        z=line.split('|')
        require(len(z)==6 and z[0]=='MEM','ROW_FORMAT')
        a=dict(v.split('=',1) for v in z[1:])
        start=int(a['offset']);size=int(a['length'])
        require(start>=0 and size>0 and start+size<=len(b),'BOUNDS')
        blob=b[start:start+size]
        require(sha(blob)==a['sha256'],'ROW_SHA')
        rows.append((a['band'],a['id'],blob,a['sha256'],independent_spikes(blob)))
    require(len(rows)==567,'ROWS')
    return rows

def validate(dir_name,rows,parent):
    folder=Path(dir_name)
    chunks={name:(folder/name).read_bytes() for name in FILES}
    for name in FILES[:2]:
        require(chunks[name+'.sha256']==(sha(chunks[name])+'  '+name+'\n').encode(),'SIDECAR')
    require(sha(chunks['neural-gate.hbp'])==NEURAL_SHA,'NEURAL_HBP_SHA')
    require(sha(chunks['neural-gate.json'])==JSON_SHA,'NEURAL_JSON_SHA')
    summary=json.loads(chunks['neural-gate.json'])
    require(summary['neural_hbp_sha256']==NEURAL_SHA and summary['neural_hbp_bytes']==5062131,'HBP_PROPERTIES')
    require(summary['parent_hbp_sha256']==PHOTON_SHA and summary['bank_sha256']==BANK_SHA,'PARENT_ROOT')
    require(summary['violet_missing_rows_under_erasure']==81 and
            summary['violet_missing_27_sector_aliases']==2187 and
            summary['erasure_full_bank_status']=='HELD','ERASURE_NOT_HELD')
    require(not summary['physical_photon_storage_measured'] and not summary['biological_neuron_measured']
            and not summary['real_mcp_server_operational'],'PHYSICAL_SCOPE')
    frames=chunks['neural-gate.hbp'].splitlines()
    require(len(frames)==2835,'FRAME_COUNT')
    counts=Counter();neural=Counter();false_green=Counter();strict=Counter()
    seen=set()
    for idx,line in enumerate(frames):
        x=json.loads(line)
        mode=MODES[idx//567];ordinal=idx%567
        require(x['scenario']==mode and x['ordinal']==ordinal,'FRAME_ORDER')
        require((mode,ordinal) not in seen,'DUPLICATE_FRAME')
        seen.add((mode,ordinal))
        band,site,source,source_sha,trained=rows[ordinal]
        obsparent=json.loads(parent[idx])
        obs=bytes.fromhex(obsparent['readback_hex'])
        fp=independent_spikes(obs)
        matched=fp==trained
        byte_correct=sha(obs)==source_sha
        require(x['site']==site and x['band']==band and x['sector']==ordinal%27,'ADDRESS')
        require(x['neural_reference_fp_sha256']==sha(trained) and
                x['neural_observed_fp_sha256']==sha(fp) and
                x['neural_observed_fp_hex']==fp.hex(),'NEURAL_FINGERPRINT')
        require(x['total_spikes']==sum(fp),'SPIKE_COUNT')
        require(x['fingerprint_match']==matched and x['readback_byte_exact']==byte_correct,'FALSE_RECOGNITION')
        require(x['strict_authorized']==(matched and byte_correct),'SOURCE_TRUST')
        require(x['mcp_request']['method']=='tools/call' and
                x['mcp_request']['params']['name']=='neuron.gate','NEURON_MCP_TOOL')
        require(x['mcp_request']['params']['arguments']['trusted_source_sha256']==source_sha,'MCP_TRUST_ANCHOR')
        require(x['mcp_response']['result']['status']==('ACCEPT' if x['strict_authorized'] else 'HELD'),'FALSE_GATE')
        counts[mode]+=1
        neural[mode]+=matched
        false_green[mode]+=matched and not byte_correct
        strict[mode]+=x['strict_authorized']
    require([counts[x] for x in MODES]==[567]*5,'MODE_FRAME_COUNT')
    require([neural[x] for x in MODES]==NEURAL,'NEURAL_MODEL_DRIFT')
    require([false_green[x] for x in MODES]==FALSE_GREEN,'FALSE_GREEN_MODEL_DRIFT')
    require([strict[x] for x in MODES]==STRICT,'STRICT_GATE_DRIFT')
    require([s['strict_authorized'] for s in summary['scenarios']]==STRICT,'SUMMARY_STRICT')
    require([s['false_green_neural_only'] for s in summary['scenarios']]==FALSE_GREEN,'SUMMARY_FALSE_GREEN')
    # Independent one-bit neural collision challenge: fingerprint unchanged,
    # payload SHA changed, and strict trusted-source gate must deny it.
    source=rows[0][2];target=rows[0][4]
    collision_found=False
    for p in range(min(len(source),32)):
        for bit in range(8):
            mutant=bytearray(source);mutant[p]^=1<<bit
            if independent_spikes(mutant)==target and sha(mutant)!=sha(source):
                collision_found=True;break
        if collision_found:break
    require(collision_found,'INDEPENDENT_COLLISION_NOT_FOUND')
    return chunks

def main():
    if len(sys.argv) not in (5,7):
        raise SystemExit('usage: verify_neural.py bank index photon-HBP python-output node-output [otheros-python otheros-node]')
    rows=reference_rows(sys.argv[1],sys.argv[2])
    parent=Path(sys.argv[3]).read_bytes()
    require(sha(parent)==PHOTON_SHA,'PHOTON_SOURCE_HBP_SHA')
    lines=parent.splitlines()
    require(len(lines)==2835,'PARENT_FRAMES')
    groups=[validate(where,rows,lines) for where in sys.argv[4:]]
    for group in groups[1:]:
        require(all(group[name]==groups[0][name] for name in FILES),'INDEPENDENT_LANGUAGE_OR_OS_DRIFT')
    print(json.dumps({'status':'PASS','source_rows':567,'total_frames':2835,
        'crosschecked_programs':len(groups),'neural_sha256':NEURAL_SHA,
        'false_green_neural_only':FALSE_GREEN,'strict_authorized':STRICT,
        'measured_photons':False},sort_keys=True))
if __name__=='__main__':main()
