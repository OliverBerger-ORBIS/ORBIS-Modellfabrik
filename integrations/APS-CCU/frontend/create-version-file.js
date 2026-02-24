const packageJSON = require("./package");
const fs = require("node:fs");
const { join } = require("node:path");
const { execSync } = require("node:child_process");

const projectOutputPath = join(
  __dirname,
  "projects/futurefactory/assets/version.json"
);
const appOutputPath = join(__dirname, "src/assets/version.json");

// Get git info with fallback to timestamp if git is not available
let commitHash = "unknown";
let commitDate = new Date().toISOString();

try {
  commitHash = execSync("git rev-parse --short HEAD", { stdio: ['pipe', 'pipe', 'ignore'] }).toString().trim();
  commitDate = execSync("git log -1 --format=%cd", { stdio: ['pipe', 'pipe', 'ignore'] }).toString().trim();
} catch (error) {
  // Git not available or not in a git repository - use timestamp
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  commitHash = `gitless-${timestamp}`;
  commitDate = new Date().toISOString();
}
const dependencies = Object.entries(packageJSON.dependencies).reduce(
  (acc, [key, value]) => {
    if (key.startsWith("@fischertechnik") || key.startsWith("@beemo")) {
      return Object.assign({ [key]: value }, acc);
    }
    return acc;
  },
  {}
);
const contents = {
  CCU: `${packageJSON.version}`,
  Frontend: `${packageJSON.version}`,
  "Node-RED": `${packageJSON.version}`,
  commitHash: `${process.env.CI_COMMIT_SHA ?? commitHash}`,
  commitDate: `${process.env.CI_COMMIT_DATE ?? commitDate}`,
  dependencies,
};

[projectOutputPath, appOutputPath].forEach((path) => {
  const fileContents = JSON.stringify(contents, null, 2);
  fs.writeFile(path, fileContents, "utf8", (err) => {
    if (err) {
      console.error(`'${path}' could not be injected:`, err);
      return;
    }
    console.log(`'${path}' has been injected:`, fileContents);
  });
});
