/**
 * Central mapping for detail-view SVG assets (ORBIS & DSP).
 * Update the paths here when you swap SVGs in `public/details/...`.
 * 
 * Paths are relative (without leading '/') so Angular automatically combines
 * them with the baseHref when used in [src] bindings (e.g., '/ORBIS-Modellfabrik/' for GitHub Pages).
 * 
 * For runtime resolution, use getAssetPath() function below.
 */

/**
 * Get the base href from the document, falling back to '/'.
 * This ensures assets work correctly with baseHref configurations
 * (e.g., '/ORBIS-Modellfabrik/' for GitHub Pages).
 */
export function getBaseHref(): string {
  if (typeof document === 'undefined') {
    return '/';
  }
  
  // For GitHub Pages, detect and return the correct baseHref
  const isGitHubPages = typeof window !== 'undefined' && window.location.hostname === 'oliverberger-orbis.github.io';
  
  if (isGitHubPages) {
    return '/ORBIS-Modellfabrik/';
  }
  
  // For local development, try to read from <base> tag
  const baseTag = document.querySelector('base');
  if (baseTag) {
    const hrefAttr = baseTag.getAttribute('href');
    if (hrefAttr) {
      return hrefAttr.endsWith('/') ? hrefAttr : `${hrefAttr}/`;
    }
  }
  
  return '/';
}

/**
 * Resolve an asset path with the current baseHref at runtime.
 * Use this function when you need to resolve paths dynamically.
 * For static paths in templates, use relative paths (without leading '/') directly.
 */
export function getAssetPath(relativePath: string): string {
  const baseHref = getBaseHref();
  // Remove leading slash from relativePath if present
  const cleanPath = relativePath.startsWith('/') ? relativePath.slice(1) : relativePath;
  return `${baseHref}${cleanPath}`;
}

// Relative paths (without leading '/') - Angular will combine with baseHref automatically
// when used in [src] bindings. For runtime resolution, use getAssetPath().
const ASSET_PATHS = {
  DSP_PHASE_1: 'assets/svg/dsp/methodology/phase1-data-foundation.svg',
  DSP_PHASE_2: 'assets/svg/dsp/methodology/phase2-data-integration.svg',
  DSP_PHASE_3: 'assets/svg/dsp/methodology/phase3-advanced-analytics.svg',
  DSP_PHASE_4: 'assets/svg/dsp/methodology/phase4-automation-orchestration.svg',
  DSP_PHASE_5: 'assets/svg/dsp/methodology/phase5-autonomous-enterprise.svg',

  DSP_LAYER_CLOUD: 'assets/svg/dsp/extra/database.svg',
  DSP_LAYER_EDGE: 'assets/svg/dsp/architecture/dsp-edge-box.svg',
  DSP_LAYER_SHOPFLOOR: 'assets/svg/shopfloor/shared/order-tracking.svg',
  DSP_FALLBACK: 'assets/svg/dsp/extra/workflow.svg',
  DSP_EDGE_DATABASE: 'assets/svg/dsp/extra/database.svg',
  DSP_EDGE_DIGITAL_TWIN: 'assets/svg/dsp/extra/digital-twin.svg',
  DSP_EDGE_WORKFLOW: 'assets/svg/dsp/extra/workflow.svg',
  DSP_EDGE_NETWORK: 'assets/svg/dsp/extra/network.svg',
  DSP_BUSINESS_SAP: 'assets/svg/brand/sap-logo.svg',
  DSP_BUSINESS_CLOUD: 'assets/svg/dsp/extra/cloud-computing.svg',
  DSP_BUSINESS_ANALYTICS: 'assets/svg/dsp/extra/dashboard.svg',
  DSP_BUSINESS_DATA_LAKE: 'assets/svg/dsp/extra/data-lake.svg',

  DSP_USECASE_AGGREGATION: 'assets/svg/dsp/use-cases/use-case-data-aggregation.svg',
  DSP_USECASE_TRACKTRACE: 'assets/svg/dsp/use-cases/use-case-track-trace.svg',
  DSP_USECASE_PREDICTIVE: 'assets/svg/dsp/use-cases/use-case-predictive-maintenance.svg',
  DSP_USECASE_OPTIMIZATION: 'assets/svg/dsp/use-cases/use-case-process-optimization.svg',
} as const;

/**
 * Asset path map with resolved paths (includes baseHref).
 * Paths are resolved at module load time, which works for most cases.
 * For runtime resolution, use getAssetPath() function.
 */
export const DETAIL_ASSET_MAP: Record<keyof typeof ASSET_PATHS, string> = {
  DSP_PHASE_1: getAssetPath(ASSET_PATHS.DSP_PHASE_1),
  DSP_PHASE_2: getAssetPath(ASSET_PATHS.DSP_PHASE_2),
  DSP_PHASE_3: getAssetPath(ASSET_PATHS.DSP_PHASE_3),
  DSP_PHASE_4: getAssetPath(ASSET_PATHS.DSP_PHASE_4),
  DSP_PHASE_5: getAssetPath(ASSET_PATHS.DSP_PHASE_5),

  DSP_LAYER_CLOUD: getAssetPath(ASSET_PATHS.DSP_LAYER_CLOUD),
  DSP_LAYER_EDGE: getAssetPath(ASSET_PATHS.DSP_LAYER_EDGE),
  DSP_LAYER_SHOPFLOOR: getAssetPath(ASSET_PATHS.DSP_LAYER_SHOPFLOOR),
  DSP_FALLBACK: getAssetPath(ASSET_PATHS.DSP_FALLBACK),
  DSP_EDGE_DATABASE: getAssetPath(ASSET_PATHS.DSP_EDGE_DATABASE),
  DSP_EDGE_DIGITAL_TWIN: getAssetPath(ASSET_PATHS.DSP_EDGE_DIGITAL_TWIN),
  DSP_EDGE_WORKFLOW: getAssetPath(ASSET_PATHS.DSP_EDGE_WORKFLOW),
  DSP_EDGE_NETWORK: getAssetPath(ASSET_PATHS.DSP_EDGE_NETWORK),
  DSP_BUSINESS_SAP: getAssetPath(ASSET_PATHS.DSP_BUSINESS_SAP),
  DSP_BUSINESS_CLOUD: getAssetPath(ASSET_PATHS.DSP_BUSINESS_CLOUD),
  DSP_BUSINESS_ANALYTICS: getAssetPath(ASSET_PATHS.DSP_BUSINESS_ANALYTICS),
  DSP_BUSINESS_DATA_LAKE: getAssetPath(ASSET_PATHS.DSP_BUSINESS_DATA_LAKE),

  DSP_USECASE_AGGREGATION: getAssetPath(ASSET_PATHS.DSP_USECASE_AGGREGATION),
  DSP_USECASE_TRACKTRACE: getAssetPath(ASSET_PATHS.DSP_USECASE_TRACKTRACE),
  DSP_USECASE_PREDICTIVE: getAssetPath(ASSET_PATHS.DSP_USECASE_PREDICTIVE),
  DSP_USECASE_OPTIMIZATION: getAssetPath(ASSET_PATHS.DSP_USECASE_OPTIMIZATION),
};

