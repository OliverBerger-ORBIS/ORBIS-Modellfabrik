@echo off
REM Script to build and serve the OSF Dashboard locally for testing (GitHub Pages layout)
REM The build uses baseHref /ORBIS-Modellfabrik/, so we must serve from a parent dir
REM that has ORBIS-Modellfabrik/ containing the build output.
REM Usage: scripts\serve-local.bat [port]

setlocal

set PORT=%1
if "%PORT%"=="" set PORT=4200
set BUILD_DIR=dist\apps\osf-ui\browser
set SERVE_ROOT=dist\apps\osf-ui\browser-gp
set BASE_PATH=ORBIS-Modellfabrik

echo Building OSF Dashboard for local testing...
call npm run build:github-pages

if not exist "%BUILD_DIR%" (
    echo Build failed: %BUILD_DIR% not found
    exit /b 1
)

echo Restructuring for baseHref /%BASE_PATH%/...
if exist "%SERVE_ROOT%" rmdir /s /q "%SERVE_ROOT%"
mkdir "%SERVE_ROOT%\%BASE_PATH%"
xcopy /e /i /y "%BUILD_DIR%\*" "%SERVE_ROOT%\%BASE_PATH%\"

echo Build complete!
echo.
echo Starting local server on port %PORT%...
echo Open your browser at: http://localhost:%PORT%/%BASE_PATH%/
echo.
echo Press Ctrl+C to stop the server
echo.

npx serve "%SERVE_ROOT%" -p %PORT%
