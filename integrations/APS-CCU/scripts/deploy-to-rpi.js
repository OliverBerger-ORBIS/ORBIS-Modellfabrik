#!/usr/bin/env node

const { execSync, spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const RPI_HOST = process.argv[2];
const TAG = process.argv[3] || 'userdev';

// Parse services to deploy (if specified)
const requestedServices = process.argv.slice(4).map(s => s.toLowerCase());

const allImages = [
  { service: 'central', imageName: 'ff-ccu-armv7', filename: 'ff-ccu-armv7.tar', composeService: 'central-control' },
  { service: 'nodered', imageName: 'ff-nodered-armv7', filename: 'ff-nodered-armv7.tar', composeService: 'nodered' },
  { service: 'frontend', imageName: 'ff-frontend-armv7', filename: 'ff-frontend-armv7.tar', composeService: 'frontend' }
];

// Filter images based on requested services
const imagesToDeploy = requestedServices.length > 0
  ? allImages.filter(img => requestedServices.includes(img.service))
  : allImages;

const REMOTE_DIR = '/home/ff22/fischertechnik/ff-central-control-unit';
const COMPOSE_FILE = 'docker-compose-prod.yml';

if (!RPI_HOST) {
  console.error('Error: Raspberry Pi host required');
  console.error('Usage: npm run docker:deploy -- <rpi-host> [tag] [services...]');
  console.error('');
  console.error('Examples:');
  console.error('  npm run docker:deploy -- ff22@192.168.0.100');
  console.error('  npm run docker:deploy -- ff22@192.168.0.100 v1.3.0');
  console.error('  npm run docker:deploy -- ff22@192.168.0.100 userdev frontend');
  console.error('  npm run docker:deploy -- ff22@192.168.0.100 userdev central nodered');
  console.error('');
  console.error('Available services: central, nodered, frontend');
  console.error('');
  console.error('Note: You will be prompted for SSH password if not using SSH keys.');
  console.error('To avoid password prompts, set up SSH keys:');
  console.error('  ssh-keygen -t rsa -b 4096');
  console.error('  ssh-copy-id ff22@192.168.0.100');
  process.exit(1);
}

if (imagesToDeploy.length === 0) {
  console.error('Error: No valid services specified');
  console.error('Available services: central, nodered, frontend');
  process.exit(1);
}

console.log('======================================');
console.log('Deploy to Raspberry Pi');
console.log('======================================\n');
console.log(`Target: ${RPI_HOST}`);
console.log(`Tag: ${TAG}`);
if (requestedServices.length > 0) {
  console.log(`Services: ${imagesToDeploy.map(i => i.service).join(', ')}`);
}
console.log('Auth: SSH will prompt for password if keys not set up');
console.log('');

const OUTPUT_DIR = './docker-images';

// Helper function to run commands
function runCommand(command, description) {
  console.log(description);
  execSync(command, { stdio: 'inherit', shell: true });
}

// Step 1: Save images
console.log('Step 1: Saving Docker images...');
const serviceArgs = requestedServices.length > 0 ? ' ' + requestedServices.join(' ') : '';
try {
  execSync(`node scripts/save-images.js ${TAG} ${OUTPUT_DIR}${serviceArgs}`, { stdio: 'inherit' });
} catch (error) {
  console.error('Failed to save images');
  process.exit(1);
}

// Step 2: Copy to Raspberry Pi
console.log('\nStep 2: Copying files to Raspberry Pi...');
const filesToCopy = imagesToDeploy.map(img => path.join(OUTPUT_DIR, img.filename)).join(' ');

try {
  runCommand(`scp ${filesToCopy} ${RPI_HOST}:/tmp/`, '  Copying image files...');
  console.log('  ✓ Files copied successfully\n');
} catch (error) {
  console.error('Failed to copy files');
  process.exit(1);
}

// Step 3: Deploy on Raspberry Pi
console.log('Step 3: Deploying on Raspberry Pi...');

// Construct commands to run on RPi
const remoteCommands = [
  // 1. Load images
  'cd /tmp',
  ...imagesToDeploy.map(img => `docker load -i ${img.filename}`),
  ...imagesToDeploy.map(img => `rm -f ${img.filename}`),
  
  // 2. Go to project dir
  `cd ${REMOTE_DIR}`,

  // 3. Create backup of compose file if it doesn't exist
  `if [ ! -f ${COMPOSE_FILE}.bak ]; then cp ${COMPOSE_FILE} ${COMPOSE_FILE}.bak; fi`,
  
  // 4. Update services versions in compose file
  ...imagesToDeploy.map(img => `sed -i 's|image: ghcr.io/ommsolutions/${img.imageName}:.*|image: ghcr.io/ommsolutions/${img.imageName}:${TAG}|g' ${COMPOSE_FILE}`),
  
  // 6. Start services (detached)
  `docker compose -f ${COMPOSE_FILE} up -d`
].join(' && ');

try {
  runCommand(`ssh ${RPI_HOST} "${remoteCommands}"`, '  Executing remote deployment commands...');
  console.log('  ✓ Deployment commands executed successfully\n');
} catch (error) {
  console.error('Failed to deploy');
  process.exit(1);
}

console.log('======================================');
console.log('✓ Deployment completed successfully!');
console.log('======================================\n');
console.log('Services have been updated and restarted.');
console.log(`You can check the status with: ssh ${RPI_HOST} "cd ${REMOTE_DIR} && docker compose  -f ${COMPOSE_FILE} ps"`);
console.log('');
