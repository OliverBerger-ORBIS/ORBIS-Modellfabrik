import { TestBed } from '@angular/core/testing';
import { InventoryStateService } from '../inventory-state.service';
import { firstValueFrom } from 'rxjs';
import type { InventoryOverviewState } from '@omf3/entities';

describe('InventoryStateService', () => {
  let service: InventoryStateService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [InventoryStateService],
    });
    service = TestBed.inject(InventoryStateService);
  });

  describe('Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should return null for uninitialized state', async () => {
      const state$ = service.getState$('test-env');
      const state = await firstValueFrom(state$);
      expect(state).toBeNull();
    });

    it('should return null snapshot for uninitialized state', () => {
      const snapshot = service.getSnapshot('test-env');
      expect(snapshot).toBeNull();
    });
  });

  describe('State Management', () => {
    it('should set and get state', async () => {
      const mockState: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 5, WHITE: 3, RED: 2 },
        reservedCounts: { BLUE: 1, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      service.setState('test-env', mockState);
      const state = await firstValueFrom(service.getState$('test-env'));

      expect(state).toEqual(mockState);
    });

    it('should update state', async () => {
      const state1: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 5, WHITE: 0, RED: 0 },
        reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      const state2: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 10, WHITE: 0, RED: 0 },
        reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      service.setState('test-env', state1);
      service.setState('test-env', state2);

      const state = await firstValueFrom(service.getState$('test-env'));
      expect(state).toEqual(state2);
    });

    it('should clear state', async () => {
      const mockState: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 5, WHITE: 0, RED: 0 },
        reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      service.setState('test-env', mockState);
      service.clear('test-env');

      const state = await firstValueFrom(service.getState$('test-env'));
      expect(state).toBeNull();
    });

    it('should handle multiple environments independently', async () => {
      const state1: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 5, WHITE: 0, RED: 0 },
        reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      const state2: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 0, WHITE: 10, RED: 0 },
        reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      service.setState('env1', state1);
      service.setState('env2', state2);

      const env1State = await firstValueFrom(service.getState$('env1'));
      const env2State = await firstValueFrom(service.getState$('env2'));

      expect(env1State).toEqual(state1);
      expect(env2State).toEqual(state2);
    });
  });

  describe('Snapshot', () => {
    it('should return current snapshot', () => {
      const mockState: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 5, WHITE: 0, RED: 0 },
        reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      service.setState('test-env', mockState);
      const snapshot = service.getSnapshot('test-env');

      expect(snapshot).toEqual(mockState);
    });

    it('should return null snapshot after clear', () => {
      const mockState: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 5, WHITE: 0, RED: 0 },
        reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      service.setState('test-env', mockState);
      service.clear('test-env');
      const snapshot = service.getSnapshot('test-env');

      expect(snapshot).toBeNull();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty environment key', async () => {
      const mockState: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      service.setState('', mockState);
      const state = await firstValueFrom(service.getState$(''));

      expect(state).toEqual(mockState);
    });

    it('should handle very long environment key', async () => {
      const longKey = 'a'.repeat(1000);
      const mockState: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 5, WHITE: 0, RED: 0 },
        reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      service.setState(longKey, mockState);
      const state = await firstValueFrom(service.getState$(longKey));

      expect(state).toEqual(mockState);
    });

    it('should handle special characters in environment key', async () => {
      const specialKey = 'env-with-special-chars-!@#$%^&*()';
      const mockState: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 5, WHITE: 0, RED: 0 },
        reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      service.setState(specialKey, mockState);
      const state = await firstValueFrom(service.getState$(specialKey));

      expect(state).toEqual(mockState);
    });

    it('should handle state with empty available and reserved', async () => {
      const emptyState: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      service.setState('test-env', emptyState);
      const state = await firstValueFrom(service.getState$('test-env'));

      expect(state).toEqual(emptyState);
    });

    it('should handle state with all workpiece types', async () => {
      const fullState: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 10, WHITE: 20, RED: 30 },
        reservedCounts: { BLUE: 5, WHITE: 10, RED: 15 },
        lastUpdated: new Date().toISOString(),
      };

      service.setState('test-env', fullState);
      const state = await firstValueFrom(service.getState$('test-env'));

      expect(state).toEqual(fullState);
    });

    it('should handle rapid state changes', async () => {
      const states: InventoryOverviewState[] = [
        { slots: {}, availableCounts: { BLUE: 1, WHITE: 0, RED: 0 }, reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 }, lastUpdated: new Date().toISOString() },
        { slots: {}, availableCounts: { BLUE: 2, WHITE: 0, RED: 0 }, reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 }, lastUpdated: new Date().toISOString() },
        { slots: {}, availableCounts: { BLUE: 3, WHITE: 0, RED: 0 }, reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 }, lastUpdated: new Date().toISOString() },
      ];

      states.forEach((state) => {
        service.setState('test-env', state);
      });

      const finalState = await firstValueFrom(service.getState$('test-env'));
      expect(finalState).toEqual(states[states.length - 1]);
    });

    it('should handle clear on uninitialized environment', () => {
      expect(() => {
        service.clear('uninitialized-env');
      }).not.toThrow();

      const snapshot = service.getSnapshot('uninitialized-env');
      expect(snapshot).toBeNull();
    });

    it('should handle getSnapshot on uninitialized environment', () => {
      const snapshot = service.getSnapshot('uninitialized-env');
      expect(snapshot).toBeNull();
    });

    it('should handle multiple clears', async () => {
      const mockState: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 5, WHITE: 0, RED: 0 },
        reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      service.setState('test-env', mockState);
      service.clear('test-env');
      service.clear('test-env');
      service.clear('test-env');

      const state = await firstValueFrom(service.getState$('test-env'));
      expect(state).toBeNull();
    });

    it('should handle state with null-like values', async () => {
      const stateWithZeros: InventoryOverviewState = {
        slots: {},
        availableCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
        lastUpdated: new Date().toISOString(),
      };

      service.setState('test-env', stateWithZeros);
      const state = await firstValueFrom(service.getState$('test-env'));

      expect(state).toEqual(stateWithZeros);
    });
  });
});

