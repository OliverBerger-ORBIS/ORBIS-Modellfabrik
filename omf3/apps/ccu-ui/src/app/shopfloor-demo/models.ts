/**
 * Type definitions for shopfloor layout and rendering models
 */

export type GridTuple = [number, number];

export interface GridConfig {
  rows: number;
  columns: number;
  cell_width: number;
  cell_height: number;
}

export interface IconSizingRules {
  by_role: {
    module: number;
    fixed: number;
    intersection: number;
    attachment: number;
  };
}

export interface CompoundLayout {
  positions: GridTuple[];
  size: GridTuple;
}

export interface ShopfloorModule {
  id: string;
  type: string;
  serialNumber: string;
  position: GridTuple;
  cell_w: number;
  cell_h: number;
  roleFactor: number;
  show_label: boolean;
  is_compound?: boolean;
  attached_assets?: string[];
  compound_layout?: CompoundLayout;
}

export interface ShopfloorFixedPosition {
  id: string;
  type: string;
  position: GridTuple;
  cell_w: number;
  cell_h: number;
  roleFactor: number;
  background_color?: string;
}

export interface ShopfloorIntersection {
  id: string;
  type: string;
  position: GridTuple;
  cell_w: number;
  cell_h: number;
  roleFactor: number;
  connected_modules: string[];
}

export interface ShopfloorRoad {
  from: string;
  to: string;
  direction: string;
  length: number;
}

export interface ParsedRoad {
  from: string;
  to: string;
  points: number[][];
}

export interface IntersectionMapEntry {
  id: string;
  position: GridTuple;
  center: GridTuple;
}

export interface ModulesBySerialEntry {
  id: string;
  type: string;
  position: GridTuple;
  center: GridTuple;
}

export interface ShopfloorLayout {
  _meta: {
    _description: string;
    _version: string;
    _domain: string;
    _source: string;
    _notes: string[];
  };
  grid: GridConfig;
  icon_sizing_rules: IconSizingRules;
  modules: ShopfloorModule[];
  fixed_positions: ShopfloorFixedPosition[];
  intersections: ShopfloorIntersection[];
  roads: ShopfloorRoad[];
  parsed_roads: ParsedRoad[];
  intersection_map: Record<string, IntersectionMapEntry>;
  modules_by_serial: Record<string, ModulesBySerialEntry>;
}

export interface SvgDimensions {
  width: number;
  height: number;
}

export interface ComputedIconSize {
  width: number;
  height: number;
  x: number;
  y: number;
}

export interface RenderCell {
  id: string;
  type: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  icon?: string;
  iconSvg?: string;
  iconSize?: ComputedIconSize;
  backgroundColor?: string;
  highlighted: boolean;
  is_compound?: boolean;
  subcells?: RenderSubcell[];
}

export interface RenderSubcell {
  id: string;
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  icon?: string;
  iconSvg?: string;
  iconSize?: ComputedIconSize;
  highlighted: boolean;
}

export interface RenderRoad {
  id: string;
  from: string;
  to: string;
  points: number[][];
}

export interface ShopfloorRenderModel {
  width: number;
  height: number;
  cells: RenderCell[];
  roads: RenderRoad[];
  scale: number;
}
