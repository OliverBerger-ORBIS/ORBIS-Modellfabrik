import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { Observable, forkJoin, map, switchMap, of } from 'rxjs';
import {
  ShopfloorLayout,
  ShopfloorModule,
  ShopfloorFixedPosition,
  ShopfloorIntersection,
  RenderCell,
  RenderSubcell,
  RenderRoad,
  ShopfloorRenderModel,
  SvgDimensions,
  ComputedIconSize,
} from './models';

/**
 * Asset mapping from logical keys to SVG file paths
 * Based on omf2 asset_manager.py pattern
 */
const ASSET_MAP: Record<string, string> = {
  MILL: 'shopfloor/milling-machine.svg',
  DRILL: 'shopfloor/bohrer.svg',
  HBW: 'shopfloor/stock.svg',
  DPS: 'shopfloor/robot-arm.svg',
  FTS: 'shopfloor/robotic.svg',
  AIQS: 'shopfloor/ai-assistant.svg',
  CHRG: 'shopfloor/fuel.svg',
  ORBIS: 'shopfloor/ORBIS_logo_RGB.svg',
  DSP: 'shopfloor/information-technology.svg',
  HBW_SQUARE1: 'shopfloor/factory.svg',
  HBW_SQUARE2: 'shopfloor/conveyor.svg',
  DPS_SQUARE1: 'shopfloor/warehouse.svg',
  DPS_SQUARE2: 'shopfloor/order-tracking.svg',
  'INTERSECTION-1': 'shopfloor/question.svg',
  'INTERSECTION-2': 'shopfloor/question.svg',
  'INTERSECTION-3': 'shopfloor/question.svg',
  'INTERSECTION-4': 'shopfloor/question.svg',
};

@Injectable({
  providedIn: 'root',
})
export class ShopfloorService {
  private layout?: ShopfloorLayout;
  private svgCache = new Map<string, string>();
  private svgDimensionsCache = new Map<string, SvgDimensions>();
  private highlightedCellIds = new Set<string>();

  constructor(
    private http: HttpClient,
    private sanitizer: DomSanitizer
  ) {}

  /**
   * Load shopfloor layout JSON
   */
  loadLayout(): Observable<ShopfloorLayout> {
    if (this.layout) {
      return of(this.layout);
    }

    return this.http.get<ShopfloorLayout>('shopfloor-layout.json').pipe(
      map((layout) => {
        this.layout = layout;
        return layout;
      })
    );
  }

  /**
   * Get SVG file path for a logical key
   */
  private getAssetPath(key: string): string | undefined {
    return ASSET_MAP[key];
  }

  /**
   * Fetch SVG content as text
   */
  private fetchSvgContent(path: string): Observable<string> {
    if (this.svgCache.has(path)) {
      return of(this.svgCache.get(path)!);
    }

    return this.http.get(path, { responseType: 'text' }).pipe(
      map((content) => {
        this.svgCache.set(path, content);
        return content;
      })
    );
  }

  /**
   * Parse SVG dimensions from viewBox or width/height attributes
   */
  private parseSvgDimensions(svgContent: string): SvgDimensions {
    const viewBoxMatch = svgContent.match(/viewBox=["']([^"']+)["']/);
    if (viewBoxMatch) {
      const [, , , width, height] = viewBoxMatch[1].split(/\s+/).map(Number);
      if (width && height) {
        return { width, height };
      }
    }

    const widthMatch = svgContent.match(/width=["'](\d+(?:\.\d+)?)["']/);
    const heightMatch = svgContent.match(/height=["'](\d+(?:\.\d+)?)["']/);
    if (widthMatch && heightMatch) {
      return {
        width: parseFloat(widthMatch[1]),
        height: parseFloat(heightMatch[1]),
      };
    }

    return { width: 200, height: 200 };
  }

  /**
   * Get SVG dimensions with caching
   */
  private getSvgDimensions(path: string): Observable<SvgDimensions> {
    if (this.svgDimensionsCache.has(path)) {
      return of(this.svgDimensionsCache.get(path)!);
    }

    return this.fetchSvgContent(path).pipe(
      map((content) => {
        const dimensions = this.parseSvgDimensions(content);
        this.svgDimensionsCache.set(path, dimensions);
        return dimensions;
      })
    );
  }

  /**
   * Compute final icon size using icon_sizing_rules
   */
  private computeIconSize(
    cellW: number,
    cellH: number,
    roleFactor: number,
    iconOrigW: number,
    iconOrigH: number
  ): ComputedIconSize {
    const targetW = cellW * roleFactor;
    const targetH = cellH * roleFactor;
    const scale = Math.min(targetW / iconOrigW, targetH / iconOrigH);
    const finalIconW = iconOrigW * scale;
    const finalIconH = iconOrigH * scale;

    // Center the icon in the cell
    const x = (cellW - finalIconW) / 2;
    const y = (cellH - finalIconH) / 2;

    return {
      width: finalIconW,
      height: finalIconH,
      x,
      y,
    };
  }

  /**
   * Build render model for modules
   */
  private buildModuleCells(
    modules: ShopfloorModule[],
    cellWidth: number,
    cellHeight: number
  ): Observable<RenderCell[]> {
    const cellObservables = modules.map((module) => {
      const x = module.position[1] * cellWidth;
      const y = module.position[0] * cellHeight;
      const assetPath = this.getAssetPath(module.type);

      if (!assetPath) {
        return of({
          id: module.id,
          type: module.type,
          label: module.id,
          x,
          y,
          width: module.cell_w,
          height: module.cell_h,
          highlighted: this.highlightedCellIds.has(module.id),
        } as RenderCell);
      }

      return forkJoin({
        svgContent: this.fetchSvgContent(assetPath),
        dimensions: this.getSvgDimensions(assetPath),
      }).pipe(
        switchMap(({ svgContent, dimensions }) => {
          const iconSize = this.computeIconSize(
            module.cell_w,
            module.cell_h,
            module.roleFactor,
            dimensions.width,
            dimensions.height
          );

          const cell: RenderCell = {
            id: module.id,
            type: module.type,
            label: module.id,
            x,
            y,
            width: module.cell_w,
            height: module.cell_h,
            icon: assetPath,
            iconSvg: this.sanitizer.bypassSecurityTrustHtml(svgContent),
            iconSize,
            highlighted: this.highlightedCellIds.has(module.id),
            is_compound: module.is_compound,
          };

          // Handle compound modules with subcells
          if (module.is_compound && module.attached_assets && module.compound_layout) {
            const subcellObservables = module.attached_assets.map((assetKey, index) => {
              const subcellAssetPath = this.getAssetPath(assetKey);
              if (!subcellAssetPath) {
                return of(null);
              }

              return forkJoin({
                svgContent: this.fetchSvgContent(subcellAssetPath),
                dimensions: this.getSvgDimensions(subcellAssetPath),
              }).pipe(
                map(({ svgContent, dimensions }) => {
                  const [offsetX, offsetY] = module.compound_layout!.positions[index];
                  const [subcellW, subcellH] = module.compound_layout!.size;
                  const roleFactor = this.layout?.icon_sizing_rules.by_role.attachment || 0.56;
                  const iconSize = this.computeIconSize(subcellW, subcellH, roleFactor, dimensions.width, dimensions.height);

                  return {
                    id: `${module.id}-${assetKey}`,
                    type: assetKey,
                    x: offsetX,
                    y: offsetY,
                    width: subcellW,
                    height: subcellH,
                    icon: subcellAssetPath,
                    iconSvg: this.sanitizer.bypassSecurityTrustHtml(svgContent),
                    iconSize,
                    highlighted: this.highlightedCellIds.has(module.id),
                  } as RenderSubcell;
                })
              );
            });

            return forkJoin(subcellObservables).pipe(
              map((subcells) => {
                cell.subcells = subcells.filter((s): s is RenderSubcell => s !== null);
                return cell;
              })
            );
          }

          return of(cell);
        })
      );
    });

    return forkJoin(cellObservables);
  }

  /**
   * Build render model for fixed positions
   */
  private buildFixedCells(
    fixedPositions: ShopfloorFixedPosition[],
    cellWidth: number,
    cellHeight: number
  ): Observable<RenderCell[]> {
    const cellObservables = fixedPositions.map((pos) => {
      const x = pos.position[1] * cellWidth;
      const y = pos.position[0] * cellHeight;
      const assetPath = this.getAssetPath(pos.type);

      if (!assetPath) {
        return of({
          id: pos.id,
          type: pos.type,
          label: pos.type,
          x,
          y,
          width: pos.cell_w,
          height: pos.cell_h,
          backgroundColor: pos.background_color,
          highlighted: this.highlightedCellIds.has(pos.id),
        } as RenderCell);
      }

      return forkJoin({
        svgContent: this.fetchSvgContent(assetPath),
        dimensions: this.getSvgDimensions(assetPath),
      }).pipe(
        map(({ svgContent, dimensions }) => {
          const iconSize = this.computeIconSize(pos.cell_w, pos.cell_h, pos.roleFactor, dimensions.width, dimensions.height);

          return {
            id: pos.id,
            type: pos.type,
            label: pos.type,
            x,
            y,
            width: pos.cell_w,
            height: pos.cell_h,
            icon: assetPath,
            iconSvg: this.sanitizer.bypassSecurityTrustHtml(svgContent),
            iconSize,
            backgroundColor: pos.background_color,
            highlighted: this.highlightedCellIds.has(pos.id),
          } as RenderCell;
        })
      );
    });

    return forkJoin(cellObservables);
  }

  /**
   * Build render model for intersections
   */
  private buildIntersectionCells(
    intersections: ShopfloorIntersection[],
    cellWidth: number,
    cellHeight: number
  ): Observable<RenderCell[]> {
    const cellObservables = intersections.map((intersection) => {
      const x = intersection.position[1] * cellWidth;
      const y = intersection.position[0] * cellHeight;
      const assetPath = this.getAssetPath(intersection.type);

      if (!assetPath) {
        return of({
          id: intersection.id,
          type: intersection.type,
          label: intersection.id,
          x,
          y,
          width: intersection.cell_w,
          height: intersection.cell_h,
          highlighted: this.highlightedCellIds.has(intersection.id),
        } as RenderCell);
      }

      return forkJoin({
        svgContent: this.fetchSvgContent(assetPath),
        dimensions: this.getSvgDimensions(assetPath),
      }).pipe(
        map(({ svgContent, dimensions }) => {
          const iconSize = this.computeIconSize(
            intersection.cell_w,
            intersection.cell_h,
            intersection.roleFactor,
            dimensions.width,
            dimensions.height
          );

          return {
            id: intersection.id,
            type: intersection.type,
            label: intersection.id,
            x,
            y,
            width: intersection.cell_w,
            height: intersection.cell_h,
            icon: assetPath,
            iconSvg: this.sanitizer.bypassSecurityTrustHtml(svgContent),
            iconSize,
            highlighted: this.highlightedCellIds.has(intersection.id),
          } as RenderCell;
        })
      );
    });

    return forkJoin(cellObservables);
  }

  /**
   * Build render model with computed icon sizes
   */
  getRenderModel(scale = 1.0): Observable<ShopfloorRenderModel> {
    return this.loadLayout().pipe(
      switchMap((layout) => {
        const { grid, modules, fixed_positions, intersections, parsed_roads } = layout;
        const cellWidth = grid.cell_width;
        const cellHeight = grid.cell_height;

        return forkJoin({
          moduleCells: this.buildModuleCells(modules, cellWidth, cellHeight),
          fixedCells: this.buildFixedCells(fixed_positions, cellWidth, cellHeight),
          intersectionCells: this.buildIntersectionCells(intersections, cellWidth, cellHeight),
        }).pipe(
          map(({ moduleCells, fixedCells, intersectionCells }) => {
            const allCells = [...moduleCells, ...fixedCells, ...intersectionCells];

            const roads: RenderRoad[] = parsed_roads.map((road, index) => ({
              id: `road-${index}`,
              from: road.from,
              to: road.to,
              points: road.points,
            }));

            return {
              width: grid.columns * cellWidth,
              height: grid.rows * cellHeight,
              cells: allCells,
              roads,
              scale,
            };
          })
        );
      })
    );
  }

  /**
   * Programmatically highlight a cell by id
   */
  highlightCell(cellId: string): void {
    this.highlightedCellIds.add(cellId);
  }

  /**
   * Clear cell highlighting
   */
  clearHighlights(): void {
    this.highlightedCellIds.clear();
  }

  /**
   * Toggle cell highlighting
   */
  toggleHighlight(cellId: string): void {
    if (this.highlightedCellIds.has(cellId)) {
      this.highlightedCellIds.delete(cellId);
    } else {
      this.highlightedCellIds.add(cellId);
    }
  }
}
