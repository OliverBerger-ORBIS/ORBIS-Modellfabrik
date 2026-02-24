const fse = require("fs-extra");
const path = require("path");

const srcDir = path.join("..", "common");
const destDir = path.join(".", "projects", "futurefactory", "src", "common");

try {
  fse.copySync(srcDir, destDir, { overwrite: true });
  console.log(`Copied "${srcDir}" to "${destDir}" successfully!`);
} catch (err) {
  console.error(err);
}
