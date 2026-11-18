"""Local container QA; copies sources into Linux storage so symlink controls are real."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tarfile

EVIDENCE = Path('/evidence')
results = []


def run(name, args, cwd=None):
    completed = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (EVIDENCE / (name + '.log')).write_text(completed.stdout)
    print(name, 'exit', completed.returncode, completed.stdout[-2000:], flush=True)
    results.append({'name': name, 'command': args, 'cwd': str(cwd), 'exit_code': completed.returncode})
    return completed.returncode


if run('linux-install', [sys.executable, '-m', 'pip', 'install', 'pytest==8.4.2', 'pyarrow==23.0.1',
                          'pytest-cov==7.1.0']):
    raise SystemExit(1)

for archive, target in [('warning-input.tar', '/tmp/warning'), ('pr55.tar', '/tmp/pr55')]:
    root = Path(target)
    root.mkdir()
    with tarfile.open(EVIDENCE / archive) as source:
        source.extractall(root, filter='data')
    if target.endswith('warning'):
        run('linux-warning', [sys.executable, '-m', 'pytest', '-q', 'tests/v2/terra_warning',
                              '--junitxml=/evidence/linux-warning.xml'], root)
        run('linux-accepted-regressions', [sys.executable, '-m', 'pytest', '-q', 'tests/v2/terra_pit',
            'tests/v2/test_contracts.py', 'tests/v2/test_saved_adapter.py', 'tests/v2/test_saved_adapter_review.py',
            'tests/test_prephase02_offline.py', 'tests/research_v2/test_terra_p04_01_audit.py',
            '--junitxml=/evidence/linux-accepted-regressions.xml'], root)
        run('linux-prephase', [sys.executable, '-m', 'pytest', '-q', 'tests/test_prephase02_offline.py',
                               '--junitxml=/evidence/linux-prephase.xml'], root)
        run('linux-L1-L2', [sys.executable, 'docs/research_v2/prephase02_offline/validate_offline.py',
            '--validator-commit', 'LOCAL_P04_03_SOURCE_MANIFEST', '--output', '/evidence/linux-L1-L2.json',
            '--l2-junit', '/evidence/linux-prephase.xml', '--l2-exit-code', str(results[-1]['exit_code'])], root)
        run('linux-pit-smoke', [sys.executable, '-m', 'defistress_v2.terra_pit.validate',
            '--implementation-commit', 'LOCAL_P04_03_SOURCE_MANIFEST', '--output', '/evidence/linux-pit-smoke.json'], root)
        run('linux-source-audit', [sys.executable, 'scripts/research/terra_v2/audit_p04_01.py', '--repo-root', '.',
            '--registry', 'docs/research_v2/terra_early_warning/p04_01/P04_01_DATASET_REGISTRY.json',
            '--output', '/evidence/linux-source-audit.json'], root)
    else:
        run('linux-pr55', [sys.executable, '-m', 'pytest', '-q', 'tests/v2', 'tests/test_prephase02_offline.py',
                           '--junitxml=/evidence/linux-pr55.xml'], root)

metadata = {'python': sys.version, 'platform': platform.platform(), 'results': results,
            'input_sha256': {name: hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest()
                             for name in ['warning-input.tar', 'pr55.tar']}}
(EVIDENCE / 'linux-execution.json').write_text(json.dumps(metadata, indent=2) + '\n')
raise SystemExit(any(result['exit_code'] != 0 for result in results))
