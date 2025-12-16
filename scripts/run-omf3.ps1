<#
.SYNOPSIS
  Starter script to run the OMF3 Angular app (ccu-ui) in development.

.DESCRIPTION
  - Ensures we are in the repository root
  - Installs dependencies if node_modules is missing (npm ci)
  - Starts the Nx dev server for the requested project

.PARAMETER Project
  The nx project name to serve (default: ccu-ui)

.PARAMETER Configuration
  The build configuration to use (default: development)

.EXAMPLE
  .\scripts\run-omf3.ps1
  .\scripts\run-omf3.ps1 -Project ccu-ui -Configuration development
#>

param(
    [string]$Project = 'ccu-ui',
    [string]$Configuration = 'development'
)

# Resolve repo root (one level up from scripts/)
$repoRoot = (Resolve-Path -Path "$PSScriptRoot\.." ).Path
Set-Location -Path $repoRoot

Write-Host "Repository root: $repoRoot"

# Check Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js is not installed or not in PATH. Please install Node.js LTS and try again."
    exit 1
}

# Prepare logs
$logsDir = Join-Path $repoRoot 'logs'
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }
$diagnoseLog = Join-Path $logsDir 'omf3-diagnose.log'
$serveLog = Join-Path $logsDir 'omf3.log'

# If node_modules missing, run npm ci for reproducible install (with safe fallbacks)
$nodeModulesPath = Join-Path $repoRoot 'node_modules'
if (-not (Test-Path $nodeModulesPath)) {
  Write-Host "node_modules not found — running 'npm ci' (this may take a while)..."
  Write-Host "-> Attempt: npm ci --legacy-peer-deps"
  npm ci --legacy-peer-deps 2>&1 | Tee-Object -FilePath $diagnoseLog
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "'npm ci --legacy-peer-deps' failed (exit $LASTEXITCODE). Trying 'npm ci' without flag..."
    npm ci 2>&1 | Tee-Object -FilePath $diagnoseLog -Append
    if ($LASTEXITCODE -ne 0) {
      Write-Warning "'npm ci' failed as well. Trying 'npm install --legacy-peer-deps' as last resort..."
      npm install --legacy-peer-deps 2>&1 | Tee-Object -FilePath $diagnoseLog -Append
      if ($LASTEXITCODE -ne 0) {
        Write-Error "All install attempts failed. Check $diagnoseLog for details and fix dependency issues before retrying."
        exit $LASTEXITCODE
      }
    }
  }
  else {
    Write-Host "npm ci finished successfully. See $diagnoseLog for details."
  }
}

# Start the dev server using npx nx (will block the terminal). If npx is not available, fall back to 'npm run nx -- serve'.
Write-Host "Starting Nx dev server for project '$Project' with configuration '$Configuration'..."
Write-Host 'Open http://localhost:4200 in your browser when the build finishes.'

if (Get-Command npx -ErrorAction SilentlyContinue) {
  Write-Host "Using npx to start the dev server. Logging to: $serveLog"
  # Start and tee output to log file (also prints to console)
  npx nx serve $Project --configuration=$Configuration 2>&1 | Tee-Object -FilePath $serveLog
} else {
  Write-Warning "'npx' not found in PATH — falling back to 'npm run nx -- serve'. If that fails, ensure Node.js and npm are installed and available in PATH."
  npm run nx -- serve $Project -- --configuration=$Configuration 2>&1 | Tee-Object -FilePath $serveLog
}
