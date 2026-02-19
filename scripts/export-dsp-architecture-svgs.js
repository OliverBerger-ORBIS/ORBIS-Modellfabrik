#!/usr/bin/env node
/**
 * Export DSP Architecture SVG diagrams to docs/assets/architecture/
 *
 * Requires: Puppeteer with Chrome.
 * Run: node scripts/export-dsp-architecture-svgs.js
 *
 * If Chrome is missing: npx puppeteer browsers install chrome
 *
 * If dist/ does not exist, the script builds osf-ui first.
 * Starts a static server, navigates to DSP FMF page with viewMode + step=-1 (full overview),
 * extracts the SVG from the DOM, and saves to:
 *   - docs/assets/architecture/ (für dsp-architecture-inventory.md)
 *
 * Referenced icons are inlined as base64 data URIs for standalone viewing.
 * Uses FMF (Fischertechnik Modellfabrik) config as default customer.
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const repoRoot = path.resolve(__dirname, '..');
const distRoot = path.join(repoRoot, 'dist/apps/osf-ui/browser');
const svgAssetsRoot = path.join(repoRoot, 'osf/apps/osf-ui/src/assets/svg');
const outputDir = path.join(repoRoot, 'docs/assets/architecture');
const PORT = 4211;

const DSP_VIEWS = [
  { id: 'functional', name: 'dsp-architecture-functional' },
  { id: 'component', name: 'dsp-architecture-component' },
  { id: 'deployment', name: 'dsp-architecture-deployment' },
];

/** Normalize image hrefs for standalone viewing - handle various build/locale path formats */
function fixImageHrefs(html) {
  const replacers = [
    [/href="(?:https?:\/\/[^"]*\/)?(?:[a-z]+\/)?assets\/svg\//g, 'href="../'],
    [/href="\/?(?:en|de|fr)\/assets\/svg\//g, 'href="../'],
    [/href="\/assets\/svg\//g, 'href="../'],
    [/href="assets\/svg\//g, 'href="../'],
  ];
  let out = html;
  for (const [re, replacement] of replacers) {
    out = out.replace(re, replacement);
  }
  return out;
}

const PUBLIC_SVG_ROOT = path.join(repoRoot, 'osf/apps/osf-ui/public/assets/svg');

/** Resolve SVG path – check src/assets first, then public/assets */
function resolveSvgPath(relPath) {
  const srcPath = path.join(svgAssetsRoot, relPath);
  if (fs.existsSync(srcPath)) return srcPath;
  const pubPath = path.join(PUBLIC_SVG_ROOT, relPath);
  if (fs.existsSync(pubPath)) return pubPath;
  return null;
}

/** Inline referenced SVG files as base64 data URIs */
function inlineSvgImages(html) {
  const hrefRe = /href="\.\.\/([^"]+\.svg)"/g;
  const seen = new Map();
  return html.replace(hrefRe, (_, relPath) => {
    const cacheKey = relPath;
    if (seen.has(cacheKey)) {
      return `href="${seen.get(cacheKey)}"`;
    }
    const fullPath = resolveSvgPath(relPath);
    let dataUri = `../${relPath}`;
    try {
      if (fullPath) {
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

const STANDALONE_CSS_FALLBACKS = `
/* Standalone SVG: ORBIS color palette fallbacks */
svg {
  --orbis-blue-strong: #154194;
  --orbis-blue-medium: #5071af;
  --orbis-blue-light: #8aa0ca;
  --orbis-blue-strong-rgb: 22, 65, 148;
  --orbis-blue-medium-rgb: 80, 113, 175;
  --orbis-blue-light-rgb: 138, 160, 202;
  --orbis-grey-medium: #bbbcbc;
  --orbis-grey-light: #d0d0ce;
  --orbis-grey-medium-rgb: 187, 188, 188;
  --orbis-grey-light-rgb: 208, 208, 206;
  --orbis-nightblue: #16203b;
  --neutral-lightgrey: #e5e5e5;
  --highlight-green-strong: #64a70b;
  --highlight-green-strong-rgb: 100, 167, 11;
  --highlight-green-medium: #99cd57;
  --microsoft-orange-medium: #ff8c00;
  --status-success-strong: #047857;
  --status-success-strong-rgb: 4, 120, 87;
  --status-warning-medium: #f59e0b;
  --status-error-strong: #dc2626;
  --status-error-strong-rgb: 220, 38, 38;
  --solution-petrol-strong: #0d5c5c;
  --solution-petrol-medium: #1a7f7f;
  --solution-petrol-light: #e6f2f2;
}
.step-overlay .step-overlay__title,
.step-overlay .step-overlay__description {
  fill: #ffffff !important;
}`;

/** Sanitize for standalone viewing: add xmlns, strip Angular artifacts, add width/height */
function sanitizeForStandalone(html) {
  let out = html
    .replace(/\s_ngcontent-[^=]*="[^"]*"/g, '')
    .replace(/\s_nghost-[^=]*="[^"]*"/g, '')
    .replace(/<!---->/g, '');
  if (!/xmlns="http:\/\/www\.w3\.org\/2000\/svg"/.test(out)) {
    out = out.replace(/<svg(?=\s|>)/, '<svg xmlns="http://www.w3.org/2000/svg"');
  }
  const vb = out.match(/viewBox="([^"]+)"/);
  if (vb && !/^\s*width=/.test(out)) {
    const [, coords] = vb;
    const [, , w, h] = coords.split(/\s+/);
    if (w && h) {
      out = out.replace(/<svg([^>]*)>/, `<svg$1 width="${w}" height="${h}">`);
    }
  }
  return out;
}

function injectCssFallbacks(html) {
  if (!html.includes('var(--orbis-') && !html.includes('var(--highlight-') && !html.includes('var(--neutral-')) {
    return html;
  }
  const styleOpen = html.indexOf('<style>');
  if (styleOpen === -1) {
    // Insert <style> as first child of <svg> – must not break the opening tag.
    // Replace <svg ...> with <svg ...><style>...</style> to keep viewBox etc.
    return html.replace(/<svg([^>]*)>/, '<svg$1><style>' + STANDALONE_CSS_FALLBACKS + '</style>');
  }
  const insertAt = styleOpen + '<style>'.length;
  return html.slice(0, insertAt) + STANDALONE_CSS_FALLBACKS + html.slice(insertAt);
}

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
    for (const view of DSP_VIEWS) {
      const url = `http://localhost:${PORT}/en/#/en/dsp/customer/fmf?viewMode=${view.id}&step=-1`;
      console.log(`Exporting ${view.name}...`);

      const page = await browser.newPage();
      await page.setViewport({ width: 1200, height: 1140 });
      try {
        await page.goto(url, { waitUntil: 'networkidle0', timeout: 20000 });
        await page.waitForSelector('.dsp-architecture svg, .diagram-svg', { timeout: 10000 });
        await new Promise((r) => setTimeout(r, 1500));
      } catch (e) {
        console.log(`  -> Timeout: ${view.id}`);
        await page.close();
        continue;
      }

      const svgHtml = await page.evaluate(() => {
        const svg =
          document.querySelector('.dsp-architecture__diagram-wrapper svg') ||
          document.querySelector('.dsp-architecture svg') ||
          document.querySelector('svg.diagram-svg') ||
          document.querySelector('svg');
        return svg ? svg.outerHTML : null;
      });

      if (svgHtml) {
        let processed = fixImageHrefs(svgHtml);
        processed = inlineSvgImages(processed);
        processed = injectCssFallbacks(processed);
        processed = sanitizeForStandalone(processed);
        // Replace step overlay rgba(var(...)) with concrete ORBIS green for standalone viewers
        processed = processed.replace(
          /fill="rgba\(var\(--highlight-green-strong-rgb\)[^)]*\)"/g,
          'fill="rgba(100, 167, 11, 0.95)"'
        );
        // Replace semi-transparent layer backgrounds with opaque colors (avoids checkered display in standalone viewers)
        processed = processed.replace(
          /fill="rgba\(\s*207\s*,\s*230\s*,\s*255\s*,\s*0\.5\s*\)"/g,
          'fill="#e7f2ff"'
        );
        processed = processed.replace(
          /fill="rgba\(\s*241\s*,\s*243\s*,\s*247\s*,\s*0\.8\s*\)"/g,
          'fill="#f6f7f9"'
        );
        const outPath = path.join(outputDir, `${view.name}.svg`);
        fs.writeFileSync(outPath, processed, 'utf8');
        console.log(`  -> ${path.relative(repoRoot, outPath)}`);
      } else {
        console.log(`  -> SVG not found`);
      }
      await page.close();
    }
  } finally {
    serveProc.kill();
    await browser.close();
  }
}

async function main() {
  console.log('Building osf-ui...');
  await run('npx', ['nx', 'build', 'osf-ui']);

  await exportWithPuppeteer();
  console.log('Done.');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
