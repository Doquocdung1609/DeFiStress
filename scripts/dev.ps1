$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Python virtual environment was not found. Run .\scripts\bootstrap.ps1 first."
}

# npm installs Windows command shims as .cmd files. Start-Process cannot reliably
# launch the extensionless `pnpm`/PowerShell shim, so resolve pnpm.cmd explicitly.
$pnpm = Get-Command "pnpm.cmd" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -eq $pnpm) {
    throw "pnpm.cmd was not found on PATH. Run 'npm install -g pnpm', then reopen PowerShell."
}

function Test-PortInUse([int] $Port) {
    return $null -ne (Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1)
}

function Test-DeFiStressFrontend([int] $Port) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/overview" -UseBasicParsing -TimeoutSec 3
        return $response.StatusCode -eq 200 -and $response.Content -match "DeFiStress"
    }
    catch {
        return $false
    }
}

$api = $null
$web = $null
$apiPort = 8000
$frontendPort = $null
$reuseFrontend = $false

foreach ($candidatePort in @(3000, 3100)) {
    if (Test-PortInUse $candidatePort) {
        if (Test-DeFiStressFrontend $candidatePort) {
            $frontendPort = $candidatePort
            $reuseFrontend = $true
            break
        }
    }
    else {
        $frontendPort = $candidatePort
        break
    }
}

if ($null -eq $frontendPort) {
    throw "Frontend ports 3000 and 3100 are both in use. Stop one of those listeners and run this script again."
}

try {
    if (Test-PortInUse $apiPort) {
        try {
            $health = Invoke-RestMethod -Uri "http://127.0.0.1:$apiPort/api/v1/health" -TimeoutSec 3
        }
        catch {
            throw "Port $apiPort is already in use by another service. Stop that listener and run this script again."
        }

        if ($health.service -ne "healthy") {
            throw "Port $apiPort is occupied, but the service there is not a healthy DeFiStress API."
        }

        Write-Host "Reusing the DeFiStress API already running on port $apiPort."
    }
    else {
        $api = Start-Process -FilePath $python -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--reload", "--port", "$apiPort" -WorkingDirectory $root -WindowStyle Hidden -PassThru
    }

    if ($reuseFrontend) {
        Write-Host "Reusing the DeFiStress frontend already running on port $frontendPort."
    }
    else {
        $web = Start-Process -FilePath $pnpm.Source -ArgumentList "exec", "next", "dev", "-p", "$frontendPort" -WorkingDirectory "$root\frontend" -WindowStyle Hidden -PassThru
    }
}
catch {
    foreach ($process in @($web, $api)) {
        if ($null -ne $process -and -not $process.HasExited) {
            Stop-Process -Id $process.Id -ErrorAction SilentlyContinue
        }
    }
    throw
}

$startedIds = @($api, $web) | Where-Object { $null -ne $_ } | ForEach-Object { $_.Id }
Write-Host "Development services are ready. Open http://localhost:$frontendPort/overview"
if ($startedIds.Count -gt 0) {
    Write-Host "Processes started now: $($startedIds -join ', ')"
    Write-Host "To stop each complete process tree, run: taskkill /PID <PID> /T /F"
}
