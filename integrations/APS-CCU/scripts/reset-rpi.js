#!/usr/bin/env node

const { execSync } = require('child_process');

const RPI_HOST = process.argv[2];
const REMOTE_DIR = '/home/ff22/fischertechnik/ff-central-control-unit';
const COMPOSE_FILE = 'docker-compose-prod.yml';

if (!RPI_HOST) {
  console.error('Error: Raspberry Pi host required');
  console.error('Usage: npm run docker:reset -- <rpi-host>');
  console.error('');
  console.error('Examples:');
  console.error('  npm run docker:reset -- ff22@192.168.0.100');
  process.exit(1);
}

console.log('======================================');
console.log('Reset Raspberry Pi to Original State');
console.log('======================================\n');
console.log(`Target: ${RPI_HOST}`);

// Build commands to reset:
// 1. Restore docker-compose file from backup if exists
// 2. Restart services
const remoteCommands = [
  `cd ${REMOTE_DIR}`,
  `if [ -f ${COMPOSE_FILE}.bak ]; then cp ${COMPOSE_FILE}.bak ${COMPOSE_FILE} && rm ${COMPOSE_FILE}.bak; echo "Restored from backup"; else echo "No backup found, assuming file is original"; fi`,
  `docker compose -f ${COMPOSE_FILE} up -d --remove-orphans`
].join(' && ');

function runCommand(command, description) {
  console.log(description);
  try {
    execSync(command, { stdio: 'inherit', shell: true });
    return true;
  } catch (error) {
    console.error(`Failed: ${description}`);
    return false;
  }
}

console.log('Resetting configuration and restarting services...');
if (runCommand(`ssh ${RPI_HOST} "${remoteCommands}"`, '  Executing remote reset commands...')) {
  console.log('\n  ✓ Reset commands executed successfully');
  console.log('Services have been reset to the version specified in the repository.');
} else {
  console.error('\n  ✗ Failed to reset services');
  process.exit(1);
}
