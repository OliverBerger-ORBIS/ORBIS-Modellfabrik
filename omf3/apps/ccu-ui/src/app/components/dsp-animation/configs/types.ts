/**
 * Customer configuration types for DSP animation system.
 * Enables multiple customer configurations while keeping core clean and maintainable.
 */

/**
 * Generic icon keys for reusable assets across all customers
 */
export type GenericIconKey = 
  // Devices
  | 'drill' | 'mill' | 'oven' | 'laser' | 'cnc' | 'printer-3d' 
  | 'robot-arm' | 'conveyor' | 'warehouse' | 'agv' | 'hbw'
  // Systems
  | 'warehouse-system' | 'erp' | 'mes' | 'cloud' | 'analytics'
  // Brands
  | 'sap' | 'alpha-x' | 'aws' | 'azure' | 'powerbi' | 'grafana';

/**
 * Mapping configuration for a shopfloor device
 */
export interface DeviceMapping {
  /** Abstract ID (e.g., 'sf-device-1', 'sf-device-2') */
  id: string;
  /** Customer-specific label for the device */
  label: string;
  /** Reference to generic icon */
  iconKey: GenericIconKey;
  /** Optional: override with custom icon path */
  customIconPath?: string;
}

/**
 * Mapping configuration for a shopfloor system
 */
export interface SystemMapping {
  /** Abstract ID (e.g., 'sf-system-1', 'sf-system-2') */
  id: string;
  /** Customer-specific label for the system */
  label: string;
  /** Reference to generic icon */
  iconKey: GenericIconKey;
  /** Optional: override with custom icon path */
  customIconPath?: string;
}

/**
 * Mapping configuration for a business process
 */
export interface BusinessProcessMapping {
  /** Abstract ID (e.g., 'bp-1', 'bp-2') */
  id: string;
  /** Customer-specific label for the process */
  label: string;
  /** Reference to generic system icon */
  iconKey: GenericIconKey;
  /** Brand logo key (e.g., sap, alpha-x, aws, azure) */
  brandLogoKey: GenericIconKey;
  /** Optional: override with custom brand logo path */
  customBrandPath?: string;
}

/**
 * Complete customer configuration for DSP animation
 */
export interface CustomerDspConfig {
  /** Customer identifier key */
  customerKey: string;
  /** Customer display name */
  customerName: string;
  /** Shopfloor device mappings */
  sfDevices: DeviceMapping[];
  /** Shopfloor system mappings */
  sfSystems: SystemMapping[];
  /** Business process mappings */
  bpProcesses: BusinessProcessMapping[];
  /** Optional: path to customer logo */
  customerLogoPath?: string;
}
