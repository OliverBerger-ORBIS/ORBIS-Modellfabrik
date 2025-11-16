#!/bin/bash

# Script to create a test deployment on GitHub Pages
# This allows testing if GitHub Pages is accessible before full setup
#
# Usage:
#   ./deploy-gh-pages-test.sh          # Interactive mode (asks before deleting)
#   ./deploy-gh-pages-test.sh --force  # Force mode (auto-deletes existing branch)
#   ./deploy-gh-pages-test.sh --version # Versioned mode (creates timestamped branch)

set -e

# Parse command line arguments
FORCE_MODE=false
VERSION_MODE=false

for arg in "$@"; do
    case $arg in
        --force|-f)
            FORCE_MODE=true
            shift
            ;;
        --version|-v)
            VERSION_MODE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force, -f     Automatically delete existing branch without asking"
            echo "  --version, -v   Create a versioned branch with timestamp (gh-pages-test-YYYYMMDD-HHMMSS)"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0              # Interactive mode"
            echo "  $0 --force      # Force delete and recreate"
            echo "  $0 --version    # Create versioned branch"
            exit 0
            ;;
    esac
done

# Set branch name based on mode
if [ "$VERSION_MODE" = true ]; then
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    BRANCH_NAME="gh-pages-test-${TIMESTAMP}"
    echo "📅 Verwende versionierten Branch: $BRANCH_NAME"
else
    BRANCH_NAME="gh-pages-test"
fi

BUILD_DIR="dist/apps/ccu-ui/browser"

echo "🧪 GitHub Pages Test-Deployment"
echo "================================"
echo ""
echo "Dieser Script erstellt einen Test-Deployment um zu prüfen,"
echo "ob GitHub Pages von Ihren Firmenrechnern aus erreichbar ist."
echo ""

# Check if branch already exists (only for non-versioned mode)
if [ "$VERSION_MODE" = false ] && git show-ref --quiet refs/heads/$BRANCH_NAME; then
    echo "⚠️  Branch '$BRANCH_NAME' existiert bereits."
    
    if [ "$FORCE_MODE" = true ]; then
        echo "🗑️  Lösche Branch '$BRANCH_NAME' (Force-Mode)..."
        git branch -D $BRANCH_NAME 2>/dev/null || true
        git push origin --delete $BRANCH_NAME 2>/dev/null || true
    else
        echo "Möchten Sie ihn löschen und neu erstellen? (y/n)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo "🗑️  Lösche Branch '$BRANCH_NAME'..."
            git branch -D $BRANCH_NAME 2>/dev/null || true
            git push origin --delete $BRANCH_NAME 2>/dev/null || true
        else
            echo "❌ Abbruch. Verwenden Sie:"
            echo "   - '$0 --force' um automatisch zu löschen"
            echo "   - '$0 --version' um einen versionierten Branch zu erstellen"
            exit 1
        fi
    fi
fi

echo "🔨 Schritt 1/5: Build erstellen..."
npm run build:github-pages

if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ Build fehlgeschlagen: $BUILD_DIR nicht gefunden"
    exit 1
fi

echo "✅ Build erfolgreich"
echo ""

echo "🌿 Schritt 2/5: Testbranch erstellen..."
git checkout -b $BRANCH_NAME

echo "📁 Schritt 3/5: Build-Dateien kopieren..."
# Copy all files from build directory
cp -r $BUILD_DIR/* .

# Create .nojekyll file (important for Angular)
touch .nojekyll

echo "📦 Schritt 4/5: Änderungen committen..."
git add .
git commit -m "Test: GitHub Pages deployment for accessibility check"

echo "🚀 Schritt 5/5: Branch pushen..."
git push origin $BRANCH_NAME

echo ""
echo "✅ Test-Deployment erfolgreich erstellt!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 NÄCHSTE SCHRITTE:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Aktivieren Sie GitHub Pages in den Repository-Settings:"
echo "   👉 https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik/settings/pages"
echo ""
echo "2. Wählen Sie folgende Einstellungen:"
echo "   Source: Deploy from a branch"
echo "   Branch: $BRANCH_NAME"
echo "   Folder: / (root)"
echo ""
echo "3. Klicken Sie 'Save'"
echo ""
echo "4. Warten Sie 1-2 Minuten und testen Sie die URL:"
echo "   🌐 https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/#/en/overview"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Falls die Seite erreichbar ist: GitHub Pages funktioniert!"
echo "❌ Falls nicht erreichbar: Siehe docs/deployment-alternatives.md"
echo ""
if [ "$VERSION_MODE" = true ]; then
    echo "💡 Versionierter Branch erstellt: $BRANCH_NAME"
    echo "   Alte Branches können mit 'git branch -D <branch-name>' gelöscht werden"
else
    echo "💡 Nächstes Mal können Sie verwenden:"
    echo "   - '$0 --force' um automatisch zu löschen und neu zu erstellen"
    echo "   - '$0 --version' um einen versionierten Branch zu erstellen"
fi
echo ""
