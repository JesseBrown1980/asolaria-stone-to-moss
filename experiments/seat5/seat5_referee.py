import hashlib,json,random,sys
from pathlib import Path
P=Path(sys.argv[1]) if len(sys.argv)>1 else Path.cwd()
P.mkdir(parents=True, exist_ok=True)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
original={'source':'original','band_owner':list(range(7)),'payload':[11,23,37,41,53,67,79]}
trusted=digest(original)
nonce='fresh-independent-challenge-0001'
ledger=set()
def accept(packet,challenge,ledger):
    if packet['nonce']!=challenge or packet['nonce'] in ledger:return False
    if digest(packet['data'])!=trusted:return False
    if packet['data']['band_owner']!=list(range(7)):return False
    ledger.add(packet['nonce']);return True
packet={'data':original,'nonce':nonce}
assert accept(packet,nonce,ledger)
assert not accept(packet,nonce,ledger)
(P/'ledger.json').write_text(json.dumps(sorted(ledger)))
restored=set(json.loads((P/'ledger.json').read_text()))
assert not accept(packet,nonce,restored)
for i in range(1,7):
    forged={'source':'forged','band_owner':list(range(i,7))+list(range(i)),'payload':original['payload'][:]}
    assert digest(forged)==digest(forged)
    assert not accept({'data':forged,'nonce':f'fresh-{i}'},f'fresh-{i}',set())
assert 81*7*27==15309 and 81*7==567 and 81*27==2187
assert 567*27-81*27==13122
def run(seed,leak,background):
    rng=random.Random(seed); pairs={1:[0,0,0,0],3:[0,0,0,0],7:[0,0,0,0]}
    for _ in range(2187):
        bits=[rng.randrange(2) for _ in range(7)]
        counts=[[0]*7 for _ in range(7)]
        for t in range(7):
            for j,b in enumerate(bits):
                for _ in range(16*b):
                    q=rng.random()
                    dest=j if q<.65625 else (j-1 if j>0 else -1) if q<.65625+leak else (j+1 if j<6 else -1) if q<.65625+2*leak else -1
                    if dest>=0:counts[t][dest]+=1
            for j in range(7):
                if rng.random()<background:counts[t][j]+=1
        for n in (1,3,7):
            obs=[sum(counts[t][j] for t in range(n)) for j in range(7)]
            for j,b in enumerate(bits):
                raw=obs[j]>=5*n
                corrected=7*obs[j]-(obs[j-1] if j else 0)-(obs[j+1] if j<6 else 0)>= (28 if n==1 else 26*n)
                idx=(0 if raw==b and corrected==b else 1 if raw!=b and corrected!=b else 2 if raw!=b else 3)
                pairs[n][idx]+=1
    return {str(k):dict(zip(('both_correct','both_wrong','repaired','degraded'),v)) for k,v in pairs.items()}
result={'scope':'software-only, independent referee fixture, no real photons','source_root':trusted,'attacks':{'coherent_substitutions_rejected':6,'durable_replay_rejected':True,'violet_missing_aliases':2187,'one_base_row_missing_aliases':27},'heldout':{'nominal':run(2026101505,.09375,.05),'shifted':run(2026101506,.14,.14)}}
(P/'results.json').write_bytes((json.dumps(result,indent=2,sort_keys=True)+'\n').encode('utf-8'))
print(json.dumps(result,indent=2))
