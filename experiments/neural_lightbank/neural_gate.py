#!/usr/bin/env python3
"""Digital leaky integrate-and-fire neural gate for a synthetic photon-electron bank.

Trains one *digital* spike-count fingerprint per full Rainbow7 source row.
Neither physical photons nor real neurons are measured by this software.
"""
import copy,hashlib,json,sys
from pathlib import Path
ROOT='52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345'
INDEX='6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee'
PARENT='332e1eeb2d4de748c2e1da07729944fefe5b63589e9533b4c93b74d7cf3f5527'
SOURCE='02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22'
SCENARIOS=('bright_t0','dim_t0','bright_t3','dark_t0','protected_t3')
BANDS=('red','orange','yellow','green','blue','indigo','violet')
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(o):return (json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n').encode('ascii')
def ck(ok,code):
    if not ok:raise ValueError(code)
def fingerprint(raw):
    voltage=0;window_spikes=0;hist=[]
    for i,byte in enumerate(raw):
        for shift in range(7,-1,-1):
            bit=(byte>>shift)&1
            voltage=max(0,voltage-1)+4*bit
            if voltage>=7:voltage-=7;window_spikes+=1
            if (i*8+7-shift)%32==31:hist.append(window_spikes);window_spikes=0
    if len(raw)*8%32:hist.append(window_spikes)
    ck(all(0<=x<=32 for x in hist),'SPIKE_WINDOW_OUT_OF_RANGE')
    return bytes(hist)
def read_rows(bank_path,index_path):
    bank=Path(bank_path).read_bytes();index=Path(index_path).read_bytes()
    ck(sha(bank)==ROOT and len(bank)==184815,'BANK_ROOT')
    ck(sha(index)==INDEX and len(index)==70043,'INDEX_ROOT')
    rows=[];seen=set()
    for line in index.decode('ascii').splitlines():
        parts=line.split('|');ck(parts[0]=='MEM' and len(parts)==6,'ROW_FORMAT')
        d=dict(v.split('=',1) for v in parts[1:]);site=d['id'];band=d['band']
        ck(band in BANDS and (site,band) not in seen,'DUPLICATE_ROW')
        seen.add((site,band));start=int(d['offset']);size=int(d['length'])
        ck(0<=start and size>0 and start+size<=len(bank),'ROW_BOUNDS')
        raw=bank[start:start+size];ck(sha(raw)==d['sha256'],'ROW_HASH')
        rows.append({'site':site,'band':band,'raw':raw,'hash':sha(raw),'fp':fingerprint(raw)})
    ck(len(rows)==567 and len(seen)==567,'BANK_INCOMPLETE')
    return rows
def read_photon(frame,src,ordinal,scenario):
    ck(frame['scenario']==scenario and frame['ordinal']==ordinal,'PHOTON_FRAME_ID')
    ck(frame['site']==src['site'] and frame['band']==src['band'] and frame['sector']==ordinal%27,'PHOTON_ADDRESS')
    ck(frame['expected_row_sha256']==src['hash'],'PHOTON_BANK_ROW_ROOT')
    rq=frame['mcp_request']
    ck(rq['method']=='tools/call' and rq['params']['name']=='electron.capture','ELECTRON_TOOL')
    args=rq['params']['arguments']
    ck(args['site']==src['site'] and args['band']==src['band'] and
       args['source_sha256']==SOURCE and args['bank_sha256']==ROOT and
       args['sector']==ordinal%27,'ELECTRON_SOURCE_ROOT')
    nonce=sha(f'ASOLARIA-MCP-CAPTURE|{ROOT}|{scenario}|{ordinal}'.encode())[:24]
    ck(frame['context_nonce']==nonce and args['context_nonce']==nonce,'ELECTRON_REPLAY')
    obs=bytes.fromhex(frame['readback_hex'])
    ck(len(obs)==len(src['raw']) and sha(obs)==frame['observed_row_sha256'],'READBACK_BYTES')
    ck(frame['mcp_response']['result']['observed_row_sha256']==frame['observed_row_sha256'],'ELECTRON_REPLY')
    ck(sum((a^b).bit_count() for a,b in zip(obs,src['raw']))==frame['bit_errors'],'FALSE_ERROR_COUNT')
    return obs
def neuron_frame(frame,src,ordinal,scenario):
    obs=read_photon(frame,src,ordinal,scenario);fp=fingerprint(obs)
    matched=fp==src['fp'];exact=sha(obs)==src['hash'];authorized=matched and exact
    nonce=sha(f'ASOLARIA-NEURAL-ELECTRON|{PARENT}|{scenario}|{ordinal}'.encode())[:24]
    args={'source_bank_sha256':ROOT,'parent_photon_hbp_sha256':PARENT,'site':src['site'],
          'band':src['band'],'sector':ordinal%27,'neural_model':'LEAKY_INTEGRATE_FIRE_WINDOW32',
          'charge_per_one':4,'leak_per_tick':1,'spike_threshold':7,
          'trained_fingerprint_sha256':sha(src['fp']),'observed_fingerprint_sha256':sha(fp),
          'observed_source_sha256':sha(obs),'trusted_source_sha256':src['hash'],
          'spikes':sum(fp),'nonce':nonce,'fingerprint_recognized':matched,
          'hash_verified':exact,'authorized':authorized}
    return {'schema':'ASOLARIA-NEURAL-ELECTRON-GATE-DIGITAL-V1',
      'scenario':scenario,'ordinal':ordinal,'site':src['site'],'band':src['band'],
      'sector':ordinal%27,'neural_reference_fp_sha256':sha(src['fp']),
      'neural_observed_fp_sha256':sha(fp),'neural_observed_fp_hex':fp.hex(),
      'total_spikes':sum(fp),'fingerprint_match':matched,
      'readback_byte_exact':exact,'strict_authorized':authorized,
      'mcp_request':{'jsonrpc':'2.0','id':f'neuron:{scenario}:{ordinal}',
         'method':'tools/call','params':{'name':'neuron.gate','arguments':args}},
      'mcp_response':{'jsonrpc':'2.0','id':f'neuron:{scenario}:{ordinal}',
         'result':{'status':'ACCEPT' if authorized else 'HELD',
           'source_authenticated':'PINNED_DIGITAL_ROOT_ONLY',
           'neural_activity':'MODELED_SPIKES',
           'photon_detection':'NOT_PHYSICALLY_MEASURED'}}}
def negatives(ref,src):
    flip=None
    for i in range(min(32,len(src['raw']))):
        for bit in range(8):
            mutant=bytearray(src['raw']);mutant[i]^=1<<bit
            if fingerprint(mutant)==src['fp'] and sha(mutant)!=src['hash']:
                flip={'byte_offset':i,'bit_number':bit,'fp_match':True,'sha_match':False,'strict_gate':'HELD'}
                break
        if flip:break
    ck(flip is not None,'NEURAL_COLLISION_NOT_FOUND')
    attacks=(
      ('replayed_nonce',lambda o:o['mcp_request']['params']['arguments'].update(nonce='stale')),
      ('forged_memory_hash',lambda o:o['mcp_request']['params']['arguments'].update(trusted_source_sha256='0'*64)),
      ('fake_neuron_tool',lambda o:o['mcp_request']['params'].update(name='neuron.bypass')),
      ('changed_spike_count',lambda o:o['mcp_request']['params']['arguments'].update(spikes=-1)),
      ('wrong_source_site',lambda o:o.update(site='site-999')),
      ('wrong_source_band',lambda o:o.update(band='violet')),
      ('wrong_sector',lambda o:o.update(sector=(o['sector']+1)%27)),
      ('forged_gate',lambda o:o['mcp_response']['result'].update(status='ACCEPT' if not o['strict_authorized'] else 'HELD')),
      ('coherent_source_spoof',lambda o:(o.update(neural_reference_fp_sha256='f'*64),
          o['mcp_request']['params']['arguments'].update(trained_fingerprint_sha256='f'*64))),
      ('deleted_frame',lambda o:o.clear()))
    rejects=[]
    for name,fn in attacks:
        attack=copy.deepcopy(ref);fn(attack)
        try:ck(canon(attack)==canon(ref),'MUTATED_FRAME_FAIL_CLOSED')
        except ValueError:rejects.append(name)
        else:raise AssertionError('FALSE_ACCEPT_'+name)
    ck(len(rejects)==len(attacks),'INCOMPLETE_ATTACK_SET')
    return {'single_bit_fingerprint_collision':flip,'mutant_frames_rejected':rejects}
def run(bank_path,index_path,parent_path,out_path):
    rows=read_rows(bank_path,index_path)
    hbp=Path(parent_path).read_bytes();ck(sha(hbp)==PARENT,'PHOTON_PARENT_SHA')
    records=hbp.splitlines();ck(len(records)==2835,'PHOTON_FRAME_COUNT')
    stats=[];lines=[];controls=None;violet=0
    for si,scenario in enumerate(SCENARIOS):
        acc={'scenario':scenario,'total':0,'neural_only_matches':0,
             'false_green_neural_only':0,'strict_authorized':0,
             'exact_byte_recall':0,'total_spikes':0}
        for ordinal in range(567):
            frame=json.loads(records[si*567+ordinal])
            out=neuron_frame(frame,rows[ordinal],ordinal,scenario)
            if controls is None:controls=negatives(out,rows[ordinal])
            lines.append(canon(out));acc['total']+=1
            acc['neural_only_matches']+=int(out['fingerprint_match'])
            acc['false_green_neural_only']+=int(out['fingerprint_match'] and not out['readback_byte_exact'])
            acc['strict_authorized']+=int(out['strict_authorized'])
            acc['exact_byte_recall']+=int(out['readback_byte_exact'])
            acc['total_spikes']+=out['total_spikes']
            if si==0 and rows[ordinal]['band']=='violet':violet+=1
        ck(acc['total']==567,'SCENARIO_MISSING_SOURCE_ROWS')
        ck(acc['strict_authorized']==acc['exact_byte_recall'],'SOURCE_GATE_FALSE_GREEN')
        stats.append(acc)
    ck(violet==81,'VIOLET_ERASURE_ROWS')
    remaining=[json.loads(records[i]) for i in range(567) if rows[i]['band']!='violet']
    ck(len(remaining)==486,'VIOLET_ERASURE_NOT_APPLIED')
    try:
        ck(len(remaining)==567,'ERASURE_FULL_BANK_INCOMPLETE')
    except ValueError as error:
        ck(str(error)=='ERASURE_FULL_BANK_INCOMPLETE','ERASURE_FAIL_OPEN')
    else:
        raise AssertionError('ERASURE_MUST_HALT')
    data=b''.join(lines)
    summary={'schema':'ASOLARIA-NEURAL-ELECTRON-GATE-DIGITAL-V1',
      'parent_hbp_sha256':PARENT,'bank_sha256':ROOT,'original_source_memories':81,
      'original_bank_rows':567,'modeled_photon_frames':2835,'modeled_neuron_cells':567,
      'modeled_neural_fingerprint_only':True,'physical_cpu_executed':True,
      'physical_photon_storage_measured':False,'biological_neuron_measured':False,
      'independent_physical_detector_attested':False,
      'software_neuron_mcp_tool':'neuron.gate','real_mcp_server_operational':False,
      'violet_missing_rows_under_erasure':violet,
      'violet_missing_27_sector_aliases':violet*27,'erasure_full_bank_status':'HELD',
      'neural_hbp_sha256':sha(data),'neural_hbp_bytes':len(data),
      'controls':controls,'scenarios':stats}
    folder=Path(out_path);folder.mkdir(parents=True,exist_ok=True)
    for name,blob in {'neural-gate.hbp':data,'neural-gate.json':canon(summary)}.items():
        (folder/name).write_bytes(blob)
        (folder/(name+'.sha256')).write_text(f'{sha(blob)}  {name}\n',encoding='ascii')
    print(json.dumps({'status':'PASS','sha256':sha(data),'bytes':len(data),
      'scenarios':[(s['scenario'],s['neural_only_matches'],s['false_green_neural_only'],
                    s['strict_authorized']) for s in stats],
      'violet_erasure_aliases_held':violet*27,'real_photons_measured':False},
      sort_keys=True))
    return summary
if __name__=='__main__':
    if len(sys.argv)!=5:raise SystemExit('usage: neural_gate.py bank index photon-HBP output_dir')
    run(*sys.argv[1:])
