param([int] $ApiPort = 8100, [int] $WebPort = 3100)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$state = Join-Path $root "data\runs\demo-processes.json"
$logs = Join-Path $root "data\runs"

if ($ApiPort -ne 8100 -or $WebPort -ne 3100) {
    throw "Demo ports are fixed at API 8100 and web 3100 so the browser uses the correct API."
}
if (Test-Path -LiteralPath $state) {
    throw "A demo process record already exists. Run .\scripts\stop_demo.ps1 first."
}
foreach ($port in @($ApiPort, $WebPort)) {
    if (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) {
        throw "Port $port is already occupied. Stop that service before starting this demo."
    }
}
if (-not (Test-Path -LiteralPath $python)) {
    & (Join-Path $PSScriptRoot "bootstrap.ps1")
    if ($LASTEXITCODE -ne 0) { throw "Python bootstrap failed." }
}
$pnpm = Get-Command "pnpm.cmd" -ErrorAction Stop | Select-Object -First 1
if (-not (Test-Path -LiteralPath (Join-Path $root "frontend\node_modules\next"))) {
    Push-Location (Join-Path $root "frontend")
    try { & $pnpm.Source install --frozen-lockfile; if ($LASTEXITCODE -ne 0) { throw "Frontend install failed." } }
    finally { Pop-Location }
}
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$env:DATABASE_URL = "sqlite:///$($root.Replace('\', '/'))/data/runs/demo.sqlite"
$env:APP_MODE = "FIXTURE"
$env:ASYNC_BACKEND = "local"
$env:ETH_RPC_URL = ""
$env:ETH_ARCHIVE_RPC_URL = ""
$env:GRAPH_API_KEY = ""
$env:TERRA_ARCHIVE_LCD_URL = ""
$env:TERRA_HISTORY_DATA_URL = ""
$env:CURVE_HISTORY_DATA_URL = ""
$env:BRIDGE_FLOW_DATA_URL = ""
$env:COINGECKO_API_KEY = ""
$env:NEXT_PUBLIC_API_URL = "http://localhost:$ApiPort"
$api = $null
$web = $null
try {
    $api = Start-Process -FilePath $python -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "$ApiPort" -WorkingDirectory $root -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs "demo-api.log") -RedirectStandardError (Join-Path $logs "demo-api-error.log") -PassThru
    $web = Start-Process -FilePath $pnpm.Source -ArgumentList "exec", "next", "dev", "-p", "$WebPort" -WorkingDirectory (Join-Path $root "frontend") -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs "demo-web.log") -RedirectStandardError (Join-Path $logs "demo-web-error.log") -PassThru
    $deadline = (Get-Date).AddSeconds(120)
    $ready = $false
    while ((Get-Date) -lt $deadline) {
        if ($api.HasExited -or $web.HasExited) { throw "A demo service exited during startup. Check data/runs/demo-*-error.log." }
        try {
            $health = Invoke-RestMethod -Uri "http://127.0.0.1:$ApiPort/api/v1/health" -TimeoutSec 3
            $page = Invoke-WebRequest -Uri "http://127.0.0.1:$WebPort/terra/warning-lab" -UseBasicParsing -TimeoutSec 6
            if ($health.service -eq "healthy" -and $page.StatusCode -eq 200 -and $page.Content -match "Synthetic B0") { $ready = $true; break }
        } catch { }
        Start-Sleep -Seconds 2
    }
    if (-not $ready) { throw "Demo did not become ready within 120 seconds. Check data/runs/demo-*-error.log." }
    @{ api_pid = $api.Id; web_pid = $web.Id; root = $root; api_port = $ApiPort; web_port = $WebPort } | ConvertTo-Json | Set-Content -LiteralPath $state -Encoding utf8
    Write-Host "Demo ready: http://localhost:$WebPort/terra/overview"
    Write-Host "API: http://localhost:$ApiPort/docs"
    Write-Host "Stop: .\scripts\stop_demo.ps1"
} catch {
    foreach ($process in @($web, $api)) { if ($null -ne $process -and -not $process.HasExited) { taskkill /PID $process.Id /T /F | Out-Null } }
    throw
}
