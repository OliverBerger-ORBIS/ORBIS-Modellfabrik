#!/bin/bash
set -e

echo "======================================"
echo "Dev Environment Setup"
echo "======================================"
echo ""

# Detect OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    IS_WINDOWS=true
    echo "Detected: Windows"
else
    IS_WINDOWS=false
    echo "Detected: Linux/Unix"
fi

echo ""
echo "Step 1: Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "  ✗ Node.js not found"
    echo "  → Please install Node.js 18.x from https://nodejs.org/"
    exit 1
else
    NODE_VERSION=$(node --version)
    echo "  ✓ Node.js $NODE_VERSION"
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "  ✗ npm not found"
    exit 1
else
    NPM_VERSION=$(npm --version)
    echo "  ✓ npm $NPM_VERSION"
fi

# Check Docker (optional)
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "  ✓ Docker $DOCKER_VERSION"
    HAS_DOCKER=true
else
    echo "  ⚠ Docker not found (optional - needed for full stack)"
    HAS_DOCKER=false
fi

echo ""
echo "Step 2: Installing central-control dependencies..."
cd central-control
npm install
cd ..
echo "  ✓ Central control dependencies installed"

echo ""
echo "Step 3: Installing frontend dependencies..."
cd frontend
npm install
cd ..
echo "  ✓ Frontend dependencies installed"

echo ""
echo "======================================"
echo "✓ Dev Environment Setup Complete!"
echo "======================================"
echo ""
echo "Available commands:"
echo ""
echo "Backend (Central Control):"
echo "  cd central-control"
echo "  npm start              # Start with hot reload"
echo "  npm run start:debug    # Start with debugger"
echo "  npm test               # Run tests"
echo "  npm run build          # Build for production"
echo ""
echo "Frontend:"
echo "  cd frontend"
echo "  npm start              # Start dev server (http://localhost:4200)"
echo "  npm test               # Run tests"
echo "  npm run build          # Build for production"
echo ""

if [ "$HAS_DOCKER" = true ]; then
    echo "Docker Development:"
    echo "  npm run setup          # Setup development environment"
    echo "  npm start              # Start all containers"
    echo "  npm stop               # Stop all containers"
    echo "  npm run docker:build   # Build production images"
    echo ""
fi

echo "Quick start (no Docker):"
echo "  # Terminal 1:"
echo "  cd central-control && npm start"
echo ""
echo "  # Terminal 2:"
echo "  cd frontend && npm start"
echo ""
echo "Then open http://localhost:4200 in your browser"
echo ""
