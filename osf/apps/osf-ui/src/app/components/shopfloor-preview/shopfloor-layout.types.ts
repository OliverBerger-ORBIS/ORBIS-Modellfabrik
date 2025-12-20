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

export interface ShopfloorHighlightDefaults {
  stroke_color: string;
  fill_color: string;
  stroke_width: number;
  stroke_align: 'inner' | 'center' | 'outer';
  clip_inside?: boolean;
}

export interface ShopfloorIconSizingRules {
  by_role: Partial<Record<ShopfloorCellRole | 'default', number>>;
}

export type ShopfloorCellRole =
  | 'module'
  | 'module_main_compartment'
  | 'module_sub_non_main'
  | 'intersection'
  | 'company'
  | 'software';

export interface ShopfloorPoint {
  x: number;
  y: number;
}

export interface ShopfloorSize {
  w: number;
  h: number;
}

export interface ShopfloorSubcellConfig {
  id: string;
  name: string;
  position: ShopfloorPoint;
  size: ShopfloorSize;
  center_abs: ShopfloorPoint;
  icon?: string;
  role: ShopfloorCellRole;
  is_main: boolean;
  has_details?: boolean;
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
  is_compound?: boolean;
  subcells?: ShopfloorSubcellConfig[];
  show_name?: boolean;
  has_details?: boolean;
}

export interface ShopfloorIntersectionMap {
  [intersectionId: string]: string;
}

export interface ShopfloorModuleBySerial {
  type: string;
  cell_id: string;
}

export interface ShopfloorRoadEndpoint {
  ref: string;
  cell_id: string;
  center: ShopfloorPoint;
}

export interface ParsedRoad {
  id: string;
  from: ShopfloorRoadEndpoint;
  to: ShopfloorRoadEndpoint;
  length: number;
  direction: 'NORTH' | 'SOUTH' | 'EAST' | 'WEST';
}

export interface ShopfloorFtsConfig {
  id: string;
  label: string;
  icon?: string;
  capacity?: number;
  current_position?: ShopfloorPoint;
  status?: string;
}

export interface ShopfloorLayoutConfig {
  metadata: ShopfloorLayoutMetadata;
  scaling: ShopfloorScalingConfig;
  highlight_defaults: ShopfloorHighlightDefaults;
  icon_sizing_rules: ShopfloorIconSizingRules;
  cells: ShopfloorCellConfig[];
  intersection_map: ShopfloorIntersectionMap;
  modules_by_serial: Record<string, ShopfloorModuleBySerial>;
  parsed_roads: ParsedRoad[];
  fts?: ShopfloorFtsConfig[];
}

