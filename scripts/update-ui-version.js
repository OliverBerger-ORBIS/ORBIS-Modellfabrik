const fs = require('fs');
const path = require('path');

// Paths
const rootDir = path.resolve(__dirname, '..');
const packageJsonPath = path.join(rootDir, 'package.json');
const versionFilePath = path.join(rootDir, 'osf/apps/osf-ui/src/environments/version.ts');

try {
    // 1. Read package.json
    if (!fs.existsSync(packageJsonPath)) {
        console.error('Error: package.json not found at ' + packageJsonPath);
        process.exit(1);
    }
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const version = packageJson.version;

    console.log(`Current version in package.json: ${version}`);

    // 2. Prepare content for version.ts
    const buildDate = new Date().toISOString();
    const fileContent = `export const VERSION = {
  full: '${version}',
  build: 'prod',
  buildDate: '${buildDate}',
};
`;

    // 3. Write version.ts
    // Ensure directory exists (it should, but good practice)
    const dir = path.dirname(versionFilePath);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(versionFilePath, fileContent, 'utf8');
    console.log(`Successfully updated ${versionFilePath}`);

    // 4. Write VERSION file for Python (setup.py/pyproject.toml)
    const versionFilePathPy = path.join(rootDir, 'VERSION');
    fs.writeFileSync(versionFilePathPy, version + '\n', 'utf8');
    console.log(`Successfully updated ${versionFilePathPy}`);

    console.log(`- Version: ${version}`);
    console.log(`- Date: ${buildDate}`);

} catch (error) {
    console.error('Failed to update version.ts:', error);
    process.exit(1);
}
