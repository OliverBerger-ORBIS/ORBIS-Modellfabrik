#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const REGISTRY = 'ghcr.io/ommsolutions';
const TAG = process.argv[2] || 'userdev';
const OUTPUT_DIR = process.argv[3] || './docker-images';

// Parse services to save (if specified)
const requestedServices = process.argv.slice(4).map(s => s.toLowerCase());

const allImages = [
  { service: 'central', tag: 'ff-ccu-armv7', filename: 'ff-ccu-armv7.tar' },
  { service: 'nodered', tag: 'ff-nodered-armv7', filename: 'ff-nodered-armv7.tar' },
  { service: 'frontend', tag: 'ff-frontend-armv7', filename: 'ff-frontend-armv7.tar' }
];

// Filter images based on requested services
const images = requestedServices.length > 0
  ? allImages.filter(img => requestedServices.includes(img.service))
  : allImages;

if (images.length === 0) {
  console.error('Error: No valid services specified');
  console.error('\nAvailable services: central, nodered, frontend');
  console.error('\nUsage:');
  console.error('  npm run docker:save [tag] [output-dir] [services...]');
  console.error('\nExamples:');
  console.error('  npm run docker:save                              # Save all');
  console.error('  npm run docker:save userdev                      # Save all with userdev tag');
  console.error('  npm run docker:save userdev ./images             # Save to ./images');
  console.error('  npm run docker:save userdev ./images frontend    # Save only frontend');
  process.exit(1);
}

console.log('======================================');
console.log('Save Docker Images to Files');
console.log('======================================\n');
console.log(`Tag: ${TAG}`);
console.log(`Output directory: ${OUTPUT_DIR}`);
if (requestedServices.length > 0) {
  console.log(`Services: ${images.map(i => i.service).join(', ')}`);
}
console.log('');

// Create output directory
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  console.log(`✓ Created directory: ${OUTPUT_DIR}\n`);
}

images.forEach((image, index) => {
  console.log(`Step ${index + 1}: Saving ${image.tag}:${TAG}...`);
  
  const fullTag = `${REGISTRY}/${image.tag}:${TAG}`;
  const outputPath = path.join(OUTPUT_DIR, image.filename);
  
  try {
    execSync(`docker save ${fullTag} -o ${outputPath}`, { stdio: 'inherit' });
    const stats = fs.statSync(outputPath);
    const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
    console.log(`  ✓ Saved to ${outputPath} (${sizeMB} MB)`);
  } catch (error) {
    console.error(`  ✗ Failed to save ${image.tag}`);
    process.exit(1);
  }
  console.log('');
});

console.log('======================================');
console.log('✓ All images saved successfully!');
console.log('======================================\n');
console.log(`Saved images in: ${OUTPUT_DIR}`);
console.log('');
console.log('Next steps:');
console.log('1. Copy images to Raspberry Pi:');
console.log(`   scp ${OUTPUT_DIR}/*.tar pi@<rpi-host>:/tmp/`);
console.log('');
console.log('2. Or use the deploy script:');
console.log(`   npm run docker:deploy -- <rpi-host> ${TAG}`);
console.log('');
