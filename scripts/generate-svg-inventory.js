/**
 * Generate a markdown inventory of SVG assets with inline previews.
 * Outputs to docs/svg-inventory.md and docs/svg-inventory.html (print-friendly).
 *
 * Sources scanned:
 * - osf/apps/osf-ui/src/assets/svg
 *
 * Filters out SVGs that are already documented in DSP_Architecture_Objects_Reference.md
 * Displays remaining SVGs in a tile-based layout grouped by directory.
 */

const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');

// Source directory
const SOURCE_ROOT = path.join(repoRoot, 'osf/apps/osf-ui/src/assets/svg');
const ASSET_PREFIX = 'assets/svg';

// Output files
const OUTPUT_FILE = path.join(repoRoot, 'docs/02-architecture/dsp-svg-inventory.md');

// Reference document that already documents some SVGs
const REFERENCE_DOC = path.join(
  repoRoot,
  'osf/apps/osf-ui/src/app/components/dsp-animation/configs/DSP_Architecture_Objects_Reference.md'
);

// SVGs already documented in DSP_Architecture_Objects_Reference.md
const DOCUMENTED_SVGS = new Set([
  'assets/svg/business/analytics-application.svg',
  'assets/svg/business/cloud-application.svg',
  'assets/svg/business/crm-application.svg',
  'assets/svg/business/data-lake-application.svg',
  'assets/svg/business/erp-application.svg',
  'assets/svg/business/mes-application.svg',
  'assets/svg/business/scm-application.svg',
  'assets/svg/dsp/architecture/dsp-edge-box.svg',
  'assets/svg/dsp/edge-components/edge-agent.svg',
  'assets/svg/dsp/edge-components/edge-app-server.svg',
  'assets/svg/dsp/edge-components/edge-database.svg',
  'assets/svg/dsp/edge-components/edge-disc.svg',
  'assets/svg/dsp/edge-components/edge-disi.svg',
  'assets/svg/dsp/edge-components/edge-event-bus.svg',
  'assets/svg/dsp/edge-components/edge-log-server.svg',
  'assets/svg/dsp/edge-components/edge-router.svg',
  'assets/svg/dsp/functions/edge-ai-enablement.svg',
  'assets/svg/dsp/functions/edge-analytics.svg',
  'assets/svg/dsp/functions/edge-autonomous-enterprise.svg',
  'assets/svg/dsp/functions/edge-best-of-breed.svg',
  'assets/svg/dsp/functions/edge-choreography.svg',
  'assets/svg/dsp/functions/edge-connectivity.svg',
  'assets/svg/dsp/functions/edge-digital-twin.svg',
  'assets/svg/dsp/functions/edge-event-driven.svg',
  'assets/svg/dsp/functions/edge-interoperability.svg',
  'assets/svg/dsp/functions/mc-governance.svg',
  'assets/svg/dsp/functions/mc-hierarchical-structure.svg',
  'assets/svg/dsp/functions/mc-orchestration.svg',
  'assets/svg/shopfloor/stations/aiqs-station.svg',
  'assets/svg/shopfloor/stations/chrg-station.svg',
  'assets/svg/shopfloor/stations/cnc-station.svg',
  'assets/svg/shopfloor/stations/conveyor-station.svg',
  'assets/svg/shopfloor/stations/destillation-station.svg',
  'assets/svg/shopfloor/stations/dps-station.svg',
  'assets/svg/shopfloor/stations/drill-station.svg',
  'assets/svg/shopfloor/stations/hbw-station.svg',
  'assets/svg/shopfloor/stations/hydraulic-station.svg',
  'assets/svg/shopfloor/stations/laser-station.svg',
  'assets/svg/shopfloor/stations/mill-station.svg',
  'assets/svg/shopfloor/stations/oven-station.svg',
  'assets/svg/shopfloor/stations/printer-3d-station.svg',
  'assets/svg/shopfloor/stations/pump-station.svg',
  'assets/svg/shopfloor/stations/robotic-arm-station.svg',
  'assets/svg/shopfloor/stations/weight-station.svg',
  'assets/svg/shopfloor/systems/agv-system.svg',
  'assets/svg/shopfloor/systems/any-system.svg',
  'assets/svg/shopfloor/systems/cargo-system.svg',
  'assets/svg/shopfloor/systems/factory-system.svg',
  'assets/svg/shopfloor/systems/industrial-process-system.svg',
  'assets/svg/shopfloor/systems/pump-system.svg',
  'assets/svg/shopfloor/systems/scada-system.svg',
  'assets/svg/shopfloor/systems/warehouse-system.svg',
]);

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
        const children = walk(abs, rel);
        if (children.length > 0) {
          nodes.push({
            type: 'dir',
            name: entry.name,
            children,
          });
        }
      } else if (entry.isFile() && entry.name.toLowerCase().endsWith('.svg')) {
        const relPath = `${assetPrefix}/${rel.join('/')}`;
        // Only include if not already documented
        if (!DOCUMENTED_SVGS.has(relPath)) {
          nodes.push({
            type: 'file',
            name: entry.name,
            relPath,
            absPath: abs,
            dirPath: relParts.join('/'),
          });
        }
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

function getDirName(dirPath) {
  const parts = dirPath.split('/');
  return parts[parts.length - 1] || 'root';
}

function renderTileGroup(dirPath, files) {
  const dirName = getDirName(dirPath);
  const relFromDoc = path
    .relative(path.dirname(OUTPUT_FILE), SOURCE_ROOT)
    .split(path.sep)
    .join('/');

  const tiles = files.map((file) => {
    const imgRelPath = path
      .relative(path.dirname(OUTPUT_FILE), file.absPath)
      .split(path.sep)
      .join('/');
    const fileName = file.name.replace('.svg', '');
    return `<div style="text-align: center; border: 1px solid #ddd; border-radius: 4px; padding: 12px;">
<img src="${imgRelPath}" alt="${file.name}" width="64" height="64" />
<div style="font-weight: 600; margin-top: 8px;">\`${fileName}\`</div>
<div style="font-size: 0.9em; color: #666;">${file.name}</div>
</div>`;
  });

  return [
    `### ${dirPath || 'Root'}`,
    '',
    `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 16px; margin: 16px 0;">`,
    '',
    ...tiles,
    '',
    '</div>',
    '',
  ];
}

function collectFilesByDir(node, dirPath = '', filesByDir = {}) {
  if (node.type === 'file') {
    const dir = dirPath || 'root';
    if (!filesByDir[dir]) {
      filesByDir[dir] = [];
    }
    filesByDir[dir].push(node);
  } else if (node.type === 'dir') {
    const newDirPath = dirPath ? `${dirPath}/${node.name}` : node.name;
    for (const child of node.children) {
      collectFilesByDir(child, newDirPath, filesByDir);
    }
  }
  return filesByDir;
}

function generate() {
  const sections = [];
  const now = new Date().toISOString();
  sections.push(
    '# DSP SVG Inventory',
    '',
    `_Generated: ${now}_`,
    '',
    'Diese Übersicht zeigt alle SVG-Assets, die **nicht** bereits in der [DSP Architecture Objects Reference](../../osf/apps/osf-ui/src/app/components/dsp-animation/configs/DSP_Architecture_Objects_Reference.md) dokumentiert sind.',
    '',
    '**Hinweis:** SVGs die bereits in der DSP Architecture Objects Reference dokumentiert sind, werden hier nicht angezeigt, um Redundanz zu vermeiden.',
    ''
  );

  if (!fs.existsSync(SOURCE_ROOT)) {
    sections.push(`## assets/svg`, '_not found_', '');
    fs.writeFileSync(OUTPUT_FILE, sections.join('\n'));
    console.log(`Wrote ${OUTPUT_FILE}`);
    return;
  }

  const tree = buildTree(SOURCE_ROOT, ASSET_PREFIX);
  const filesByDir = collectFilesByDir(tree);

  // Sort directories
  const sortedDirs = Object.keys(filesByDir).sort();

  if (sortedDirs.length === 0) {
    sections.push(
      '## Keine weiteren SVGs',
      '',
      'Alle SVGs sind bereits in der DSP Architecture Objects Reference dokumentiert.',
      ''
    );
  } else {
    sections.push('## Verfügbare SVG-Assets (nach Verzeichnissen gruppiert)', '');

    for (const dir of sortedDirs) {
      const files = filesByDir[dir].sort((a, b) => a.name.localeCompare(b.name));
      sections.push(...renderTileGroup(dir, files));
    }
  }

  fs.writeFileSync(OUTPUT_FILE, sections.join('\n'));
  console.log(`Wrote ${OUTPUT_FILE}`);
  console.log(`Total SVG files found: ${Object.values(filesByDir).flat().length}`);
  console.log(`Filtered out ${DOCUMENTED_SVGS.size} already documented SVGs`);
}

generate();
