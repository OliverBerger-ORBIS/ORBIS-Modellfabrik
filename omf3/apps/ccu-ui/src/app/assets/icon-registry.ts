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
  | 'edge-network'
  | 'edge-interoperability'
  | 'edge-event-driven'
  | 'edge-choreography'
  | 'edge-best-of-breed'
  | 'edge-ai-enablement'
  | 'edge-autonomous-enterprise'
  | 'mc-hierarchical-structure'
  | 'mc-orchestration'
  | 'mc-governance'
  | 'logo-edge-a'
  | 'logo-edge-b'
  | 'logo-edge-c'
  | 'edge-component-disc'
  | 'edge-component-event-bus'
  | 'edge-component-app-server'
  | 'edge-component-router'
  | 'edge-component-agent'
  | 'edge-component-log-server'
  | 'edge-component-disi'
  | 'edge-component-database'
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
  | 'device-stone-oven'
  | 'shopfloor-systems'
  | 'shopfloor-fts'
  | 'shopfloor-mes'
  | 'shopfloor-scada'
  | 'shopfloor-aps'
  | 'shopfloor-warehouse'
  | 'shopfloor-factory'
  | 'shopfloor-it'
  | 'ux-box'
  | 'mc-box'
  | 'erp-application'
  | 'bp-cloud-apps'
  | 'bp-analytics'
  | 'bp-data-lake'
  | 'bp-business-process'
  | 'mes-application'
  | 'aws-logo'
  | 'google-cloud-logo'
  | 'logo-edge'
  | 'logo-mc'
  // Generic device icons
  | 'generic-device-drill' | 'generic-device-mill' | 'generic-device-oven'
  | 'generic-device-laser' | 'generic-device-cnc' | 'generic-device-printer-3d'
  | 'generic-device-robot-arm' | 'generic-device-conveyor' | 'generic-device-warehouse'
  | 'generic-device-agv' | 'generic-device-hbw'
  // Generic system icons
  | 'generic-system-warehouse-system' | 'generic-system-erp' | 'generic-system-mes'
  | 'generic-system-cloud' | 'generic-system-analytics'
  // Generic brand icons
  | 'generic-brand-sap' | 'generic-brand-alpha-x' | 'generic-brand-aws'
  | 'generic-brand-azure' | 'generic-brand-powerbi' | 'generic-brand-grafana';

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
  'logo-dsp': ICONS.brand.dsp,
  'logo-grafana': ICONS.brand.grafana,
  'logo-distributed': ICONS.dsp.architecture.edgeBox,

  'edge-connectivity': ICONS.dsp.functions.connectivity,
  'edge-digital-twin': ICONS.dsp.functions.digitalTwin,
  'edge-data-storage': ICONS.dsp.functions.dataStorage,
  'edge-analytics': ICONS.dsp.functions.analytics,
  'edge-network': ICONS.dsp.functions.connectivity,
  'edge-interoperability': 'assets/svg/dsp/functions/edge-interoperability.svg',
  'edge-event-driven': 'assets/svg/dsp/functions/edge-event-driven.svg',
  'edge-choreography': 'assets/svg/dsp/functions/edge-choreography.svg',
  'edge-best-of-breed': 'assets/svg/dsp/functions/edge-best-of-breed.svg',
  'edge-ai-enablement': 'assets/svg/dsp/functions/edge-ai-enablement.svg',
  'edge-autonomous-enterprise': 'assets/svg/dsp/functions/edge-autonomous-enterprise.svg',
  'mc-hierarchical-structure': 'assets/svg/dsp/functions/mc-hierarchical-structure.svg',
  'mc-orchestration': 'assets/svg/dsp/functions/mc-orchestration.svg',
  'mc-governance': 'assets/svg/dsp/functions/mc-governance.svg',
  'logo-edge-a': 'assets/svg/dsp/architecture/dsp-edge-box.svg',
  'logo-edge-b': 'assets/svg/dsp/architecture/dsp-edge-box.svg',
  'logo-edge-c': 'assets/svg/dsp/architecture/dsp-edge-box.svg',

  'edge-component-disc': ICONS.dsp.edgeComponents.disc,
  'edge-component-event-bus': ICONS.dsp.edgeComponents.eventBus,
  'edge-component-app-server': ICONS.dsp.edgeComponents.appServer,
  'edge-component-router': ICONS.dsp.edgeComponents.router,
  'edge-component-agent': ICONS.dsp.edgeComponents.agent,
  'edge-component-log-server': ICONS.dsp.edgeComponents.logServer,
  'edge-component-disi': ICONS.dsp.edgeComponents.disi,
  'edge-component-database': ICONS.dsp.edgeComponents.database,

  'device-drill': ICONS.shopfloor.stations.drill,
  'device-hbw': ICONS.shopfloor.stations.hbw,
  'device-mill': ICONS.shopfloor.stations.mill,
  'device-aiqs': ICONS.shopfloor.stations.aiqs,
  'device-dps': ICONS.shopfloor.stations.dps,
  'device-chrg': ICONS.shopfloor.stations.chrg,
  'device-plc': ICONS.shopfloor.systems.any,
  'device-robot-arm': ICONS.shopfloor.stations.dps,
  'device-conveyor': 'assets/svg/shopfloor/stations/conveyor-station.svg',
  'device-camera': ICONS.shopfloor.stations.aiqs,
  'device-sensor': ICONS.shopfloor.systems.any,
  'device-printer': ICONS.shopfloor.systems.any,
  'device-stone-oven': 'assets/svg/shopfloor/stations/oven-station.svg',

  'shopfloor-systems': ICONS.shopfloor.systems.any,
  'shopfloor-fts': ICONS.shopfloor.systems.fts,
  'shopfloor-mes': ICONS.shopfloor.shared.question,
  'shopfloor-scada': ICONS.shopfloor.systems.any,
  'shopfloor-aps': ICONS.shopfloor.stations.dps,
  'shopfloor-warehouse': 'assets/svg/shopfloor/systems/warehouse-system.svg',
  'shopfloor-factory': 'assets/svg/shopfloor/systems/factory-system.svg',
  'shopfloor-it': ICONS.shopfloor.systems.any,

  'ux-box': ICONS.dsp.architecture.uxBox,
  'mc-box': ICONS.dsp.architecture.mcBox,

  'erp-application': ICONS.business.erp,
  'bp-cloud-apps': ICONS.business.cloud,
  'bp-analytics': ICONS.business.analytics,
  'bp-data-lake': ICONS.business.dataLake,
  'bp-business-process': ICONS.dsp.functions.workflow,
  'mes-application': ICONS.business.mes,
  'aws-logo': 'assets/svg/brand/aws-logo.svg',
  'google-cloud-logo': 'assets/svg/brand/google-cloud-logo.svg',
  'logo-edge': 'assets/svg/dsp/architecture/dsp-edge-box.svg',
  'logo-mc': 'assets/svg/dsp/architecture/dsp-mc-box.svg',
  
  // Generic device icons (using existing shopfloor station icons from src/assets/svg/shopfloor/stations/)
  'generic-device-drill': 'assets/svg/shopfloor/stations/drill-station.svg',
  'generic-device-mill': 'assets/svg/shopfloor/stations/mill-station.svg',
  'generic-device-oven': 'assets/svg/shopfloor/stations/oven-station.svg',
  'generic-device-laser': 'assets/svg/shopfloor/stations/mill-station.svg', // Using mill as fallback for laser (not available)
  'generic-device-cnc': 'assets/svg/shopfloor/stations/mill-station.svg', // Using mill as fallback for CNC (not available)
  'generic-device-printer-3d': 'assets/svg/shopfloor/stations/mixer.svg', // Using mixer as fallback for 3D printer (not available)
  'generic-device-robot-arm': 'assets/svg/shopfloor/stations/chrg-station.svg', // Using chrg (robot arm) for robot-arm
  'generic-device-conveyor': 'assets/svg/shopfloor/stations/conveyor-station.svg',
  'generic-device-warehouse': 'assets/svg/shopfloor/stations/hbw-station.svg', // Using HBW for warehouse
  'generic-device-agv': 'assets/svg/shopfloor/stations/dps-station.svg', // Using DPS as fallback for AGV (not available)
  'generic-device-hbw': 'assets/svg/shopfloor/stations/hbw-station.svg',
  
  // Generic system icons (using existing business application icons from src/assets/svg/business/)
  'generic-system-warehouse-system': 'assets/svg/shopfloor/systems/warehouse-system.svg',
  'generic-system-erp': 'assets/svg/business/erp-application.svg',
  'generic-system-mes': 'assets/svg/business/mes-application.svg',
  'generic-system-cloud': 'assets/svg/business/cloud-application.svg',
  'generic-system-analytics': 'assets/svg/business/analytics-application.svg',
  
  // Generic brand icons (using existing brand icons from src/assets/svg/brand/)
  'generic-brand-sap': 'assets/svg/brand/sap-logo.svg',
  'generic-brand-alpha-x': 'assets/svg/brand/sap-logo.svg', // Using SAP as fallback for Alpha-X (not available)
  'generic-brand-aws': 'assets/svg/brand/aws-logo.svg',
  'generic-brand-azure': 'assets/svg/brand/azure-logo.svg',
  'generic-brand-powerbi': 'assets/svg/brand/azure-logo.svg', // Using Azure as fallback for PowerBI (not available)
  'generic-brand-grafana': 'assets/svg/brand/grafana-logo.svg',
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
