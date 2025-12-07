/**
 * Generate a markdown inventory of SVG assets with inline previews.
 * Outputs to docs/svg-inventory.md and docs/svg-inventory.html (print-friendly).
 *
 * Sources scanned:
 * - omf3/apps/ccu-ui/public/assets/svg (only)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const repoRoot = path.resolve(__dirname, '..');

// Scan only the served assets to avoid duplicates (public is copied verbatim).
const SOURCES = [
  {
    label: 'public/assets/svg',
    root: path.join(repoRoot, 'omf3/apps/ccu-ui/public/assets/svg'),
    assetPrefix: 'assets/svg',
  },
];

const OUTPUT_FILE = path.join(repoRoot, 'docs/svg-inventory.md');
const OUTPUT_HTML_FILE = path.join(repoRoot, 'docs/svg-inventory.html');
const PREVIEW_SIZE = 32;

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
          absPath: abs,
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

function renderTree(node, prefix = '') {
  if (node.type === 'file') {
    // Inline preview (relative path from docs/svg-inventory.md)
    const relFromDoc = path
      .relative(path.dirname(OUTPUT_FILE), node.absPath)
      .split(path.sep)
      .join('/');
    const preview = `<img src="${relFromDoc}" alt="${node.name}" width="${PREVIEW_SIZE}" height="${PREVIEW_SIZE}" />`;

    return [`${prefix}- ${node.name} — \`${node.relPath}\`<br>${prefix}  ${preview}`];
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

  const htmlSections = [];
  htmlSections.push(
    '<!doctype html>',
    '<html>',
    '<head>',
    '<meta charset="utf-8" />',
    '<title>SVG Inventory</title>',
    '<style>',
    'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 24px; color: #1f2937; }',
    'details { margin-bottom: 16px; }',
    'summary { font-weight: 600; cursor: pointer; }',
    'ul { list-style: none; padding-left: 16px; }',
    'li { margin: 6px 0; }',
    '.file { display: flex; align-items: center; gap: 8px; }',
    '.file img { border: 1px solid #e5e7eb; padding: 2px; background: #fff; }',
    '.path { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; color: #4b5563; }',
    '</style>',
    '</head>',
    '<body>',
    `<h1>SVG Inventory</h1>`,
    `<p><em>Generated: ${now}</em></p>`
  );

  for (const source of SOURCES) {
    if (!fs.existsSync(source.root)) {
      sections.push(`## ${source.label}`, '_not found_', '');
      continue;
    }
    const tree = buildTree(source.root, source.assetPrefix);
    const rendered = renderTree(tree);
    sections.push(
      `## ${source.label}`,
      '',
      '<details open>',
      `<summary>${source.label}</summary>`,
      '',
      ...rendered,
      '',
      '</details>',
      ''
    );

    htmlSections.push(
      `<h2>${source.label}</h2>`,
      '<details open>',
      `<summary>${source.label}</summary>`,
      renderHtmlList(tree.children),
      '</details>'
    );
  }

  fs.writeFileSync(OUTPUT_FILE, sections.join('\n'));
  htmlSections.push('</body>', '</html>');
  fs.writeFileSync(OUTPUT_HTML_FILE, htmlSections.join('\n'));
  console.log(`Wrote ${OUTPUT_FILE}`);
  console.log(`Wrote ${OUTPUT_HTML_FILE}`);
}

function renderHtmlList(children) {
  const items = children.map((child) => renderHtml(child)).join('\n');
  return `<ul>\n${items}\n</ul>`;
}

function renderHtml(node) {
  if (node.type === 'file') {
    const relFromDoc = path
      .relative(path.dirname(OUTPUT_FILE), node.absPath)
      .split(path.sep)
      .join('/');
    const preview = `<img src="${relFromDoc}" alt="${escapeHtml(node.name)}" width="${PREVIEW_SIZE}" height="${PREVIEW_SIZE}" />`;
    return `<li class="file"><span>${escapeHtml(node.name)}</span><span class="path">\`${escapeHtml(node.relPath)}\`</span>${preview}</li>`;
  }
  const childrenHtml = renderHtmlList(node.children);
  return `<li><details open><summary>${escapeHtml(node.name)}</summary>${childrenHtml}</details></li>`;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

generate();

