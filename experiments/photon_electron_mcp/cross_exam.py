#!/usr/bin/env python3
"""Independent full-byte/mathematical cross-exam of the photon-electron memory model.

Tests a *classical software photodetector model* executed on real computers.
Does not claim an optical storage medium or independently measured photoelectrons.
"""
import hashlib
import json
import math
from collections import Counter
from math import comb
from pathlib import Path
import sys

BANK_ROOT = '52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345'
INDEX_ROOT = '6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee'
BANDS = ('red','orange','yellow','green','blue','indigo','violet')
WAVELENGTHS = (650,610,580,530,470,440,405)
SCENARIOS = ('bright_t0','dim_t0','bright_t3','dark_t0','protected_t3')
EXPECTED = (0,239145,57,824,0)


def sha(b): return hashlib.sha256(b).hexdigest()


def check(c,reason):
    if not c: raise AssertionError(reason)


def load_index(bank,index):
    check(sha(bank)==BANK_ROOT and len(bank)==184815,'FROZEN_BANK_DIFFERENCE')
    check(sha(index)==INDEX_ROOT and len(index)==70043,'FROZEN_BASE_INDEX_DIFFERENCE')
    rows=[]
    for n,line in enumerate(index.decode('ascii').splitlines()):
        fields=line.split('|')
        check(fields[0]=='MEM' and len(fields)==6,'BAD_ROW')
        d=dict(part.split('=',1) for part in fields[1:])
        check(set(d)=={'band','id','offset','length','sha256'},'BAD_ROW_FIELDS')
        offset,length=int(d['offset']),int(d['length'])
        check(0<=offset<len(bank) and length>0 and offset+length<=len(bank),'OUT_OF_RANGE')
        raw=bank[offset:offset+length]
        check(sha(raw)==d['sha256'],'ROW_SHA_MISMATCH')
        check(d['band'] in BANDS and d['id'].startswith('site-'),'ROW_ADDRESS')
        rows.append((d['band'],d['id'],raw,d['sha256']))
    check(len(rows)==567,'BANK_INCOMPLETE')
    return rows


def majority_error(p,count):
    return sum(comb(count,k)*p**k*(1-p)**(count-k)
               for k in range(count//2+1,count+1))


def examine(bank_file,index_file,results_file,hbp_file):
    rows=load_index(Path(bank_file).read_bytes(),Path(index_file).read_bytes())
    bank=Path(bank_file).read_bytes()
    n1=sum(b.bit_count() for b in bank)
    n0=len(bank)*8-n1
    check((n1,n0)==(662443,816077),'BIT_HISTOGRAM_DRIFT')
    result=json.loads(Path(results_file).read_bytes())
    hbp=Path(hbp_file).read_bytes()
    check(sha(hbp)==result['photon_hbp_sha256'],'OUTPUT_HBP_SHA_MISMATCH')
    check(len(hbp)==result['photon_hbp_bytes'],'OUTPUT_HBP_SIZE_MISMATCH')
    scenarios=result['scenarios']
    check(len(scenarios)==5,'SCENARIO_COUNT')
    check(tuple(x['scenario'] for x in scenarios)==SCENARIOS,'SCENARIO_ORDER')
    check(len(hbp.splitlines())==2835,'EXACT_FRAME_COUNT')
    by_scenario=Counter();actual_err=Counter();exact=Counter();bits_by_scenario=Counter()
    for line in hbp.splitlines():
        x=json.loads(line);sc=x['scenario']
        check(sc in SCENARIOS,'UNKNOWN_SCENARIO')
        ordinal=x['ordinal']
        check(type(ordinal)==int and 0<=ordinal<567,'BAD_ORDINAL')
        band,site,raw,expected_sha=rows[ordinal]
        check(x['band']==band and x['site']==site and x['sector']==ordinal%27,'ADDRESS_MISMATCH')
        check(x['wavelength_nm_assumed']==WAVELENGTHS[BANDS.index(band)],'WAVELENGTH_MISMATCH')
        check(x['expected_row_sha256']==expected_sha,'UNTRUSTED_EXPECTED_SHA')
        out=bytes.fromhex(x['readback_hex'])
        check(len(out)==len(raw) and sha(out)==x['observed_row_sha256'],'OBSERVED_READBACK_DRIFT')
        err=sum((a^b).bit_count() for a,b in zip(raw,out))
        check(err==x['bit_errors'],'FALSE_REPORTED_ERRORS')
        check(x['photoelectrons_modeled']<=x['emitted_photons_modeled'],'EXTRA_PHOTOELECTRONS')
        check(x['mcp_request']['params']['name']=='electron.capture','WRONG_ELECTRON_TOOL')
        check(x['mcp_request']['method']=='tools/call','WRONG_METHOD')
        check(x['mcp_response']['result']['observed_row_sha256']==x['observed_row_sha256'],'REPLY_TAMPER')
        nonce=sha(f'ASOLARIA-MCP-CAPTURE|{BANK_ROOT}|{sc}|{ordinal}'.encode())[:24]
        check(x['context_nonce']==nonce and
              x['mcp_request']['params']['arguments']['context_nonce']==nonce,'REPLAY_NONCE')
        by_scenario[sc]+=1
        actual_err[sc]+=err
        exact[sc]+=int(err==0)
        bits_by_scenario[sc]+=len(raw)*8
    audit=[]
    for sc,s in zip(SCENARIOS,scenarios):
        photons=s['photons_per_one']
        t=s['hold_ticks']
        copies=s['replicas']
        p=(4/5)**(t+2)
        d=1/1000 if s['dark_per_1000'] else 0
        q1=(1-p)**photons*(1-d)
        q0=d
        expectation=n1*majority_error(q1,copies)+n0*majority_error(q0,copies)
        variance=n1*majority_error(q1,copies)*(1-majority_error(q1,copies))+n0*majority_error(q0,copies)*(1-majority_error(q0,copies))
        tol=6*math.sqrt(max(variance,1))+2
        observed=actual_err[sc]
        check(observed==s['bit_errors'] and exact[sc]==s['exact_rows'],'SUMMARY_DISAGREES_WITH_BYTES')
        check(by_scenario[sc]==567 and bits_by_scenario[sc]==1478520,'INCOMPLETE_SCENARIO')
        check(abs(observed-expectation)<tol,'EXCEEDS_6_SIGMA_MODEL_EXPECTATION')
        audit.append({'scenario':sc,'assumed_photoelectron_probability':round(p,8),
                      'analytic_expected_bit_errors':round(expectation,6),
                      'observed_deterministic_bit_errors':observed,
                      'exact_full_bank_rows':exact[sc],
                      'analytic_standard_deviation':round(math.sqrt(variance),6),
                      'difference_z':round((observed-expectation)/math.sqrt(max(variance,1)),4)})
    check(tuple(actual_err[x] for x in SCENARIOS)==EXPECTED,'FROZEN_SOFTWARE_FIXTURE_DRIFT')
    check(result['physical_computation_executed'] and not result['physical_photon_detection_measured']
          and not result['optical_storage_measured'],'BAD_PHYSICAL_SCOPE')
    print(json.dumps({'status':'PASS',
        'method':'independent full-bank bitwise analysis + classical binomial expectation',
        'distinct_source_ones':n1,'distinct_source_zeros':n0,
        'frames':sum(by_scenario.values()),
        'total_readback_bytes_across_scenarios':len(bank)*5,
        'models':audit},sort_keys=True))


if __name__=='__main__':
    if len(sys.argv)!=5:
        raise SystemExit('usage: cross_exam.py bank.jsonl index.hbi results.json photon-electron.hbp')
    examine(*sys.argv[1:])
