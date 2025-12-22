@echo off
REM scripts\run-osf.bat - Starter for OSF dev server
REM Usage: run-osf.bat [project] [configuration]

SET "PROJECT=%~1"
IF "%PROJECT%"=="" SET "PROJECT=osf-ui"
SET "CONFIG=%~2"
IF "%CONFIG%"=="" SET "CONFIG=development"

REM change to repo root (one level up from scripts\)
PUSHD %~dp0\..

where node >nul 2>&1
IF ERRORLEVEL 1 (
  echo Node.js not found in PATH. Please install Node.js LTS and try again.
  POPD
  exit /b 1
)

IF NOT EXIST node_modules (
  echo node_modules not found - running npm ci...
  npm ci || (
    echo npm ci failed
    POPD
    exit /b 1
  )
)

echo Starting Nx dev server for project %PROJECT% with configuration %CONFIG%...
 npx nx serve %PROJECT% --configuration=%CONFIG%

POPD
