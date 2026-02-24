/**
 * Collects the versions of the modules from the factsheet.json files in the current working directory and its subdirectories.
 * It is limited to 5 subdirectories deep.
 */
// eslint-disable-next-line @typescript-eslint/no-var-requires
const fs = require('fs');
// eslint-disable-next-line @typescript-eslint/no-var-requires
const path = require('path');

const versionsList = {};

function processFile(filePath) {
  const data = fs.readFileSync(filePath, 'utf8');
  const factsheet = JSON.parse(data);
  const seriesName = factsheet.typeSpecification.seriesName;
  const version = factsheet.version;
  versionsList[seriesName] = version;
}

function processDirectory(dirPath, maxdepth = undefined, depth = 1) {
  const files = fs.readdirSync(dirPath);
  for (const file of files) {
    const filePath = path.join(dirPath, file);
    const stats = fs.statSync(filePath);
    if (stats.isDirectory()) {
      if (file !== '.git' && file !== 'node_modules' && (!maxdepth || depth < maxdepth)) {
        processDirectory(filePath, maxdepth, depth + 1);
      }
    } else if (stats.isFile() && path.basename(file) === 'factsheet.json') {
      processFile(filePath);
    }
  }
}

// use the first parameter as the root directory if it is provided. If none is provided, show an error message and exit.
if (process.argv.length < 3) {
  console.error('Please provide the root directory to search as the first parameter.');
  process.exit(1);
}
//use the next parameter as maxdepth if it is provided
const maxdepth = process.argv.length > 3 ? parseInt(process.argv[3]) : undefined;
processDirectory(process.argv[2], maxdepth);

console.log(JSON.stringify(versionsList, null, 2));
