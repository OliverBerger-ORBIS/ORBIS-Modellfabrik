#!/usr/bin/env node
/**
 * Build and serve OSF Dashboard locally with GitHub Pages layout.
 * The build uses baseHref /ORBIS-Modellfabrik/, so we copy the output
 * into ORBIS-Modellfabrik/ subdirectory so assets and chunks resolve correctly.
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const BUILD_DIR = path.join(__dirname, '../dist/apps/osf-ui/browser');
const SERVE_ROOT = path.join(__dirname, '../dist/apps/osf-ui/browser-gp');
const BASE_PATH = 'ORBIS-Modellfabrik';
const PORT = process.env.PORT || 4200;

function copyRecursive(src, dest) {
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    for (const entry of fs.readdirSync(src)) {
      copyRecursive(path.join(src, entry), path.join(dest, entry));
    }
  } else {
    fs.copyFileSync(src, dest);
  }
}

console.log('🔨 Building OSF Dashboard for local testing...');
execSync('npm run build:github-pages', { stdio: 'inherit' });

if (!fs.existsSync(BUILD_DIR)) {
  console.error('❌ Build failed:', BUILD_DIR, 'not found');
  process.exit(1);
}

console.log('📁 Restructuring for baseHref /' + BASE_PATH + '/...');
if (fs.existsSync(SERVE_ROOT)) {
  fs.rmSync(SERVE_ROOT, { recursive: true });
}
const targetDir = path.join(SERVE_ROOT, BASE_PATH);
fs.mkdirSync(targetDir, { recursive: true });
copyRecursive(BUILD_DIR, targetDir);

console.log('✅ Build complete!');
console.log('');
console.log('🚀 Starting local server on port', PORT, '...');
console.log('📱 Open your browser at: http://localhost:' + PORT + '/' + BASE_PATH + '/');
console.log('');
console.log('Press Ctrl+C to stop the server');
console.log('');

execSync(`npx serve "${SERVE_ROOT}" -p ${PORT}`, { stdio: 'inherit' });
