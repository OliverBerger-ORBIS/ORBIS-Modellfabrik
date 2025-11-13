import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import type {
  ShopfloorLayoutConfig,
  ShopfloorRenderModel,
  CellRenderModel,
  IconRenderModel,
  RouteRenderModel,
  SvgMetadata,
  CellRole,
} from './shopfloor-layout.models';

/**
 * Service for loading and processing shopfloor layout configuration
 */
@Injectable({
  providedIn: 'root',
})
export class ShopfloorLayoutService {
  private readonly layoutUrl = '/shopfloor/shopfloor_layout.json';
  private readonly svgBasePath = '/shopfloor/';
  private svgMetadataCache = new Map<string, SvgMetadata>();

  constructor(private http: HttpClient) {}

  /**
   * Load the shopfloor layout configuration and prepare render model
   */
  async loadShopfloorLayout(): Promise<ShopfloorRenderModel> {
    const config = await firstValueFrom(
      this.http.get<ShopfloorLayoutConfig>(this.layoutUrl)
    );

    // Parse cell size from "200x200" format
    const [cellWidth, cellHeight] = config.grid.cell_size
      .split('x')
      .map((s) => parseInt(s, 10));

    // Compute viewBox based on grid dimensions
    const totalWidth = config.grid.columns * cellWidth;
    const totalHeight = config.grid.rows * cellHeight;
    const viewBox = `0 0 ${totalWidth} ${totalHeight}`;

    // Process all cells (modules, fixed_positions, intersections)
    const cells: CellRenderModel[] = [];

    // Add intersection cells
    for (const intersection of config.intersections) {
      const cell = await this.createIntersectionCell(
        intersection,
        cellWidth,
        cellHeight,
        config
      );
      cells.push(cell);
    }

    // Add module cells
    for (const module of config.modules) {
      const cell = await this.createModuleCell(
        module,
        cellWidth,
        cellHeight,
        config
      );
      cells.push(cell);
    }

    // Add fixed position cells
    for (const fixedPos of config.fixed_positions) {
      const cell = await this.createFixedPositionCell(
        fixedPos,
        cellWidth,
        cellHeight,
        config
      );
      cells.push(cell);
    }

    // Process roads into route render models
    const routes = this.createRoutes(config, cells, cellWidth, cellHeight);

    return {
      viewBox,
      cellWidth,
      cellHeight,
      cells,
      routes,
    };
  }

  /**
   * Create a render model for an intersection cell
   */
  private async createIntersectionCell(
    intersection: ShopfloorLayoutConfig['intersections'][0],
    cellWidth: number,
    cellHeight: number,
    config: ShopfloorLayoutConfig
  ): Promise<CellRenderModel> {
    const [row, col] = intersection.position;
    const x = col * cellWidth;
    const y = row * cellHeight;

    // Try to find intersection SVG (e.g., intersection1.svg)
    const svgFileName = this.getIntersectionSvgName(intersection.type);
    const icon = await this.createIconRenderModel(
      svgFileName,
      x,
      y,
      cellWidth,
      cellHeight,
      'intersection',
      config
    );

    return {
      id: intersection.id,
      type: intersection.type,
      role: 'intersection',
      x,
      y,
      width: cellWidth,
      height: cellHeight,
      icon,
    };
  }

  /**
   * Create a render model for a module cell
   */
  private async createModuleCell(
    module: ShopfloorLayoutConfig['modules'][0],
    cellWidth: number,
    cellHeight: number,
    config: ShopfloorLayoutConfig
  ): Promise<CellRenderModel> {
    const [row, col] = module.position;
    const x = col * cellWidth;
    const y = row * cellHeight;

    // Get actual cell dimensions (may be different for compound modules)
    const width = module.cell_size ? module.cell_size[0] : cellWidth;
    const height = module.cell_size ? module.cell_size[1] : cellHeight;

    // Get SVG file name for the module type
    const svgFileName = this.getModuleSvgName(module.type);
    const icon = await this.createIconRenderModel(
      svgFileName,
      x,
      y,
      width,
      height,
      'module_main_compartment',
      config
    );

    // Handle compound modules with subcells
    let subcells: CellRenderModel['subcells'];
    if (module.is_compound && module.compound_layout && module.attached_assets) {
      subcells = await this.createSubcells(
        module,
        x,
        y,
        config
      );
    }

    return {
      id: module.id,
      type: module.type,
      role: 'module_main_compartment',
      x,
      y,
      width,
      height,
      icon,
      subcells,
      label: module.show_label ? module.id : undefined,
    };
  }

  /**
   * Create subcells for compound modules
   */
  private async createSubcells(
    module: ShopfloorLayoutConfig['modules'][0],
    parentX: number,
    parentY: number,
    config: ShopfloorLayoutConfig
  ) {
    if (!module.compound_layout || !module.attached_assets) return [];

    const subcells = [];
    const [subcellWidth, subcellHeight] = module.compound_layout.size;

    for (let i = 0; i < module.attached_assets.length; i++) {
      const assetId = module.attached_assets[i];
      const [offsetX, offsetY] = module.compound_layout.positions[i];
      
      // Extract asset type from ID (e.g., "HBW_SQUARE1" -> look for square SVG)
      const svgFileName = this.getSubcellSvgName(assetId);
      
      subcells.push({
        id: assetId,
        svgUrl: `${this.svgBasePath}${svgFileName}`,
        x: parentX + offsetX,
        y: parentY + offsetY,
        width: subcellWidth,
        height: subcellHeight,
      });
    }

    return subcells;
  }

  /**
   * Create a render model for a fixed position cell
   */
  private async createFixedPositionCell(
    fixedPos: ShopfloorLayoutConfig['fixed_positions'][0],
    cellWidth: number,
    cellHeight: number,
    config: ShopfloorLayoutConfig
  ): Promise<CellRenderModel> {
    const [row, col] = fixedPos.position;
    const x = col * cellWidth;
    const y = row * cellHeight;

    // Get actual cell dimensions
    const width = fixedPos.cell_size ? fixedPos.cell_size[0] : cellWidth;
    const height = fixedPos.cell_size ? fixedPos.cell_size[1] : cellHeight;

    // Determine role based on type
    const role: CellRole = fixedPos.type.toLowerCase().includes('orbis') 
      ? 'company' 
      : 'software';

    // Get SVG file name
    const svgFileName = this.getFixedPositionSvgName(fixedPos.type);
    const icon = await this.createIconRenderModel(
      svgFileName,
      x,
      y,
      width,
      height,
      role,
      config
    );

    return {
      id: fixedPos.id,
      type: fixedPos.type,
      role,
      x,
      y,
      width,
      height,
      backgroundColor: fixedPos.background_color,
      icon,
    };
  }

  /**
   * Create icon render model with computed size based on role
   */
  private async createIconRenderModel(
    svgFileName: string,
    cellX: number,
    cellY: number,
    cellWidth: number,
    cellHeight: number,
    role: CellRole,
    config: ShopfloorLayoutConfig
  ): Promise<IconRenderModel | undefined> {
    if (!svgFileName) return undefined;

    const svgUrl = `${this.svgBasePath}${svgFileName}`;
    
    // Fetch SVG metadata
    const metadata = await this.fetchSvgMetadata(svgUrl);
    if (!metadata) return undefined;

    // Get role-based sizing factor
    const sizingRules = config.icon_sizing_rules?.by_role || {
      intersection: 0.8,
      module_main_compartment: 0.8,
      module_sub_non_main: 0.9,
      company: 0.6,
      software: 0.6,
      default: 0.75,
    };
    const roleFactor = sizingRules[role] || sizingRules.default;

    // Compute final icon size using the formula from problem statement
    const targetW = cellWidth * roleFactor;
    const targetH = cellHeight * roleFactor;
    const scale = Math.min(targetW / metadata.width, targetH / metadata.height);
    const finalIconW = metadata.width * scale;
    const finalIconH = metadata.height * scale;

    // Center the icon within the cell
    const iconX = cellX + (cellWidth - finalIconW) / 2;
    const iconY = cellY + (cellHeight - finalIconH) / 2;

    return {
      svgUrl,
      x: iconX,
      y: iconY,
      width: finalIconW,
      height: finalIconH,
      intrinsicWidth: metadata.width,
      intrinsicHeight: metadata.height,
    };
  }

  /**
   * Fetch and parse SVG metadata (viewBox or width/height)
   */
  private async fetchSvgMetadata(svgUrl: string): Promise<SvgMetadata | null> {
    // Check cache first
    if (this.svgMetadataCache.has(svgUrl)) {
      return this.svgMetadataCache.get(svgUrl)!;
    }

    try {
      const svgContent = await firstValueFrom(
        this.http.get(svgUrl, { responseType: 'text' })
      );

      // Parse viewBox or width/height attributes
      const metadata = this.parseSvgMetadata(svgContent);
      
      // Cache the result
      this.svgMetadataCache.set(svgUrl, metadata);
      
      return metadata;
    } catch (error) {
      console.warn(`Failed to fetch SVG metadata for ${svgUrl}:`, error);
      return null;
    }
  }

  /**
   * Parse SVG content to extract dimensions
   */
  private parseSvgMetadata(svgContent: string): SvgMetadata {
    // Create a temporary parser
    const parser = new DOMParser();
    const doc = parser.parseFromString(svgContent, 'image/svg+xml');
    const svgElement = doc.querySelector('svg');

    if (!svgElement) {
      // Fallback to default
      return { width: 200, height: 200 };
    }

    // Try to get viewBox first
    const viewBox = svgElement.getAttribute('viewBox');
    if (viewBox) {
      const parts = viewBox.split(/\s+/);
      if (parts.length === 4) {
        const width = parseFloat(parts[2]);
        const height = parseFloat(parts[3]);
        if (!isNaN(width) && !isNaN(height)) {
          return { width, height, viewBox };
        }
      }
    }

    // Fallback to width/height attributes
    const widthAttr = svgElement.getAttribute('width');
    const heightAttr = svgElement.getAttribute('height');
    
    const width = widthAttr ? parseFloat(widthAttr) : 200;
    const height = heightAttr ? parseFloat(heightAttr) : 200;

    return { width, height };
  }

  /**
   * Create routes from roads configuration
   */
  private createRoutes(
    config: ShopfloorLayoutConfig,
    cells: CellRenderModel[],
    cellWidth: number,
    cellHeight: number
  ): RouteRenderModel[] {
    const routes: RouteRenderModel[] = [];
    
    // Build a lookup map for cell centers
    const cellCenters = new Map<string, [number, number]>();
    
    for (const cell of cells) {
      cellCenters.set(cell.id, [
        cell.x + cell.width / 2,
        cell.y + cell.height / 2,
      ]);
      
      // Also add by type for modules (serialNumber lookup)
      const module = config.modules.find(m => m.id === cell.id);
      if (module?.serialNumber) {
        cellCenters.set(module.serialNumber, [
          cell.x + cell.width / 2,
          cell.y + cell.height / 2,
        ]);
      }
    }

    // Process each road
    for (let i = 0; i < config.roads.length; i++) {
      const road = config.roads[i];
      const fromCenter = cellCenters.get(road.from);
      const toCenter = cellCenters.get(road.to);

      if (fromCenter && toCenter) {
        routes.push({
          id: `route-${i}`,
          points: [fromCenter, toCenter],
          strokeWidth: 2,
        });
      }
    }

    return routes;
  }

  /**
   * Map intersection type to SVG filename
   */
  private getIntersectionSvgName(type: string): string {
    // Extract number from type like "INTERSECTION-1" -> "intersection1.svg"
    const match = type.match(/INTERSECTION-(\d+)/i);
    if (match) {
      return `intersection${match[1]}.svg`;
    }
    return 'question.svg'; // fallback
  }

  /**
   * Map module type to SVG filename
   */
  private getModuleSvgName(type: string): string {
    const typeMap: Record<string, string> = {
      MILL: 'milling-machine.svg',
      DRILL: 'bohrer.svg',
      AIQS: 'ai-assistant.svg',
      HBW: 'warehouse.svg',
      DPS: 'conveyor.svg',
      CHRG: 'fuel.svg',
    };
    return typeMap[type] || 'factory.svg';
  }

  /**
   * Map subcell asset ID to SVG filename
   */
  private getSubcellSvgName(assetId: string): string {
    // For now, we don't have separate square SVGs, use stock as placeholder
    return 'stock.svg';
  }

  /**
   * Map fixed position type to SVG filename
   */
  private getFixedPositionSvgName(type: string): string {
    const typeMap: Record<string, string> = {
      ORBIS: 'ORBIS_logo_RGB.svg',
      DSP: 'information-technology.svg',
    };
    return typeMap[type] || 'factory.svg';
  }
}
