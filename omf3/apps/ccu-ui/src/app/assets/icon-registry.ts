import { ICONS, type IconRegistry } from '../shared/icons/icon.registry';

/**
 * Legacy IconKey union retained for DSP detail configuration.
 * Maps onto the new ICONS registry paths under assets/svg.
 */
export type IconKey =
  | 'logo-orbis'
  | 'logo-sap'
  | 'logo-azure'
  | 'logo-dsp'
  | 'logo-grafana'
  | 'logo-distributed'
  | 'edge-connectivity'
  | 'edge-digital-twin'
  | 'edge-data-storage'
  | 'edge-analytics'
  | 'edge-workflow'
  | 'edge-network'
  | 'device-drill'
  | 'device-hbw'
  | 'device-mill'
  | 'device-aiqs'
  | 'device-dps'
  | 'device-chrg'
  | 'device-plc'
  | 'device-robot-arm'
  | 'device-conveyor'
  | 'device-camera'
  | 'device-sensor'
  | 'device-printer'
  | 'shopfloor-systems'
  | 'shopfloor-fts'
  | 'shopfloor-mes'
  | 'shopfloor-scada'
  | 'shopfloor-aps'
  | 'shopfloor-warehouse'
  | 'shopfloor-it'
  | 'ux-dashboard'
  | 'ux-monitor'
  | 'erp-application'
  | 'bp-cloud-apps'
  | 'bp-analytics'
  | 'bp-data-lake'
  | 'bp-business-process';

export interface FunctionIconConfig {
  iconKey: IconKey;
  size: number;
}

/**
 * Central mapping from IconKey to asset file paths (new svg structure).
 * Paths are relative (no leading slash) and served from /assets/.
 */
export const ICON_MAP: Record<IconKey, string> = {
  'logo-orbis': ICONS.brand.orbis,
  'logo-sap': ICONS.brand.sap,
  'logo-azure': ICONS.brand.azure,
  'logo-dsp': ICONS.brand.orbis,
  'logo-grafana': ICONS.brand.grafana,
  'logo-distributed': ICONS.dsp.architecture.edgeBox,

  'edge-connectivity': ICONS.dsp.functions.connectivity,
  'edge-digital-twin': ICONS.dsp.functions.digitalTwin,
  'edge-data-storage': ICONS.dsp.functions.dataStorage,
  'edge-analytics': ICONS.dsp.functions.analytics,
  'edge-workflow': ICONS.dsp.functions.workflow,
  'edge-network': ICONS.dsp.functions.connectivity,

  'device-drill': ICONS.shopfloor.stations.drill,
  'device-hbw': ICONS.shopfloor.stations.hbw,
  'device-mill': ICONS.shopfloor.stations.mill,
  'device-aiqs': ICONS.shopfloor.stations.aiqs,
  'device-dps': ICONS.shopfloor.stations.dps,
  'device-chrg': ICONS.shopfloor.stations.chrg,
  'device-plc': ICONS.shopfloor.systems.any,
  'device-robot-arm': ICONS.shopfloor.stations.dps,
  'device-conveyor': ICONS.shopfloor.systems.any,
  'device-camera': ICONS.shopfloor.stations.aiqs,
  'device-sensor': ICONS.shopfloor.systems.any,
  'device-printer': ICONS.shopfloor.systems.any,

  'shopfloor-systems': ICONS.shopfloor.systems.any,
  'shopfloor-fts': ICONS.shopfloor.systems.fts,
  'shopfloor-mes': ICONS.shopfloor.shared.question,
  'shopfloor-scada': ICONS.shopfloor.systems.any,
  'shopfloor-aps': ICONS.shopfloor.stations.dps,
  'shopfloor-warehouse': ICONS.shopfloor.stations.hbw,
  'shopfloor-it': ICONS.shopfloor.systems.any,

  'ux-dashboard': ICONS.dsp.architecture.smartFactoryDashboard,
  'ux-monitor': ICONS.dsp.architecture.cockpitBox,

  'erp-application': ICONS.business.erp,
  'bp-cloud-apps': ICONS.business.cloud,
  'bp-analytics': ICONS.business.analytics,
  'bp-data-lake': ICONS.business.dataLake,
  'bp-business-process': ICONS.dsp.functions.workflow,
};

export function getIconPath(key: IconKey | undefined | null): string {
  if (!key) {
    return ICONS.shopfloor.shared.question;
  }
  const path = ICON_MAP[key];
  if (!path) {
    return ICONS.shopfloor.shared.question;
  }
  return path.startsWith('/') ? path.slice(1) : path;
}

export { ICONS, type IconRegistry } from '../shared/icons/icon.registry';
