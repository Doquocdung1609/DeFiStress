#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/ruff check backend sim tests scripts
.venv/bin/python -m pytest
(cd frontend && pnpm test && pnpm lint && pnpm build)
