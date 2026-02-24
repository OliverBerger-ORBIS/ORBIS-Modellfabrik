#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('======================================');
console.log('Development Environment Setup');
console.log('======================================\n');

// Install root dependencies
console.log('Step 1: Installing root dependencies...');
try {
  execSync('npm install', { stdio: 'inherit' });
  console.log('✓ Root dependencies installed\n');
} catch (error) {
  console.error('Failed to install root dependencies');
  process.exit(1);
}

// Install central-control dependencies
console.log('Step 2: Installing central-control dependencies...');
try {
  execSync('cd central-control && npm install', { stdio: 'inherit', shell: true });
  console.log('✓ Central-control dependencies installed\n');
} catch (error) {
  console.error('Failed to install central-control dependencies');
  process.exit(1);
}

// Install frontend dependencies
console.log('Step 3: Installing frontend dependencies...');
try {
  execSync('cd frontend && npm install', { stdio: 'inherit', shell: true });
  console.log('✓ Frontend dependencies installed\n');
} catch (error) {
  console.error('Failed to install frontend dependencies');
  process.exit(1);
}

console.log('======================================');
console.log('✓ Development Environment Ready!');
console.log('======================================\n');
console.log('Available commands:');
console.log('  npm start                    - Start development containers');
console.log('  npm run build:frontend       - Build frontend');
console.log('  npm run build:central        - Build central-control');
console.log('  npm run docker:build         - Build Docker images');
console.log('  npm run docker:save          - Save images to files');
console.log('  npm run docker:deploy        - Deploy to Raspberry Pi');
console.log('');
console.log('Development workflow:');
console.log('  1. Connect to factory wi-fi');
console.log('  2. Start services: npm start');
console.log('  3. Frontend will be at http://localhost:4200');
console.log('  4. MQTT broker at 192.168.0.1:1883');
console.log('');
