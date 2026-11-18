#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
state="$root/data/runs/demo-processes.posix"
if [[ ! -f "$state" ]]; then echo "No demo process record found."; exit 0; fi
read -r api_pid web_pid < "$state"
kill "$web_pid" "$api_pid" 2>/dev/null || true
rm -f "$state"
echo "Demo stopped. Saved results remain in data/runs/demo.sqlite."
