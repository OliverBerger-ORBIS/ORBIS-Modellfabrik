@echo off
REM Script to create a test deployment on GitHub Pages
REM This allows testing if GitHub Pages is accessible before full setup

setlocal EnableDelayedExpansion

set BRANCH_NAME=gh-pages-test
set BUILD_DIR=dist\apps\ccu-ui\browser

echo GitHub Pages Test-Deployment
echo ================================
echo.
echo Dieser Script erstellt einen Test-Deployment um zu pruefen,
echo ob GitHub Pages von Ihren Firmenrechnern aus erreichbar ist.
echo.

REM Check if branch exists
git show-ref --quiet refs/heads/%BRANCH_NAME% 2>nul
if %errorlevel% equ 0 (
    echo Branch '%BRANCH_NAME%' existiert bereits.
    echo Moechten Sie ihn loeschen und neu erstellen? (j/n)
    set /p response=
    if /i "!response!"=="j" (
        echo Loesche Branch '%BRANCH_NAME%'...
        git branch -D %BRANCH_NAME% 2>nul
        git push origin --delete %BRANCH_NAME% 2>nul
    ) else (
        echo Abbruch. Bitte loeschen Sie den Branch manuell.
        exit /b 1
    )
)

echo Schritt 1/5: Build erstellen...
call npm run build:netlify

if not exist "%BUILD_DIR%" (
    echo Build fehlgeschlagen: %BUILD_DIR% nicht gefunden
    exit /b 1
)

echo Build erfolgreich
echo.

echo Schritt 2/5: Testbranch erstellen...
git checkout -b %BRANCH_NAME%

echo Schritt 3/5: Build-Dateien kopieren...
xcopy /E /I /Y "%BUILD_DIR%\*" .

REM Create .nojekyll file
type nul > .nojekyll

echo Schritt 4/5: Aenderungen committen...
git add .
git commit -m "Test: GitHub Pages deployment for accessibility check"

echo Schritt 5/5: Branch pushen...
git push origin %BRANCH_NAME%

echo.
echo Test-Deployment erfolgreich erstellt!
echo.
echo ========================================================
echo NAECHSTE SCHRITTE:
echo ========================================================
echo.
echo 1. Aktivieren Sie GitHub Pages in den Repository-Settings:
echo    https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik/settings/pages
echo.
echo 2. Waehlen Sie folgende Einstellungen:
echo    Source: Deploy from a branch
echo    Branch: %BRANCH_NAME%
echo    Folder: / (root)
echo.
echo 3. Klicken Sie 'Save'
echo.
echo 4. Warten Sie 1-2 Minuten und testen Sie die URL:
echo    https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/
echo.
echo ========================================================
echo.
echo Falls die Seite erreichbar ist: GitHub Pages funktioniert!
echo Falls nicht erreichbar: Siehe docs/deployment-alternatives.md
echo.
