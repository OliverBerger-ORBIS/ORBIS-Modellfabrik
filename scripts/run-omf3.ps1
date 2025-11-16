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

# If node_modules missing, run npm ci for reproducible install
if (-not (Test-Path "$repoRoot\node_modules")) {
    Write-Host "node_modules not found — running 'npm ci' (this may take a while)..."
    npm ci
    if ($LASTEXITCODE -ne 0) {
        Write-Error "'npm ci' failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
}

# Start the dev server using npx nx (will block the terminal)
Write-Host "Starting Nx dev server for project '$Project' with configuration '$Configuration'..."
Write-Host "Open http://localhost:4200 in your browser when the build finishes."

# Use npx so we don't require a global nx install
npx nx serve $Project --configuration=$Configuration
