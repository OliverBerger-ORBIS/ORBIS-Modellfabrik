import { Injectable, inject } from '@angular/core';
import type {
  ShopfloorLayoutConfig,
  ShopfloorPoint,
  ParsedRoad,
  ShopfloorCellConfig,
  ShopfloorRoadEndpoint,
} from '../components/shopfloor-preview/shopfloor-layout.types';
import { ShopfloorMappingService } from './shopfloor-mapping.service';

export interface RouteSegment {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

/**
 * Service for FTS route calculation and pathfinding
 * Extracted from AgvTabComponent to improve maintainability and reusability
 */
@Injectable({ providedIn: 'root' })
export class AgvRouteService {
  private readonly mappingService = inject(ShopfloorMappingService);
  private parsedRoads: ParsedRoad[] = [];
  private cellById = new Map<string, ShopfloorCellConfig>();
  private cellByRouteRef = new Map<string, ShopfloorCellConfig>();
  private aliasToNodeKey = new Map<string, string>();
  private nodePoints = new Map<string, ShopfloorPoint>();

  /**
   * Check if layout has been initialized
   */
  isLayoutInitialized(): boolean {
    return this.nodePoints.size > 0;
  }
  
  /**
   * Get available node IDs (for debugging)
   */
  getAvailableNodeIds(): string[] {
    return Array.from(this.nodePoints.keys());
  }

  /**
   * Initialize the service with shopfloor layout configuration
   * Must be called before using route calculation methods
   */
  initializeLayout(config: ShopfloorLayoutConfig): void {
    // Roads are already parsed in config.parsed_roads
    this.parsedRoads = config.parsed_roads ?? [];

    // Initialize centralized mapping
    this.mappingService.initializeLayout(config);

    // Build cell map and route ref map
    this.cellById.clear();
    this.cellByRouteRef.clear();
    this.aliasToNodeKey.clear();
    this.nodePoints.clear();

    for (const cell of config.cells) {
      this.cellById.set(cell.id, cell);
    }

    // Register module aliases
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

    // Register intersection aliases
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

    // Register intersections
    const intersectionById = new Map<string, ShopfloorCellConfig>();
    Object.entries(config.intersection_map ?? {}).forEach(([id, cellId]) => {
      const cell = this.cellById.get(cellId);
      if (cell) {
        intersectionById.set(id, cell);
        registerIntersectionAliases(id, cell);
      }
    });

    // Register modules
    Object.entries(config.modules_by_serial ?? {}).forEach(([serial, meta]) => {
      const cell = this.cellById.get(meta.cell_id);
      if (cell) {
        registerModuleAliases(serial, cell);
      }
    });

    // Build node points map from parsed roads (with adjusted points for main compartments)
    const registerNode = (ref: string, point: ShopfloorPoint) => {
      // Get canonical ref (e.g., "intersection:1" or "serial:SVR3QA0022")
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

      // Store point under canonical ref
      if (!this.nodePoints.has(canonical)) {
        this.nodePoints.set(canonical, adjustedPoint);
      }

      // Also store under original ref for direct lookup
      if (ref !== canonical && !this.nodePoints.has(ref)) {
        this.nodePoints.set(ref, adjustedPoint);
      }

      // Register all aliases to point to canonical
      if (!this.aliasToNodeKey.has(ref)) {
        this.aliasToNodeKey.set(ref, canonical);
      }
    };

    // First, register all nodes from parsed roads
    for (const road of this.parsedRoads) {
      registerNode(road.from.ref, road.from.center);
      registerNode(road.to.ref, road.to.center);
    }

    // Then, explicitly register intersection points by their ID from intersection_map
    // This ensures that "1", "2", "3", "4" can be found directly
    Object.entries(config.intersection_map ?? {}).forEach(([id, cellId]) => {
      const cell = this.cellById.get(cellId);
      if (cell) {
        const center: ShopfloorPoint = {
          x: cell.position.x + cell.size.w / 2,
          y: cell.position.y + cell.size.h / 2,
        };
        // Register intersection by its ID (e.g., "1", "2", "3", "4")
        const canonical = `intersection:${id}`;
        if (!this.nodePoints.has(canonical)) {
          this.nodePoints.set(canonical, center);
        }
        if (!this.nodePoints.has(id)) {
          this.nodePoints.set(id, center);
        }
        // Also register cell.id and cell.name as aliases
        if (cell.id && !this.nodePoints.has(cell.id)) {
          this.nodePoints.set(cell.id, center);
        }
        if (cell.name && !this.nodePoints.has(cell.name)) {
          this.nodePoints.set(cell.name, center);
        }
      }
    });
  }

  /**
   * Resolve node reference to canonical form
   */
  resolveNodeRef(value: string | undefined): string | null {
    if (!value) {
      return null;
    }
    // Try direct lookup
    const direct =
      this.aliasToNodeKey.get(value) ??
      this.aliasToNodeKey.get(value.toLowerCase()) ??
      this.aliasToNodeKey.get(value.toUpperCase());
    if (direct) {
      return direct;
    }
    // Try intersection: prefix for numeric IDs
    if (value.match(/^\d+$/)) {
      const intersectionRef = `intersection:${value}`;
      if (this.aliasToNodeKey.has(intersectionRef)) {
        return intersectionRef;
      }
    }
    // Try serial: prefix for module serials
    if (value.match(/^[A-Z0-9]+$/)) {
      const serialRef = `serial:${value}`;
      if (this.aliasToNodeKey.has(serialRef)) {
        return serialRef;
      }
    }
    return value;
  }

  /**
   * Get node position by node ID
   */
  getNodePosition(nodeId: string): ShopfloorPoint | null {
    const resolvedId = this.resolveNodeRef(nodeId) ?? nodeId;
    return this.nodePoints.get(resolvedId) ?? this.nodePoints.get(nodeId) ?? null;
  }

  /**
   * Find route path using BFS (Breadth-First Search)
   */
  findRoutePath(start: string, target: string): string[] | null {
    // Resolve node references to canonical form
    const startRef = this.resolveNodeRef(start);
    const targetRef = this.resolveNodeRef(target);

    if (!startRef || !targetRef) {
      console.warn('[AgvRouteService] Cannot resolve node refs:', { start, target, startRef, targetRef });
      return null;
    }

    const graph = new Map<string, Set<string>>();
    for (const road of this.parsedRoads) {
      // Resolve road endpoints to canonical form
      const fromRef = this.resolveNodeRef(road.from.ref) ?? road.from.ref;
      const toRef = this.resolveNodeRef(road.to.ref) ?? road.to.ref;
      this.addEdge(graph, fromRef, toRef);
      this.addEdge(graph, toRef, fromRef);
    }

    const queue: string[] = [startRef];
    const visited = new Set<string>([startRef]);
    const previous = new Map<string, string>();

    while (queue.length > 0) {
      const current = queue.shift()!;
      if (current === targetRef) {
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

    if (!visited.has(targetRef)) {
      console.warn('[AgvRouteService] No path found:', {
        start,
        target,
        startRef,
        targetRef,
        graphSize: graph.size,
        graphKeys: Array.from(graph.keys()).slice(0, 10),
      });
      return null;
    }

    const path: string[] = [];
    let cursor: string | undefined = targetRef;
    while (cursor) {
      path.unshift(cursor);
      cursor = previous.get(cursor);
    }
    console.log('[AgvRouteService] Route path found:', { start, target, startRef, targetRef, path });
    return path;
  }

  /**
   * Find road between two nodes
   */
  findRoadBetween(a: string, b: string): ParsedRoad | null {
    return (
      this.parsedRoads.find((road) => road.from.ref === a && road.to.ref === b) ??
      this.parsedRoads.find((road) => road.from.ref === b && road.to.ref === a) ??
      null
    );
  }

  /**
   * Build road segment with trimmed endpoints
   */
  buildRoadSegment(road: ParsedRoad, trimToCenter: boolean = false): RouteSegment | null {
    const fromPoint = this.resolveRoutePoint(road.from);
    const toPoint = this.resolveRoutePoint(road.to);

    // Determine if the target node is a module (only modules get trimmed in Active Orders)
    const toCell = this.cellByRouteRef.get(road.to.ref);
    const isTargetModule = toCell?.role === 'module';

    // FTS-Tab: trimToCenter=true → route goes all the way to center (no trimming)
    // Active-Orders: trim when target is a module, otherwise go to center
    const shouldTrim = !trimToCenter && isTargetModule;

    if (shouldTrim) {
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

    // Route to exact centers (no trimming)
    return {
      x1: fromPoint.x,
      y1: fromPoint.y,
      x2: toPoint.x,
      y2: toPoint.y,
    };
  }

  /**
   * Compute stationary position: 60% of the route from intersection/road to module center
   */
  computeStationaryPosition(nodeId: string): ShopfloorPoint | null {
    // Resolve node ID to canonical form
    const resolvedId = this.resolveNodeRef(nodeId) ?? nodeId;
    let moduleCenter = this.nodePoints.get(resolvedId);

    // Try direct lookup if not found
    if (!moduleCenter) {
      moduleCenter = this.nodePoints.get(nodeId);
    }

    if (!moduleCenter) {
      console.warn('[AgvRouteService] Cannot find module center for stationary position:', nodeId, 'resolved:', resolvedId);
      return null;
    }

    // Find the road/intersection that connects to this module
    const connectedRoad = this.parsedRoads.find((road) => {
      const fromRef = this.resolveNodeRef(road.from.ref) ?? road.from.ref;
      const toRef = this.resolveNodeRef(road.to.ref) ?? road.to.ref;
      return fromRef === resolvedId || toRef === resolvedId || road.from.ref === nodeId || road.to.ref === nodeId;
    });

    if (!connectedRoad) {
      // No road found - try to find intersection connected to this module
      const allConnectedRoads = this.parsedRoads.filter((road) => {
        const fromRef = this.resolveNodeRef(road.from.ref) ?? road.from.ref;
        const toRef = this.resolveNodeRef(road.to.ref) ?? road.to.ref;
        return fromRef === resolvedId || toRef === resolvedId || road.from.ref === nodeId || road.to.ref === nodeId;
      });

      if (allConnectedRoads.length === 0) {
        // Still no road found, use module center directly (fallback)
        console.warn('[AgvRouteService] No connected road found for module:', nodeId, 'resolved:', resolvedId);
        return moduleCenter;
      }

      // Use first connected road
      const road = allConnectedRoads[0];
      const fromRef = this.resolveNodeRef(road.from.ref) ?? road.from.ref;
      const toRef = this.resolveNodeRef(road.to.ref) ?? road.to.ref;
      const isFromNode = fromRef === resolvedId || road.from.ref === nodeId;

      const otherEndpoint = isFromNode ? road.to.center : road.from.center;

      // Calculate 60% of the route from other endpoint to module center
      const direction = {
        x: moduleCenter.x - otherEndpoint.x,
        y: moduleCenter.y - otherEndpoint.y,
      };

      const distance = Math.hypot(direction.x, direction.y);
      if (distance === 0) return moduleCenter;

      // Position at 60% of the route to module center
      const ratio = 0.6;
      return {
        x: otherEndpoint.x + direction.x * ratio,
        y: otherEndpoint.y + direction.y * ratio,
      };
    }

    // Get the other endpoint (intersection or other module)
    const fromRef = this.resolveNodeRef(connectedRoad.from.ref) ?? connectedRoad.from.ref;
    const toRef = this.resolveNodeRef(connectedRoad.to.ref) ?? connectedRoad.to.ref;
    const isFromNode = fromRef === resolvedId || connectedRoad.from.ref === nodeId;

    const otherEndpoint = isFromNode ? connectedRoad.to.center : connectedRoad.from.center;

    // Calculate 60% of the route from other endpoint to module center
    const direction = {
      x: moduleCenter.x - otherEndpoint.x,
      y: moduleCenter.y - otherEndpoint.y,
    };

    const distance = Math.hypot(direction.x, direction.y);
    if (distance === 0) return moduleCenter;

    // Position at 60% of the route to module center
    const ratio = 0.6;
    return {
      x: otherEndpoint.x + direction.x * ratio,
      y: otherEndpoint.y + direction.y * ratio,
    };
  }

  // Private helper methods

  private addEdge(graph: Map<string, Set<string>>, from: string, to: string): void {
    if (!graph.has(from)) {
      graph.set(from, new Set());
    }
    graph.get(from)!.add(to);
  }

  private resolveRoutePoint(node: ShopfloorRoadEndpoint): ShopfloorPoint {
    const canonical = this.aliasToNodeKey.get(node.ref) ?? node.ref;
    const point = this.nodePoints.get(canonical) ?? node.center;
    return { ...point };
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
    return 0.2; // 20% inset = ~30% of route visible
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

  private distanceToBounds(
    point: ShopfloorPoint,
    direction: ShopfloorPoint,
    bounds: { left: number; top: number; width: number; height: number }
  ): number {
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
}


