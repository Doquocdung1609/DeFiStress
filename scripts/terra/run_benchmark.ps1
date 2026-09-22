$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
& "$root\.venv\Scripts\python.exe" "$PSScriptRoot\run_model_benchmark.py" @args
