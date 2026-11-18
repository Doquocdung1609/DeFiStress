#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
mkdir -p data/runs
state=data/runs/demo-processes.posix
if [[ -e "$state" ]]; then
  echo "Demo process record exists. Run scripts/stop_demo.sh first." >&2
  exit 1
fi
for port in 8100 3100; do
  if (echo > "/dev/tcp/127.0.0.1/$port") 2>/dev/null; then
    echo "Port $port is occupied." >&2
    exit 1
  fi
done
if [[ ! -x .venv/bin/python ]]; then
  python3.12 -m venv .venv
  .venv/bin/python -m pip install -e .
fi
if [[ ! -d frontend/node_modules/next ]]; then
  (cd frontend && pnpm install --frozen-lockfile)
fi
export DATABASE_URL="sqlite:///$root/data/runs/demo.sqlite"
export APP_MODE=FIXTURE ASYNC_BACKEND=local ETH_RPC_URL= ETH_ARCHIVE_RPC_URL= GRAPH_API_KEY=
export TERRA_ARCHIVE_LCD_URL= TERRA_HISTORY_DATA_URL= CURVE_HISTORY_DATA_URL= BRIDGE_FLOW_DATA_URL= COINGECKO_API_KEY=
export NEXT_PUBLIC_API_URL=http://localhost:8100
.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8100 > data/runs/demo-api.log 2>&1 &
api_pid=$!
(cd frontend && pnpm exec next dev -p 3100) > data/runs/demo-web.log 2>&1 &
web_pid=$!
ready=0
for _ in {1..60}; do
  if ! kill -0 "$api_pid" 2>/dev/null || ! kill -0 "$web_pid" 2>/dev/null; then break; fi
  if curl -fsS http://127.0.0.1:8100/api/v1/health >/dev/null 2>&1 && curl -fsS http://127.0.0.1:3100/terra/warning-lab | grep -q 'Synthetic B0'; then
    ready=1
    break
  fi
  sleep 2
done
if [[ "$ready" -ne 1 ]]; then
  kill "$web_pid" "$api_pid" 2>/dev/null || true
  echo "Demo did not start; read data/runs/demo-*.log." >&2
  exit 1
fi
printf '%s %s\n' "$api_pid" "$web_pid" > "$state"
echo "Demo ready: http://localhost:3100/terra/overview"
echo "Stop: scripts/stop_demo.sh"
