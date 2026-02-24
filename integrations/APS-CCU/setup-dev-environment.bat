@echo off
setlocal enabledelayedexpansion

echo ======================================
echo Dev Environment Setup
echo ======================================
echo.

echo Step 1: Checking prerequisites...

REM Check Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo   [X] Node.js not found
    echo   -^> Please install Node.js 18.x from https://nodejs.org/
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
    echo   [OK] Node.js !NODE_VERSION!
)

REM Check npm
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo   [X] npm not found
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
    echo   [OK] npm !NPM_VERSION!
)

REM Check Docker (optional)
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo   [!] Docker not found (optional - needed for full stack)
    set HAS_DOCKER=false
) else (
    for /f "tokens=*" %%i in ('docker --version') do set DOCKER_VERSION=%%i
    echo   [OK] Docker !DOCKER_VERSION!
    set HAS_DOCKER=true
)

echo.
echo Step 2: Installing central-control dependencies...
cd central-control
call npm install
if %errorlevel% neq 0 (
    echo   [X] Failed to install central-control dependencies
    cd ..
    exit /b 1
)
cd ..
echo   [OK] Central control dependencies installed

echo.
echo Step 3: Installing frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo   [X] Failed to install frontend dependencies
    cd ..
    exit /b 1
)
cd ..
echo   [OK] Frontend dependencies installed

echo.
echo ======================================
echo [OK] Dev Environment Setup Complete!
echo ======================================
echo.
echo Available commands:
echo.
echo Backend (Central Control):
echo   cd central-control
echo   npm start              # Start with hot reload
echo   npm run start:debug    # Start with debugger
echo   npm test               # Run tests
echo   npm run build          # Build for production
echo.
echo Frontend:
echo   cd frontend
echo   npm start              # Start dev server (http://localhost:4200)
echo   npm test               # Run tests
echo   npm run build          # Build for production
echo.

if "!HAS_DOCKER!"=="true" (
    echo Docker Development:
    echo   npm run setup          # Setup development environment
    echo   npm start              # Start all containers
    echo   npm stop               # Stop all containers
    echo   npm run docker:build   # Build production images
    echo.
)

echo Quick start (no Docker):
echo   # Terminal 1:
echo   cd central-control ^&^& npm start
echo.
echo   # Terminal 2:
echo   cd frontend ^&^& npm start
echo.
echo Then open http://localhost:4200 in your browser
echo.

pause
