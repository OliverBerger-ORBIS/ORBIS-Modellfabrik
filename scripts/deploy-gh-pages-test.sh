#!/bin/bash

# Script to create a test deployment on GitHub Pages
# This allows testing if GitHub Pages is accessible before full setup

set -e

BRANCH_NAME="gh-pages-test"
BUILD_DIR="dist/apps/ccu-ui/browser"

echo "🧪 GitHub Pages Test-Deployment"
echo "================================"
echo ""
echo "Dieser Script erstellt einen Test-Deployment um zu prüfen,"
echo "ob GitHub Pages von Ihren Firmenrechnern aus erreichbar ist."
echo ""

# Check if gh-pages-test branch already exists
if git show-ref --quiet refs/heads/$BRANCH_NAME; then
    echo "⚠️  Branch '$BRANCH_NAME' existiert bereits."
    echo "Möchten Sie ihn löschen und neu erstellen? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "🗑️  Lösche Branch '$BRANCH_NAME'..."
        git branch -D $BRANCH_NAME 2>/dev/null || true
        git push origin --delete $BRANCH_NAME 2>/dev/null || true
    else
        echo "❌ Abbruch. Bitte löschen Sie den Branch manuell oder verwenden Sie einen anderen Namen."
        exit 1
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
echo "   🌐 https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Falls die Seite erreichbar ist: GitHub Pages funktioniert!"
echo "❌ Falls nicht erreichbar: Siehe docs/deployment-alternatives.md"
echo ""
echo "💡 Um zum ursprünglichen Branch zurückzukehren:"
echo "   git checkout $(git branch --show-current)"
echo ""
