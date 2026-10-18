"""Read-only Phase 00 checks. No simulation, network access, or source writes."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--manifest', type=Path, default=Path(__file__).with_name('V1_RELEASE_MANIFEST.json'))
    p.add_argument('--git-object', action='store_true', help='Read pinned Git objects; ignore checkout line endings')
    p.add_argument('--smoke', action='store_true', help='Run five existing pure HF/liquidation tests, never the engine')
    args = p.parse_args()
    root = args.repo.resolve()
    m = json.loads(args.manifest.read_text(encoding='utf-8'))
    errors = []
    verified = 0
    ast_files = 0
    for x in m['artifacts']:
        # Never promote tree-only/manifest-only evidence to an observed SHA-256.
        if x['observed_sha256'] is None:
            continue
        path = root / x['path']
        try:
            if args.git_object:
                b = subprocess.run(['git', '-C', str(root), 'cat-file', 'blob', x['git_blob_sha']],
                                   check=True, capture_output=True).stdout
            else:
                b = path.read_bytes()
            sha = hashlib.sha256(b).hexdigest()
            blob = hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
            if sha != x['observed_sha256'] or blob != x['git_blob_sha']:
                raise ValueError('exact-byte checksum mismatch; do not silently normalize')
            verified += 1
            if x['path'].endswith('.py') and x['path'].startswith(('sim/', 'backend/', 'tests/', 'scripts/')):
                ast.parse(b, filename=x['path'])
                ast_files += 1
        except Exception as exc:
            errors.append({'path': x['path'], 'error': str(exc)})
    smoke = []
    if args.smoke and not errors:
        if args.git_object:
            raise SystemExit('--smoke requires a separately verified clean filesystem checkout')
        os.chdir(root)
        sys.path.insert(0, str(root))
        sys.dont_write_bytecode = True
        for path in ['sim/tests/test_health_factor.py', 'sim/tests/test_liquidation.py']:
            try:
                namespace = runpy.run_path(path)
                for name, fn in namespace.items():
                    if name.startswith('test_') and callable(fn):
                        try:
                            fn()
                            smoke.append({'test': path + '::' + name, 'status': 'PASS'})
                        except Exception as exc:
                            smoke.append({'test': path + '::' + name, 'status': 'FAIL', 'error': str(exc)})
            except Exception as exc:
                errors.append({'path': path, 'error': str(exc)})
    ok = not errors and all(x['status'] == 'PASS' for x in smoke)
    print(json.dumps({'status': 'PASS_SCOPED_CHECKS' if ok else 'FAIL',
                     'verified_sha256_files': verified, 'python_ast_files': ast_files,
                     'tree_only_files_not_byte_checked': sum(x['observed_sha256'] is None for x in m['artifacts']),
                     'smoke_tests': smoke, 'errors': errors,
                     'full_reproduction_claimed': False, 'freeze_authorized': False}, indent=2))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
