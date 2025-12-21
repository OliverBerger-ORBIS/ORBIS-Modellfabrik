/**
 * Customer configuration types for DSP animation system.
 * Enables multiple customer configurations while keeping core clean and maintainable.
 */

/**
 * Generic icon keys for reusable assets across all customers
 * Keys follow the pattern: <name>-station.svg (devices), <name>-system.svg (systems), <name>-application.svg (business)
 */
export type GenericIconKey = 
  // Devices (legacy keys without -station suffix, kept for backward compatibility)
  | 'drill' | 'mill' | 'oven' | 'laser' | 'cnc' | 'printer-3d' 
  | 'robot-arm' | 'conveyor' | 'warehouse' | 'agv' | 'hbw'
  | 'hydraulic' | 'weight'
  // Devices (new semantic keys with -station suffix)
  | 'cnc-station' | 'hydraulic-station' | 'printer-3d-station' | 'weight-station' | 'laser-station'
  // Systems (legacy keys without -system suffix, kept for backward compatibility)
  | 'warehouse-system' | 'erp' | 'mes' | 'cloud' | 'analytics'
  | 'scada' | 'industrial-process' | 'cargo' | 'pump'
  // Systems (new semantic keys with -system suffix)
  | 'scada-system' | 'industrial-process-system' | 'cargo-system' | 'pump-system'
  | 'any-system' | 'agv-system'
  // Brands
  | 'sap' | 'alpha-x' | 'aws' | 'azure' | 'powerbi' | 'grafana';

/**
 * Mapping configuration for a shopfloor device
 */
export interface DeviceMapping {
  /** Container ID (e.g., 'sf-device-mill', 'sf-device-drill', 'sf-device-hbw') */
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
  /** Container ID (e.g., 'sf-system-any', 'sf-system-fts', 'sf-system-warehouse') */
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
  /** Container ID (e.g., 'bp-erp', 'bp-mes', 'bp-cloud') */
  id: string;
  /** Customer-specific label for the process */
  label: string;
  /** Reference to generic system icon */
  iconKey: GenericIconKey;
  /** Brand logo key (e.g., sap, alpha-x, aws, azure) */
  brandLogoKey: GenericIconKey;
  /** Optional: override with custom icon path */
  customIconPath?: string;
  /** Optional: override with custom brand logo path */
  customBrandLogoPath?: string;
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
