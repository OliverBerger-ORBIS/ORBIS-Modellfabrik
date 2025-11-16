@echo off
REM Script to build and serve the OMF3 Dashboard locally for testing
REM Usage: scripts\serve-local.bat [port]

setlocal

set PORT=%1
if "%PORT%"=="" set PORT=4200
set BUILD_DIR=dist\apps\ccu-ui\browser

echo Building OMF3 Dashboard for local testing...
call npm run build:netlify

if not exist "%BUILD_DIR%" (
    echo Build failed: %BUILD_DIR% not found
    exit /b 1
)

echo Build complete!
echo.
echo Starting local server on port %PORT%...
echo Open your browser at: http://localhost:%PORT%
echo.
echo Press Ctrl+C to stop the server
echo.

npx serve "%BUILD_DIR%" -p %PORT%
