/**
 * Icon configuration for DSP Architecture Refactor component.
 * 
 * Maps box IDs to SVG asset paths from the existing icon registry.
 * This ensures consistent icon usage across the application.
 */

import { ICONS } from '../../shared/icons/icon.registry';

/**
 * Icon mapping for Business Layer boxes
 */
export const BUSINESS_LAYER_ICONS: Record<string, string> = {
  'bp-1': ICONS.business.erp,
  'bp-2': ICONS.business.crm,
  'bp-3': ICONS.business.scm,
  'bp-4': ICONS.business.cloud,
  'bp-5': ICONS.business.analytics,
  'bp-6': ICONS.business.dataLake,
};

/**
 * Icon mapping for DSP Layer boxes
 */
export const DSP_LAYER_ICONS: Record<string, string> = {
  'dsp-smartfactory-dashboard': ICONS.dsp.architecture.smartFactoryDashboard,
  'dsp-edge': ICONS.dsp.architecture.edgeBox,
  'dsp-management-cockpit': ICONS.dsp.architecture.cockpitBox,
  // Edge components
  'edge-connectivity': ICONS.dsp.functions.connectivity,
  'edge-digital-twin': ICONS.dsp.functions.digitalTwin,
  'edge-process-logic': ICONS.dsp.functions.processLogic,
  'edge-analytics': ICONS.dsp.functions.analytics,
  'edge-buffering': ICONS.dsp.functions.buffering,
  'edge-data-storage': ICONS.dsp.functions.dataStorage,
  'edge-workflow': ICONS.dsp.functions.workflow,
};

/**
 * Icon mapping for Shopfloor Systems layer
 */
export const SHOPFLOOR_SYSTEMS_ICONS: Record<string, string> = {
  'sf-system-1': ICONS.shopfloor.systems.factory,
  'sf-system-2': ICONS.shopfloor.systems.warehouse,
  'sf-system-3': ICONS.shopfloor.systems.agv,
  'sf-system-4': ICONS.shopfloor.systems.any,
};

/**
 * Icon mapping for Shopfloor Devices layer
 */
export const SHOPFLOOR_DEVICES_ICONS: Record<string, string> = {
  'sf-device-mill': ICONS.shopfloor.stations.mill,
  'sf-device-drill': ICONS.shopfloor.stations.drill,
  'sf-device-aiqs': ICONS.shopfloor.stations.aiqs,
  'sf-device-hbw': ICONS.shopfloor.stations.hbw,
  'sf-device-dps': ICONS.shopfloor.stations.dps,
  'sf-device-chrg': ICONS.shopfloor.stations.chrg,
};

/**
 * Combined icon map for all layers
 */
export const ARCHITECTURE_ICONS: Record<string, string> = {
  ...BUSINESS_LAYER_ICONS,
  ...DSP_LAYER_ICONS,
  ...SHOPFLOOR_SYSTEMS_ICONS,
  ...SHOPFLOOR_DEVICES_ICONS,
};

/**
 * Get icon path for a box ID, with fallback to question mark icon
 */
export function getIconForBox(boxId: string): string {
  return ARCHITECTURE_ICONS[boxId] || ICONS.shopfloor.shared.question;
}

/**
 * Check if an icon exists for a given box ID
 */
export function hasIcon(boxId: string): boolean {
  return boxId in ARCHITECTURE_ICONS;
}
