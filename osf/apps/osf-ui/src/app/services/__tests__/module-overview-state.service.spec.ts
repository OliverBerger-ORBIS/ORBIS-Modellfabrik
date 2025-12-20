import { TestBed } from '@angular/core/testing';
import { ModuleOverviewStateService } from '../module-overview-state.service';
import { firstValueFrom } from 'rxjs';
import type { ModuleOverviewState } from '@osf/entities';

describe('ModuleOverviewStateService', () => {
  let service: ModuleOverviewStateService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ModuleOverviewStateService],
    });
    service = TestBed.inject(ModuleOverviewStateService);
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
      const mockState: ModuleOverviewState = {
        modules: {},
        transports: {},
      };

      service.setState('test-env', mockState);
      const state = await firstValueFrom(service.getState$('test-env'));

      expect(state).toEqual(mockState);
    });

    it('should update state', async () => {
      const state1: ModuleOverviewState = {
        modules: {
          'module-1': {
            id: 'module-1',
            connected: true,
            availability: 'available',
            configured: true,
            messageCount: 0,
            lastUpdate: new Date().toISOString(),
          },
        },
        transports: {},
      };

      const state2: ModuleOverviewState = {
        modules: {
          'module-1': {
            id: 'module-1',
            connected: true,
            availability: 'busy',
            configured: true,
            messageCount: 1,
            lastUpdate: new Date().toISOString(),
          },
        },
        transports: {},
      };

      service.setState('test-env', state1);
      service.setState('test-env', state2);

      const state = await firstValueFrom(service.getState$('test-env'));
      expect(state).toEqual(state2);
    });

    it('should clear state', async () => {
      const mockState: ModuleOverviewState = {
        modules: {
          'module-1': {
            id: 'module-1',
            connected: true,
            availability: 'available',
            configured: true,
            messageCount: 0,
            lastUpdate: new Date().toISOString(),
          },
        },
        transports: {},
      };

      service.setState('test-env', mockState);
      service.clear('test-env');

      const state = await firstValueFrom(service.getState$('test-env'));
      expect(state).toBeNull();
    });

    it('should handle multiple environments independently', async () => {
      const state1: ModuleOverviewState = {
        modules: {
          'module-1': {
            id: 'module-1',
            connected: true,
            availability: 'available',
            configured: true,
            messageCount: 0,
            lastUpdate: new Date().toISOString(),
          },
        },
        transports: {},
      };

      const state2: ModuleOverviewState = {
        modules: {
          'module-2': {
            id: 'module-2',
            connected: true,
            availability: 'available',
            configured: true,
            messageCount: 0,
            lastUpdate: new Date().toISOString(),
          },
        },
        transports: {},
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
      const mockState: ModuleOverviewState = {
        modules: {
          'module-1': {
            id: 'module-1',
            connected: true,
            availability: 'available',
            configured: true,
            messageCount: 0,
            lastUpdate: new Date().toISOString(),
          },
        },
        transports: {},
      };

      service.setState('test-env', mockState);
      const snapshot = service.getSnapshot('test-env');

      expect(snapshot).toEqual(mockState);
    });

    it('should return null snapshot after clear', () => {
      const mockState: ModuleOverviewState = {
        modules: {
          'module-1': {
            id: 'module-1',
            connected: true,
            availability: 'available',
            configured: true,
            messageCount: 0,
            lastUpdate: new Date().toISOString(),
          },
        },
        transports: {},
      };

      service.setState('test-env', mockState);
      service.clear('test-env');
      const snapshot = service.getSnapshot('test-env');

      expect(snapshot).toBeNull();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty environment key', async () => {
      const mockState: ModuleOverviewState = {
        modules: {},
        transports: {},
      };

      service.setState('', mockState);
      const state = await firstValueFrom(service.getState$(''));

      expect(state).toEqual(mockState);
    });

    it('should handle very long environment key', async () => {
      const longKey = 'a'.repeat(1000);
      const mockState: ModuleOverviewState = {
        modules: {},
        transports: {},
      };

      service.setState(longKey, mockState);
      const state = await firstValueFrom(service.getState$(longKey));

      expect(state).toEqual(mockState);
    });

    it('should handle state with empty modules and transports', async () => {
      const emptyState: ModuleOverviewState = {
        modules: {},
        transports: {},
      };

      service.setState('test-env', emptyState);
      const state = await firstValueFrom(service.getState$('test-env'));

      expect(state).toEqual(emptyState);
    });

    it('should handle rapid state changes', async () => {
      const baseModule = {
        id: 'm1',
        connected: true,
        availability: 'available' as const,
        configured: true,
        messageCount: 0,
        lastUpdate: new Date().toISOString(),
      };

      const states: ModuleOverviewState[] = [
        { modules: { m1: { ...baseModule, availability: 'available' } }, transports: {} },
        { modules: { m1: { ...baseModule, availability: 'busy' } }, transports: {} },
        { modules: { m1: { ...baseModule, availability: 'unavailable' } }, transports: {} },
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
      const mockState: ModuleOverviewState = {
        modules: {
          'module-1': {
            id: 'module-1',
            connected: true,
            availability: 'available',
            configured: true,
            messageCount: 0,
            lastUpdate: new Date().toISOString(),
          },
        },
        transports: {},
      };

      service.setState('test-env', mockState);
      service.clear('test-env');
      service.clear('test-env');
      service.clear('test-env');

      const state = await firstValueFrom(service.getState$('test-env'));
      expect(state).toBeNull();
    });
  });
});

