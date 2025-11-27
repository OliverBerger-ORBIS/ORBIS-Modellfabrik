/**
 * Central Icon Key Registry for DSP Architecture visualization.
 * Maps semantic icon keys to actual file paths under assets/icons/.
 *
 * Use icon keys in configuration objects instead of direct filenames
 * to allow easy asset swapping without touching component logic.
 */

/**
 * Semantic icon key union type covering all supported icons.
 * Categories: logos, edge functions, devices, shopfloor systems, UX, business processes.
 */
export type IconKey =
  // Logos
  | 'logo-orbis'
  | 'logo-sap'
  | 'logo-azure'
  | 'logo-dsp'
  // Edge function icons
  | 'edge-connectivity'
  | 'edge-digital-twin'
  | 'edge-data-storage'
  | 'edge-analytics'
  | 'edge-workflow'
  | 'edge-network'
  // Device icons
  | 'device-plc'
  | 'device-robot-arm'
  | 'device-conveyor'
  | 'device-camera'
  | 'device-sensor'
  | 'device-printer'
  // Shopfloor system icons
  | 'shopfloor-systems'
  | 'shopfloor-mes'
  | 'shopfloor-scada'
  | 'shopfloor-aps'
  | 'shopfloor-warehouse'
  // UX icons
  | 'ux-dashboard'
  | 'ux-monitor'
  // Business process icons
  | 'bp-sap-shopfloor'
  | 'bp-cloud-apps'
  | 'bp-analytics'
  | 'bp-data-lake'
  | 'bp-business-process';

/**
 * Configuration for function icons displayed inside containers.
 */
export interface FunctionIconConfig {
  iconKey: IconKey;
  size: number;
}

/**
 * Central mapping from IconKey to asset file paths.
 * All paths are relative to the public folder root.
 */
export const ICON_MAP: Record<IconKey, string> = {
  // Logos
  'logo-orbis': 'shopfloor/ORBIS_logo_RGB.svg',
  'logo-sap': 'details/dsp/sap.svg',
  'logo-azure': 'details/dsp/azure.svg',
  'logo-dsp': 'shopfloor/ORBIS_logo_RGB.svg',

  // Edge function icons
  'edge-connectivity': 'details/dsp/network.svg',
  'edge-digital-twin': 'details/dsp/digital-twin.svg',
  'edge-data-storage': 'details/dsp/database.svg',
  'edge-analytics': 'details/dsp/dashboard.svg',
  'edge-workflow': 'details/dsp/workflow.svg',
  'edge-network': 'details/dsp/network.svg',

  // Device icons
  'device-plc': 'shopfloor/information-technology.svg',
  'device-robot-arm': 'shopfloor/robot-arm.svg',
  'device-conveyor': 'shopfloor/conveyor.svg',
  'device-camera': 'shopfloor/ai-assistant.svg',
  'device-sensor': 'shopfloor/information-technology.svg',
  'device-printer': 'shopfloor/information-technology.svg',

  // Shopfloor system icons
  'shopfloor-systems': 'shopfloor/factory.svg',
  'shopfloor-mes': 'shopfloor/information-technology.svg',
  'shopfloor-scada': 'shopfloor/information-technology.svg',
  'shopfloor-aps': 'shopfloor/order-tracking.svg',
  'shopfloor-warehouse': 'shopfloor/warehouse.svg',

  // UX icons
  'ux-dashboard': 'details/orbis/dashboard.svg',
  'ux-monitor': 'details/orbis/work.svg',

  // Business process icons
  'bp-sap-shopfloor': 'details/dsp/sap.svg',
  'bp-cloud-apps': 'details/dsp/cloud-computing.svg',
  'bp-analytics': 'details/dsp/dashboard.svg',
  'bp-data-lake': 'details/dsp/data-lake.svg',
  'bp-business-process': 'details/orbis/workflow_1.svg',
};

/**
 * Resolves an IconKey to its full asset path.
 * Returns a fallback path if the key is not found.
 *
 * @param key - The semantic icon key to resolve
 * @returns The resolved asset path (without leading slash)
 */
export function getIconPath(key: IconKey | undefined | null): string {
  if (!key) {
    return 'shopfloor/question.svg';
  }
  const path = ICON_MAP[key];
  if (!path) {
    return 'shopfloor/question.svg';
  }
  // Ensure no leading slash for consistent usage
  return path.startsWith('/') ? path.slice(1) : path;
}
