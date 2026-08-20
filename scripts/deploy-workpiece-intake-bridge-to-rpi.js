#!/usr/bin/env node
/**
 * Build armv7 workpiece-intake-bridge image, save, scp, docker load on RPi,
 * refresh compose service from repo APS compose, up -d.
 *
 * Usage: node scripts/deploy-workpiece-intake-bridge-to-rpi.js [ff22@192.168.0.100] [tag]
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const RPI_HOST = process.argv[2] || 'ff22@192.168.0.100';
const TAG = process.argv[3] || '1.0.0';
const rootDir = path.resolve(__dirname, '..');
const IMAGE = `orbis-workpiece-intake-bridge:${TAG}`;
const TAR = `orbis-workpiece-intake-bridge-arm32-${TAG.replace(/[^a-z0-9.-]/gi, '-')}.tar`;
const deployDir = path.join(rootDir, 'deploy', 'osf-workpiece-intake-bridge', 'docker-images');
const tarPath = path.join(deployDir, TAR);
const bridgeDir = path.join(rootDir, 'osf-workpiece-intake-bridge');
const composeSrc = path.join(rootDir, 'integrations', 'APS-CCU', 'docker-compose-prod.yml');
const remoteDir = '/home/ff22/fischertechnik/ff-central-control-unit';

function run(cmd, opts = {}) {
  console.log(`\n$ ${cmd}`);
  execSync(cmd, { stdio: 'inherit', cwd: rootDir, ...opts });
}

fs.mkdirSync(deployDir, { recursive: true });

console.log('======================================');
console.log('Deploy workpiece intake bridge → RPi');
console.log(`Target: ${RPI_HOST}  Image: ${IMAGE}`);
console.log('======================================');

run(
  `docker buildx build --platform linux/arm/v7 -t ${IMAGE} -f osf-workpiece-intake-bridge/Dockerfile osf-workpiece-intake-bridge --load`
);
run(`docker save ${IMAGE} -o "${tarPath}"`);
run(`scp "${tarPath}" ${RPI_HOST}:/tmp/${TAR}`);
run(`scp "${composeSrc}" ${RPI_HOST}:${remoteDir}/docker-compose-prod.yml`);
run(
  `ssh ${RPI_HOST} "docker load -i /tmp/${TAR} && cd ${remoteDir} && docker compose -f docker-compose-prod.yml up -d osf-workpiece-intake-bridge && docker ps --filter name=osf-workpiece-intake-bridge --format 'table {{.Names}}\\t{{.Image}}\\t{{.Status}}'"`
);

console.log('\n✓ Bridge deploy finished');
console.log('Verify: ssh … "docker logs osf-workpiece-intake-bridge-prod --tail 30"');
console.log('Topic: osf/workpiece/intake');
