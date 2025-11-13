/**
 * Data models for shopfloor layout configuration
 */

export interface ShopfloorLayoutConfig {
  grid: GridConfig;
  modules: ModuleConfig[];
  fixed_positions: FixedPositionConfig[];
  intersections: IntersectionConfig[];
  roads: RoadConfig[];
  icon_sizing_rules?: IconSizingRules;
}

export interface GridConfig {
  rows: number;
  columns: number;
  cell_size: string; // e.g., "200x200"
}

export interface ModuleConfig {
  id: string;
  type: string;
  serialNumber: string;
  position: [number, number]; // [row, column]
  cell_size?: [number, number]; // [width, height] in pixels
  is_compound?: boolean;
  attached_assets?: string[];
  compound_layout?: {
    positions: [number, number][];
    size: [number, number];
  };
  show_label?: boolean;
}

export interface FixedPositionConfig {
  id: string;
  type: string;
  position: [number, number]; // [row, column]
  cell_size?: [number, number]; // [width, height] in pixels
  background_color?: string;
}

export interface IntersectionConfig {
  id: string;
  type: string;
  position: [number, number]; // [row, column]
  connected_modules?: string[];
}

export interface RoadConfig {
  length: number;
  from: string;
  to: string;
  direction: string;
}

export interface IconSizingRules {
  by_role: {
    intersection: number;
    module_main_compartment: number;
    module_sub_non_main: number;
    company: number;
    software: number;
    default: number;
  };
}

/**
 * Render model with computed positions and sizes
 */
export interface ShopfloorRenderModel {
  viewBox: string;
  cellWidth: number;
  cellHeight: number;
  cells: CellRenderModel[];
  routes: RouteRenderModel[];
}

export interface CellRenderModel {
  id: string;
  type: string;
  role: CellRole;
  x: number;
  y: number;
  width: number;
  height: number;
  backgroundColor?: string;
  icon?: IconRenderModel;
  subcells?: SubcellRenderModel[];
  label?: string;
}

export interface IconRenderModel {
  svgUrl: string;
  x: number;
  y: number;
  width: number;
  height: number;
  intrinsicWidth: number;
  intrinsicHeight: number;
}

export interface SubcellRenderModel {
  id: string;
  svgUrl: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface RouteRenderModel {
  id: string;
  points: [number, number][];
  strokeWidth: number;
}

export type CellRole = 
  | 'intersection' 
  | 'module_main_compartment' 
  | 'module_sub_non_main' 
  | 'company' 
  | 'software' 
  | 'default';

/**
 * SVG metadata extracted from SVG files
 */
export interface SvgMetadata {
  width: number;
  height: number;
  viewBox?: string;
}
