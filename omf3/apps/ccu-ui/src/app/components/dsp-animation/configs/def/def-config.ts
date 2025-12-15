/**
 * DEF (Digital Engineering Facility) Example Customer Configuration
 * Demonstrates different equipment and systems using the same generic icons
 */
import type { CustomerDspConfig } from '../types';

export const DEF_CONFIG: CustomerDspConfig = {
  customerKey: 'def',
  customerName: 'Digital Engineering Facility',
  
  // Shopfloor devices - Different equipment than FMF
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
    {
      id: 'sf-device-6',
      label: 'Robot Assembly Cell',
      iconKey: 'robot-arm',
    },
    {
      id: 'sf-device-7',
      label: 'Quality Inspection',
      iconKey: 'robot-arm',
    },
    {
      id: 'sf-device-8',
      label: 'Heat Treatment',
      iconKey: 'oven',
    },
  ],
  
  // Shopfloor systems
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
  
  // Business processes - Different systems than FMF
  bpProcesses: [
    {
      id: 'bp-1',
      label: 'ERP System',
      iconKey: 'erp',
      brandLogoKey: 'alpha-x', // Different ERP vendor
    },
    {
      id: 'bp-2',
      label: 'MES Platform',
      iconKey: 'mes',
      brandLogoKey: 'alpha-x',
    },
    {
      id: 'bp-3',
      label: 'Cloud Services',
      iconKey: 'cloud',
      brandLogoKey: 'azure', // Different cloud provider
    },
    {
      id: 'bp-4',
      label: 'Analytics Dashboard',
      iconKey: 'analytics',
      brandLogoKey: 'powerbi', // Different analytics platform
    },
    {
      id: 'bp-5',
      label: 'Data Platform',
      iconKey: 'cloud',
      brandLogoKey: 'azure',
    },
  ],
  
  customerLogoPath: 'assets/customers/def/logo.svg',
};
