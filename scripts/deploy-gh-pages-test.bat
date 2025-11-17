@echo off
REM Script to create a test deployment on GitHub Pages
REM This allows testing if GitHub Pages is accessible before full setup

setlocal EnableDelayedExpansion

set BRANCH_NAME=gh-pages-test
set BUILD_DIR=dist\apps\ccu-ui\browser
set WORKTREE_DIR=.gh-pages-worktree

echo GitHub Pages Test-Deployment
echo ================================
echo.
echo Dieser Script erstellt einen Test-Deployment um zu pruefen,
echo ob GitHub Pages von Ihren Firmenrechnern aus erreichbar ist.
echo.

REM Save current branch
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i

REM Check if branch exists
git show-ref --quiet refs/heads/%BRANCH_NAME% 2>nul
if %errorlevel% equ 0 (
    echo Branch '%BRANCH_NAME%' existiert bereits.
    echo Moechten Sie ihn aktualisieren? (j/n)
    set /p response=
    if /i not "!response!"=="j" (
        echo Abbruch. Verwenden Sie den Linux-Script fuer mehr Optionen.
        exit /b 1
    )
)

echo Schritt 1/6: Build erstellen...
call npm run build:github-pages

if not exist "%BUILD_DIR%" (
    echo Build fehlgeschlagen: %BUILD_DIR% nicht gefunden
    exit /b 1
)

echo Build erfolgreich
echo.

echo Schritt 2/6: Worktree fuer Deployment vorbereiten...
REM Remove worktree directory if it exists
if exist "%WORKTREE_DIR%" (
    echo Raeume altes Worktree auf...
    git worktree remove -f "%WORKTREE_DIR%" 2>nul
    if exist "%WORKTREE_DIR%" rmdir /s /q "%WORKTREE_DIR%"
)

REM Create orphan branch if it doesn't exist
git show-ref --quiet refs/heads/%BRANCH_NAME% 2>nul
if %errorlevel% neq 0 (
    echo Erstelle neuen Branch '%BRANCH_NAME%'...
    git worktree add --detach "%WORKTREE_DIR%"
    cd "%WORKTREE_DIR%"
    git checkout --orphan %BRANCH_NAME%
    git rm -rf . 2>nul
    REM Create an initial empty commit so the branch exists (skip hooks)
    git commit --allow-empty --no-verify -m "Initial commit for GitHub Pages deployment"
    cd ..
    git worktree remove -f "%WORKTREE_DIR%"
    if exist "%WORKTREE_DIR%" rmdir /s /q "%WORKTREE_DIR%"
)

REM Create worktree for the deployment branch
git worktree add "%WORKTREE_DIR%" %BRANCH_NAME%

echo Schritt 3/6: Build-Dateien in Worktree kopieren...
cd "%WORKTREE_DIR%"

REM Clear worktree (but keep .git)
for /f "tokens=*" %%i in ('dir /b /a-d') do (
    if not "%%i"==".git" del /q "%%i"
)
for /f "tokens=*" %%i in ('dir /b /ad') do (
    if not "%%i"==".git" rmdir /s /q "%%i"
)

REM Copy build files
xcopy /E /I /Y "..\%BUILD_DIR%\*" .

REM Create .nojekyll file
type nul > .nojekyll

echo Schritt 4/6: Aenderungen committen...
git add .
git diff --staged --quiet
if %errorlevel% neq 0 (
    REM Skip pre-commit hooks for deployment commits (only build artifacts)
    git commit --no-verify -m "Deploy: GitHub Pages deployment for accessibility check"
) else (
    echo Keine Aenderungen zu committen
)

echo Schritt 5/6: Branch pushen...
git push -f origin %BRANCH_NAME%

REM Return to project root
cd ..

echo Schritt 6/6: Worktree aufraeumen...
git worktree remove "%WORKTREE_DIR%"
if exist "%WORKTREE_DIR%" rmdir /s /q "%WORKTREE_DIR%"

REM Return to original branch
git checkout "%CURRENT_BRANCH%"

echo.
echo Test-Deployment erfolgreich erstellt!
echo.
echo ========================================================
echo NAECHSTE SCHRITTE:
echo ========================================================
echo.
git show-ref --quiet refs/remotes/origin/%BRANCH_NAME% 2>nul
if %errorlevel% equ 0 (
    echo Branch '%BRANCH_NAME%' wurde aktualisiert.
    echo GitHub Pages Settings bleiben erhalten.
) else (
    echo 1. Aktivieren Sie GitHub Pages in den Repository-Settings:
    echo    https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik/settings/pages
    echo.
    echo 2. Waehlen Sie folgende Einstellungen:
    echo    Source: Deploy from a branch
    echo    Branch: %BRANCH_NAME%
    echo    Folder: / (root)
    echo.
    echo 3. Klicken Sie 'Save'
)
echo.
echo 4. Warten Sie 1-2 Minuten und testen Sie die URL:
echo    https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/#/en/overview
echo.
echo ========================================================
echo.
echo Falls die Seite erreichbar ist: GitHub Pages funktioniert!
echo Falls nicht erreichbar: Siehe docs/deployment-alternatives.md
echo.
echo Sicherheitshinweis: Dieses Script verwendet git worktree, um
echo sicher mit dem Deployment-Branch zu arbeiten, ohne Ihre
echo Projekt-Dateien zu beeinflussen.
echo.
