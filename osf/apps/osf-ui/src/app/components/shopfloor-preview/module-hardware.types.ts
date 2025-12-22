/**
 * TypeScript interfaces for module hardware configuration (OPC-UA stations and TXT controllers)
 * Corresponds to: osf/apps/osf-ui/public/shopfloor/modules_hardware.json
 */

export interface OpcUaStationConfig {
  /** IP address of the OPC-UA server */
  ip_address: string;
  /** IP range reserved for this station (DHCP reservation) */
  ip_range?: string;
  /** OPC-UA endpoint URL (e.g., "opc.tcp://192.168.0.90:4840") */
  endpoint: string;
  /** Human-readable description of the station hardware */
  description: string;
}

export interface TxtControllerConfig {
  /** TXT controller ID (e.g., "TXT4.0-p0F4") */
  id: string;
  /** TXT controller name (e.g., "TXT-DPS") */
  name: string;
  /** IP address of the TXT controller (DHCP-assigned, may change) */
  ip_address: string;
  /** MQTT client ID used by this TXT controller */
  mqtt_client?: string;
  /** Human-readable description of the controller purpose */
  description: string;
}

export interface ModuleHardwareConfig {
  /** Module serial number (key, e.g., "SVR4H73275") */
  serial_number: string;
  /** Module name (e.g., "DPS", "HBW", "MILL") */
  module_name: string;
  /** Module type/category (e.g., "Input/Output", "Processing", "Storage") */
  module_type: string;
  /** OPC-UA station configuration (null if module has no OPC-UA server) */
  opc_ua_station: OpcUaStationConfig | null;
  /** Array of TXT controllers assigned to this module (empty array if none) */
  txt_controllers: TxtControllerConfig[];
}

export interface ModulesHardwareConfig {
  metadata: {
    version: string;
    last_updated: string;
    description: string;
    source?: string;
  };
  /** Map of serial number to module hardware configuration */
  modules: Record<string, ModuleHardwareConfig>;
}

