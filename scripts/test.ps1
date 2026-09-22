$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
& ".\.venv\Scripts\ruff.exe" check backend sim tests scripts
& ".\.venv\Scripts\python.exe" -m pytest
Push-Location -LiteralPath "$root\frontend"
try {
    & pnpm.cmd test
    & pnpm.cmd lint
    & pnpm.cmd build
} finally { Pop-Location }
