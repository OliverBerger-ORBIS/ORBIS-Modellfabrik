#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

const REGISTRY = 'ghcr.io/ommsolutions';
const TAG = process.argv[2] || 'userdev';
const PLATFORM = 'linux/arm/v7';

// Parse services to build (if specified)
const requestedServices = process.argv.slice(3).map(s => s.toLowerCase());

const allImages = [
  { name: 'Central Control', service: 'central', dockerfile: 'central-control/Dockerfile', tag: 'ff-ccu-armv7' },
  { name: 'Node-RED', service: 'nodered', dockerfile: 'nodeRed/Dockerfile', tag: 'ff-nodered-armv7', context: './nodeRed' },
  { name: 'Frontend', service: 'frontend', dockerfile: 'frontend/Dockerfile', tag: 'ff-frontend-armv7' }
];

// Filter images based on requested services
const images = requestedServices.length > 0
  ? allImages.filter(img => requestedServices.includes(img.service))
  : allImages;

if (images.length === 0) {
  console.error('Error: No valid services specified');
  console.error('\nAvailable services: central, nodered, frontend');
  console.error('\nUsage:');
  console.error('  npm run docker:build [tag] [services...]');
  console.error('\nExamples:');
  console.error('  npm run docker:build                     # Build all with userdev tag');
  console.error('  npm run docker:build userdev             # Build all with userdev tag');
  console.error('  npm run docker:build v1.4.0              # Build all with v1.4.0 tag');
  console.error('  npm run docker:build userdev frontend    # Build only frontend');
  console.error('  npm run docker:build userdev central nodered  # Build central and nodered');
  process.exit(1);
}

console.log('======================================');
console.log('Build Docker Images for Production');
console.log('======================================\n');
console.log(`Building for platform: ${PLATFORM}`);
console.log(`Tag: ${TAG}`);
if (requestedServices.length > 0) {
  console.log(`Services: ${images.map(i => i.service).join(', ')}`);
}
console.log('');

// Check if buildx is available
try {
  execSync('docker buildx version', { stdio: 'pipe' });
} catch (error) {
  console.error('Error: docker buildx is not available');
  console.error('Please install Docker Desktop or enable buildx');
  process.exit(1);
}

images.forEach((image, index) => {
  console.log(`Step ${index + 1}: Building ${image.name} image...`);
  
  const context = image.context || '.';
  const fullTag = `${REGISTRY}/${image.tag}:${TAG}`;
  
  try {
    execSync(
      `docker buildx build --no-cache --platform=${PLATFORM} -f ${image.dockerfile} -t ${fullTag} ${context}`,
      { stdio: 'inherit' }
    );
    console.log(`  ✓ Built ${fullTag}`);
    
    // Tag as latest if not already latest
    if (TAG !== 'latest') {
      execSync(`docker tag ${fullTag} ${REGISTRY}/${image.tag}:latest`, { stdio: 'inherit' });
      console.log(`  ✓ Tagged as ${REGISTRY}/${image.tag}:latest`);
    }
  } catch (error) {
    console.error(`  ✗ Failed to build ${image.name}`);
    process.exit(1);
  }
  console.log('');
});

console.log('======================================');
console.log('✓ All images built successfully!');
console.log('======================================\n');
console.log('Built images:');
images.forEach(img => console.log(`  - ${REGISTRY}/${img.tag}:${TAG}`));
console.log('');
console.log('Next steps:');
console.log('1. Save images to file:');
console.log(`   npm run docker:save -- ${TAG}`);
console.log('');
console.log('2. Deploy to Raspberry Pi:');
console.log(`   npm run docker:deploy -- <rpi-host> ${TAG}`);
console.log('');
