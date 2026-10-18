"""Release evidence and original checkout byte provisioning; never runs a research simulation."""
from __future__ import annotations

import argparse
import ast
import email
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import venv
import zipfile

BUILDER = 'scripts/research/build_scientific_integration_v1.py'
DECLARED = '5a1bbd87ccf065763c3f82d921b977dadb21c520d073e5a2f69498f42ed094a2'
LOCK = '3f6e5302483681209e2408531eb5a15389f9fded'


def run(args: list[str], **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def git(*args: str) -> bytes:
    return run(['git', *args], capture_output=True).stdout


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def facts(b: bytes) -> dict:
    lf = b.replace(b'\r\n', b'\n')
    try:
        text = '\0' not in b.decode('utf-8')
    except UnicodeDecodeError:
        text = False
    return {'size_bytes': len(b), 'sha256_git_bytes': digest(b),
            'sha256_crlf_representation': digest(lf.replace(b'\n', b'\r\n')) if text else None}


def collect(out: Path) -> None:
    head = git('rev-parse', 'HEAD').decode().strip()
    # All large tracked files plus complete research bundle families; no row/statistic calculation.
    entries = []
    current_blobs = {}
    all_entries = git('ls-tree', '-r', '-l', '-z', head).split(b'\0')
    for entry in all_entries:
        if not entry:
            continue
        meta, path_bytes = entry.split(b'\t', 1)
        mode, kind, oid, size = meta.decode().split()
        if kind != 'blob':
            continue
        p = path_bytes.decode('utf-8')
        current_blobs[p] = oid
        selected = int(size) >= 1000000 or p.startswith((
            'data/processed/research_final/frozen_v3/',
            'data/processed/research_final/oracle_transmission_diagnostic_v1/',
            'data/processed/research_final/scientific_integration_v1/',
            'data/processed/research_final/level3_extension/deep_stress/checkpoints/',
            'data/processed/research_final/level3_extension/historical/',
            'data/processed/research_final/level3_p1_targeted_repair/historical/',
        ))
        if not selected:
            continue
        try:
            b = git('cat-file', 'blob', oid)
            actual = hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
            if len(b) != int(size) or actual != oid:
                raise ValueError('Git object byte/size mismatch')
            row = {'path': p, 'git_blob_sha': oid, **facts(b), 'status': 'FULL_BYTES_VERIFIED'}
        except Exception as exc:
            row = {'path': p, 'git_blob_sha': oid, 'status': 'UNVERIFIED', 'error': str(exc)}
        entries.append(row)
    write(out / 'large-artifacts.json', {'source_commit': head, 'method': 'git cat-file complete bytes; SHA1 header and SHA256 computed; not a scientific row audit', 'records': entries})
    seen = set()
    versions = []
    for commit in git('log', '--all', '--format=%H', '--', BUILDER).decode().splitlines():
        try:
            oid = git('rev-parse', f'{commit}:{BUILDER}').decode().strip()
        except subprocess.CalledProcessError:
            continue
        if oid in seen:
            continue
        seen.add(oid)
        b = git('cat-file', 'blob', oid)
        f = facts(b)
        versions.append({'commit': commit, 'git_blob_sha': oid, **f,
                         'matches_declaration': DECLARED in (f['sha256_git_bytes'], f['sha256_crlf_representation'])})
    write(out / 'generator-history.json', {'declared_sha256': DECLARED, 'path': BUILDER,
        'source_commit': head, 'search_scope': 'all fetched refs, unique blobs in git log --all -- path',
        'records': versions, 'matching_objects': [x for x in versions if x['matches_declaration']]})
    frozen = git('ls-tree', '-r', '-z', LOCK).split(b'\0')
    changed = []
    for entry in frozen:
        if not entry:
            continue
        meta, p = entry.split(b'\t', 1)
        expected = meta.decode().split()[2]
        path = p.decode()
        if path.startswith(('sim/', 'backend/', 'data/processed/research_final/', 'docs/research_final/', 'data/processed/mainnet/')):
            if current_blobs.get(path) != expected:
                changed.append(path)
    write(out / 'source-preservation.json', {'scientific_lock': LOCK, 'head': head, 'changed_paths': changed})
    # Diagnose old manifest declarations without mutating original files.
    legacy = []
    for bundle in ['level3_extension', 'level3_p1_targeted_repair', 'oracle_transmission_diagnostic_v1', 'scientific_integration_v1', 'final_accepted_claims_v1']:
        root = f'data/processed/research_final/{bundle}'
        m = json.loads(git('show', f'{head}:{root}/manifest.json'))
        for field in ['artifact_hashes', 'report_hashes', 'implementation_hashes']:
            for path, expected in m.get(field, {}).items():
                if not isinstance(expected, str):
                    continue
                full = f'{root}/{path}' if field == 'artifact_hashes' else path
                try:
                    oid = git('rev-parse', f'{head}:{full}').decode().strip()
                    b = git('cat-file', 'blob', oid)
                    f = facts(b)
                    status = 'EXACT' if expected == f['sha256_git_bytes'] else 'CRLF_REPRESENTATION' if expected == f['sha256_crlf_representation'] else 'MISMATCH'
                    legacy.append({'path': full, 'manifest': root + '/manifest.json', 'field': field,
                                   'expected': expected, 'git_blob_sha': oid, **f, 'status': status})
                except Exception as exc:
                    legacy.append({'path': full, 'expected': expected, 'status': 'UNVERIFIED', 'error': str(exc)})
    write(out / 'legacy-manifest-checks.json', legacy)
    # Log byte-exact external fixture identities separately from scientific baseline.
    fixtures = Path('docs/research_v2/phase00/g1/legacy_docx_inputs')
    write(out / 'legacy-docx-inputs.json', [{'path': str(p), 'sha256': digest(p.read_bytes()),
          'size_bytes': p.stat().st_size} for p in sorted(fixtures.glob('*.docx'))])


def checkout(out: Path) -> None:
    """Recreate declared checkout byte domains using Git attributes, never change Git blobs."""
    head = git('rev-parse', 'HEAD').decode().strip()
    run(['git', 'config', '--local', 'core.autocrlf', 'false'])
    run(['git', 'config', '--local', 'core.eol', 'lf'])
    constraints = {}
    unresolved = []
    for bundle in ['frozen_v3', 'level3_extension', 'level3_p1_targeted_repair',
                   'oracle_transmission_diagnostic_v1', 'scientific_integration_v1', 'final_accepted_claims_v1']:
        root = f'data/processed/research_final/{bundle}'
        m = json.loads(git('show', f'{head}:{root}/manifest.json'))
        for field in ['artifact_hashes', 'report_hashes', 'implementation_hashes', 'code_hashes']:
            for path, expected in m.get(field, {}).items():
                if not isinstance(expected, str):
                    continue
                full = f'{root}/{path}' if field == 'artifact_hashes' else path
                b = git('show', f'{head}:{full}')
                text = Path(full).suffix.lower() in ['.json', '.csv', '.md', '.py', '.txt', '.jsonl']
                if not text:
                    domain = 'binary' if digest(b) == expected else None
                else:
                    lf = b.replace(b'\r\n', b'\n')
                    domain = 'lf' if digest(lf) == expected else 'crlf' if digest(lf.replace(b'\n', b'\r\n')) == expected else None
                if domain is None:
                    unresolved.append({'path': full, 'expected': expected, 'reason': 'not LF/CRLF representation of current Git object'})
                    continue
                constraints.setdefault(full, set()).add(domain)
    # G0 inventory records the original per-path checkout bytes as well as Git LF bytes.
    inventory = json.loads(git('show', f'{head}:artifacts/manuscript_p3/P3_LOCKED_EVIDENCE_INVENTORY.json'))
    for record in inventory['records']:
        full = record['original_artifact_path']
        expected = record.get('checksums', {}).get('checkout_sha256')
        if not expected:
            continue
        b = git('show', f'{head}:{full}')
        text = Path(full).suffix.lower() in ['.json', '.csv', '.md', '.py', '.txt', '.jsonl']
        lf = b.replace(b'\r\n', b'\n')
        if not text:
            domain = 'binary' if digest(b) == expected else None
        else:
            domain = 'lf' if digest(lf) == expected else 'crlf' if digest(lf.replace(b'\n', b'\r\n')) == expected else None
        if domain is None:
            raise ValueError(f'Cannot restore G0 input checkout bytes: {full}')
        constraints.setdefault(full, set()).add(domain)
    conflicts = {p: sorted(v) for p, v in constraints.items() if len(v) > 1}
    if conflicts:
        write(out / 'checkout-policy-conflicts.json', conflicts)
        raise ValueError('Contradictory byte declarations; cannot provision checkout honestly')
    attr = ['* text=auto eol=crlf', '*.docx -text', '*.png -text', '*.gz -text', '*.zip -text']
    for path, values in sorted(constraints.items()):
        domain = next(iter(values))
        attr.append(f'"{path}" -text' if domain in ['binary', 'lf'] else f'"{path}" text eol=crlf')
    info = Path(git('rev-parse', '--git-path', 'info/attributes').decode().strip())
    info.parent.mkdir(parents=True, exist_ok=True)
    info.write_text('\n'.join(attr) + '\n', encoding='utf-8', newline='\n')
    run(['git', 'checkout-index', '--force', '--all'])
    # checkout-index can retain stat-clean existing files despite new EOL attributes.
    # Materialize only line-ending representations of the exact Git objects, then verify bytes.
    materialized = []
    for path, values in sorted(constraints.items()):
        domain = next(iter(values))
        raw = git('show', f'{head}:{path}')
        lf = raw.replace(b'\r\n', b'\n')
        expected_bytes = raw if domain == 'binary' else lf if domain == 'lf' else lf.replace(b'\n', b'\r\n')
        Path(path).write_bytes(expected_bytes)
        actual_bytes = Path(path).read_bytes()
        if actual_bytes != expected_bytes:
            raise ValueError(f'Checkout byte provisioning failed: {path}')
        materialized.append({'path': path, 'domain': domain, 'checkout_sha256': digest(actual_bytes),
                             'git_bytes_sha256': digest(raw), 'size_bytes': len(actual_bytes)})
    write(out / 'checkout-byte-verification.json', materialized)
    # Refresh stat metadata only; never stage, suppress or assume-unchanged a source file.
    index_before = git('write-tree').decode().strip()
    # Force an exact content comparison before trusting Windows cached stat/EOL status.
    run(['git', 'diff', '--exit-code', '--'])
    run(['git', 'diff', '--cached', '--exit-code', '--'])
    subprocess.run(['git', 'update-index', '--really-refresh'], check=False, capture_output=True)
    if git('write-tree').decode().strip() != index_before:
        raise ValueError('Index content changed during stat refresh')
    status = git('status', '--porcelain', '--untracked-files=no').decode().strip()
    if status:
        write(out / 'checkout-status-diagnostics.json', {
            'status': status, 'index_tree': index_before,
            'attributes': git('check-attr', '--all', '--', 'scripts/research/build_final_accepted_claims_v1.py').decode(),
            'diff': git('diff', '--', 'scripts/research/build_final_accepted_claims_v1.py').decode(errors='replace')})
    if status:
        raise ValueError(f'Checkout normalization changed tracked source content: {status}')
    write(out / 'checkout-policy.json', {'head': head, 'method': 'untracked .git/info/attributes; Git checkout-index',
        'tracked_source_diff': status, 'rules': attr, 'unresolved_declarations_not_overridden': unresolved,
        'interpretation': 'Original declared LF and CRLF byte domains restored per path; assertions unchanged; Git blobs unchanged'})


def environment(out: Path) -> None:
    packages = []
    for d in importlib.metadata.distributions():
        name = re.sub(r'[-_.]+', '-', d.metadata['Name']).lower()
        if name != 'defi-stress-lab':
            packages.append((name, d.version))
    packages = sorted(set(packages))
    resolved = out / 'requirements.resolved.txt'
    resolved.write_text(''.join(f'{n}=={v}\n' for n, v in packages), encoding='utf-8', newline='\n')
    wheelhouse = out.parent / 'v1-g1-wheelhouse'
    wheelhouse.mkdir(exist_ok=True)
    run([sys.executable, '-m', 'pip', 'download', '--only-binary=:all:', '--no-deps',
         '-r', str(resolved), '-d', str(wheelhouse)])
    wheels = {}
    for p in sorted(wheelhouse.glob('*.whl')):
        with zipfile.ZipFile(p) as z:
            metadata = email.message_from_bytes(z.read(next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))))
        key = (re.sub(r'[-_.]+', '-', metadata['Name']).lower(), metadata['Version'])
        wheels[key] = {'file': p.name, 'size_bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())}
    if set(packages) != set(wheels):
        raise ValueError(f'Wheel coverage mismatch: {set(packages) - set(wheels)}')
    lock = out / 'requirements-windows-py312.lock.txt'
    header = '# Newly resolved/tested Windows CPython 3.12 environment; not recovered historical V1 environment.\n'
    lock.write_text(header + ''.join(f'{n}=={v} --hash=sha256:{wheels[(n,v)]["sha256"]}\n' for n,v in packages), encoding='utf-8', newline='\n')
    smoke_env = out.parent / 'v1-g1-clean-smoke'
    venv.create(smoke_env, with_pip=True, clear=True)
    python = smoke_env / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    run([str(python), '-m', 'pip', 'install', '--no-index', '--find-links', str(wheelhouse),
         '--require-hashes', '-r', str(lock)])
    run([str(python), '-m', 'pip', 'check'])
    clean_packages = json.loads(run([str(python), '-m', 'pip', 'list', '--format=json'], capture_output=True).stdout)
    if sorted((re.sub(r'[-_.]+', '-', p['name']).lower(), p['version']) for p in clean_packages) != packages:
        raise ValueError('Fresh environment distribution set differs from lock')
    run([str(python), '-m', 'pytest', '-q', 'sim/tests/test_health_factor.py',
         'sim/tests/test_liquidation.py', f'--junitxml={out / "environment-smoke.xml"}'])
    committed = git('show', 'HEAD:docs/research_v2/phase00/g1/requirements-windows-py312.lock.txt')
    if committed != lock.read_bytes():
        raise ValueError('Installed environment does not reproduce committed lock exactly')
    write(out / 'environment-verified.json', {'python': sys.version, 'executable': sys.executable,
          'platform': platform.platform(), 'machine': platform.machine(), 'os': os.name,
          'runner_image': {k: os.environ.get(k) for k in ['ImageOS','ImageVersion','RUNNER_OS','RUNNER_ARCH']},
          'packages': [{'name': n, 'version': v, **wheels[(n,v)]} for n,v in packages],
          'lock_sha256': digest(lock.read_bytes()), 'clean_install': 'PASS', 'pip_check': 'PASS', 'clean_distribution_versions_match': True,
          'smoke': '5 existing tests PASS', 'container_used': False,
          'docker_digest': 'NOT_APPLICABLE_NO_CONTAINER_USED',
          'scope': 'New tested target environment, not a recovered historical environment',
          'run_id': os.environ.get('GITHUB_RUN_ID'), 'source_commit': git('rev-parse', 'HEAD').decode().strip()})


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['collect', 'environment', 'checkout'])
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.mode == 'collect':
        collect(args.output)
    elif args.mode == 'checkout':
        checkout(args.output)
    else:
        environment(args.output)


if __name__ == '__main__':
    main()
