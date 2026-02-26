#!/usr/bin/env node

/**
 * Build OSF-UI Docker image for RPi (ARM) or local (AMD64).
 * Builds Angular app on host first (avoids QEMU/Node WebAssembly issues for ARM cross-build).
 * Usage: node scripts/build-osf-ui-docker.js [platform] [tag]
 *   platform: arm (default, for RPi) | amd64 (local test)
 *   tag: image tag (default: latest)
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const platformArg = process.argv[2] || 'arm';
const tag = process.argv[3] || 'latest';

const PLATFORMS = {
  arm: 'linux/arm64',  // 64-bit ARM for RPi 4/5 (aarch64)
  armv7: 'linux/arm/v7',  // 32-bit for older RPi
  amd64: 'linux/amd64',
};

const platform = PLATFORMS[platformArg] || PLATFORMS.arm;
const imageName = 'orbis-osf-ui';

const rootDir = path.resolve(__dirname, '..');
const dockerfilePath = path.join(rootDir, 'deploy', 'osf-ui', 'Dockerfile');
const distPath = path.join(rootDir, 'dist', 'apps', 'osf-ui', 'browser');

console.log('======================================');
console.log('Build OSF-UI Docker Image');
console.log('======================================\n');
console.log(`Platform: ${platform} (${platformArg})`);
console.log(`Tag: ${imageName}:${tag}`);
console.log(`Context: ${rootDir}`);
console.log('');

try {
  execSync('docker buildx version', { stdio: 'pipe' });
} catch {
  console.error('Error: docker buildx not available');
  process.exit(1);
}

// Step 1: Build Angular app on host (fast, native - avoids QEMU/WASM issues)
console.log('Step 1/2: Building OSF-UI on host...\n');
try {
  execSync('npm run update-version && npx nx reset && npx nx build osf-ui --configuration=production', {
    cwd: rootDir,
    stdio: 'inherit',
  });
} catch {
  console.error('\n✗ Host build failed');
  process.exit(1);
}

if (!fs.existsSync(distPath)) {
  console.error(`\n✗ Expected build output at ${distPath}`);
  process.exit(1);
}

// Step 2: Build Docker image (nginx only - no Node, works for any platform)
console.log('\nStep 2/2: Building Docker image...\n');
try {
  execSync(
    `docker buildx build --platform=${platform} -f ${dockerfilePath} -t ${imageName}:${tag} ${rootDir}`,
    { stdio: 'inherit' }
  );
  console.log(`\n✓ Built ${imageName}:${tag}`);
  console.log('\nNext steps:');
  if (platformArg === 'arm' || platformArg === 'arm64') {
    console.log('  1. Save: docker save orbis-osf-ui:latest -o deploy/osf-ui/docker-images/osf-ui-arm64.tar');
    console.log('  2. Deploy: scp to RPi, docker load');
  } else {
    console.log('  Run locally: docker compose -f deploy/docker-compose.osf-ui.yml up -d');
    console.log('  Access: http://localhost:8080');
  }
} catch (error) {
  console.error('\n✗ Build failed');
  process.exit(1);
}
