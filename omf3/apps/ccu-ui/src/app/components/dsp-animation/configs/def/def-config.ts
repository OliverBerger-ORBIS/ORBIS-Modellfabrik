/**
 * DEF (Digital Engineering Facility) Example Customer Configuration
 * Demonstrates different equipment and systems using abstract IDs
 */
import type { CustomerDspConfig } from '../types';

export const DEF_CONFIG: CustomerDspConfig = {
  customerKey: 'def',
  customerName: 'Digital Engineering Facility',
  
  // Shopfloor devices - 5 devices with abstract IDs
  sfDevices: [
    {
      id: 'sf-device-1',
      label: 'Laser Cutting Station',
      iconKey: 'laser',
    },
    {
      id: 'sf-device-2',
      label: 'CNC Router',
      iconKey: 'cnc',
    },
    {
      id: 'sf-device-3',
      label: '3D Printer Array',
      iconKey: 'printer-3d',
    },
    {
      id: 'sf-device-4',
      label: 'Automated Storage',
      iconKey: 'warehouse',
    },
    {
      id: 'sf-device-5',
      label: 'Material Conveyor',
      iconKey: 'conveyor',
    },
  ],
  
  // Shopfloor systems - 4 systems with abstract IDs
  sfSystems: [
    {
      id: 'sf-system-1',
      label: 'Generic System',
      iconKey: 'warehouse-system',
    },
    {
      id: 'sf-system-2',
      label: 'AGV Fleet',
      iconKey: 'agv',
    },
    {
      id: 'sf-system-3',
      label: 'Central Warehouse',
      iconKey: 'warehouse-system',
    },
    {
      id: 'sf-system-4',
      label: 'Production Line',
      iconKey: 'warehouse-system',
    },
  ],
  
  // Business processes - 4 applications (no bp-cloud)
  bpProcesses: [
    {
      id: 'bp-erp',
      label: 'ERP System',
      iconKey: 'erp',
      brandLogoKey: 'alpha-x', // Different ERP vendor
    },
    {
      id: 'bp-mes',
      label: 'MES Platform',
      iconKey: 'mes',
      brandLogoKey: 'alpha-x',
    },
    {
      id: 'bp-analytics',
      label: 'Analytics Dashboard',
      iconKey: 'analytics',
      brandLogoKey: 'powerbi', // Different analytics platform
    },
    {
      id: 'bp-data-lake',
      label: 'Data Platform',
      iconKey: 'cloud',
      brandLogoKey: 'azure',
    },
  ],
  
  customerLogoPath: 'assets/customers/def/logo.svg',
};
