$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$state = Join-Path $root "data\runs\demo-processes.json"
if (-not (Test-Path -LiteralPath $state)) { Write-Host "No demo process record found."; exit 0 }
$record = Get-Content -LiteralPath $state -Raw | ConvertFrom-Json
if ($record.root -ne $root) { throw "Process record belongs to another workspace." }
foreach ($pidValue in @($record.web_pid, $record.api_pid)) {
    if (Get-Process -Id $pidValue -ErrorAction SilentlyContinue) { taskkill /PID $pidValue /T /F | Out-Null }
}
Remove-Item -LiteralPath $state
Write-Host "Demo stopped. Saved results remain in data/runs/demo.sqlite."
