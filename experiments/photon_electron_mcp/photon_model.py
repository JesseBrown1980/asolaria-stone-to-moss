#!/usr/bin/env python3
"""Preregistered classical photon-count / photoelectron detector model on physical CPU.

NOT a photon source, photonic memory medium, MCP server, or optical measurement.
The electron.capture JSON-RPC requests are a software model of electronic control.
"""
import copy
import hashlib
import json
import math
import sys
from pathlib import Path

SOURCE_SHA = '02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22'
BANK_SHA = '52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345'
INDEX_SHA = '6b105769bf236c156cafa4dd4e3647fe45778c191a7e32ac7df63e84d287d0ee'
BANDS = ('red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet')
WAVELENGTHS = (650, 610, 580, 530, 470, 440, 405)
SCHEMA = 'ASOLARIA-PHOTON-ELECTRON-MCP-CLASSICAL-V1'
SCENARIOS = (
    ('bright_t0', 24, 0, 0, 1),
    ('dim_t0', 1, 0, 0, 1),
    ('bright_t3', 24, 3, 0, 1),
    ('dark_t0', 24, 0, 1, 1),
    ('protected_t3', 24, 3, 1, 5),
)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(obj):
    return (json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode('ascii')


def check(condition, reason):
    if not condition:
        raise ValueError(reason)


class XorShift32:
    def __init__(self, scenario, ordinal):
        seed = hashlib.sha256(f'ASOLARIA-PHOTON-ELECTRON-V1|{BANK_SHA}|{scenario}|{ordinal}'.encode()).digest()
        self.x = int.from_bytes(seed[:4], 'little') or 0x6D2B79F5

    def take(self):
        x = self.x
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        self.x = x & 0xFFFFFFFF
        return self.x


def cdf_thresholds(n, ticks):
    num, den = 16 * 4**ticks, 25 * 5**ticks
    total = den**n
    s = 0
    thresholds = []
    for k in range(n + 1):
        s += math.comb(n, k) * num**k * (den - num)**(n - k)
        thresholds.append(s * (1 << 32) // total)
    check(thresholds[-1] == (1 << 32), 'BINOMIAL_CDF_MASS')
    return thresholds


def sampled_electrons(rng, table):
    value = rng.take()
    for k, upper in enumerate(table):
        if value < upper:
            return k
    raise ValueError('BAD_DETECTOR_CDF')


def energy_yj_per_photon(nm):
    # h=6.62607015e-34 J*s, c=299792458 m/s, lambda=nm*1e-9 m.
    # exact integer nearest-yoctojoule photon-energy approximation.
    numerator = 662607015 * 299792458
    denominator = 10**9 * nm
    return (numerator + denominator // 2) // denominator


def load_source(source_path, bank_path, index_path):
    src, bank, idx = (Path(p).read_bytes() for p in (source_path, bank_path, index_path))
    check(sha(src) == SOURCE_SHA, 'SOURCE_ROOT_MISMATCH')
    check(sha(bank) == BANK_SHA and len(bank) == 184815, 'BANK_ROOT_MISMATCH')
    check(sha(idx) == INDEX_SHA and len(idx) == 70043, 'INDEX_ROOT_MISMATCH')
    source = json.loads(src)
    check(source['schema'] == 'ASOLARIA-SEAT1-81-RGB-LIGHTBANK-V1' and len(source['records']) == 81,
          'ORIGINAL_81_INVALID')
    lines = idx.decode('ascii').splitlines()
    check(len(lines) == 567 and idx.endswith(b'\n'), 'BANK_ROWS_INVALID')
    rows = []
    seen = set()
    for n, line in enumerate(lines):
        parts = line.split('|')
        check(len(parts) == 6 and parts[0] == 'MEM', 'ROW_FORMAT')
        kv = dict(field.split('=', 1) for field in parts[1:])
        check(set(kv) == {'band', 'id', 'offset', 'length', 'sha256'}, 'INDEX_FIELDS')
        band, site = kv['band'], kv['id']
        check(band in BANDS and site in (f'site-{x:03d}' for x in range(81)), 'BAND_SITE_INVALID')
        check((band, site) not in seen, 'DUPLICATE_BANK_ROW')
        seen.add((band, site))
        offset, size = int(kv['offset']), int(kv['length'])
        check(size > 0 and offset >= 0 and offset + size <= len(bank), 'INDEX_BOUNDS')
        raw = bank[offset:offset + size]
        check(sha(raw) == kv['sha256'], 'ROW_HASH_INVALID')
        record = json.loads(raw)
        check(record['schema'] == 'ASOLARIA-RAINBOW7-BANK-ENTRY-V1' and record['id'] == site
              and record['band'] == band and record['address'] == f'rainbow7/{band}/{site}'
              and record['record'] == source['records'][int(site[-3:])], 'RECORD_ANCESTRY')
        rows.append({'ordinal': n, 'band': band, 'site': site, 'raw': raw, 'sha': kv['sha256'],
                     'sector': n % 27, 'wavelength': WAVELENGTHS[BANDS.index(band)]})
    check(len(seen) == 567 and len({r['site'] for r in rows}) == 81, 'INCOMPLETE_BANK')
    return rows


def frame(row, scenario):
    name, pulse, ticks, dark_per_1000, copies = scenario
    rng = XorShift32(name, row['ordinal'])
    cdf = cdf_thresholds(pulse, ticks)
    emitted = photoelectrons = dark_electrons = errors = 0
    recovered = bytearray()
    for byte in row['raw']:
        rebuilt = 0
        for shift in range(7, -1, -1):
            bit = (byte >> shift) & 1
            votes = 0
            for _ in range(copies):
                if bit:
                    emitted += pulse
                    photo = sampled_electrons(rng, cdf)
                    photoelectrons += photo
                else:
                    photo = 0
                dark = 1 if dark_per_1000 and rng.take() < ((1 << 32) // 1000) else 0
                dark_electrons += dark
                votes += bool(photo + dark)
            observed = int(votes > copies // 2)
            errors += observed != bit
            rebuilt = (rebuilt << 1) | observed
        recovered.append(rebuilt)
    check(photoelectrons <= emitted, 'ELECTRON_PHOTON_CONSERVATION')
    check(dark_electrons <= len(row['raw']) * 8 * copies, 'DARK_ELECTRON_BOUND')
    observed_sha = sha(recovered)
    nonce = sha(f'ASOLARIA-MCP-CAPTURE|{BANK_SHA}|{name}|{row["ordinal"]}'.encode())[:24]
    msg_id = f'{name}:{row["ordinal"]}'
    request = {'jsonrpc': '2.0', 'id': msg_id, 'method': 'tools/call', 'params': {
        'name': 'electron.capture', 'arguments': {
            'source_sha256': SOURCE_SHA, 'bank_sha256': BANK_SHA,
            'site': row['site'], 'band': row['band'], 'sector': row['sector'],
            'wavelength_nm_assumed': row['wavelength'], 'held_ticks_assumed': ticks,
            'context_nonce': nonce, 'expected_row_sha256': row['sha'],
            'observed_row_sha256': observed_sha,
            'emitted_photons_modeled': emitted, 'photoelectrons_modeled': photoelectrons,
            'dark_electrons_modeled': dark_electrons}}}
    response = {'jsonrpc': '2.0', 'id': msg_id, 'result': {
        'status': 'EXACT_READBACK' if errors == 0 else 'BIT_ERRORS',
        'electron_engine': 'SIMULATED', 'photoelectrons_modeled': photoelectrons,
        'observed_row_sha256': observed_sha}}
    return {'schema': SCHEMA, 'scenario': name, 'ordinal': row['ordinal'],
            'site': row['site'], 'band': row['band'], 'sector': row['sector'],
            'wavelength_nm_assumed': row['wavelength'], 'expected_row_sha256': row['sha'],
            'observed_row_sha256': observed_sha, 'readback_hex': recovered.hex(),
            'bit_errors': errors, 'emitted_photons_modeled': emitted,
            'photoelectrons_modeled': photoelectrons, 'dark_electrons_modeled': dark_electrons,
            'emitted_energy_yJ_assumed': emitted * energy_yj_per_photon(row['wavelength']),
            'context_nonce': nonce, 'mcp_request': request, 'mcp_response': response}


def require_frame(candidate, reference):
    # The reference comes from independently pinned source material; matching a
    # self-attached digest without the reference is NOT sufficient authentication.
    check(canon(candidate) == canon(reference), 'INDEPENDENT_TRUTH_MISMATCH')
    arg = candidate['mcp_request']['params']['arguments']
    check(candidate['mcp_request']['method'] == 'tools/call'
          and candidate['mcp_request']['params']['name'] == 'electron.capture'
          and arg['source_sha256'] == SOURCE_SHA and arg['bank_sha256'] == BANK_SHA,
          'MCP_AUTHORITY_OR_TOOL')
    check(candidate['mcp_response']['id'] == candidate['mcp_request']['id'] and
          candidate['mcp_response']['result']['photoelectrons_modeled'] == candidate['photoelectrons_modeled'],
          'MCP_RESPONSE_BINDING')
    check(sha(bytes.fromhex(candidate['readback_hex'])) == candidate['observed_row_sha256'],
          'READBACK_DIGEST')


def negative_controls(frames):
    original = frames[0]
    negatives = (
        ('changed_band', lambda o: o.update(band='violet')),
        ('swapped_wavelength', lambda o: o.update(wavelength_nm_assumed=405)),
        ('reassigned_sector', lambda o: o.update(sector=(o['sector'] + 1) % 27)),
        ('forged_source_root', lambda o: o['mcp_request']['params']['arguments'].update(source_sha256='0'*64)),
        ('changed_row_hash', lambda o: o.update(expected_row_sha256='a'*64)),
        ('counterfeit_electron', lambda o: o.update(photoelectrons_modeled=o['emitted_photons_modeled']+1)),
        ('replay_context_nonce', lambda o: o.update(context_nonce='stale-nonce')),
        ('wrong_tool_name', lambda o: o['mcp_request']['params'].update(name='photon.fake')),
        ('modified_readback', lambda o: o.update(readback_hex='00'+o['readback_hex'][2:])),
        ('response_mismatch', lambda o: o['mcp_response']['result'].update(photoelectrons_modeled=-1)),
        ('missing_frame', lambda o: o.clear()),
        ('coherent_local_hash_spoof', lambda o: (o.update(observed_row_sha256='f'*64),
                                                o['mcp_request']['params']['arguments'].update(observed_row_sha256='f'*64),
                                                o['mcp_response']['result'].update(observed_row_sha256='f'*64))),
    )
    rejected = []
    for name, modify in negatives:
        fake = copy.deepcopy(original)
        modify(fake)
        try:
            require_frame(fake, original)
        except (ValueError, KeyError, TypeError) as exc:
            rejected.append(name + ':' + str(exc))
        else:
            raise AssertionError('ATTACK_ACCEPTED:' + name)
    check(len(rejected) == len(negatives), 'NEGATIVE_TEST_COVERAGE')
    return rejected


def run(source_path, bank_path, index_path, dest_path):
    rows = load_source(source_path, bank_path, index_path)
    dest = Path(dest_path)
    dest.mkdir(parents=True, exist_ok=True)
    lines = []
    cases = []
    negatives = None
    for scenario in SCENARIOS:
        stats = {'scenario': scenario[0], 'photons_per_one': scenario[1], 'hold_ticks': scenario[2],
                 'dark_per_1000': scenario[3], 'replicas': scenario[4], 'rows': 0,
                 'source_bytes': 0, 'bit_windows': 0, 'bit_errors': 0, 'exact_rows': 0,
                 'emitted_photons_modeled': 0, 'photoelectrons_modeled': 0,
                 'dark_electrons_modeled': 0, 'emitted_energy_yJ_assumed': 0}
        for row in rows:
            data = frame(row, scenario)
            if negatives is None:
                negatives = negative_controls([data])
            require_frame(data, data)
            lines.append(canon(data))
            stats['rows'] += 1
            stats['source_bytes'] += len(row['raw'])
            stats['bit_windows'] += len(row['raw']) * 8 * scenario[4]
            stats['bit_errors'] += data['bit_errors']
            stats['exact_rows'] += data['bit_errors'] == 0
            for attr in ('emitted_photons_modeled', 'photoelectrons_modeled',
                         'dark_electrons_modeled', 'emitted_energy_yJ_assumed'):
                stats[attr] += data[attr]
        check(stats['rows'] == 567 and stats['source_bytes'] == 184815, 'INCOMPLETE_FULL_BANK')
        cases.append(stats)
    check(len(lines) == 2835, 'MISSING_SIMULATED_FRAMES')
    hbp = b''.join(lines)
    result = {
        'schema': SCHEMA, 'source_sha256': SOURCE_SHA, 'bank_sha256': BANK_SHA,
        'index_sha256': INDEX_SHA, 'original_memory_records': 81,
        'stored_bank_rows': 567, 'retained_bank_bytes': 184815,
        'modeled_wavelengths_nm': dict(zip(BANDS, WAVELENGTHS)),
        'physical_computation_executed': True,
        'physical_photon_detection_measured': False,
        'optical_storage_measured': False,
        'electron_charge_physically_measured': False,
        'external_origin_authenticated': False,
        'mcp_transport_real_server': False,
        'software_electron_mcp_tool_name': 'electron.capture',
        'quantum_effect_verified': False,
        'model_name': 'CLASSICAL_ON_OFF_KEYING_WITH_BINOMIAL_PHOTODETECTION_AND_REPETITION',
        'photon_hbp_sha256': sha(hbp), 'photon_hbp_bytes': len(hbp),
        'negative_controls_rejected': len(negatives), 'negative_control_reasons': negatives,
        'scenarios': cases}
    files = {'photon-electron.hbp': hbp, 'results.json': canon(result)}
    for name, data in files.items():
        (dest / name).write_bytes(data)
        (dest / (name+'.sha256')).write_bytes(f'{sha(data)}  {name}\n'.encode('ascii'))
    print(json.dumps({'status':'PASS','hbp_sha256':sha(hbp),
                      'hbp_bytes':len(hbp),'negative_controls':len(negatives),
                      'scenarios':[(x['scenario'],x['bit_errors'],x['exact_rows']) for x in cases]},
                     sort_keys=True))
    return result


if __name__ == '__main__':
    if len(sys.argv) != 5:
        raise SystemExit('usage: photon_model.py source-json stored-bank-jsonl base-index-hbi output_dir')
    run(*sys.argv[1:])
