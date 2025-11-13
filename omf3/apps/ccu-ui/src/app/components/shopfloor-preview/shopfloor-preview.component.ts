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
import type { OrderActive, ProductionStep } from '@omf3/entities';
import { SHOPFLOOR_ASSET_MAP } from '@omf3/testing-fixtures';

type GridTuple = [number, number];

interface ShopfloorModule {
  id: string;
  type: string;
  serialNumber?: string;
  position: GridTuple;
  cell_size?: GridTuple;
  is_compound?: boolean;
  attached_assets?: string[];
  compound_layout?: {
    positions: GridTuple[];
    size: GridTuple;
  };
  show_label?: boolean;
}

interface ShopfloorFixedPosition {
  id: string;
  type: string;
  position: GridTuple;
  cell_size?: GridTuple;
  background_color?: string;
}

interface ShopfloorIntersection {
  id: string;
  type: string;
  position: GridTuple;
}

interface ShopfloorRoad {
  from: string;
  to: string;
}

interface ShopfloorLayout {
  grid: {
    rows: number;
    columns: number;
    cell_size?: string;
  };
  modules: ShopfloorModule[];
  fixed_positions: ShopfloorFixedPosition[];
  intersections: ShopfloorIntersection[];
  roads: ShopfloorRoad[];
}

interface RenderBox {
  id: string;
  label: string;
  top: number;
  left: number;
  width: number;
  height: number;
  icon?: string;
  background?: string;
  attached?: RenderAttachment[];
  highlighted: boolean;
  compound?: boolean;
  compoundOffset?: number;
  mainHeight?: number;
  mainWidth?: number;
}

interface RenderAttachment {
  id: string;
  label: string;
  top: number;
  left: number;
  width: number;
  height: number;
  icon: string;
  highlighted: boolean;
}

interface RenderIntersection {
  id: string;
  top: number;
  left: number;
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

interface RoutePoint {
  x: number;
  y: number;
}

interface RouteOverlay {
  x: number;
  y: number;
  icon: string;
}

interface RouteComputation {
  segments?: RouteSegment[];
  endpoints?: RoutePoint[];
  overlay?: RouteOverlay;
  intersections?: string[];
}

interface ShopfloorView {
  width: number;
  height: number;
  modules: RenderBox[];
  fixedPositions: RenderBox[];
  intersections: RenderIntersection[];
  roads: RenderRoad[];
  activeRouteSegments?: RouteSegment[];
  routeEndpoints?: RoutePoint[];
  routeOverlay?: RouteOverlay;
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
  @Output() cellSelected = new EventEmitter<{ id: string; kind: 'module' | 'fixed' }>();

  viewModel: ShopfloorView | null = null;
  private layout?: ShopfloorLayout;

  constructor(
    private readonly http: HttpClient,
    private readonly cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.http
      .get<ShopfloorLayout>('shopfloor/shopfloor_layout.json')
      .subscribe({
        next: (layout) => {
          this.layout = layout;
          this.updateViewModel();
          this.cdr.markForCheck();
        },
        error: (err) => {
          console.error('Failed to load shopfloor layout', err);
        },
      });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (
      changes['activeStep'] ||
      changes['order'] ||
      changes['highlightModulesOverride'] ||
      changes['highlightFixedOverride']
    ) {
      this.updateViewModel();
    }
  }

  private updateViewModel(): void {
    if (!this.layout) {
      return;
    }

    const [cellWidth, cellHeight] = this.parseCellSize(this.layout.grid.cell_size);
    const width = Math.max(1, this.layout.grid.columns) * cellWidth;
    const height = Math.max(1, this.layout.grid.rows) * cellHeight;

    const highlightModules = new Set<string>();
    const highlightIntersections = new Set<string>();
    let routeSegments: RouteSegment[] | undefined;
    let routeEndpoints: RoutePoint[] | undefined;
    let routeOverlay: RouteOverlay | undefined;

    const nodeLookup = new Map<string, RoutePoint>();
    const intersectionLookup = new Map<string, RoutePoint>();

    this.layout.intersections.forEach((intersection) => {
      const center = this.computeCellCenter(intersection.position, cellWidth, cellHeight);
      nodeLookup.set(intersection.id, center);
      nodeLookup.set(intersection.type, center);
      intersectionLookup.set(intersection.id, center);
      intersectionLookup.set(intersection.type, center);
    });

    const step = this.activeStep ?? null;
    if (step) {
      if (step.type === 'MANUFACTURE') {
        if (step.moduleType) {
          highlightModules.add(step.moduleType);
        }
        if (step.dependentActionId === 'FTS' || step.moduleType === 'FTS') {
          highlightModules.add('FTS');
        }
      } else if (step.type === 'NAVIGATION') {
        highlightModules.add('FTS');
      }
    }

    const moduleHighlightSet =
      this.highlightModulesOverride && this.highlightModulesOverride.length > 0
        ? new Set(this.highlightModulesOverride)
        : highlightModules;

    const fixedHighlightSet =
      this.highlightFixedOverride && this.highlightFixedOverride.length > 0
        ? new Set(this.highlightFixedOverride)
        : highlightModules;

    const modules = this.layout.modules.map((mod) =>
      this.buildBox(mod, cellWidth, cellHeight, moduleHighlightSet, nodeLookup)
    );

    const fixedPositions = this.layout.fixed_positions.map((pos) =>
      this.buildFixedPosition(pos, cellWidth, cellHeight, fixedHighlightSet, nodeLookup)
    );

    const roads = this.layout.roads
      .map((road) => this.buildRoad(road, nodeLookup))
      .filter((road): road is RenderRoad => road !== null);

    if (step && step.type === 'NAVIGATION') {
      const route = this.computeRoute(step, intersectionLookup);
      routeSegments = route.segments;
      routeEndpoints = route.endpoints;
      routeOverlay = route.overlay;
      route.intersections?.forEach((key) => highlightIntersections.add(key));
    }

    const intersections = this.layout.intersections.map((node) =>
      this.buildIntersection(node, cellWidth, cellHeight, highlightIntersections, nodeLookup)
    );

    this.viewModel = {
      width,
      height,
      modules,
      fixedPositions,
      intersections,
      roads,
      activeRouteSegments: routeSegments,
      routeEndpoints,
      routeOverlay,
    };
  }

  private parseCellSize(cellSize?: string): [number, number] {
    if (!cellSize) {
      return [200, 200];
    }

    const [width, height] = cellSize.split('x').map((value) => Number.parseInt(value, 10));
    return [Number.isFinite(width) ? width : 200, Number.isFinite(height) ? height : 200];
  }

  private buildBox(
    mod: ShopfloorModule,
    cellWidth: number,
    cellHeight: number,
    highlightModules: Set<string>,
    nodeLookup: Map<string, { x: number; y: number }>
  ): RenderBox {
    const cellTop = mod.position[0] * cellHeight;
    const cellLeft = mod.position[1] * cellWidth;
    const width = mod.cell_size?.[0] ?? cellWidth;
    const compoundOffset = mod.is_compound ? (mod.compound_layout?.size?.[1] ?? 100) : 0;
    const height = mod.is_compound ? mod.cell_size?.[1] ?? cellHeight : cellHeight;
    const top = mod.is_compound ? Math.max(0, cellTop - compoundOffset) : cellTop;
    const left = cellLeft;

    const icon = this.getAssetPath(mod.type) ?? this.getAssetPath(mod.id);

    const highlighted =
      highlightModules.has(mod.id) ||
      highlightModules.has(mod.type) ||
      (!!mod.serialNumber && highlightModules.has(mod.serialNumber));

    const mainHeight = height - compoundOffset;
    const mainWidth = width;

    const centerX = left + mainWidth / 2;
    const centerY = mod.is_compound ? top + compoundOffset + mainHeight / 2 : top + height / 2;

    nodeLookup.set(mod.id, { x: centerX, y: centerY });
    nodeLookup.set(mod.type, { x: centerX, y: centerY });
    if (mod.serialNumber) {
      nodeLookup.set(mod.serialNumber, { x: centerX, y: centerY });
    }

    const attached =
      mod.attached_assets
        ?.map((asset, index) => {
          const iconPath = this.getAssetPath(asset);
          if (!iconPath) return null;

          const [offsetX, offsetY] = mod.compound_layout?.positions?.[index] ?? [index * 100, 0];
          const [childWidth, childHeight] = mod.compound_layout?.size ?? [100, 100];
          const scaleFactor = 0.56;
          const scaledWidth = childWidth * scaleFactor;
          const scaledHeight = childHeight * scaleFactor;

          const attachmentTop = offsetY + (childHeight - scaledHeight) / 2;
          const attachmentLeft = offsetX + (childWidth - scaledWidth) / 2;

          return {
            id: `${mod.id}-${asset}-${index}`,
            label: asset,
            top: attachmentTop,
            left: attachmentLeft,
            width: scaledWidth,
            height: scaledHeight,
            icon: iconPath,
            highlighted,
          } as RenderAttachment;
        })
        .filter((item): item is RenderAttachment => item !== null) ?? [];

    return {
      id: mod.id,
      label: mod.id,
      top,
      left,
      width,
      height,
      icon,
      highlighted,
      attached,
      compound: Boolean(mod.is_compound),
      compoundOffset,
      mainHeight,
      mainWidth,
    };
  }

  private buildFixedPosition(
    pos: ShopfloorFixedPosition,
    cellWidth: number,
    cellHeight: number,
    highlightModules: Set<string>,
    nodeLookup: Map<string, RoutePoint>
  ): RenderBox {
    const width = pos.cell_size?.[0] ?? cellWidth;
    const height = pos.cell_size?.[1] ?? cellHeight / 2;
    const top = pos.position[0] * cellHeight;
    const left = pos.position[1] * cellWidth;
    const icon = this.getAssetPath(pos.type);

    nodeLookup.set(pos.id, { x: left + width / 2, y: top + height / 2 });
    nodeLookup.set(pos.type, { x: left + width / 2, y: top + height / 2 });

    return {
      id: pos.id,
      label: pos.type,
      top,
      left,
      width,
      height,
      icon,
      background: pos.background_color,
      highlighted: highlightModules.has(pos.id) || highlightModules.has(pos.type),
    };
  }

  private buildIntersection(
    node: ShopfloorIntersection,
    cellWidth: number,
    cellHeight: number,
    highlight: Set<string>,
    lookup: Map<string, RoutePoint>
  ): RenderIntersection {
    const top = node.position[0] * cellHeight + cellHeight / 2;
    const left = node.position[1] * cellWidth + cellWidth / 2;

    lookup.set(node.id, { x: left, y: top });
    lookup.set(node.type, { x: left, y: top });

    return {
      id: node.id,
      top,
      left,
      highlighted: highlight.has(node.id) || highlight.has(node.type),
    };
  }

  private buildRoad(road: ShopfloorRoad, lookup: Map<string, RoutePoint>): RenderRoad | null {
    const start = this.lookupCoordinate(road.from, lookup);
    const end = this.lookupCoordinate(road.to, lookup);
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

  private findInLookup(
    key: string,
    lookup: Map<string, RoutePoint>
  ): RoutePoint | undefined {
    for (const variant of [key, key.toUpperCase(), key.toLowerCase()]) {
      const point = lookup.get(variant);
      if (point) {
        return point;
      }
    }
    return undefined;
  }

  private lookupCoordinate(
    key: string,
    lookup: Map<string, RoutePoint>,
    preferIntersection = false
  ): RoutePoint | undefined {
    const direct = this.findInLookup(key, lookup);

    if (preferIntersection) {
      const intersection = this.findConnectedIntersection(key, lookup);
      return intersection ?? direct;
    }

    if (direct) {
      return direct;
    }

    return this.findConnectedIntersection(key, lookup);
  }

  private findConnectedIntersection(
    key: string,
    lookup: Map<string, RoutePoint>
  ): RoutePoint | undefined {
    const linkedRoad = this.layout?.roads.find((r) => r.from === key || r.to === key);
    if (!linkedRoad) {
      return undefined;
    }

    const intersectionKey = linkedRoad.from === key ? linkedRoad.to : linkedRoad.from;
    return this.findInLookup(intersectionKey, lookup);
  }

  private getAssetPath(key?: string | null): string | undefined {
    if (!key) {
      return undefined;
    }
    const asset = SHOPFLOOR_ASSET_MAP[key];
    if (!asset) {
      return undefined;
    }
    return asset.startsWith('/') ? asset.slice(1) : asset;
  }

  private computeRouteMidpoint(segments: RouteSegment[]): RoutePoint | null {
    let totalLength = 0;
    for (const segment of segments) {
      totalLength += Math.hypot(segment.x2 - segment.x1, segment.y2 - segment.y1);
    }

    if (totalLength === 0) {
      return null;
    }

    const target = totalLength / 2;
    let accumulated = 0;

    for (const segment of segments) {
      const segmentLength = Math.hypot(segment.x2 - segment.x1, segment.y2 - segment.y1);
      if (accumulated + segmentLength >= target) {
        const remaining = target - accumulated;
        const ratio = remaining / segmentLength;
        return {
          x: segment.x1 + (segment.x2 - segment.x1) * ratio,
          y: segment.y1 + (segment.y2 - segment.y1) * ratio,
        };
      }
      accumulated += segmentLength;
    }

    const last = segments[segments.length - 1];
    return { x: last.x2, y: last.y2 };
  }

  private computeRoute(
    step: ProductionStep | null,
    intersectionLookup: Map<string, RoutePoint>
  ): RouteComputation {
    if (!step || step.type !== 'NAVIGATION') {
      return {};
    }

    const graph = this.buildGraphFromLayout();
    if (!graph) {
      return {};
    }

    const startKey = this.resolveRouteNodeKey(step.source, graph);
    const targetKey = this.resolveRouteNodeKey(step.target, graph);

    if (!startKey || !targetKey) {
      return {};
    }

    const path = this.findShortestPath(startKey, targetKey, graph);
    if (!path || path.length < 2) {
      return {};
    }

    const intersectionPath = this.extractIntersectionPath(path);
    if (intersectionPath.length < 2) {
      return {};
    }

    const segments = this.buildSegmentsFromIntersectionPath(intersectionPath, intersectionLookup);
    if (segments.length === 0) {
      return {};
    }

    const startPoint = intersectionLookup.get(
      this.canonicalIntersectionKey(intersectionPath[0]) ?? intersectionPath[0]
    );
    const endPoint = intersectionLookup.get(
      this.canonicalIntersectionKey(intersectionPath[intersectionPath.length - 1]) ??
        intersectionPath[intersectionPath.length - 1]
    );
    const endpoints = [startPoint, endPoint].filter((point): point is RoutePoint => Boolean(point));

    const overlayPoint = this.computeRouteMidpoint(segments);
    const ftsIcon = this.getAssetPath('FTS');
    const overlay = overlayPoint && ftsIcon ? { x: overlayPoint.x, y: overlayPoint.y, icon: ftsIcon } : undefined;

    return {
      segments,
      endpoints,
      overlay,
      intersections: intersectionPath,
    };
  }

  private buildGraphFromLayout(): Map<string, Set<string>> | null {
    if (!this.layout) {
      return null;
    }

    const graph = new Map<string, Set<string>>();

    const ensureNode = (key: string) => {
      if (!graph.has(key)) {
        graph.set(key, new Set());
      }
    };

    for (const road of this.layout.roads) {
      ensureNode(road.from);
      ensureNode(road.to);
      graph.get(road.from)!.add(road.to);
      graph.get(road.to)!.add(road.from);
    }

    return graph;
  }

  private resolveRouteNodeKey(key: string | undefined, graph: Map<string, Set<string>>): string | null {
    if (!this.layout || !key) {
      return null;
    }

    for (const variant of [key, key.toUpperCase(), key.toLowerCase()]) {
      if (graph.has(variant)) {
        return variant;
      }
    }

    const module = this.layout.modules.find((mod) =>
      [mod.id, mod.type, mod.serialNumber]
        .filter((alias): alias is string => typeof alias === 'string' && alias.length > 0)
        .map((alias) => alias.toLowerCase())
        .includes(key.toLowerCase())
    );

    if (module) {
      const connected = this.layout.roads.find((road) => road.from === module.serialNumber || road.to === module.serialNumber);
      if (connected) {
        const intersectionKey = this.canonicalIntersectionKey(connected.from === module.serialNumber ? connected.to : connected.from);
        if (intersectionKey && graph.has(intersectionKey)) {
          return intersectionKey;
        }
      }
    }

    const intersectionKey = this.canonicalIntersectionKey(key);
    if (intersectionKey && graph.has(intersectionKey)) {
      return intersectionKey;
    }

    return graph.has(key) ? key : null;
  }

  private findShortestPath(
    start: string,
    target: string,
    graph: Map<string, Set<string>>
  ): string[] | null {
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

  private extractIntersectionPath(path: string[]): string[] {
    if (!this.layout) {
      return [];
    }

    const intersections: string[] = [];

    for (let i = 0; i < path.length; i += 1) {
      const currentIntersection = this.canonicalIntersectionKey(path[i]);
      if (currentIntersection) {
        if (intersections[intersections.length - 1] !== currentIntersection) {
          intersections.push(currentIntersection);
        }
        continue;
      }

      const next = path[i + 1];
      const nextIntersection = next ? this.canonicalIntersectionKey(next) : null;
      if (nextIntersection) {
        if (intersections[intersections.length - 1] !== nextIntersection) {
          intersections.push(nextIntersection);
        }
      }
    }

    return intersections;
  }

  private buildSegmentsFromIntersectionPath(
    intersectionPath: string[],
    intersectionLookup: Map<string, RoutePoint>
  ): RouteSegment[] {
    const segments: RouteSegment[] = [];

    for (let i = 0; i < intersectionPath.length - 1; i += 1) {
      const fromKey = this.canonicalIntersectionKey(intersectionPath[i]) ?? intersectionPath[i];
      const toKey = this.canonicalIntersectionKey(intersectionPath[i + 1]) ?? intersectionPath[i + 1];

      const fromPoint = intersectionLookup.get(fromKey);
      const toPoint = intersectionLookup.get(toKey);

      if (!fromPoint || !toPoint) {
        continue;
      }

      segments.push({ x1: fromPoint.x, y1: fromPoint.y, x2: toPoint.x, y2: toPoint.y });
    }

    return segments;
  }

  private canonicalIntersectionKey(key: string): string | null {
    if (!this.layout) {
      return null;
    }

    const match = this.layout.intersections.find(
      (intersection) =>
        intersection.id === key ||
        intersection.type === key ||
        intersection.id === key.toUpperCase() ||
        intersection.id === key.toLowerCase()
    );

    return match?.id ?? null;
  }

  private trimSegmentAtIntersection(from: RoutePoint, to: RoutePoint): RouteSegment | null {
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const length = Math.hypot(dx, dy);

    if (length === 0) {
      return null;
    }

    const inset = 24; // keep a small gap to intersection center
    const ux = dx / length;
    const uy = dy / length;

    return {
      x1: from.x + ux * inset,
      y1: from.y + uy * inset,
      x2: to.x - ux * inset,
      y2: to.y - uy * inset,
    };
  }

  private computeCellCenter(position: GridTuple, cellWidth: number, cellHeight: number): RoutePoint {
    const [row, col] = position;
    return {
      x: col * cellWidth + cellWidth / 2,
      y: row * cellHeight + cellHeight / 2,
    };
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
      return $localize`:@@shopfloorPreviewNavLabel:Route ${step.source} → ${step.target}`;
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
    if (this.activeStep?.type === 'NAVIGATION') {
      return 'FTS';
    }
    return (this.order?.orderType ?? '').toUpperCase() || 'ORDER';
  }

  onModuleClick(box: RenderBox, event: MouseEvent): void {
    if (!this.selectionEnabled) {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    this.cellSelected.emit({ id: box.id, kind: 'module' });
  }

  onFixedClick(box: RenderBox, event: MouseEvent): void {
    if (!this.selectionEnabled) {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    this.cellSelected.emit({ id: box.id, kind: 'fixed' });
  }
}

