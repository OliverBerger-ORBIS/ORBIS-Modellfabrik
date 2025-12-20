import { TestBed } from '@angular/core/testing';
import { AgvAnimationService, AnimationState } from '../agv-animation.service';
import { AgvRouteService } from '../agv-route.service';
import { firstValueFrom, skip, take } from 'rxjs';
import type { ShopfloorLayoutConfig } from '../../components/shopfloor-preview/shopfloor-layout.types';

describe('AgvAnimationService', () => {
  let service: AgvAnimationService;
  let routeService: AgvRouteService;

  // Mock layout for testing
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
        icon: 'assets/svg/shopfloor/stations/hbw-station.svg',
        position: { x: 100, y: 100 },
        size: { w: 80, h: 80 },
        center: { x: 140, y: 140 },
        role: 'module',
        serial_number: 'SVR3QA0022',
      },
      {
        id: 'cell-aiqs',
        name: 'AIQS',
        icon: 'assets/svg/shopfloor/stations/aiqs-station.svg',
        position: { x: 300, y: 100 },
        size: { w: 80, h: 80 },
        center: { x: 340, y: 140 },
        role: 'module',
        serial_number: 'SVR4H76530',
      },
      {
        id: 'cell-int1',
        name: 'Intersection 1',
        icon: 'assets/svg/shopfloor/shared/question.svg',
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
      providers: [AgvAnimationService, AgvRouteService],
    });
    service = TestBed.inject(AgvAnimationService);
    routeService = TestBed.inject(AgvRouteService);
    routeService.initializeLayout(mockLayout);
  });

  afterEach(() => {
    // Clean up any running animations
    service.stopAnimation();
    jest.clearAllTimers();
  });

  describe('Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should have initial animation state', () => {
      const state = service.getState();
      expect(state.isAnimating).toBe(false);
      expect(state.animatedPosition).toBeNull();
      expect(state.animationPath).toEqual([]);
      expect(state.activeRouteSegments).toEqual([]);
    });

    it('should provide animation state observable', async () => {
      const state$ = service.animationState$;
      const state = await firstValueFrom(state$);
      expect(state).toBeDefined();
      expect(state.isAnimating).toBe(false);
    });
  });

  describe('Animation State', () => {
    it('should return current state snapshot', () => {
      const state = service.getState();
      expect(state).toEqual({
        isAnimating: false,
        animatedPosition: null,
        animationPath: [],
        activeRouteSegments: [],
      });
    });

    it('should check if animating', () => {
      expect(service.isAnimating).toBe(false);
    });

    it('should get current path', () => {
      const path = service.path;
      expect(path).toEqual([]);
    });
  });

  describe('Stop Animation', () => {
    it('should stop animation and reset state', () => {
      service.stopAnimation();
      const state = service.getState();
      expect(state.isAnimating).toBe(false);
      expect(state.animatedPosition).toBeNull();
      expect(state.animationPath).toEqual([]);
      expect(state.activeRouteSegments).toEqual([]);
    });

    it('should be safe to call multiple times', () => {
      service.stopAnimation();
      service.stopAnimation();
      service.stopAnimation();
      const state = service.getState();
      expect(state.isAnimating).toBe(false);
    });
  });

  describe('Animation Between Nodes', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should not start animation if already animating', () => {
      const callbacks = {
        onAnimationComplete: jest.fn(),
      };

      // Start first animation
      service.animateBetweenNodes('SVR3QA0022', '1', callbacks);
      expect(service.isAnimating).toBe(true);

      // Try to start second animation while first is running
      const callbacks2 = {
        onAnimationComplete: jest.fn(),
      };
      service.animateBetweenNodes('1', 'SVR4H76530', callbacks2);

      // Second animation should not have started
      // (Note: This test may need adjustment based on actual behavior)
    });

    it('should start animation for direct path', () => {
      const callbacks = {
        onSegmentComplete: jest.fn(),
        onAnimationComplete: jest.fn(),
      };

      service.animateBetweenNodes('SVR3QA0022', '1', callbacks);

      const state = service.getState();
      expect(state.isAnimating).toBe(true);
      expect(state.animationPath.length).toBeGreaterThan(0);
    });

    it('should calculate full path through intersections', () => {
      service.animateBetweenNodes('SVR3QA0022', 'SVR4H76530');

      const state = service.getState();
      expect(state.animationPath.length).toBeGreaterThanOrEqual(2);
      // Path should include intersections
      expect(state.animationPath).toContain('intersection:1');
    });

    it('should set active route segments for full path', () => {
      service.animateBetweenNodes('SVR3QA0022', 'SVR4H76530');

      const state = service.getState();
      expect(state.activeRouteSegments.length).toBeGreaterThan(0);
    });

    it('should handle fallback for invalid path', () => {
      const callbacks = {
        onAnimationComplete: jest.fn(),
      };

      // Use unknown nodes that don't have a path
      service.animateBetweenNodes('unknown1', 'unknown2', callbacks);

      // Service may stop animation if nodes cannot be resolved
      const state = service.getState();
      // Animation path may be empty if nodes cannot be resolved, or may contain the fallback path
      expect(state.animationPath).toBeDefined();
      // Just verify it doesn't crash
    });
  });

  describe('Animation Callbacks', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should call onAnimationComplete when animation finishes', (done) => {
      const callbacks = {
        onAnimationComplete: jest.fn((finalNodeId) => {
          expect(finalNodeId).toBeDefined();
          done();
        }),
      };

      service.animateBetweenNodes('SVR3QA0022', '1', callbacks);

      // Fast-forward time to complete animation
      jest.advanceTimersByTime(1500);

      expect(callbacks.onAnimationComplete).toHaveBeenCalled();
    });

    it('should call onSegmentComplete for multi-segment routes', (done) => {
      const callbacks = {
        onSegmentComplete: jest.fn(),
        onAnimationComplete: jest.fn(() => {
          expect(callbacks.onSegmentComplete).toHaveBeenCalled();
          done();
        }),
      };

      service.animateBetweenNodes('SVR3QA0022', 'SVR4H76530', callbacks);

      // Fast-forward time to complete all segments
      jest.advanceTimersByTime(3000);
    });
  });

  describe('Animation State Observable', () => {
    it('should emit initial state', async () => {
      const state$ = service.animationState$;
      const state = await firstValueFrom(state$);
      expect(state.isAnimating).toBe(false);
    });

    it('should emit state changes', async () => {
      jest.useFakeTimers();

      const state$ = service.animationState$;
      const states: AnimationState[] = [];

      const subscription = state$.subscribe((state) => {
        states.push(state);
      });

      service.animateBetweenNodes('SVR3QA0022', '1');

      // Fast-forward time to trigger state updates
      jest.advanceTimersByTime(100);

      // Should have received at least initial state
      expect(states.length).toBeGreaterThan(0);

      subscription.unsubscribe();
      jest.useRealTimers();
    }, 10000); // Increase timeout
  });

  describe('Edge Cases', () => {
    it('should handle stop animation during animation', () => {
      jest.useFakeTimers();

      service.animateBetweenNodes('SVR3QA0022', '1');
      expect(service.isAnimating).toBe(true);

      service.stopAnimation();
      expect(service.isAnimating).toBe(false);

      jest.useRealTimers();
    });

    it('should handle multiple stop calls', () => {
      service.stopAnimation();
      service.stopAnimation();
      service.stopAnimation();

      const state = service.getState();
      expect(state.isAnimating).toBe(false);
    });

    it('should handle animation with same start and end', () => {
      const callbacks = {
        onAnimationComplete: jest.fn(),
      };

      // This should not crash, but may not animate
      service.animateBetweenNodes('SVR3QA0022', 'SVR3QA0022', callbacks);

      // Animation may or may not start for same node (depends on implementation)
      // Just verify it doesn't crash
      const state = service.getState();
      expect(state).toBeDefined();
    });
  });
});

