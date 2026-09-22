$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
if (-not (Test-Path -LiteralPath ".venv")) { py -3.12 -m venv .venv }
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -e ".[dev]"
Push-Location -LiteralPath "$root\frontend"
try { & pnpm install } finally { Pop-Location }
Write-Host "Bootstrap complete. Copy .env.example to .env before REAL_MAINNET mode."
