#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('======================================');
console.log('Starting Development Environment');
console.log('======================================\n');

// Check if setup has been run
const packagesExist = fs.existsSync(path.join(__dirname, '..', 'frontend', 'packages'));
const centralModulesExist = fs.existsSync(path.join(__dirname, '..', 'central-control', 'node_modules'));
const frontendModulesExist = fs.existsSync(path.join(__dirname, '..', 'frontend', 'node_modules'));

if (!packagesExist || !centralModulesExist || !frontendModulesExist) {
  console.log('⚠️  First time setup required\n');
  console.log('Running setup...\n');
  try {
    execSync('node scripts/setup.js', { stdio: 'inherit' });
  } catch (error) {
    console.error('\n❌ Setup failed');
    process.exit(1);
  }
  console.log('');
}

// Start Docker Compose
console.log('Starting Docker Compose services...\n');

const args = process.argv.slice(2);
const detached = args.includes('-d') || args.includes('--detached');
const hostArg = args.find(a => !a.startsWith('-')) || '192.168.0.100';

const isLocal = hostArg === 'local' || hostArg === 'localhost';
const factoryHost = isLocal ? 'localhost' : hostArg;

console.log(isLocal ? 'Using Local MQTT Broker' : `Using Factory Host: ${factoryHost}`);

// Update frontend environment
const envPath = path.join(__dirname, '..', 'frontend', 'src', 'environments', 'environment.ts');
if (fs.existsSync(envPath)) {
  let envContent = fs.readFileSync(envPath, 'utf8');
  envContent = envContent.replace(/mqttHost: '.*'/, `mqttHost: '${factoryHost}'`);
  fs.writeFileSync(envPath, envContent);
  console.log(`Updated frontend environment to use ${factoryHost}`);
}

if (!isLocal) {
  console.log('Stopping containers on Factory...');
  try {
    execSync(`ssh ff22@${factoryHost} "docker stop central-control-prod || true"`, { stdio: 'inherit' });
  } catch (e) {
    console.warn('Failed to stop containers on factory. Continuing...');
  }
  process.env.MQTT_URL = `mqtt://${factoryHost}`;
} 
try {
  const services = isLocal ? '' : 'frontend central-control';
  execSync(`docker compose up${detached ? ' -d' : ''} ${services}`, { stdio: 'inherit' });
} catch (error) {
  // User likely pressed Ctrl+C, which is normal
  console.log('\n\nServices stopped');
}
