#!/usr/bin/env python3
"""Seat2 R6: independently authored synthetic signed-spectrum and order falsifiers."""
import base64, copy, hashlib, itertools, json, math, secrets, sys
from collections import defaultdict
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
BANDS=('red','orange','yellow','green','blue','indigo','violet')
PORTS=(2,5,0,6,1,4,3)
SRC='02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22'
BANK='52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345'
BASE='6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee'
ALIASES='2480163f9bab77fb4e3730719fce8ef162ba97eac6eceee14bc9c4dfb77ec35e'
AUTH='9c64cddd3be7b57eb498f3809f78a346fa3e4ce5bc80869adb867edec8b21c6f'
WIT='eba347587f749f6a0e58e7a6be83081cf1a204e880fe527f82a38063f1da1a0d'
NONCE='SEAT4-R5-REPRODUCIBLE-TEST-NONCE-NOT-UNPREDICTABLE'
DOMAIN_A='ASOLARIA-SEAT4-AUTH-MAP-V1\n'
DOMAIN_W='ASOLARIA-SEAT4-OBS-V1\n'
def sha(data):return hashlib.sha256(data).hexdigest()
def canon(obj):return json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def wire(domain,obj):return (domain+canon(obj)+'\n').encode('utf8')
def key(name):
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(
        ('ASOLARIA-SEAT4-R5-'+name+'-TEST-ONLY-20261015').encode()).digest())
def pub(key):return key.public_key().public_bytes(
    encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw).hex()
def sign(key,domain,msg):
    return {'payload':msg,'signature':base64.b64encode(key.sign(wire(domain,msg))).decode('ascii')}
def verify(public,domain,signed):
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(public)).verify(
            base64.b64decode(signed['signature'],validate=True),wire(domain,signed['payload']))
        return True
    except (InvalidSignature,ValueError,KeyError,TypeError):return False
def mathclass(n):
    r,g,b=n//9,(n//3)%3,n%3
    S=r+g+b;Q=r*r+g*g+b*b-r*g-r*b-g*b
    raw=(S*S,Q,Q);gcd=math.gcd(*raw)
    P=tuple(x//gcd for x in raw) if gcd else 'DARK'
    W=(r+4*g+3*b+4*r*g)%8
    return P,W
def make_map():
    return dict(schema='ASOLARIA-SEAT4-SPECTRUM-MAPPING-V1',source81_sha256=SRC,
        source_bank_sha256=BANK,base_index_sha256=BASE,alias_index_sha256=ALIASES,
        bands=list(BANDS),ports=list(PORTS),nonce=NONCE,epoch=20261015,
        sector_count=27,site_count=81)
def frame(m,sector,site,seq):
    obs=[]
    for band,port in zip(m['bands'],m['ports']):
        row=sha(f'ROUND6-SYNTHETIC-MOCK|{band}|{site}'.encode())
        tag=sha(f"ASOLARIA-SEAT4-OBS-TAG-V1|{m['source_bank_sha256']}|{sector}|{site}|{band}|{port}|{row}|20261015|{m['nonce']}".encode())
        obs.append(dict(band=band,port=port,entry_sha256=row,tag=tag))
    return dict(schema='ASOLARIA-SEAT4-SPECTRUM-OBS-V1',source_bank_sha256=m['source_bank_sha256'],
        mapping_sha256=sha(wire(DOMAIN_A,m)),nonce=m['nonce'],epoch=20261015,
        sequence=seq,sector=sector,coords=[sector//9,(sector//3)%3,sector%3],
        site=site,observations=obs)
def crypto_only(m,f):return verify(AUTH,DOMAIN_A,m) and verify(WIT,DOMAIN_W,f)
def policy(m,f,seen,sector,site,seq,nonce=NONCE):
    if not crypto_only(m,f):return 'BAD_SIGNATURE'
    mp=m['payload'];p=f['payload']
    if tuple(mp[k] for k in ('source81_sha256','source_bank_sha256','base_index_sha256','alias_index_sha256'))!=(SRC,BANK,BASE,ALIASES):
        return 'BAD_SOURCE_ROOT'
    if mp['bands']!=list(BANDS) or mp['ports']!=list(PORTS):return 'BAD_CHANNEL_OWNER'
    if mp['nonce']!=nonce or p['nonce']!=nonce or mp['epoch']!=20261015 or p['epoch']!=20261015:return 'STALE_CONTEXT'
    if (p['sector'],p['site'],p['sequence'])!=(sector,site,seq):return 'BAD_LOCATION'
    if p['coords']!=[sector//9,(sector//3)%3,sector%3]:return 'BAD_ORDER'
    if p['source_bank_sha256']!=BANK or p['mapping_sha256']!=sha(wire(DOMAIN_A,mp)):return 'BAD_BINDING'
    if len(p['observations'])!=7:return 'ERASURE'
    if len({o['port'] for o in p['observations']})!=7:return 'DUPLICATE_PORT'
    for i,(band,port) in enumerate(zip(BANDS,PORTS)):
        row=sha(f'ROUND6-SYNTHETIC-MOCK|{band}|{site}'.encode())
        tag=sha(f'ASOLARIA-SEAT4-OBS-TAG-V1|{BANK}|{sector}|{site}|{band}|{port}|{row}|20261015|{nonce}'.encode())
        if p['observations'][i]!=dict(band=band,port=port,entry_sha256=row,tag=tag):
            return 'BAD_OBSERVATION'
    k=(p['epoch'],p['nonce'],p['sequence'])
    if k in seen or (seen and seq<=max(z[2] for z in seen)):return 'REPLAY'
    seen.add(k)
    return 'PASS_TEST_FIXTURE'
def run():
    ak=key('AUTHORITY');wk=key('WITNESS')
    assert pub(ak)==AUTH and pub(wk)==WIT
    inv={};cl=defaultdict(list)
    for sector in range(27):
        klass,w=mathclass(sector);assert (klass,w) not in inv
        inv[klass,w]=sector;cl[str(klass)].append(sector)
    assert sorted(map(len,cl.values()))==[1,2,3,3,6,6,6] and len(inv)==27
    old=sign(ak,DOMAIN_A,make_map())
    f=sign(wk,DOMAIN_W,frame(old['payload'],0,0,1))
    assert crypto_only(old,f) and policy(old,f,set(),0,0,1)=='PASS_TEST_FIXTURE'
    seen=set();assert policy(old,f,seen,0,0,1)=='PASS_TEST_FIXTURE'
    assert policy(old,f,seen,0,0,1)=='REPLAY'
    assert policy(old,f,set(),0,0,1)=='PASS_TEST_FIXTURE' # reset ledger is NOT freshness
    assert policy(old,f,set(),0,0,1,secrets.token_hex(16))=='STALE_CONTEXT'
    erased=copy.deepcopy(f['payload']);erased['observations'].pop()
    erasure=sign(wk,DOMAIN_W,erased)
    assert crypto_only(old,erasure) and policy(old,erasure,set(),0,0,1)=='ERASURE'
    stale=copy.deepcopy(f['payload']);stale['nonce']='stale'
    assert policy(old,sign(wk,DOMAIN_W,stale),set(),0,0,1)=='STALE_CONTEXT'
    changed=copy.deepcopy(f);changed['payload']['observations'][0]['tag']='0'*64
    assert not crypto_only(old,changed)
    fake=copy.deepcopy(old['payload']);fake['source_bank_sha256']='f'*64
    fake=sign(ak,DOMAIN_A,fake)
    fake_frame=sign(wk,DOMAIN_W,frame(fake['payload'],0,0,1))
    assert crypto_only(fake,fake_frame) and policy(fake,fake_frame,set(),0,0,1)=='BAD_SOURCE_ROOT'
    port_cases=bare_accept=bound_reject=0
    for p in itertools.permutations(PORTS):
        if p==PORTS:continue
        m=copy.deepcopy(old['payload']);m['ports']=list(p)
        signed_map=sign(ak,DOMAIN_A,m)
        signed_frame=sign(wk,DOMAIN_W,frame(m,0,0,1))
        port_cases+=1
        bare_accept+=crypto_only(signed_map,signed_frame)
        bound_reject+=(policy(signed_map,signed_frame,set(),0,0,1)=='BAD_CHANNEL_OWNER')
    assert (port_cases,bare_accept,bound_reject)==(5039,5039,5039)
    seen=set()
    for sector in range(27):
        for site in range(81):
            seq=sector*81+site+1
            packet=sign(wk,DOMAIN_W,frame(old['payload'],sector,site,seq))
            assert policy(old,packet,seen,sector,site,seq)=='PASS_TEST_FIXTURE'
    result=dict(schema='ASOLARIA-SEAT2-R6-EXTERNAL-ANCHOR-CROSS-EXAM-V1',
        status='DIGITAL_TESTS_PASS_ORIGIN_PHYSICAL_HELD',
        original_pr88_signer_blob='36e8f399b851a5c8d16596ab7a21397e1bef35d6',
        original_pr90_head='4db24bc72e6852bc2363501c59b7c0240f5c357d',
        cases=dict(ordered_identities=27,normalized_classes=7,
            public_fixture_signing_keys_recovered=2,
            signed_mock_frames=2187,logical_mock_channels=15309,
            coherent_signed_port_forgeries_accepted_by_bare_crypto=bare_accept,
            same_forgeries_rejected_by_fixed_external_binding=bound_reject,
            replay_rejected_when_ledger_persists=True,
            whole_session_replay_possible_when_ledger_resets=True,
            local_fresh_challenge_rejected_old_frame=True,
            re_signed_erasure_rejected=True,
            coherent_source_spoof_rejected_against_fixed_external_root=True),
        claimed_scope='NEW_SYNTHETIC_MOCK_ROWS_NOT_REPLAY_OF_PR88_ARCHIVE',
        externally_authenticated_source=False,physical_photon_storage_measured=False,
        biological_neural_memory_measured=False)
    return result
if __name__=='__main__':
    out=Path(sys.argv[1] if len(sys.argv)>1 else '.')
    out.mkdir(parents=True,exist_ok=True)
    b=(canon(run())+'\n').encode()
    (out/'results.json').write_bytes(b)
    (out/'SHA256SUMS').write_bytes((sha(b)+'  results.json\n').encode())
    print(f'SEAT2_R6_PASS sha256={sha(b)}')
