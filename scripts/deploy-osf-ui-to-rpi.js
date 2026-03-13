#!/usr/bin/env node

/**
 * Deploy OSF-UI Docker image to Raspberry Pi.
 * Verhält sich wie CCU-Deploy: Build (immer frisch), Save, Transfer, Load,
 * Compose aktualisieren (sed Image-Tag), Services neu starten.
 *
 * Single Source of Truth: package.json → version.ts (via update-version beim Build)
 *
 * ⚠️ PLATFORM: RPi mit CCU-Stack nutzt 32-bit (armv7) – wie ff-ccu-armv7.
 *    NICHT arm/arm64 verwenden → Container crasht (Exit 159). Siehe DR-23.
 *
 * Usage: node scripts/deploy-osf-ui-to-rpi.js <rpi-host> [tag]
 *   rpi-host: e.g. ff22@192.168.0.100
 *   tag: optional, default = package.json version (z.B. 0.8.8)
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const RPI_HOST = process.argv[2];
const rootDir = path.resolve(__dirname, '..');
const packageJsonPath = path.join(rootDir, 'package.json');

// Version: package.json (Single Source of Truth) oder optionaler Override
let TAG = process.argv[3];
if (!TAG) {
  const pkg = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  TAG = pkg.version;
}

const IMAGE_NAME = 'orbis-osf-ui';
const REMOTE_DIR = '/home/ff22/fischertechnik/ff-central-control-unit';
const COMPOSE_FILE = 'docker-compose-prod.yml';
// DR-23: RPi mit CCU (ff-*-armv7) = 32-bit. arm64 führt zu Crash.
const PLATFORM = process.env.OSF_UI_RPI_PLATFORM || 'armv7';
const TAR_FILENAME = `osf-ui-${PLATFORM === 'armv7' ? 'arm32' : 'arm64'}-${TAG.replace(/[^a-z0-9.-]/gi, '-')}.tar`;
const DEPLOY_DIR = path.join(rootDir, 'deploy', 'osf-ui', 'docker-images');

if (!RPI_HOST) {
  console.error('Error: Raspberry Pi host required');
  console.error('Usage: node scripts/deploy-osf-ui-to-rpi.js <rpi-host> [tag]');
  console.error('');
  console.error('Examples:');
  console.error('  npm run docker:osf-ui:deploy -- ff22@192.168.0.100');
  console.error('  npm run docker:osf-ui:deploy -- ff22@192.168.0.100 0.8.8');
  console.error('');
  console.error('Platform: armv7 (default, 32-bit wie CCU) | OSF_UI_RPI_PLATFORM=arm für 64-bit RPi');
  console.error('Tag default = package.json version (Single Source of Truth)');
  process.exit(1);
}

console.log('======================================');
console.log('Deploy OSF-UI to Raspberry Pi');
console.log('======================================\n');
console.log(`Target: ${RPI_HOST}`);
console.log(`Version/Tag: ${TAG} (from package.json)`);
console.log(`Platform: ${PLATFORM} (32-bit RPi, wie CCU)`);
console.log('');

// Step 1: Immer bauen (frisches Image mit aktueller Version)
console.log('Step 1: Building OSF-UI (update-version + Angular + Docker)...\n');
try {
  execSync(`node scripts/build-osf-ui-docker.js ${PLATFORM} ${TAG}`, { cwd: rootDir, stdio: 'inherit' });
} catch {
  console.error('\n✗ Build failed');
  process.exit(1);
}

// Step 2: Save to tar
if (!fs.existsSync(DEPLOY_DIR)) {
  fs.mkdirSync(DEPLOY_DIR, { recursive: true });
}
const tarPath = path.join(DEPLOY_DIR, TAR_FILENAME);
console.log('\nStep 2: Saving image to file...');
execSync(`docker save ${IMAGE_NAME}:${TAG} -o ${tarPath}`, { stdio: 'inherit' });
console.log(`  ✓ Saved to ${tarPath}\n`);

// Step 3: SCP to RPi
console.log('Step 3: Transferring to Raspberry Pi...');
execSync(`scp ${tarPath} ${RPI_HOST}:/tmp/${TAR_FILENAME}`, { stdio: 'inherit' });
console.log('  ✓ Transferred\n');

// Step 4: Load + Update Compose + Restart (wie CCU-Deploy)
console.log('Step 4: Deploying on Raspberry Pi (load, sed, compose up)...');
const remoteCommands = [
  `docker load -i /tmp/${TAR_FILENAME}`,
  `rm -f /tmp/${TAR_FILENAME}`,
  `cd ${REMOTE_DIR}`,
  `sed -i 's|image: ${IMAGE_NAME}:.*|image: ${IMAGE_NAME}:${TAG}|g' ${COMPOSE_FILE}`,
  `docker compose -f ${COMPOSE_FILE} up -d`,
].join(' && ');

try {
  execSync(`ssh ${RPI_HOST} "${remoteCommands}"`, { stdio: 'inherit' });
  console.log('  ✓ Deployment complete\n');
} catch {
  console.error('\n✗ Remote deployment failed');
  process.exit(1);
}

console.log('======================================');
console.log('✓ OSF-UI deployed successfully!');
console.log('======================================');
console.log(`\nVersion: ${TAG}`);
console.log(`Access: http://192.168.0.100:8080 (or <rpi-ip>:8080)`);
console.log('');
console.log('Verify: ssh ' + RPI_HOST + ' "docker ps | grep osf-ui"');
console.log('');
