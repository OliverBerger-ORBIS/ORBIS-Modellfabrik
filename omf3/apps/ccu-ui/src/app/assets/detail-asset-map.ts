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
  ORBIS_PHASE_1: 'details/orbis/data-lake.svg',
  ORBIS_PHASE_2: 'details/orbis/semantic.svg',
  ORBIS_PHASE_3: 'details/orbis/dashboard.svg',
  ORBIS_PHASE_4: 'details/orbis/workflow_1.svg',
  ORBIS_PHASE_5: 'details/orbis/ai.svg',
  ORBIS_FALLBACK: 'details/orbis/stack.svg',

  DSP_LAYER_CLOUD: 'details/dsp/database.svg',
  DSP_LAYER_EDGE: 'details/orbis/distributed.svg',
  DSP_LAYER_SHOPFLOOR: 'details/orbis/work.svg',
  DSP_FALLBACK: 'details/dsp/workflow.svg',
  DSP_EDGE_DATABASE: 'details/dsp/database.svg',
  DSP_EDGE_DIGITAL_TWIN: 'details/dsp/digital-twin.svg',
  DSP_EDGE_WORKFLOW: 'details/dsp/workflow.svg',
  DSP_EDGE_NETWORK: 'details/dsp/network.svg',
  DSP_BUSINESS_SAP: 'details/dsp/sap.svg',
  DSP_BUSINESS_CLOUD: 'details/dsp/cloud-computing.svg',
  DSP_BUSINESS_ANALYTICS: 'details/dsp/dashboard.svg',
  DSP_BUSINESS_DATA_LAKE: 'details/dsp/data-lake.svg',

  ORBIS_USECASE_AGGREGATION: 'details/orbis/consolidate.svg',
  ORBIS_USECASE_TRACKTRACE: 'details/orbis/integration.svg',
  ORBIS_USECASE_PREDICTIVE: 'details/orbis/ai-algorithm.svg',
  ORBIS_USECASE_OPTIMIZATION: 'details/orbis/database-management.svg',
} as const;

/**
 * Asset path map with resolved paths (includes baseHref).
 * Paths are resolved at module load time, which works for most cases.
 * For runtime resolution, use getAssetPath() function.
 */
export const DETAIL_ASSET_MAP: Record<keyof typeof ASSET_PATHS, string> = {
  ORBIS_PHASE_1: getAssetPath(ASSET_PATHS.ORBIS_PHASE_1),
  ORBIS_PHASE_2: getAssetPath(ASSET_PATHS.ORBIS_PHASE_2),
  ORBIS_PHASE_3: getAssetPath(ASSET_PATHS.ORBIS_PHASE_3),
  ORBIS_PHASE_4: getAssetPath(ASSET_PATHS.ORBIS_PHASE_4),
  ORBIS_PHASE_5: getAssetPath(ASSET_PATHS.ORBIS_PHASE_5),
  ORBIS_FALLBACK: getAssetPath(ASSET_PATHS.ORBIS_FALLBACK),

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

  ORBIS_USECASE_AGGREGATION: getAssetPath(ASSET_PATHS.ORBIS_USECASE_AGGREGATION),
  ORBIS_USECASE_TRACKTRACE: getAssetPath(ASSET_PATHS.ORBIS_USECASE_TRACKTRACE),
  ORBIS_USECASE_PREDICTIVE: getAssetPath(ASSET_PATHS.ORBIS_USECASE_PREDICTIVE),
  ORBIS_USECASE_OPTIMIZATION: getAssetPath(ASSET_PATHS.ORBIS_USECASE_OPTIMIZATION),
};

