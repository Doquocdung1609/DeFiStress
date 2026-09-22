#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
"$root/.venv/bin/python" "$root/scripts/terra/run_historical_replay.py" "$@"
