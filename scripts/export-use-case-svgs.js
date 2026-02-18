#!/usr/bin/env node
/**
 * Export Use-Case SVG diagrams to assets/svg/use-cases/
 *
 * Requires: Puppeteer with Chrome.
 * Run: node scripts/export-use-case-svgs.js
 *
 * If Chrome is missing: npx puppeteer browsers install chrome
 *
 * If dist/ does not exist, the script builds osf-ui first.
 * Starts a static server, navigates to each Use-Case (Overview/Step 0),
 * extracts the SVG from the DOM, and saves to:
 *   - osf/apps/osf-ui/src/assets/svg/use-cases/
 *   - docs/assets/use-cases/uc-XX/ (für use-case-inventory.md)
 *
 * Referenced icons (DSP-Edge, MILL, DRILL etc.) are inlined as base64 data URIs
 * so the export works standalone (e.g. in Markdown, file://, GitHub).
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const repoRoot = path.resolve(__dirname, '..');
const distRoot = path.join(repoRoot, 'dist/apps/osf-ui/browser');
const svgAssetsRoot = path.join(repoRoot, 'osf/apps/osf-ui/src/assets/svg');
const outputDir = path.join(svgAssetsRoot, 'use-cases');
const docsAssetsRoot = path.join(repoRoot, 'docs/assets/use-cases');
const PORT = 4210;

/** Mapping: export name -> docs subfolder */
const USE_CASE_DOCS_FOLDERS = {
  'uc-01-track-trace-genealogy': 'uc-01',
  'uc-02-three-data-pools': 'uc-02',
  'uc-03-ai-lifecycle': 'uc-03',
  'uc-04-closed-loop-quality': 'uc-04',
  'uc-05-predictive-maintenance': 'uc-05',
  'uc-06-event-to-process-map': 'uc-06',
  'uc-07-process-optimization': 'uc-07',
};

/** Normalize image hrefs to ../path form (relative to use-cases/) */
function fixImageHrefs(html) {
  return html
    .replace(/href="\/?(?:en|de)\/assets\/svg\//g, 'href="../')
    .replace(/href="assets\/svg\//g, 'href="../');
}

/** Inline referenced SVG files as base64 data URIs for standalone viewing (Markdown, file://) */
function inlineSvgImages(html) {
  const hrefRe = /href="\.\.\/([^"]+\.svg)"/g;
  const seen = new Map();
  return html.replace(hrefRe, (_, relPath) => {
    const cacheKey = relPath;
    if (seen.has(cacheKey)) {
      return `href="${seen.get(cacheKey)}"`;
    }
    const fullPath = path.join(svgAssetsRoot, relPath);
    let dataUri = `../${relPath}`;
    try {
      if (fs.existsSync(fullPath)) {
        const content = fs.readFileSync(fullPath, 'utf8');
        const b64 = Buffer.from(content, 'utf8').toString('base64');
        dataUri = `data:image/svg+xml;base64,${b64}`;
        seen.set(cacheKey, dataUri);
      }
    } catch {
      /* keep original href on error */
    }
    return `href="${dataUri}"`;
  });
}

/** Inject CSS variable fallbacks for standalone SVG viewing (e.g. UC-06 uses var(--orbis-*)) */
const STANDALONE_CSS_FALLBACKS = `
/* Standalone SVG: ORBIS color palette fallbacks */
svg {
  --orbis-blue-strong: #154194;
  --orbis-blue-strong-rgb: 22, 65, 148;
  --orbis-grey-medium: #bbbcbc;
  --orbis-grey-light: #d0d0ce;
  --orbis-grey-medium-rgb: 187, 188, 188;
  --orbis-grey-light-rgb: 208, 208, 206;
  --orbis-nightblue: #16203b;
  --highlight-green-medium: #99cd57;
  --status-success-strong: #047857;
  --status-success-strong-rgb: 4, 120, 87;
  --status-warning-medium: #f59e0b;
  --status-error-strong: #dc2626;
  --status-error-strong-rgb: 220, 38, 38;
}`;

function injectCssFallbacks(html) {
  if (!html.includes('var(--orbis-') && !html.includes('var(--highlight-') && !html.includes('var(--status-')) {
    return html;
  }
  const styleOpen = html.indexOf('<style>');
  if (styleOpen === -1) return html;
  const insertAt = styleOpen + '<style>'.length;
  return html.slice(0, insertAt) + STANDALONE_CSS_FALLBACKS + html.slice(insertAt);
}

const USE_CASES = [
  { id: 'uc-01', route: 'track-trace-genealogy', name: 'uc-01-track-trace-genealogy' },
  { id: 'uc-02', route: 'three-data-pools', name: 'uc-02-three-data-pools' },
  { id: 'uc-03', route: 'ai-lifecycle', name: 'uc-03-ai-lifecycle' },
  { id: 'uc-04', route: 'closed-loop-quality', name: 'uc-04-closed-loop-quality' },
  { id: 'uc-05', route: 'predictive-maintenance', name: 'uc-05-predictive-maintenance' },
  { id: 'uc-06', route: 'interoperability', name: 'uc-06-event-to-process-map' },
  { id: 'uc-07', route: 'process-optimization', name: 'uc-07-process-optimization' },
];

function run(cmd, args, opts = {}) {
  return new Promise((resolve, reject) => {
    const proc = spawn(cmd, args, { cwd: repoRoot, stdio: 'inherit', ...opts });
    proc.on('close', (code) => (code === 0 ? resolve() : reject(new Error(`Exit ${code}`))));
  });
}

async function startServe() {
  const http = await import('http');
  const serveHandler = (await import('serve-handler')).default;
  const server = http.default.createServer((req, res) =>
    serveHandler(req, res, {
      public: distRoot,
      cleanUrls: false,
      rewrites: [
        { source: '/en', destination: '/en/index.html' },
        { source: '/en/**', destination: '/en/index.html' },
        { source: '/de', destination: '/de/index.html' },
        { source: '/de/**', destination: '/de/index.html' },
        { source: '/fr', destination: '/fr/index.html' },
        { source: '/fr/**', destination: '/fr/index.html' },
      ],
    })
  );
  server.listen(PORT);
  await new Promise((resolve) => setTimeout(resolve, 800));
  return { kill: () => server.close() };
}

async function ensurePuppeteerChrome() {
  const puppeteer = await import('puppeteer').catch(() => null);
  if (!puppeteer) {
    console.error('Missing puppeteer. Install with: npm install puppeteer --save-dev');
    process.exit(1);
  }
  try {
    return await puppeteer.default.launch({ headless: true });
  } catch (err) {
    const msg = err?.message || '';
    if (msg.includes('Could not find Chrome') || msg.includes('executable path')) {
      console.error('Puppeteer needs Chrome. Install with:');
      console.error('  npx puppeteer browsers install chrome');
      console.error('');
      process.exit(1);
    }
    throw err;
  }
}

async function exportWithPuppeteer() {
  const browser = await ensurePuppeteerChrome();
  fs.mkdirSync(outputDir, { recursive: true });

  const serveProc = await startServe();
  try {
    for (const uc of USE_CASES) {
      for (const locale of ['en', 'de']) {
        const suffix = locale === 'en' ? 'EN' : 'DE';
        const url = `http://localhost:${PORT}/${locale}/#/${locale}/dsp/use-case/${uc.route}`;
        console.log(`Exporting ${uc.id} (${locale})...`);

          const page = await browser.newPage();
          await page.setViewport({ width: 1920, height: 1080 });
          try {
            await page.goto(url, { waitUntil: 'networkidle0', timeout: 20000 });
            await page.waitForSelector('[class*="svg-wrapper"] svg, svg[id$="_root"]', { timeout: 10000 });
          } catch (e) {
            console.log(`  -> Timeout: ${uc.route}`);
            await page.close();
            continue;
          }

          const svgHtml = await page.evaluate(() => {
            const svg = document.querySelector('[class*="svg-wrapper"] svg') || document.querySelector('svg[id$="_root"]') || document.querySelector('svg');
            return svg ? svg.outerHTML : null;
          });

          if (svgHtml) {
            let processed = fixImageHrefs(svgHtml);
            processed = inlineSvgImages(processed);
            processed = injectCssFallbacks(processed);
            const outPath = path.join(outputDir, `${uc.name}-${suffix}.svg`);
            fs.writeFileSync(outPath, processed, 'utf8');
            console.log(`  -> ${path.relative(repoRoot, outPath)}`);
            // Kopie nach docs/assets/use-cases/uc-XX/ für use-case-inventory.md
            const docsFolder = USE_CASE_DOCS_FOLDERS[uc.name];
            if (docsFolder) {
              const docsDir = path.join(docsAssetsRoot, docsFolder);
              fs.mkdirSync(docsDir, { recursive: true });
              const docsPath = path.join(docsDir, `${uc.name}-${suffix}.svg`);
              fs.writeFileSync(docsPath, processed, 'utf8');
              console.log(`  -> ${path.relative(repoRoot, docsPath)}`);
            }
          } else {
            console.log(`  -> SVG not found`);
          }
          await page.close();
        }
    }
  } finally {
    serveProc.kill();
    await browser.close();
  }
}

async function main() {
  // Immer neu bauen, damit der Export die aktuellen UC-Änderungen erfasst
  console.log('Building osf-ui...');
  await run('npx', ['nx', 'build', 'osf-ui']);

  await exportWithPuppeteer();
  console.log('Done.');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
