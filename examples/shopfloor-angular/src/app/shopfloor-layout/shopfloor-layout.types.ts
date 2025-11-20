/**
 * Shopfloor Layout Types
 * Based on OMF3 shopfloor-preview types from:
 * omf3/apps/ccu-ui/src/app/components/shopfloor-preview/shopfloor-layout.types.ts
 * 
 * Simplified for example purposes - subset of full OMF3 types
 * Compatible with OMF3 layout configuration format
 */

export interface ShopfloorLayoutMetadata {
  canvas: { width: number; height: number; units: string };
  created_by?: string;
  description?: string;
}

export interface ShopfloorScalingConfig {
  default_percent: number;
  min_percent: number;
  max_percent: number;
  mode: 'viewBox' | 'transform';
}

export type ShopfloorCellRole = 'module' | 'company' | 'software';

export interface ShopfloorPoint {
  x: number;
  y: number;
}

export interface ShopfloorSize {
  w: number;
  h: number;
}

export interface ShopfloorCellConfig {
  id: string;
  name: string;
  position: ShopfloorPoint;
  size: ShopfloorSize;
  center?: ShopfloorPoint;
  role: ShopfloorCellRole;
  serial_number?: string;
  icon?: string;
  background_color?: string;
  show_name?: boolean;
  has_details?: boolean;
}

export interface ShopfloorModuleBySerial {
  type: string;
  cell_id: string;
}

export interface ShopfloorLayoutConfig {
  metadata: ShopfloorLayoutMetadata;
  scaling: ShopfloorScalingConfig;
  cells: ShopfloorCellConfig[];
  modules_by_serial: Record<string, ShopfloorModuleBySerial>;
}
