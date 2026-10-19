"""Offline verification of this bounded archive-access dossier, not gate promotion."""
import base64
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path


def load(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def main():
    folder = Path(__file__).resolve().parent
    root = folder.parent
    evidence = folder / 'evidence'
    provenance = load(folder / 'EVIDENCE_PROVENANCE.json')
    for row in provenance['preserved_files']:
        raw = (root / row['path']).read_bytes()
        assert len(raw) == row['size_bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
        if 'uncompressed_sha256' in row:
            data = gzip.decompress(raw)
            assert len(data) == row['uncompressed_size'] and hashlib.sha256(data).hexdigest() == row['uncompressed_sha256']
    manifest = load(evidence / 'collection_manifest.json')
    for row in manifest['files']:
        raw = (evidence / row['path']).read_bytes()
        assert len(raw) == row['size_bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
    result = load(evidence / 'INDEPENDENT_ARCHIVE_COMPARISON.json')
    assert (root / 'INDEPENDENT_ARCHIVE_COMPARISON.json').read_bytes() == (evidence / 'INDEPENDENT_ARCHIVE_COMPARISON.json').read_bytes()
    assert result['source_commit'] == provenance['collection_source_commit']
    assert result['overall_gate'] == 'BLOCKED' and result['phase02_authorized'] is False
    assert result['registration_unchanged'] is True and result['new_simulation'] is False
    statuses = {}
    for provider in ['drpc', 'subquery', 'blockreq']:
        observations = [x for x in result['observations'] if x['provider']['id'] == provider]
        assert len(observations) == 3 and all(len(x['passes']) == 2 for x in observations)
        statuses[provider] = Counter(f['status'] for x in observations for p in x['passes'] for f in p['fields'])
        assert all(x['backend_independence'] == 'UNVERIFIED' for x in observations)
    assert statuses['drpc'] == {'AGREES': 174}
    assert statuses['subquery'] == statuses['blockreq'] == {'BLOCKED_MISSING_DATA': 174}
    registry = load(root / 'SAMPLE_REGISTRATION.json')
    hashes = {b['expected_hash'] for b in registry['blocks']}
    numbers = {hex(b['number']) for b in registry['blocks']}
    response_count = 0
    for path in evidence.glob('*response-entities.json.gz'):
        for row in load(path):
            body = base64.b64decode(row['response_entity_base64'], validate=True)
            assert len(body) == row['response_size_bytes']
            assert hashlib.sha256(body).hexdigest() == row['response_entity_sha256']
            assert row['started_at_utc'] <= row['completed_at_utc']
            requests = json.loads(base64.b64decode(row['request_body_base64'], validate=True))
            if not isinstance(requests, list):
                requests = [requests]
            for request in requests:
                assert request['method'] in {'eth_chainId', 'eth_getBlockByNumber', 'eth_call'}
                if request['method'] == 'eth_getBlockByNumber':
                    assert request['params'][0] in numbers and request['params'][1] is False
                if request['method'] == 'eth_call':
                    selector = request['params'][1]
                    assert selector['blockHash'] in hashes and selector['requireCanonical'] is True
            response_count += 1
    assert response_count == 102
    print(json.dumps({'saved_bytes_and_boundaries': 'PASS', 'preserved_files': len(provenance['preserved_files']),
                      'original_manifest_entries': len(manifest['files']), 'http_response_entities': response_count,
                      'registered_value_rows': statuses, 'independent_historical_state_values_compared': 0,
                      'archive_independence_gate': 'BLOCKED', 'phase02_authorized': False}, indent=2))


if __name__ == '__main__':
    main()
