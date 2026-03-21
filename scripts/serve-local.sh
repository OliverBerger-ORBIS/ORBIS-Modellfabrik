#!/bin/bash

# Script to build and serve the OSF Dashboard locally for testing (GitHub Pages layout)
# The build uses baseHref /ORBIS-Modellfabrik/, so we must serve from a parent dir
# that has ORBIS-Modellfabrik/ containing the build output.
# Usage: ./scripts/serve-local.sh [port]

set -e

PORT=${1:-4200}
BUILD_DIR="dist/apps/osf-ui/browser"
SERVE_ROOT="dist/apps/osf-ui/browser-gp"
BASE_PATH="ORBIS-Modellfabrik"

echo "🔨 Building OSF Dashboard for local testing..."
npm run build:github-pages

if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ Build failed: $BUILD_DIR not found"
    exit 1
fi

echo "📁 Restructuring for baseHref /$BASE_PATH/..."
rm -rf "$SERVE_ROOT"
mkdir -p "$SERVE_ROOT/$BASE_PATH"
cp -r "$BUILD_DIR"/* "$SERVE_ROOT/$BASE_PATH/"

echo "✅ Build complete!"
echo ""
echo "🚀 Starting local server on port $PORT..."
echo "📱 Open your browser at: http://localhost:$PORT/$BASE_PATH/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npx serve "$SERVE_ROOT" -p "$PORT"
