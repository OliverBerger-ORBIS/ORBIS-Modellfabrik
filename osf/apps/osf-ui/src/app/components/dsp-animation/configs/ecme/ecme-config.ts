/**
 * ECME (European Company Manufacturing Everything) Customer Configuration
 * Demonstrates different equipment and systems using new SVG icons
 */
import type { CustomerDspConfig } from '../types';

export const ECME_CONFIG: CustomerDspConfig = {
  customerKey: 'ecme',
  customerName: 'European Company Manufacturing Everything',
  
  // Shopfloor devices - 5 devices with new SVG icons
  sfDevices: [
    {
      id: 'sf-device-1',
      label: $localize`:@@deviceCNC:CNC / Station`,
      iconKey: 'cnc',
      customIconPath: 'device-cnc',
    },
    {
      id: 'sf-device-2',
      label: $localize`:@@deviceHydraulic:Hydraulic / Station`,
      iconKey: 'hydraulic',
      customIconPath: 'device-hydraulic',
    },
    {
      id: 'sf-device-3',
      label: $localize`:@@devicePrinter3D:3D Printer / Station`,
      iconKey: 'printer-3d',
      customIconPath: 'device-printer-3d',
    },
    {
      id: 'sf-device-4',
      label: $localize`:@@deviceWeight:Weight / Station`,
      iconKey: 'weight',
      customIconPath: 'device-weight',
    },
    {
      id: 'sf-device-5',
      label: $localize`:@@deviceLaser:Laser / Station`,
      iconKey: 'laser',
      customIconPath: 'device-laser',
    },
  ],
  
  // Shopfloor systems - 4 systems with new SVG icons
  sfSystems: [
    {
      id: 'sf-system-1',
      label: $localize`:@@dspArchLabelScada:SCADA / System`,
      iconKey: 'scada',
      customIconPath: 'shopfloor-scada',
    },
    {
      id: 'sf-system-2',
      label: $localize`:@@dspArchLabelIndustrialProcess:Industrial Process / System`,
      iconKey: 'industrial-process',
      customIconPath: 'shopfloor-industrial-process',
    },
    {
      id: 'sf-system-3',
      label: $localize`:@@dspArchLabelCargo:Cargo / System`,
      iconKey: 'cargo',
      customIconPath: 'shopfloor-cargo',
    },
    {
      id: 'sf-system-4',
      label: $localize`:@@dspArchLabelPump:Pump / System`,
      iconKey: 'pump',
      customIconPath: 'shopfloor-pump',
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
