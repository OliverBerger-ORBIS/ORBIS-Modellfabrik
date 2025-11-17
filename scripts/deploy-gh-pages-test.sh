#!/bin/bash

# Script to create a test deployment on GitHub Pages
# This allows testing if GitHub Pages is accessible before full setup
#
# Usage:
#   ./deploy-gh-pages-test.sh          # Interactive mode (asks before updating)
#   ./deploy-gh-pages-test.sh --force  # Force mode (auto-updates without asking)
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
            echo "  --force, -f     Automatically update existing branch without asking"
            echo "  --version, -v   Create a versioned branch with timestamp (gh-pages-test-YYYYMMDD-HHMMSS)"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0              # Interactive mode"
            echo "  $0 --force      # Force update"
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
WORKTREE_DIR=".gh-pages-worktree"

echo "🧪 GitHub Pages Test-Deployment"
echo "================================"
echo ""
echo "Dieser Script erstellt einen Test-Deployment um zu prüfen,"
echo "ob GitHub Pages von Ihren Firmenrechnern aus erreichbar ist."
echo ""

# Save current branch
CURRENT_BRANCH=$(git branch --show-current)

# Check if branch already exists (only for non-versioned mode)
if [ "$VERSION_MODE" = false ] && git show-ref --quiet refs/heads/$BRANCH_NAME; then
    echo "⚠️  Branch '$BRANCH_NAME' existiert bereits."
    
    if [ "$FORCE_MODE" = true ]; then
        echo "🔄 Aktualisiere Branch '$BRANCH_NAME' (Force-Mode)..."
    else
        echo "Möchten Sie ihn aktualisieren? (y/n)"
        read -r response
        if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo "❌ Abbruch. Verwenden Sie:"
            echo "   - '$0 --force' um automatisch zu aktualisieren"
            echo "   - '$0 --version' um einen versionierten Branch zu erstellen"
            exit 1
        fi
    fi
fi

echo "🔨 Schritt 1/6: Build erstellen..."
npm run build:github-pages

if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ Build fehlgeschlagen: $BUILD_DIR nicht gefunden"
    exit 1
fi

echo "✅ Build erfolgreich"
echo ""

echo "🌿 Schritt 2/6: Worktree für Deployment vorbereiten..."
# Remove worktree directory if it exists
if [ -d "$WORKTREE_DIR" ]; then
    echo "🧹 Räume altes Worktree auf..."
    git worktree remove -f "$WORKTREE_DIR" 2>/dev/null || rm -rf "$WORKTREE_DIR"
fi

# Create orphan branch if it doesn't exist
if ! git show-ref --quiet refs/heads/$BRANCH_NAME; then
    echo "📝 Erstelle neuen Branch '$BRANCH_NAME'..."
    # Create a temporary worktree with orphan branch
    git worktree add --detach "$WORKTREE_DIR"
    cd "$WORKTREE_DIR"
    git checkout --orphan $BRANCH_NAME
    git rm -rf . 2>/dev/null || true
    # Create an initial empty commit so the branch exists
    git commit --allow-empty -m "Initial commit for GitHub Pages deployment"
    cd ..
    git worktree remove -f "$WORKTREE_DIR"
    rm -rf "$WORKTREE_DIR"
fi

# Create worktree for the deployment branch
git worktree add "$WORKTREE_DIR" $BRANCH_NAME

echo "📁 Schritt 3/6: Build-Dateien in Worktree kopieren..."
# Clear worktree (but keep .git)
cd "$WORKTREE_DIR"
find . -maxdepth 1 ! -name '.' ! -name '..' ! -name '.git' -exec rm -rf {} +

# Copy build files
cp -r "../$BUILD_DIR/"* .

# Create .nojekyll file (important for Angular)
touch .nojekyll

echo "📦 Schritt 4/6: Änderungen committen..."
git add .
if git diff --staged --quiet; then
    echo "ℹ️  Keine Änderungen zu committen"
else
    git commit -m "Deploy: GitHub Pages deployment for accessibility check"
fi

echo "🚀 Schritt 5/6: Branch pushen..."
git push -f origin $BRANCH_NAME

# Return to project root
cd ..

echo "🧹 Schritt 6/6: Worktree aufräumen..."
git worktree remove "$WORKTREE_DIR"
rm -rf "$WORKTREE_DIR"

# Return to original branch
git checkout "$CURRENT_BRANCH"

echo ""
echo "✅ Test-Deployment erfolgreich erstellt!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 NÄCHSTE SCHRITTE:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
if git show-ref --quiet refs/remotes/origin/$BRANCH_NAME; then
    if [ "$VERSION_MODE" = false ]; then
        echo "ℹ️  Branch '$BRANCH_NAME' wurde aktualisiert."
        echo "   GitHub Pages Settings bleiben erhalten."
    else
        echo "1. Aktivieren Sie GitHub Pages in den Repository-Settings:"
        echo "   👉 https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik/settings/pages"
        echo ""
        echo "2. Wählen Sie folgende Einstellungen:"
        echo "   Source: Deploy from a branch"
        echo "   Branch: $BRANCH_NAME"
        echo "   Folder: / (root)"
        echo ""
        echo "3. Klicken Sie 'Save'"
    fi
else
    echo "1. Aktivieren Sie GitHub Pages in den Repository-Settings:"
    echo "   👉 https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik/settings/pages"
    echo ""
    echo "2. Wählen Sie folgende Einstellungen:"
    echo "   Source: Deploy from a branch"
    echo "   Branch: $BRANCH_NAME"
    echo "   Folder: / (root)"
    echo ""
    echo "3. Klicken Sie 'Save'"
fi
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
    echo "   - '$0 --force' um automatisch zu aktualisieren"
    echo "   - '$0 --version' um einen versionierten Branch zu erstellen"
fi
echo ""
echo "🔒 Sicherheitshinweis: Dieses Script verwendet git worktree, um"
echo "   sicher mit dem Deployment-Branch zu arbeiten, ohne Ihre"
echo "   Projekt-Dateien zu beeinflussen."
echo ""
