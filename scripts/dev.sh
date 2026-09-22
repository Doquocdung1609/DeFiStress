#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
trap 'kill 0' EXIT
.venv/bin/python -m uvicorn backend.app.main:app --reload --port 8000 &
(cd frontend && pnpm dev) &
wait
