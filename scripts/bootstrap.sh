#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
(cd frontend && pnpm install)
echo "Bootstrap complete. Copy .env.example to .env before REAL_MAINNET mode."
