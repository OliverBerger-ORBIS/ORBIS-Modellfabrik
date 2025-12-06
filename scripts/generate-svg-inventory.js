/**
 * Generate a markdown inventory of SVG assets with optional usage references.
 * Outputs to docs/svg-inventory.md.
 *
 * Sources scanned:
 * - omf3/apps/ccu-ui/public/assets/svg
 * - omf3/apps/ccu-ui/src/assets/svg
 *
 * Usage detection: searches for the asset path (`assets/svg/...`) in
 * `omf3/apps/ccu-ui/src` via ripgrep. This is best-effort and may miss
 * dynamic usages.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const repoRoot = path.resolve(__dirname, '..');

const SOURCES = [
  {
    label: 'public/assets/svg',
    root: path.join(repoRoot, 'omf3/apps/ccu-ui/public/assets/svg'),
    assetPrefix: 'assets/svg',
  },
  {
    label: 'src/assets/svg',
    root: path.join(repoRoot, 'omf3/apps/ccu-ui/src/assets/svg'),
    assetPrefix: 'assets/svg',
  },
];

const OUTPUT_FILE = path.join(repoRoot, 'docs/svg-inventory.md');

function readDirSafe(dir) {
  try {
    return fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return [];
  }
}

function buildTree(rootDir, assetPrefix) {
  function walk(currentAbs, relParts) {
    const entries = readDirSafe(currentAbs);
    const nodes = [];
    for (const entry of entries) {
      const abs = path.join(currentAbs, entry.name);
      const rel = relParts.concat(entry.name);
      if (entry.isDirectory()) {
        nodes.push({
          type: 'dir',
          name: entry.name,
          children: walk(abs, rel),
        });
      } else if (entry.isFile() && entry.name.toLowerCase().endsWith('.svg')) {
        const relPath = `${assetPrefix}/${rel.join('/')}`;
        nodes.push({
          type: 'file',
          name: entry.name,
          relPath,
        });
      }
    }
    return nodes.sort((a, b) => {
      if (a.type !== b.type) return a.type === 'dir' ? -1 : 1;
      return a.name.localeCompare(b.name);
    });
  }

  return {
    type: 'dir',
    name: path.basename(rootDir),
    children: walk(rootDir, []),
    rootLabel: assetPrefix,
  };
}

function findUsage(relAssetPath) {
  // Search in src/ for the asset path string
  const searchRoot = path.join(repoRoot, 'omf3/apps/ccu-ui/src');
  try {
    const cmd = `rg --no-heading --line-number --fixed-strings "${relAssetPath}" "${searchRoot}"`;
    const output = execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
    return output
      .trim()
      .split('\n')
      .filter(Boolean)
      .map((line) => line.trim());
  } catch {
    return [];
  }
}

function renderTree(node, prefix = '') {
  if (node.type === 'file') {
    const usage = findUsage(node.relPath);
    const usageText = usage.length
      ? ` _(uses: ${usage.join('; ')})_`
      : ' _(uses: none found)_';
    return [`${prefix}- ${node.name} — \`${node.relPath}\`${usageText}`];
  }

  const lines = [`${prefix}- ${node.name}`];
  const childPrefix = `${prefix}  `;
  for (const child of node.children) {
    lines.push(...renderTree(child, childPrefix));
  }
  return lines;
}

function generate() {
  const sections = [];
  const now = new Date().toISOString();
  sections.push('# SVG Inventory', '', `_Generated: ${now}_`, '');

  for (const source of SOURCES) {
    if (!fs.existsSync(source.root)) {
      sections.push(`## ${source.label}`, '_not found_', '');
      continue;
    }
    const tree = buildTree(source.root, source.assetPrefix);
    sections.push(`## ${source.label}`, '', ...renderTree(tree), '');
  }

  fs.writeFileSync(OUTPUT_FILE, sections.join('\n'));
  console.log(`Wrote ${OUTPUT_FILE}`);
}

generate();

