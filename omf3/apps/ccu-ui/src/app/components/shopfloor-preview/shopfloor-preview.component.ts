import { CommonModule } from '@angular/common';
import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  EventEmitter,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges,
} from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { firstValueFrom } from 'rxjs';
import type { OrderActive, ProductionStep } from '@omf3/entities';
import { SHOPFLOOR_ASSET_MAP } from '@omf3/testing-fixtures';
import type {
  ParsedRoad,
  ShopfloorCellConfig,
  ShopfloorLayoutConfig,
  ShopfloorPoint,
  ShopfloorCellRole,
  ShopfloorRoadEndpoint,
} from './shopfloor-layout.types';

interface RenderAttachment {
  id: string;
  top: number;
  left: number;
  width: number;
  height: number;
  icon: string;
}

interface RenderModule {
  id: string;
  label: string;
  top: number;
  left: number;
  width: number;
  height: number;
  icon?: string;
  iconWidth: number;
  iconHeight: number;
  iconTop: number;
  iconLeft: number;
  highlighted: boolean;
  showLabel: boolean;
  attachments: RenderAttachment[];
}

interface RenderFixed {
  id: string;
  label: string;
  top: number;
  left: number;
  width: number;
  height: number;
  background?: string;
  icon?: string;
  highlighted: boolean;
  showLabel: boolean;
}

interface RenderIntersection {
  id: string;
  top: number;
  left: number;
  width: number;
  height: number;
  icon?: string;
  iconScale: number;
  highlighted: boolean;
}

interface RenderRoad {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

interface RouteSegment {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

interface RouteOverlay {
  x: number;
  y: number;
  icon: string;
  svgContent?: SafeHtml; // SVG content for inline rendering with color change
  width?: number;
  height?: number;
}

interface ShopfloorView {
  width: number;
  height: number;
  modules: RenderModule[];
  fixedPositions: RenderFixed[];
  intersections: RenderIntersection[];
  roads: RenderRoad[];
  activeRouteSegments?: RouteSegment[];
  routeEndpoints?: ShopfloorPoint[];
  routeOverlay?: RouteOverlay;
}

interface RouteGraphEdge {
  from: string;
  to: string;
}

@Component({
  standalone: true,
  selector: 'app-shopfloor-preview',
  imports: [CommonModule],
  templateUrl: './shopfloor-preview.component.html',
  styleUrl: './shopfloor-preview.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ShopfloorPreviewComponent implements OnInit, OnChanges {
  @Input({ required: true }) order: OrderActive | null | undefined;
  @Input() activeStep?: ProductionStep | null;
  @Input() scale = 0.6;
  @Input() highlightModulesOverride: string[] | null = null;
  @Input() highlightFixedOverride: string[] | null = null;
  @Input() selectionEnabled = false;
  @Input() badgeText?: string;
  @Input() infoText?: string;
  @Input() showBaseRoads = true;
  @Output() cellSelected = new EventEmitter<{ id: string; kind: 'module' | 'fixed' }>();
  @Output() cellDoubleClicked = new EventEmitter<{ id: string; kind: 'module' | 'fixed' }>();

  viewModel: ShopfloorView | null = null;

  private layoutConfig?: ShopfloorLayoutConfig;
  private parsedRoads: ParsedRoad[] = [];
  private cellById = new Map<string, ShopfloorCellConfig>();
  private aliasToNodeKey = new Map<string, string>();
  private nodePoints = new Map<string, ShopfloorPoint>();
  private cellByRouteRef = new Map<string, ShopfloorCellConfig>();
  private iconSizing = new Map<string, number>();

  constructor(
    private readonly http: HttpClient,
    private readonly cdr: ChangeDetectorRef,
    private readonly sanitizer: DomSanitizer
  ) {}

  ngOnInit(): void {
    this.http.get<ShopfloorLayoutConfig>('shopfloor/shopfloor_layout.json').subscribe({
      next: (config) => {
        this.layoutConfig = config;
        this.parsedRoads = config.parsed_roads ?? [];
        this.indexLayout(config);
        if (config.scaling && this.scale === 0.6) {
          this.scale = config.scaling.default_percent / 100;
        }
        this.updateViewModel();
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Failed to load shopfloor layout', error);
      },
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['activeStep'] || changes['order'] || changes['highlightModulesOverride'] || changes['highlightFixedOverride']) {
      this.updateViewModel();
    }
  }

  get infoLabel(): string {
    if (this.infoText) {
      return this.infoText;
    }
    const step = this.activeStep;
    if (!step) {
      return $localize`:@@shopfloorPreviewNoActiveStep:All steps completed.`;
    }
    if (step.type === 'NAVIGATION') {
      // Resolve source and target to readable names
      const source = step.source ?? '';
      const target = step.target ?? '';
      // Use direct values (e.g., "HBW", "DRILL") or resolve if needed
      const sourceName = source === 'START' ? $localize`:@@shopfloorPreviewStart:START` : source;
      const targetName = target === 'END' ? $localize`:@@shopfloorPreviewEnd:END` : target;
      return `${sourceName} → ${targetName}`;
    }
    if (step.moduleType) {
      return $localize`:@@shopfloorPreviewModuleLabel:Module ${step.moduleType}`;
    }
    return step.type;
  }

  get badgeLabel(): string {
    if (this.badgeText) {
      return this.badgeText;
    }
    const activeStep = this.activeStep;
    if (activeStep?.type === 'NAVIGATION') {
      return 'FTS';
    }
    const orderType = (this.order?.orderType ?? '').toUpperCase();
    if (orderType === 'STORAGE') {
      return $localize`:@@shopfloorPreviewBadgeStorage:STORAGE`;
    }
    return $localize`:@@shopfloorPreviewBadgeProduction:PRODUCTION`;
  }

  onModuleActivate(module: RenderModule, event: Event): void {
    if (!this.selectionEnabled) {
      return;
    }
    event.stopPropagation();
    this.cellSelected.emit({ id: module.id, kind: 'module' });
  }

  onModuleDouble(module: RenderModule, event: Event): void {
    if (!this.selectionEnabled) {
      return;
    }
    event.stopPropagation();
    this.cellDoubleClicked.emit({ id: module.id, kind: 'module' });
  }

  onFixedActivate(fixed: RenderFixed, event: Event): void {
    if (!this.selectionEnabled) {
      return;
    }
    event.stopPropagation();
    this.cellSelected.emit({ id: fixed.id, kind: 'fixed' });
  }

  onFixedDouble(fixed: RenderFixed, event: Event): void {
    if (!this.selectionEnabled) {
      return;
    }
    event.stopPropagation();
    this.cellDoubleClicked.emit({ id: fixed.id, kind: 'fixed' });
  }

  private indexLayout(config: ShopfloorLayoutConfig): void {
    this.cellById.clear();
    this.aliasToNodeKey.clear();
    this.nodePoints.clear();
    this.cellByRouteRef.clear();
    this.iconSizing.clear();

    Object.entries(config.icon_sizing_rules?.by_role ?? {}).forEach(([role, factor]) => {
      this.iconSizing.set(role, factor);
    });
    if (!this.iconSizing.has('default')) {
      this.iconSizing.set('default', 0.75);
    }

    for (const cell of config.cells) {
      this.cellById.set(cell.id, cell);
    }

    const serialToCellId = new Map<string, string>();
    Object.entries(config.modules_by_serial ?? {}).forEach(([serial, meta]) => {
      serialToCellId.set(serial, meta.cell_id);
    });

    const registerModuleAliases = (serial: string, cell: ShopfloorCellConfig) => {
      const canonical = `serial:${serial}`;
      this.cellByRouteRef.set(canonical, cell);
      this.aliasToNodeKey.set(canonical, canonical);
      [serial, cell.id, cell.name, cell.icon]
        .filter((alias): alias is string => Boolean(alias))
        .forEach((alias) => {
          this.aliasToNodeKey.set(alias, canonical);
          this.aliasToNodeKey.set(alias.toLowerCase(), canonical);
          this.aliasToNodeKey.set(alias.toUpperCase(), canonical);
        });
    };

    const registerIntersectionAliases = (intersectionId: string, cell: ShopfloorCellConfig) => {
      const canonical = `intersection:${intersectionId}`;
      this.cellByRouteRef.set(canonical, cell);
      this.aliasToNodeKey.set(canonical, canonical);
      [intersectionId, cell.id, cell.name]
        .filter((alias): alias is string => Boolean(alias))
        .forEach((alias) => {
          this.aliasToNodeKey.set(alias, canonical);
          this.aliasToNodeKey.set(alias.toLowerCase(), canonical);
          this.aliasToNodeKey.set(alias.toUpperCase(), canonical);
        });
    };

    const intersectionById = new Map<string, ShopfloorCellConfig>();
    Object.entries(config.intersection_map ?? {}).forEach(([id, cellId]) => {
      const cell = this.cellById.get(cellId);
      if (cell) {
        intersectionById.set(id, cell);
        registerIntersectionAliases(id, cell);
      }
    });

    for (const [serial, cellId] of serialToCellId.entries()) {
      const cell = this.cellById.get(cellId);
      if (cell) {
        registerModuleAliases(serial, cell);
      }
    }

    const registerNode = (ref: string, point: ShopfloorPoint) => {
      if (!this.nodePoints.has(ref)) {
        const canonical = this.aliasToNodeKey.get(ref) ?? ref;
        const cell = this.cellByRouteRef.get(canonical) ?? this.cellByRouteRef.get(ref);
        let adjustedPoint: ShopfloorPoint = { ...point };
        if (cell?.is_compound && cell.subcells) {
          const main = cell.subcells.find((sub) => sub.is_main);
          if (main) {
            adjustedPoint = {
              x: cell.position.x + main.position.x + main.size.w / 2,
              y: cell.position.y + main.position.y + main.size.h / 2,
            };
          }
        }
        this.nodePoints.set(ref, adjustedPoint);
      }
      if (!this.aliasToNodeKey.has(ref)) {
        this.aliasToNodeKey.set(ref, ref);
      }
    };

    for (const road of this.parsedRoads) {
      registerNode(road.from.ref, road.from.center);
      registerNode(road.to.ref, road.to.center);
    }
  }

  private updateViewModel(): void {
    if (!this.layoutConfig) {
      return;
    }

    const width = this.layoutConfig.metadata.canvas.width;
    const height = this.layoutConfig.metadata.canvas.height;

    const moduleHighlightSet = this.buildHighlightAliasSet(this.highlightModulesOverride);
    const fixedHighlightSet = this.buildHighlightAliasSet(this.highlightFixedOverride);
    this.applyActiveStepHighlights(moduleHighlightSet, fixedHighlightSet);

    const modules = this.layoutConfig.cells
      .filter((cell) => cell.role === 'module')
      .map((cell) => this.createModuleRender(cell, moduleHighlightSet));

    const fixedPositions = this.layoutConfig.cells
      .filter((cell) => cell.role === 'company' || cell.role === 'software')
      .map((cell) => this.createFixedRender(cell, fixedHighlightSet));

    const intersections = this.layoutConfig.cells
      .filter((cell) => cell.role === 'intersection')
      .map((cell) => this.createIntersectionRender(cell));

    const roads = this.showBaseRoads
      ? this.parsedRoads
          .map((road) => this.buildRoadSegment(road))
          .filter((segment): segment is RenderRoad => segment !== null)
      : [];

    const route = this.computeActiveRoute();

    this.viewModel = {
      width,
      height,
      modules,
      fixedPositions,
      intersections,
      roads,
      activeRouteSegments: route?.segments,
      routeEndpoints: route?.endpoints,
      routeOverlay: route?.overlay,
    };
  }

  private buildHighlightAliasSet(values: string[] | null): Set<string> {
    const set = new Set<string>();
    if (!values) {
      return set;
    }
    values.forEach((value) => this.addHighlightAlias(set, value));
    return set;
  }

  private addHighlightAlias(target: Set<string>, value: string | null | undefined): void {
    if (!value) {
      return;
    }
    target.add(value);
    const canonical = this.aliasToNodeKey.get(value) ?? this.aliasToNodeKey.get(value.toLowerCase());
    if (canonical) {
      target.add(canonical);
    }
  }

  private applyActiveStepHighlights(moduleSet: Set<string>, fixedSet: Set<string>): void {
    const step = this.activeStep;
    if (!step) {
      return;
    }

    if (step.type !== 'NAVIGATION' && step.moduleType) {
      this.addHighlightAlias(moduleSet, step.moduleType);
    }
  }

  private createModuleRender(cell: ShopfloorCellConfig, highlightAliases: Set<string>): RenderModule {
    const mainSubcell = cell.subcells?.find((sub) => sub.is_main);
    const iconArea = mainSubcell
      ? {
          x: mainSubcell.position.x,
          y: mainSubcell.position.y,
          width: mainSubcell.size.w,
          height: mainSubcell.size.h,
        }
      : { x: 0, y: 0, width: cell.size.w, height: cell.size.h };

    const mainScale = this.getRoleScale('module_main_compartment');
    const iconWidth = iconArea.width * mainScale;
    const iconHeight = iconArea.height * mainScale;
    const iconLeft = iconArea.x + (iconArea.width - iconWidth) / 2;
    const iconTop = iconArea.y + (iconArea.height - iconHeight) / 2;

    const iconKey = mainSubcell?.icon ?? cell.icon ?? cell.name ?? cell.id;
    const icon = this.getAssetPath(iconKey);

    const attachmentScale = this.getRoleScale('module_sub_non_main');
    const attachments: RenderAttachment[] = (cell.subcells ?? [])
      .filter((sub) => !sub.is_main)
      .map((sub) => {
        const scaledWidth = sub.size.w * attachmentScale;
        const scaledHeight = sub.size.h * attachmentScale;
        return {
          id: sub.id,
          top: sub.position.y + (sub.size.h - scaledHeight) / 2,
          left: sub.position.x + (sub.size.w - scaledWidth) / 2,
          width: scaledWidth,
          height: scaledHeight,
          icon: this.getAssetPath(sub.icon ?? sub.id) ?? '',
        };
      })
      .filter((attachment) => attachment.icon.length > 0);

    const highlightCandidates = [cell.id, cell.name ?? '', iconKey];
    if (cell.serial_number) {
      highlightCandidates.push(`serial:${cell.serial_number}`);
      highlightCandidates.push(cell.serial_number);
    }
    const highlighted = highlightCandidates.some((candidate) => candidate && highlightAliases.has(candidate));

    return {
      id: cell.id,
      label: cell.name ?? cell.id,
      top: cell.position.y,
      left: cell.position.x,
      width: cell.size.w,
      height: cell.size.h,
      icon,
      iconWidth,
      iconHeight,
      iconTop,
      iconLeft,
      highlighted,
      showLabel: cell.show_name !== false,
      attachments,
    };
  }

  private createFixedRender(cell: ShopfloorCellConfig, highlightAliases: Set<string>): RenderFixed {
    const iconKey = cell.icon ?? cell.name ?? cell.id;
    const icon = this.getAssetPath(iconKey);
    const highlightCandidates = [cell.id, cell.name ?? '', iconKey];
    const highlighted = highlightCandidates.some((candidate) => candidate && highlightAliases.has(candidate));

    return {
      id: cell.id,
      label: cell.name ?? cell.id,
      top: cell.position.y,
      left: cell.position.x,
      width: cell.size.w,
      height: cell.size.h,
      background: cell.background_color,
      icon,
      highlighted,
      showLabel: cell.show_name !== false,
    };
  }

  private createIntersectionRender(cell: ShopfloorCellConfig): RenderIntersection {
    const iconScale = this.getRoleScale('intersection');
    return {
      id: cell.id,
      top: cell.position.y,
      left: cell.position.x,
      width: cell.size.w,
      height: cell.size.h,
      icon: this.getAssetPath(cell.icon ?? cell.name ?? cell.id),
      iconScale,
      highlighted: false,
    };
  }

  private buildRoadSegment(road: ParsedRoad): RenderRoad | null {
    const fromPoint = this.resolveRoutePoint(road.from);
    const toPoint = this.resolveRoutePoint(road.to);
    const start = this.trimPointTowards(road.from.ref, fromPoint, toPoint);
    const end = this.trimPointTowards(road.to.ref, toPoint, fromPoint);
    if (!start || !end) {
      return null;
    }
    return {
      x1: start.x,
      y1: start.y,
      x2: end.x,
      y2: end.y,
    };
  }

  private trimPointTowards(ref: string, point: ShopfloorPoint, target: ShopfloorPoint): ShopfloorPoint | null {
    const cell = this.cellByRouteRef.get(ref);
    if (!cell) {
      return { ...point };
    }
    const direction = { x: target.x - point.x, y: target.y - point.y };
    const length = Math.hypot(direction.x, direction.y);
    if (length === 0) {
      return { ...point };
    }

    const insetFraction = this.getTrimInsetFraction(cell);
    if (insetFraction <= 0) {
      return { ...point };
    }

    const bounds = this.getCellBounds(cell);
    const distanceToEdge = this.distanceToBounds(point, direction, bounds);
    if (distanceToEdge <= 0) {
      return { ...point };
    }

    const margin = distanceToEdge * insetFraction;
    const travel = Math.max(0, distanceToEdge - margin);
    const ux = direction.x / length;
    const uy = direction.y / length;

    return {
      x: point.x + ux * travel,
      y: point.y + uy * travel,
    };
  }

  private getTrimInsetFraction(cell: ShopfloorCellConfig): number {
    if (cell.role === 'intersection') {
      return 0;
    }
    return 0.2;
  }

  private getCellBounds(cell: ShopfloorCellConfig): { left: number; top: number; width: number; height: number } {
    if (cell.is_compound && cell.subcells) {
      const main = cell.subcells.find((sub) => sub.is_main);
      if (main) {
        return {
          left: cell.position.x + main.position.x,
          top: cell.position.y + main.position.y,
          width: main.size.w,
          height: main.size.h,
        };
      }
    }
    return {
      left: cell.position.x,
      top: cell.position.y,
      width: cell.size.w,
      height: cell.size.h,
    };
  }

  private distanceToBounds(point: ShopfloorPoint, direction: ShopfloorPoint, bounds: { left: number; top: number; width: number; height: number }): number {
    const { left, top, width, height } = bounds;
    const right = left + width;
    const bottom = top + height;
    const length = Math.hypot(direction.x, direction.y);
    if (length === 0) {
      return 0;
    }
    const ux = direction.x / length;
    const uy = direction.y / length;
    const distances: number[] = [];

    if (Math.abs(ux) > 1e-6) {
      const boundaryX = ux > 0 ? right : left;
      const t = (boundaryX - point.x) / ux;
      if (t > 0) {
        distances.push(t);
      }
    }

    if (Math.abs(uy) > 1e-6) {
      const boundaryY = uy > 0 ? bottom : top;
      const t = (boundaryY - point.y) / uy;
      if (t > 0) {
        distances.push(t);
      }
    }

    return distances.length ? Math.min(...distances) : 0;
  }

  private getRoleScale(role: ShopfloorCellRole): number {
    const key = role.toLowerCase();
    if (this.iconSizing.has(role)) {
      return this.iconSizing.get(role)!;
    }
    if (this.iconSizing.has(key)) {
      return this.iconSizing.get(key)!;
    }
    return this.iconSizing.get('default') ?? 0.75;
  }

  private getAssetPath(key?: string | null): string | undefined {
    if (!key) {
      return undefined;
    }
    const asset = SHOPFLOOR_ASSET_MAP[key] ?? SHOPFLOOR_ASSET_MAP[key.toUpperCase()];
    if (!asset) {
      return undefined;
    }
    return asset.startsWith('/') ? asset.slice(1) : asset;
  }

  /**
   * Load SVG and change fill color from #154194 to orange (#f97316)
   * Returns SafeHtml for inline rendering
   */
  private async loadSvgWithOrangeFill(svgPath: string): Promise<SafeHtml | undefined> {
    try {
      const response = await firstValueFrom(this.http.get(svgPath, { responseType: 'text' }));
      if (!response) {
        return undefined;
      }
      // Replace all occurrences of #154194 (blue) with #f97316 (orange) in SVG
      // Also replace RGB equivalent rgb(21, 65, 148) and any stroke/fill attributes
      let orangeSvg = response.replace(/#154194/g, '#f97316');
      orangeSvg = orangeSvg.replace(/rgb\(21,\s*65,\s*148\)/gi, 'rgb(249, 115, 22)');
      orangeSvg = orangeSvg.replace(/fill="#154194"/g, 'fill="#f97316"');
      orangeSvg = orangeSvg.replace(/stroke="#154194"/g, 'stroke="#f97316"');
      orangeSvg = orangeSvg.replace(/fill:#154194/g, 'fill:#f97316');
      orangeSvg = orangeSvg.replace(/stroke:#154194/g, 'stroke:#f97316');
      
      // Debug: Check if replacement worked
      if (orangeSvg.includes('#154194')) {
        console.warn('[ShopfloorPreview] SVG color replacement may have failed, still contains #154194');
      }
      
      // Use bypassSecurityTrustHtml to preserve SVG content (SVG is safe)
      return this.sanitizer.bypassSecurityTrustHtml(orangeSvg);
    } catch (error) {
      console.error('Failed to load SVG:', error);
      return undefined;
    }
  }

  private computeActiveRoute(): { segments: RouteSegment[]; endpoints: ShopfloorPoint[]; overlay?: RouteOverlay } | null {
    if (!this.activeStep || this.activeStep.type !== 'NAVIGATION' || !this.layoutConfig) {
      return null;
    }

    const startRef = this.resolveNodeRef(this.activeStep.source);
    const targetRef = this.resolveNodeRef(this.activeStep.target);
    if (!startRef || !targetRef) {
      return null;
    }

    const path = this.findRoutePath(startRef, targetRef);
    if (!path || path.length < 2) {
      return null;
    }

    const segments: RouteSegment[] = [];
    const endpoints: ShopfloorPoint[] = [];

    for (let i = 0; i < path.length - 1; i += 1) {
      const from = path[i];
      const to = path[i + 1];
      const road = this.findRoadBetween(from, to);
      if (!road) {
        continue;
      }
      const segment = this.buildRoadSegment(road);
      if (!segment) {
        continue;
      }
      if (segments.length === 0) {
        endpoints.push({ x: segment.x1, y: segment.y1 });
      }
      segments.push(segment);
      if (i === path.length - 2) {
        endpoints.push({ x: segment.x2, y: segment.y2 });
      }
    }

    if (segments.length === 0) {
      return null;
    }

    const overlayPoint = this.computeRouteMidpoint(segments);
    const overlayIcon = this.getAssetPath('FTS');

    // Load SVG with orange fill color for FTS
    let svgContent: SafeHtml | undefined;
    if (overlayIcon) {
      // Ensure path starts with / for HttpClient
      const svgPath = overlayIcon.startsWith('/') ? overlayIcon : `/${overlayIcon}`;
      // Load SVG asynchronously - we'll handle this in updateViewModel
      this.loadSvgWithOrangeFill(svgPath).then((content) => {
        if (content && this.viewModel?.routeOverlay) {
          this.viewModel.routeOverlay.svgContent = content;
          this.cdr.markForCheck();
        }
      });
    }

    return {
      segments,
      endpoints,
      overlay:
        overlayPoint && overlayIcon
          ? { x: overlayPoint.x, y: overlayPoint.y, icon: overlayIcon, svgContent, width: 80, height: 80 }
          : undefined,
    };
  }

  private resolveNodeRef(value: string | undefined): string | null {
    if (!value) {
      return null;
    }
    const direct = this.aliasToNodeKey.get(value) ?? this.aliasToNodeKey.get(value.toLowerCase()) ?? this.aliasToNodeKey.get(value.toUpperCase());
    if (direct) {
      return direct;
    }
    if (value.startsWith('serial:') || value.startsWith('intersection:')) {
      return value;
    }
    return null;
  }

  private resolveRoutePoint(node: ShopfloorRoadEndpoint): ShopfloorPoint {
    const canonical = this.aliasToNodeKey.get(node.ref) ?? node.ref;
    const point = this.nodePoints.get(canonical) ?? node.center;
    return { ...point };
  }

  private findRoutePath(start: string, target: string): string[] | null {
    const graph = new Map<string, Set<string>>();
    for (const road of this.parsedRoads) {
      this.addEdge(graph, road.from.ref, road.to.ref);
      this.addEdge(graph, road.to.ref, road.from.ref);
    }

    const queue: string[] = [start];
    const visited = new Set<string>([start]);
    const previous = new Map<string, string>();

    while (queue.length > 0) {
      const current = queue.shift()!;
      if (current === target) {
        break;
      }
      for (const neighbor of graph.get(current) ?? []) {
        if (visited.has(neighbor)) {
          continue;
        }
        visited.add(neighbor);
        previous.set(neighbor, current);
        queue.push(neighbor);
      }
    }

    if (!visited.has(target)) {
      return null;
    }

    const path: string[] = [];
    let cursor: string | undefined = target;
    while (cursor) {
      path.unshift(cursor);
      cursor = previous.get(cursor);
    }
    return path;
  }

  private addEdge(graph: Map<string, Set<string>>, from: string, to: string): void {
    if (!graph.has(from)) {
      graph.set(from, new Set());
    }
    graph.get(from)!.add(to);
  }

  private findRoadBetween(a: string, b: string): ParsedRoad | null {
    return (
      this.parsedRoads.find((road) => road.from.ref === a && road.to.ref === b) ??
      this.parsedRoads.find((road) => road.from.ref === b && road.to.ref === a) ??
      null
    );
  }

  private computeRouteMidpoint(segments: RouteSegment[]): ShopfloorPoint | null {
    if (segments.length === 0) {
      return null;
    }

    const lengths = segments.map((segment) => Math.hypot(segment.x2 - segment.x1, segment.y2 - segment.y1));
    const totalLength = lengths.reduce((acc, value) => acc + value, 0);
    if (totalLength === 0) {
      return null;
    }

    let remaining = totalLength / 2;
    for (let i = 0; i < segments.length; i += 1) {
      const length = lengths[i];
      const segment = segments[i];
      if (remaining <= length) {
        const ratio = remaining / length;
        return {
          x: segment.x1 + (segment.x2 - segment.x1) * ratio,
          y: segment.y1 + (segment.y2 - segment.y1) * ratio,
        };
      }
      remaining -= length;
    }

    const last = segments[segments.length - 1];
    return { x: last.x2, y: last.y2 };
  }
}

