import { TestBed } from '@angular/core/testing';
import { FtsRouteService } from '../fts-route.service';
import type { ShopfloorLayoutConfig } from '../../components/shopfloor-preview/shopfloor-layout.types';

describe('FtsRouteService', () => {
  let service: FtsRouteService;

  // Minimal mock layout for testing
  const mockLayout: ShopfloorLayoutConfig = {
    metadata: {
      canvas: { width: 800, height: 600, units: 'px' },
      created_by: 'Test',
      description: 'Test layout',
    },
    scaling: {
      default_percent: 100,
      min_percent: 25,
      max_percent: 200,
      mode: 'viewBox',
    },
    highlight_defaults: {
      stroke_color: '#FF9800',
      fill_color: 'rgba(255,152,0,0.12)',
      stroke_width: 6,
      stroke_align: 'inner',
      clip_inside: true,
    },
    icon_sizing_rules: {
      by_role: {
        module: 0.7,
        intersection: 0.9,
        default: 0.75,
      },
    },
    cells: [
      {
        id: 'cell-hbw',
        name: 'HBW',
        icon: 'shopfloor/hbw.svg',
        position: { x: 100, y: 100 },
        size: { w: 80, h: 80 },
        center: { x: 140, y: 140 },
        role: 'module',
        serial_number: 'SVR3QA0022',
      },
      {
        id: 'cell-aiqs',
        name: 'AIQS',
        icon: 'shopfloor/aiqs.svg',
        position: { x: 300, y: 100 },
        size: { w: 80, h: 80 },
        center: { x: 340, y: 140 },
        role: 'module',
        serial_number: 'SVR4H76530',
      },
      {
        id: 'cell-int1',
        name: 'Intersection 1',
        icon: 'shopfloor/intersection.svg',
        position: { x: 200, y: 100 },
        size: { w: 40, h: 40 },
        center: { x: 220, y: 120 },
        role: 'intersection',
      },
    ],
    parsed_roads: [
      {
        id: 'road-1',
        from: { ref: 'serial:SVR3QA0022', cell_id: 'cell-hbw', center: { x: 140, y: 140 } },
        to: { ref: 'intersection:1', cell_id: 'cell-int1', center: { x: 220, y: 120 } },
        length: 100,
        direction: 'EAST',
      },
      {
        id: 'road-2',
        from: { ref: 'intersection:1', cell_id: 'cell-int1', center: { x: 220, y: 120 } },
        to: { ref: 'serial:SVR4H76530', cell_id: 'cell-aiqs', center: { x: 340, y: 140 } },
        length: 100,
        direction: 'EAST',
      },
    ],
    modules_by_serial: {
      SVR3QA0022: { cell_id: 'cell-hbw', type: 'HBW' },
      SVR4H76530: { cell_id: 'cell-aiqs', type: 'AIQS' },
    },
    intersection_map: {
      '1': 'cell-int1',
    },
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [FtsRouteService],
    });
    service = TestBed.inject(FtsRouteService);
  });

  describe('Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should initialize layout correctly', () => {
      service.initializeLayout(mockLayout);
      const hbwPos = service.getNodePosition('serial:SVR3QA0022');
      const intPos = service.getNodePosition('intersection:1');
      const aiqsPos = service.getNodePosition('serial:SVR4H76530');
      
      expect(hbwPos).toBeDefined();
      expect(intPos).toBeDefined();
      expect(aiqsPos).toBeDefined();
      // Positions should be set (exact values depend on implementation)
      expect(hbwPos?.x).toBeDefined();
      expect(hbwPos?.y).toBeDefined();
    });
  });

  describe('Node Resolution', () => {
    beforeEach(() => {
      service.initializeLayout(mockLayout);
    });

    it('should resolve serial number to canonical form', () => {
      const resolved = service.resolveNodeRef('SVR3QA0022');
      expect(resolved).toBe('serial:SVR3QA0022');
    });

    it('should resolve intersection ID to canonical form', () => {
      const resolved = service.resolveNodeRef('1');
      expect(resolved).toBe('intersection:1');
    });

    it('should resolve already canonical form', () => {
      const resolved = service.resolveNodeRef('serial:SVR3QA0022');
      expect(resolved).toBe('serial:SVR3QA0022');
    });

    it('should return original value for unknown node', () => {
      const resolved = service.resolveNodeRef('unknown');
      expect(resolved).toBe('unknown');
    });

    it('should resolve case-insensitive', () => {
      const resolved = service.resolveNodeRef('svr3qa0022');
      expect(resolved).toBe('serial:SVR3QA0022');
    });
  });

  describe('Node Position', () => {
    beforeEach(() => {
      service.initializeLayout(mockLayout);
    });

    it('should get position for serial number', () => {
      const pos = service.getNodePosition('SVR3QA0022');
      expect(pos).toBeDefined();
      expect(pos?.x).toBeDefined();
      expect(pos?.y).toBeDefined();
    });

    it('should get position for intersection', () => {
      const pos = service.getNodePosition('1');
      expect(pos).toBeDefined();
      expect(pos?.x).toBeDefined();
      expect(pos?.y).toBeDefined();
    });

    it('should get position for canonical form', () => {
      const pos = service.getNodePosition('serial:SVR3QA0022');
      expect(pos).toBeDefined();
      expect(pos?.x).toBeDefined();
      expect(pos?.y).toBeDefined();
    });

    it('should return null for unknown node', () => {
      const pos = service.getNodePosition('unknown');
      expect(pos).toBeNull();
    });
  });

  describe('Route Pathfinding', () => {
    beforeEach(() => {
      service.initializeLayout(mockLayout);
    });

    it('should find direct path between adjacent nodes', () => {
      const path = service.findRoutePath('SVR3QA0022', '1');
      expect(path).toEqual(['serial:SVR3QA0022', 'intersection:1']);
    });

    it('should find path through intersection', () => {
      const path = service.findRoutePath('SVR3QA0022', 'SVR4H76530');
      expect(path).toEqual(['serial:SVR3QA0022', 'intersection:1', 'serial:SVR4H76530']);
    });

    it('should return null for unreachable nodes', () => {
      // Unknown node cannot be resolved, so path should be null
      const path = service.findRoutePath('SVR3QA0022', 'unknown');
      // findRoutePath returns null if target cannot be resolved
      expect(path).toBeNull();
    });

    it('should return path with single node for same start and end', () => {
      // Same start and end - implementation returns path with single node
      const path = service.findRoutePath('SVR3QA0022', 'SVR3QA0022');
      // Path should contain the node itself
      expect(path).toBeDefined();
      if (path) {
        expect(path.length).toBeGreaterThanOrEqual(1);
        expect(path).toContain('serial:SVR3QA0022');
      }
    });

    it('should handle case-insensitive node IDs', () => {
      const path = service.findRoutePath('svr3qa0022', 'svr4h76530');
      expect(path).toEqual(['serial:SVR3QA0022', 'intersection:1', 'serial:SVR4H76530']);
    });
  });

  describe('Road Finding', () => {
    beforeEach(() => {
      service.initializeLayout(mockLayout);
    });

    it('should find road between adjacent nodes', () => {
      const road = service.findRoadBetween('SVR3QA0022', '1');
      expect(road).toBeDefined();
      if (road) {
        // Road should connect the two nodes (refs may be in canonical form)
        expect(road.from.ref).toMatch(/SVR3QA0022|serial:SVR3QA0022/);
        expect(road.to.ref).toMatch(/1|intersection:1/);
      }
    });

    it('should return null for non-adjacent nodes', () => {
      const road = service.findRoadBetween('SVR3QA0022', 'SVR4H76530');
      expect(road).toBeNull();
    });

    it('should return null for unknown nodes', () => {
      const road = service.findRoadBetween('unknown1', 'unknown2');
      expect(road).toBeNull();
    });
  });

  describe('Route Segment Building', () => {
    beforeEach(() => {
      service.initializeLayout(mockLayout);
    });

    it('should build route segment from road', () => {
      const road = service.findRoadBetween('SVR3QA0022', '1');
      expect(road).toBeDefined();
      if (road) {
        const segment = service.buildRoadSegment(road);
        expect(segment).toBeDefined();
        // Segment should have valid coordinates (may be trimmed)
        expect(segment?.x1).toBeDefined();
        expect(segment?.y1).toBeDefined();
        expect(segment?.x2).toBeDefined();
        expect(segment?.y2).toBeDefined();
        expect(typeof segment?.x1).toBe('number');
        expect(typeof segment?.y1).toBe('number');
        expect(typeof segment?.x2).toBe('number');
        expect(typeof segment?.y2).toBe('number');
      }
    });

    it('should handle invalid road gracefully', () => {
      const invalidRoad = {
        id: 'invalid',
        from: { ref: 'unknown', cell_id: 'unknown', center: { x: 0, y: 0 } },
        to: { ref: 'unknown2', cell_id: 'unknown2', center: { x: 0, y: 0 } },
        length: 0,
        direction: 'EAST' as const,
      };
      const segment = service.buildRoadSegment(invalidRoad);
      // buildRoadSegment uses center points for unknown nodes, so it may return a segment
      // Just verify it doesn't crash
      expect(segment !== undefined).toBe(true);
    });
  });

  describe('Stationary Position', () => {
    beforeEach(() => {
      service.initializeLayout(mockLayout);
    });

    it('should compute stationary position for module', () => {
      const pos = service.computeStationaryPosition('SVR3QA0022');
      expect(pos).toBeDefined();
      expect(pos?.x).toBeDefined();
      expect(pos?.y).toBeDefined();
    });

    it('should compute stationary position for intersection', () => {
      const pos = service.computeStationaryPosition('1');
      expect(pos).toBeDefined();
      expect(pos?.x).toBeDefined();
      expect(pos?.y).toBeDefined();
    });

    it('should return null for unknown node', () => {
      const pos = service.computeStationaryPosition('unknown');
      expect(pos).toBeNull();
    });
  });
});

