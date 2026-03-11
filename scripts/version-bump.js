#!/usr/bin/env node
/**
 * Version Bump – Single Command für Release
 * 
 * Nutzung: npm run version:bump -- 0.8.8
 * 
 * Macht:
 * 1. package.json "version" aktualisieren
 * 2. update-ui-version.js ausführen → version.ts, VERSION
 * 
 * Single Source of Truth: package.json
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const rootDir = path.resolve(__dirname, '..');
const packagePath = path.join(rootDir, 'package.json');

const newVersion = process.argv[2] || process.env.NEW_VERSION;
if (!newVersion || !/^\d+\.\d+\.\d+(-[a-z0-9.]+)?$/i.test(newVersion)) {
  console.error('Verwendung: npm run version:bump -- 0.8.8');
  console.error('Oder: NEW_VERSION=0.8.8 npm run version:bump');
  process.exit(1);
}

const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
const oldVersion = pkg.version;
pkg.version = newVersion;
fs.writeFileSync(packagePath, JSON.stringify(pkg, null, 2) + '\n', 'utf8');
console.log(`package.json: ${oldVersion} → ${newVersion}`);

execSync('node scripts/update-ui-version.js', { cwd: rootDir, stdio: 'inherit' });
console.log('✓ version.ts und VERSION aktualisiert. Nächster Schritt: CHANGELOG Eintrag, commit, push.');
