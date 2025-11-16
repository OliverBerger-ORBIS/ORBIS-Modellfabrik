#!/bin/bash

# Script to build and serve the OMF3 Dashboard locally for testing
# Usage: ./scripts/serve-local.sh [port]

set -e

PORT=${1:-4200}
BUILD_DIR="dist/apps/ccu-ui/browser"

echo "🔨 Building OMF3 Dashboard for local testing..."
npm run build:netlify

if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ Build failed: $BUILD_DIR not found"
    exit 1
fi

echo "✅ Build complete!"
echo ""
echo "🚀 Starting local server on port $PORT..."
echo "📱 Open your browser at: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npx serve "$BUILD_DIR" -p "$PORT"
