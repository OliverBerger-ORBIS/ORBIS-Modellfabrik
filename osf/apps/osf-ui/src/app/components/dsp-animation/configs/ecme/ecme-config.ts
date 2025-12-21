/**
 * ECME (European Company Manufacturing Everything) Customer Configuration
 * Demonstrates different equipment and systems using new SVG icons
 */
import type { CustomerDspConfig } from '../types';

export const ECME_CONFIG: CustomerDspConfig = {
  customerKey: 'ecme',
  customerName: 'European Company Manufacturing Everything',
  
  // Shopfloor devices - 5 devices with semantic IDs
  sfDevices: [
    {
      id: 'sf-device-cnc',
      label: $localize`:@@deviceCNC:CNC / Station`,
      iconKey: 'cnc-station',
    },
    {
      id: 'sf-device-hydraulic',
      label: $localize`:@@deviceHydraulic:Hydraulic / Station`,
      iconKey: 'hydraulic-station',
    },
    {
      id: 'sf-device-printer-3d',
      label: $localize`:@@devicePrinter3D:3D Printer / Station`,
      iconKey: 'printer-3d-station',
    },
    {
      id: 'sf-device-weight',
      label: $localize`:@@deviceWeight:Weight / Station`,
      iconKey: 'weight-station',
    },
    {
      id: 'sf-device-laser',
      label: $localize`:@@deviceLaser:Laser / Station`,
      iconKey: 'laser-station',
    },
  ],
  
  // Shopfloor systems - 4 systems with semantic IDs
  sfSystems: [
    {
      id: 'sf-system-scada',
      label: $localize`:@@dspArchLabelScada:SCADA / System`,
      iconKey: 'scada-system',
    },
    {
      id: 'sf-system-industrial-process',
      label: $localize`:@@dspArchLabelIndustrialProcess:Industrial Process / System`,
      iconKey: 'industrial-process-system',
    },
    {
      id: 'sf-system-cargo',
      label: $localize`:@@dspArchLabelCargo:Cargo / System`,
      iconKey: 'cargo-system',
    },
    {
      id: 'sf-system-pump',
      label: $localize`:@@dspArchLabelPump:Pump / System`,
      iconKey: 'pump-system',
    },
  ],
  
  // Business processes - 4 applications (no bp-cloud)
  bpProcesses: [
    {
      id: 'bp-erp',
      label: $localize`:@@dspArchLabelERP:ERP Applications`,
      iconKey: 'erp',
      brandLogoKey: 'alpha-x',
    },
    {
      id: 'bp-mes',
      label: $localize`:@@dspArchLabelMESApp:MES Applications`,
      iconKey: 'mes',
      brandLogoKey: 'alpha-x',
    },
    {
      id: 'bp-analytics',
      label: $localize`:@@dspArchLabelAnalytics:Analytical\nApplications`,
      iconKey: 'analytics',
      brandLogoKey: 'powerbi',
    },
    {
      id: 'bp-data-lake',
      label: $localize`:@@dspArchLabelDataLake:Data Lake`,
      iconKey: 'cloud',
      customIconPath: 'bp-data-lake',
      brandLogoKey: 'azure',
    },
  ],
  
  customerLogoPath: 'assets/customers/ecme/logo.svg',
};
