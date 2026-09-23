param(
  [string]$RepoRoot = ".",
  [string]$ReplicationZip = "",
  [switch]$AllowProxy
)

$ErrorActionPreference = "Stop"
$python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (!(Test-Path $python)) { throw "Python venv not found: $python" }

$pack = Split-Path -Parent $MyInvocation.MyCommand.Path
$raw = Join-Path $RepoRoot "data\raw\terra_may2022_v1"
$processed = Join-Path $RepoRoot "data\processed"
New-Item -ItemType Directory -Force -Path $raw | Out-Null
New-Item -ItemType Directory -Force -Path $processed | Out-Null
$out = Join-Path $processed "terra_may2022_v1.csv"

$args = @(
  (Join-Path $pack "build_terra_may2022_v1.py"),
  "--repo-root", $RepoRoot,
  "--work-dir", $raw,
  "--output", $out
)
if ($ReplicationZip) { $args += @("--replication-zip", $ReplicationZip) }
if ($AllowProxy) { $args += "--allow-proxy" } else { $args += "--strict" }

& $python @args
if ($LASTEXITCODE -ne 0) { throw "Terra dataset BUILD failed with exit code $LASTEXITCODE. Validation/import were not run." }
if (!(Test-Path $out)) { throw "Build reported success but output file is missing: $out" }

$status = if ($AllowProxy) { "QUALITY_WARNING" } else { "REAL_HISTORICAL" }
$sourceType = if ($AllowProxy) { "REPLICATION_ONCHAIN_WITH_PRECRISIS_PROXIES" } else { "REPLICATION_ONCHAIN" }
& $python (Join-Path $RepoRoot "scripts\terra\validate_dataset.py") `
  --input $out `
  --dataset-version terra_may2022_v1 `
  --status $status `
  --source-name "Liu-Makarov-Schoar replication + Terra Classic" `
  --source-type $sourceType `
  --chain-id columbus-5 `
  --output (Join-Path $processed "terra_may2022_v1_validation.json")
if ($LASTEXITCODE -ne 0) { throw "Terra dataset VALIDATION failed with exit code $LASTEXITCODE. Import was not run." }

& $python (Join-Path $RepoRoot "scripts\terra\import_dataset.py") `
  --input $out `
  --dataset-version terra_may2022_v1 `
  --status $status `
  --source-name "Liu-Makarov-Schoar replication + Terra Classic" `
  --source-type $sourceType `
  --chain-id columbus-5 `
  --raw-reference "doi:10.17632/j5d8n7hzdy.4" `
  --manifest-output (Join-Path $processed "terra_may2022_v1_import_manifest.json")
if ($LASTEXITCODE -ne 0) { throw "Terra dataset IMPORT failed with exit code $LASTEXITCODE." }

Write-Host "Imported terra_may2022_v1 with status $status"
