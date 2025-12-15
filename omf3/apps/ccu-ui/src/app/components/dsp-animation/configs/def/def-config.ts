/**
 * DEF (Digital Engineering Facility) Example Customer Configuration
 * Demonstrates different equipment and systems using the same generic icons
 */
import type { CustomerDspConfig } from '../types';

export const DEF_CONFIG: CustomerDspConfig = {
  customerKey: 'def',
  customerName: 'Digital Engineering Facility',
  
  // Shopfloor devices - Different equipment than FMF
  // Using EXISTING container IDs but with different labels/icons
  sfDevices: [
    {
      id: 'sf-device-mill', // Reusing mill slot for laser
      label: 'Laser Cutting Station',
      iconKey: 'laser',
    },
    {
      id: 'sf-device-drill', // Reusing drill slot for CNC
      label: 'CNC Router',
      iconKey: 'cnc',
    },
    {
      id: 'sf-device-aiqs', // Reusing AIQS slot for 3D printer
      label: '3D Printer Array',
      iconKey: 'printer-3d',
    },
    {
      id: 'sf-device-hbw', // Reusing HBW slot for automated storage
      label: 'Automated Storage',
      iconKey: 'warehouse',
    },
    {
      id: 'sf-device-dps', // Reusing DPS slot for conveyor
      label: 'Material Conveyor',
      iconKey: 'conveyor',
    },
    {
      id: 'sf-device-chrg', // Reusing CHRG slot for robot
      label: 'Robot Assembly Cell',
      iconKey: 'robot-arm',
    },
    {
      id: 'sf-device-conveyor', // Reusing conveyor slot for quality inspection
      label: 'Quality Inspection',
      iconKey: 'robot-arm',
    },
    {
      id: 'sf-device-stone-oven', // Reusing oven slot for heat treatment
      label: 'Heat Treatment',
      iconKey: 'oven',
    },
  ],
  
  // Shopfloor systems
  // Using EXISTING container IDs but with different labels
  sfSystems: [
    {
      id: 'sf-system-any',
      label: 'Generic System',
      iconKey: 'warehouse-system',
    },
    {
      id: 'sf-system-fts',
      label: 'AGV Fleet',
      iconKey: 'agv',
    },
    {
      id: 'sf-system-warehouse',
      label: 'Central Warehouse',
      iconKey: 'warehouse-system',
    },
    {
      id: 'sf-system-factory',
      label: 'Production Line',
      iconKey: 'warehouse-system',
    },
  ],
  
  // Business processes - Different systems than FMF
  // Using EXISTING container IDs but with different labels and brand logos
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
      id: 'bp-cloud',
      label: 'Cloud Services',
      iconKey: 'cloud',
      brandLogoKey: 'azure', // Different cloud provider
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
